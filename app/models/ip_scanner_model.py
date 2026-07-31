"""
Model: Scanner de IPs
Responsável pela lógica de varredura de IPs usando UniFi, OCS e Ping
"""

import requests
import urllib3
import platform
import subprocess
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Callable
from enum import Enum

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IPStatus(Enum):
    """Status possíveis de um IP"""
    FREE = "free"
    OCCUPIED = "occupied"
    UNKNOWN = "unknown"


class IPSource(Enum):
    """Fonte de descoberta do IP"""
    UNIFI = "UniFi"
    OCS = "OCS"
    UNIFI_OCS = "UniFi+OCS"
    PING = "Ping"
    FREE = "Livre"


@dataclass
class IPInfo:
    """Classe de dados para informações de um IP"""
    ip_address: str
    name: str = "N/A"
    setor: str = "N/A"
    manufacturer: str = "N/A"
    model: str = "N/A"
    mac: str = "N/A"
    system: str = "N/A"
    ram: str = "N/A"
    source: str = "N/A"
    first_seen: str = "N/A"
    last_seen: str = "N/A"
    last_inventory: str = "N/A"
    status: IPStatus = IPStatus.UNKNOWN
    latency: str = "N/A"  # Latência em ms
    packet_loss: str = "N/A"  # Perda de pacotes em %
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "IP ADDRESS": self.ip_address,
            "NAME": self.name,
            "SETOR": self.setor,
            "MANUFACTURER": self.manufacturer,
            "MODEL": self.model,
            "MAC": self.mac,
            "SYSTEM": self.system,
            "RAM": self.ram,
            "SOURCE": self.source,
            "FIRST SEEN": self.first_seen,
            "LAST SEEN": self.last_seen,
            "LAST INVENTORY": self.last_inventory,
            "STATUS": self.status.value,
            "LATENCY": self.latency,
            "PACKET_LOSS": self.packet_loss
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'IPInfo':
        """Cria instância a partir de dicionário"""
        status_str = data.get("STATUS", "unknown")
        try:
            status = IPStatus(status_str)
        except ValueError:
            status = IPStatus.UNKNOWN
            
        return cls(
            ip_address=data.get("IP ADDRESS", "N/A"),
            name=data.get("NAME", "N/A"),
            setor=data.get("SETOR", "N/A"),
            manufacturer=data.get("MANUFACTURER", "N/A"),
            model=data.get("MODEL", "N/A"),
            mac=data.get("MAC", "N/A"),
            system=data.get("SYSTEM", "N/A"),
            ram=data.get("RAM", "N/A"),
            source=data.get("SOURCE", "N/A"),
            first_seen=data.get("FIRST SEEN", "N/A"),
            last_seen=data.get("LAST SEEN", "N/A"),
            last_inventory=data.get("LAST INVENTORY", "N/A"),
            status=status,
            latency=data.get("LATENCY", "N/A"),
            packet_loss=data.get("PACKET_LOSS", "N/A")
        )


class IPScannerModel:
    """
    Modelo principal para varredura de IPs.
    Consulta UniFi, OCS Reports e realiza ping para identificar IPs ocupados/livres.
    """
    
    def __init__(self, unifi_config: Dict = None, ocs_config: Dict = None,
                 scan_config: Dict = None, proxy_config: Dict = None):
        self.unifi_config = unifi_config or {}
        self.ocs_config = ocs_config or {}
        self.scan_config = scan_config or {}
        self.proxy_config = proxy_config or {}
        
        self.session = self._make_session(for_local_ip=True)
        
        self._is_scanning = False
        self._cancel_requested = False
        
    def configure(self, unifi_config: Dict = None, ocs_config: Dict = None,
                  scan_config: Dict = None, proxy_config: Dict = None):
        """Atualiza configurações"""
        if unifi_config:
            self.unifi_config = unifi_config
        if ocs_config:
            self.ocs_config = ocs_config
        if scan_config:
            self.scan_config = scan_config
        if proxy_config is not None:
            self.proxy_config = proxy_config
            self.session = self._make_session(for_local_ip=True)
    
    # ==================== Proxy / Session Helper ====================
    
    def _make_session(self, for_local_ip: bool = False) -> requests.Session:
        """
        Cria requests.Session com proxy configurado.
        
        Args:
            for_local_ip: Se True e bypass_local ativo, ignora proxy
                          (usado nos probes HTTP para IPs da rede local).
        """
        s = requests.Session()
        s.verify = False
        
        proxy_cfg = self.proxy_config
        enabled      = proxy_cfg.get('enabled', False)
        bypass_local = proxy_cfg.get('bypass_local', True)
        
        # Probes locais com bypass ativo → sem proxy nenhum
        if for_local_ip and bypass_local:
            s.trust_env = False
            s.proxies = {'http': '', 'https': ''}
            return s
        
        if enabled:
            host = proxy_cfg.get('host', '').strip()
            user = proxy_cfg.get('username', '').strip()
            pwd  = proxy_cfg.get('password', '')
            
            if host:
                if user and pwd:
                    from urllib.parse import urlparse, urlunparse
                    parsed = urlparse(host)
                    netloc = f'{user}:{pwd}@{parsed.hostname}'
                    if parsed.port:
                        netloc += f':{parsed.port}'
                    proxy_url = urlunparse((
                        parsed.scheme or 'http', netloc,
                        parsed.path, '', '', ''
                    ))
                else:
                    proxy_url = host
                s.proxies = {'http': proxy_url, 'https': proxy_url}
            else:
                s.trust_env = False
        else:
            # Proxy desabilitado → ignora config do sistema operacional
            s.trust_env = False
            s.proxies = {'http': '', 'https': ''}
        
        return s
    
    # ==================== UniFi Helpers ====================
    
    def login_unifi(self) -> bool:
        """Autentica no controlador UniFi"""
        try:
            host = self.unifi_config.get('host', '')
            url = f"{host}/api/login"
            payload = {
                "username": self.unifi_config.get('username', ''),
                "password": self.unifi_config.get('password', '')
            }
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[UniFi] Falha no login: {e}")
            return False
    
    def get_unifi_clients(self, site_name: str = 'default') -> List[Dict]:
        """Obtém lista de clientes do UniFi"""
        host = self.unifi_config.get('host', '')
        endpoints = [
            f"{host}/api/s/{site_name}/stat/alluser",
            f"{host}/api/s/{site_name}/stat/sta",
            f"{host}/api/s/{site_name}/rest/user",
            f"{host}/proxy/network/api/s/{site_name}/stat/alluser"
        ]
        
        all_clients = []
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)
                response.raise_for_status()
                data = response.json()
                clients = data.get('data', []) if isinstance(data, dict) else []
                all_clients.extend(clients)
            except Exception:
                continue
        
        # Unificar por MAC
        unique = {}
        for client in all_clients:
            mac = client.get('mac') or client.get('mac_addr')
            if mac:
                unique[mac] = client
        
        return list(unique.values())
    
    def find_unifi_by_ip(self, clients: List[Dict], ip: str) -> Optional[IPInfo]:
        """Busca informações de um IP na lista de clientes UniFi"""
        for client in clients:
            client_ip = (client.get('ip') or client.get('fixed_ip') or 
                        client.get('last_ip') or client.get('use_fixedip'))
            
            if client_ip == ip:
                return IPInfo(
                    ip_address=ip,
                    name=client.get('name') or client.get('hostname') or client.get('friendly_name') or 'N/A',
                    manufacturer=client.get('oui') or 'N/A',
                    mac=client.get('mac') or 'N/A',
                    source=IPSource.UNIFI.value,
                    first_seen=self._format_timestamp(client.get('first_seen')),
                    last_seen=self._format_timestamp(client.get('last_seen') or client.get('_last_seen_by_uap')),
                    status=IPStatus.OCCUPIED
                )
        return None
    
    # ==================== OCS Helpers ====================
    
    def fetch_all_ocs_computers(self, ip_filter: str = None, timeout: int = 30) -> Dict[str, Dict]:
        """
        Busca computadores do OCS filtrados por faixa de IP.
        Usa login via formulário e adiciona colunas extras.
        
        Colunas após adicionar extras:
        0:TAG, 1:Last inventory, 2:Computer, 3:User, 4:OS, 5:RAM, 6:CPU,
        7:Manufacturer, 8:Serial, 9:Model, 10:IP address, 11:Select, 12:Delete
        """
        try:
            base_url = self.ocs_config.get('base_url', '')
            username = self.ocs_config.get('username', '')
            password = self.ocs_config.get('password', '')
            
            if not base_url or not username:
                return {}
            
            if not ip_filter:
                ip_base = self.scan_config.get('ip_base', '203.0.113')
                ip_filter = f"{ip_base}."
            
            session = self._make_session(for_local_ip=True)
            
            # Construir URL corretamente
            url = base_url.rstrip('/')
            if '/index.php' not in url:
                url = f"{url}/index.php"
            
            # Passo 1: GET inicial para cookies
            try:
                session.get(url, timeout=10)
            except Exception:
                pass
            
            # Passo 2: Login via formulário
            login_data = {
                'LOGIN': username,
                'PASSWD': password,
                'Valid_CNX': 'Send',
            }
            
            response = session.post(url, data=login_data, timeout=10)
            
            # Verificar se login falhou (ainda mostra tela de login)
            if 'name=\'LOGIN\'' in response.text or 'name="LOGIN"' in response.text:
                return {}
            
            # Passo 3: Acessar All Computers
            session.get(url, params={'function': 'visu_computers'}, timeout=15)
            
            # Passo 4: Adicionar colunas extras
            colunas_extras = ['Manufacturer', 'Serial number', 'Model', 'IP address', 'RAM']
            for coluna in colunas_extras:
                form_data = {
                    'SHOW': 'SHOW',
                    'pcparpage': '1000000',
                    'restCollist_show_all': coluna,
                }
                try:
                    session.post(
                        url,
                        params={'function': 'visu_computers'},
                        data=form_data,
                        timeout=10
                    )
                except Exception:
                    pass
            
            # Passo 5: Aplicar filtro IP
            form_data = {
                'SHOW': 'SHOW',
                'pcparpage': '1000000',
                'FILTRE': 'h.ipaddr',
                'FILTRE_VALUE': ip_filter,
                'SUB_FILTRE': 'Filter',
            }
            
            response = session.post(
                url,
                params={'function': 'visu_computers'},
                data=form_data,
                timeout=timeout
            )
            
            if response.status_code != 200:
                return {}
            
            html = response.text
            ocs_data = {}
            
            # Detectar índices das colunas pelos cabeçalhos
            headers = re.findall(r"<th[^>]*>.*?</th>", html, re.S | re.I)
            
            col_map = {'computer': 2, 'manufacturer': 7, 'model': 9, 'ip': 10, 'lastdate': -1, 'osname': -1, 'ram': -1}  # Padrão
            
            for i, h in enumerate(headers):
                text = re.sub(r'<[^>]+>', '', h).strip()
                h_lower = h.lower()
                if 'Computer' in text and 'Id' not in text:
                    col_map['computer'] = i
                elif 'IP' in text.lower() and 'address' in text.lower():
                    col_map['ip'] = i
                elif 'Manufacturer' in text:
                    col_map['manufacturer'] = i
                elif 'Model' in text:
                    col_map['model'] = i
                elif 'Last' in text and ('date' in text.lower() or 'inventory' in text.lower() or 'seen' in text.lower()):
                    col_map['lastdate'] = i
                elif 'h.osname' in h_lower or 'operating system' in text.lower():
                    col_map['osname'] = i
                elif 'h.memory' in h_lower or text.strip().upper() == 'RAM' or text.strip().lower() == 'memory':
                    col_map['ram'] = i
            
            IDX_COMPUTER = col_map['computer']
            IDX_MANUFACTURER = col_map['manufacturer']
            IDX_MODEL = col_map['model']
            IDX_IP = col_map['ip']
            IDX_LASTDATE = col_map['lastdate']
            IDX_OSNAME = col_map['osname']
            IDX_RAM = col_map['ram']
            
            # Extrair dados do tbody
            tbody_match = re.search(r"<tbody[^>]*>(.*?)</tbody>", html, re.S | re.I)
            if not tbody_match:
                return {}
            
            tbody = tbody_match.group(1)
            rows = re.findall(r"<tr\s+class='ta'[^>]*>(.*?)</tr>", tbody, re.S | re.I)
            
            for row in rows:
                cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)
                
                if len(cells) <= max(IDX_COMPUTER, IDX_MANUFACTURER, IDX_MODEL, IDX_IP):
                    continue
                
                # Computer (NAME) - extrair do link <a>
                computer_cell = cells[IDX_COMPUTER]
                computer_match = re.search(r">([^<]+)</a>", computer_cell)
                computer_name = computer_match.group(1).strip() if computer_match else re.sub(r'<[^>]+>', '', computer_cell).strip()
                
                # Manufacturer - texto limpo
                manufacturer = re.sub(r'<[^>]+>', '', cells[IDX_MANUFACTURER]).strip()
                if manufacturer in ('&nbsp', '&nbsp;', ''):
                    manufacturer = 'N/A'
                
                # Model - texto limpo
                model = re.sub(r'<[^>]+>', '', cells[IDX_MODEL]).strip()
                if model in ('&nbsp', '&nbsp;', ''):
                    model = 'N/A'
                
                # Last inventory date (h.lastdate)
                lastdate = 'N/A'
                if IDX_LASTDATE >= 0 and IDX_LASTDATE < len(cells):
                    lastdate = re.sub(r'<[^>]+>', '', cells[IDX_LASTDATE]).strip()
                    if lastdate in ('&nbsp', '&nbsp;', ''):
                        lastdate = 'N/A'
                
                # OS Name (h.osname)
                osname = 'N/A'
                if IDX_OSNAME >= 0 and IDX_OSNAME < len(cells):
                    osname = re.sub(r'<[^>]+>', '', cells[IDX_OSNAME]).strip()
                    if osname in ('&nbsp', '&nbsp;', ''):
                        osname = 'N/A'
                
                # RAM (h.memory) — OCS armazena em MB
                ram = 'N/A'
                if IDX_RAM >= 0 and IDX_RAM < len(cells):
                    raw_ram = re.sub(r'<[^>]+>', '', cells[IDX_RAM]).strip()
                    if raw_ram and raw_ram not in ('&nbsp', '&nbsp;', ''):
                        try:
                            mb = int(raw_ram)
                            if mb >= 1024:
                                ram = f"{mb // 1024} GB"
                            else:
                                ram = f"{mb} MB"
                        except ValueError:
                            ram = raw_ram  # já vem formatado
                
                # IP address - texto limpo
                ip_address = re.sub(r'<[^>]+>', '', cells[IDX_IP]).strip()
                
                if ip_address and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_address):
                    ocs_data[ip_address] = {
                        'name': computer_name or 'N/A',
                        'manufacturer': manufacturer,
                        'model': model,
                        'last_inventory': lastdate,
                        'system': osname,
                        'ram': ram,
                    }
            
            return ocs_data
            
        except Exception:
            return {}
    
    def query_ocs_by_ip(self, ip: str, timeout: int = 8) -> Optional[IPInfo]:
        """Fallback - não usado"""
        return None
    
    # ==================== Utilitários ====================
    
    def _format_timestamp(self, ts) -> str:
        """Formata timestamp Unix para string legível"""
        try:
            return datetime.fromtimestamp(int(ts)).strftime('%d/%m/%Y %H:%M:%S')
        except Exception:
            return 'N/A'
    
    def ping_ip(self, ip: str, timeout: int = 1, count: int = 3) -> Tuple[bool, str, str]:
        """
        Realiza ping para verificar se IP está ativo.
        Retorna: (is_alive, latency_ms, packet_loss_percent)
        """
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                cmd = ['ping', '-n', str(count), '-w', str(int(timeout * 1000)), ip]
                creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout * count + 2,
                    creationflags=creationflags
                )
            else:
                cmd = ['ping', '-c', str(count), '-W', str(int(timeout)), ip]
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout * count + 2
                )
            
            output = proc.stdout
            is_alive = proc.returncode == 0
            
            # Extrair latência média
            latency = "N/A"
            if system == 'windows':
                # Windows: "Média = 5ms"
                match = re.search(r'[Mm].+[=:]\s*(\d+)\s*ms', output)
                if match:
                    latency = f"{match.group(1)} ms"
            else:
                # Linux: "rtt min/avg/max/mdev = 0.5/1.2/2.0/0.5 ms"
                match = re.search(r'rtt.+?=\s*[\d.]+/([\d.]+)/', output)
                if match:
                    latency = f"{float(match.group(1)):.1f} ms"
            
            # Extrair perda de pacotes
            packet_loss = "N/A"
            if system == 'windows':
                # Windows: "Perdidos = 0 (0% de perda)"
                match = re.search(r'\((\d+)%.*[Pp]erd', output)
                if match:
                    packet_loss = f"{match.group(1)}%"
                else:
                    match = re.search(r'(\d+)%\s*(loss|perda)', output, re.I)
                    if match:
                        packet_loss = f"{match.group(1)}%"
            else:
                # Linux: "3 packets transmitted, 3 received, 0% packet loss"
                match = re.search(r'(\d+)%\s*packet\s*loss', output)
                if match:
                    packet_loss = f"{match.group(1)}%"
            
            # Se está vivo mas não conseguiu extrair, assume valores bons
            if is_alive:
                if latency == "N/A":
                    latency = "< 1 ms"
                if packet_loss == "N/A":
                    packet_loss = "0%"
            
            return is_alive, latency, packet_loss
            
        except Exception:
            return False, "N/A", "100%"
    
    def generate_ip_list(self) -> List[str]:
        """Gera lista de IPs a serem escaneados baseado na configuração"""
        ip_base = self.scan_config.get('ip_base', '203.0.113')
        start_ip = self.scan_config.get('start_ip', 1)
        end_ip = self.scan_config.get('end_ip', 254)
        exclude_ranges = self.scan_config.get('exclude_ranges', [])
        
        ips = []
        for i in range(start_ip, end_ip + 1):
            # Verificar se está em faixa excluída
            excluded = False
            for exclude_start, exclude_end in exclude_ranges:
                if exclude_start <= i <= exclude_end:
                    excluded = True
                    break
            
            if not excluded:
                ips.append(f"{ip_base}.{i}")
        
        return ips
    
    # ==================== Intelbras Camera Detection ====================

    def probe_intelbras(self, ip: str) -> bool:
        """
        Detecta câmera/NVR/DVR Intelbras via HTTP.
        Considera positivo se a página de login contiver padrões
        exclusivos da interface web Intelbras (login_pin, GM_PIN, login_logo).
        Retorna True se identificado como câmera Intelbras.
        """
        INTELBRAS_MARKERS = [
            'id="login_pin"',
            "id='login_pin'",
            'id="GM_PIN"',
            "id='GM_PIN'",
            'id="login_logo"',
            "id='login_logo'",
            'id="GM_deviceName"',
            "id='GM_deviceName'",
            'login-input-item fn-hide',
        ]
        s = self._make_session(for_local_ip=True)
        for port in (80, 8080, 443):
            scheme = "https" if port == 443 else "http"
            url = f"{scheme}://{ip}" if port in (80, 443) else f"http://{ip}:{port}"
            try:
                r = s.get(url, timeout=3, allow_redirects=True, verify=False)
                if r.status_code == 200:
                    text = r.text
                    if any(marker in text for marker in INTELBRAS_MARKERS):
                        return True
            except Exception:
                continue
        return False

    # ==================== Grandstream VoIP Detection ====================
    
    def probe_grandstream(self, ip: str) -> Optional[Dict]:
        """
        Detecta telefone Grandstream via HTTP (Passo 1).
        Se HTTP 200 e webapp.nocache.js presente, e Grandstream.
        """
        base = f"http://{ip}"
        s = self._make_session(for_local_ip=True)
        try:
            r = s.get(base, timeout=3, allow_redirects=True)
            if r.status_code == 200 and "webapp.nocache.js" in r.text.lower():
                return {
                    'name':         'Grandstream',
                    'manufacturer': 'Grandstream',
                    'model':        'Grandstream',
                }
        except Exception:
            pass
        return None
    def scan_single_ip(self, ip: str, unifi_clients: List[Dict], ocs_cache: Dict = None) -> IPInfo:
        """Escaneia um único IP"""
        if self._cancel_requested:
            return IPInfo(ip_address=ip, status=IPStatus.UNKNOWN)
        
        timeout = self.scan_config.get('ping_timeout', 1)
        
        # Fazer ping primeiro para obter latência
        is_alive, latency, packet_loss = self.ping_ip(ip, timeout)
        
        # 1. Verificar UniFi
        info = self.find_unifi_by_ip(unifi_clients, ip) if unifi_clients else None
        
        if info:
            # Enriquecer com dados do OCS (do cache)
            if ocs_cache and ip in ocs_cache:
                ocs_data = ocs_cache[ip]
                if ocs_data.get('name') and ocs_data['name'] != 'N/A':
                    info.name = ocs_data['name']
                    info.source = IPSource.UNIFI_OCS.value
                if ocs_data.get('manufacturer') and ocs_data['manufacturer'] != 'N/A':
                    info.manufacturer = ocs_data['manufacturer']
                if ocs_data.get('model') and ocs_data['model'] != 'N/A':
                    info.model = ocs_data['model']
                if ocs_data.get('last_inventory') and ocs_data['last_inventory'] != 'N/A':
                    info.last_inventory = ocs_data['last_inventory']
                if ocs_data.get('system') and ocs_data['system'] != 'N/A':
                    info.system = ocs_data['system']
                if ocs_data.get('ram') and ocs_data['ram'] != 'N/A':
                    info.ram = ocs_data['ram']
            
            # Adicionar dados de ping
            info.latency = latency
            info.packet_loss = packet_loss
            
            # Detectar tipo de dispositivo pelo manufacturer (UniFi/OCS)
            mfr = (info.manufacturer or '').lower()
            if 'intelbras' in mfr:
                info.name   = info.name if info.name not in ('N/A', '') else 'Câmera'
                info.model  = info.model if info.model not in ('N/A', '') else 'Câmera'
                info.system = 'Câmera'
                info.ram    = 'Câmera'
                info.last_inventory = info.last_inventory if info.last_inventory not in ('N/A', '') else 'Câmera'
                info.source = 'HTTP' if info.source == IPSource.UNIFI.value else info.source
            elif 'grandstream' in mfr:
                info.name   = info.name if info.name not in ('N/A', '') else 'Telefone'
                info.model  = info.model if info.model not in ('N/A', '') else 'Telefone'
                info.system = 'Telefone'
                info.ram    = 'Telefone'
                info.last_inventory = info.last_inventory if info.last_inventory not in ('N/A', '') else 'Telefone'
                info.source = 'HTTP' if info.source == IPSource.UNIFI.value else info.source
            
            return info
        
        # 2. Verificar OCS (do cache)
        if ocs_cache and ip in ocs_cache:
            ocs_data = ocs_cache[ip]
            return IPInfo(
                ip_address=ip,
                name=ocs_data.get('name', 'N/A'),
                manufacturer=ocs_data.get('manufacturer', 'N/A'),
                model=ocs_data.get('model', 'N/A'),
                system=ocs_data.get('system', 'N/A'),
                ram=ocs_data.get('ram', 'N/A'),
                last_inventory=ocs_data.get('last_inventory', 'N/A'),
                source=IPSource.OCS.value,
                status=IPStatus.OCCUPIED,
                latency=latency,
                packet_loss=packet_loss
            )
        
        # 3. Verificar Ping
        if is_alive:
            # 3.1 Tentar detectar câmera Intelbras via HTTP
            if self.probe_intelbras(ip):
                return IPInfo(
                    ip_address=ip,
                    name='Câmera',
                    setor='Câmera',
                    manufacturer='Intelbras',
                    model='Câmera',
                    mac='Câmera',
                    system='Câmera',
                    ram='Câmera',
                    source='HTTP',
                    first_seen='Câmera',
                    last_seen='Câmera',
                    last_inventory='Câmera',
                    status=IPStatus.OCCUPIED,
                    latency=latency,
                    packet_loss=packet_loss
                )

            # 3.2 Tentar detectar telefone VoIP Grandstream
            # Tenta sempre — mesmo sem senha, a detecção pelo GWT já é suficiente
            gs_info = None
            try:
                gs_info = self.probe_grandstream(ip)
            except Exception:
                gs_info = None
            
            if gs_info:
                return IPInfo(
                    ip_address=ip,
                    name='Telefone',
                    manufacturer='Grandstream',
                    model='Telefone',
                    system='Telefone',
                    ram='Telefone',
                    last_inventory='Telefone',
                    source='HTTP',
                    status=IPStatus.OCCUPIED,
                    latency=latency,
                    packet_loss=packet_loss
                )
            
            return IPInfo(
                ip_address=ip,
                source=IPSource.PING.value,
                first_seen="Reachable",
                status=IPStatus.OCCUPIED,
                latency=latency,
                packet_loss=packet_loss
            )
        
        # 4. IP Livre
        return IPInfo(
            ip_address=ip,
            source=IPSource.FREE.value,
            status=IPStatus.FREE,
            latency="N/A",
            packet_loss="N/A"
        )
    
    def scan_all(
        self,
        progress_callback: Callable[[int, int, str], None] = None,
        complete_callback: Callable[[List[IPInfo], Set[str], Set[str]], None] = None
    ) -> Tuple[List[IPInfo], Set[str], Set[str]]:
        """
        Executa varredura completa de todos os IPs configurados.
        
        Args:
            progress_callback: Função chamada para reportar progresso (atual, total, mensagem)
            complete_callback: Função chamada ao completar (resultados, ips_livres, ips_ocupados)
        
        Returns:
            Tupla com (lista de IPInfo, set de IPs livres, set de IPs ocupados)
        """
        self._is_scanning = True
        self._cancel_requested = False
        
        results: List[IPInfo] = []
        free_ips: Set[str] = set()
        occupied_ips: Set[str] = set()
        
        # Conectar ao UniFi
        unifi_clients = []
        if progress_callback:
            progress_callback(0, 100, "Conectando ao UniFi...")
        
        if self.login_unifi():
            if progress_callback:
                progress_callback(0, 100, "Obtendo clientes UniFi...")
            unifi_clients = self.get_unifi_clients()
        
        # Buscar todos os computadores do OCS (uma única vez) filtrados pela faixa de IP
        ocs_cache = {}
        if progress_callback:
            progress_callback(0, 100, "Consultando OCS Inventory...")
        
        try:
            # Passar o filtro de IP baseado na configuração de scan
            ip_base = self.scan_config.get('ip_base', '203.0.113')
            ip_filter = f"{ip_base}."  # Ex: "203.0.113."
            
            ocs_cache = self.fetch_all_ocs_computers(ip_filter=ip_filter)
            if progress_callback:
                if ocs_cache:
                    progress_callback(0, 100, f"OCS: {len(ocs_cache)} computadores na faixa {ip_filter}")
                else:
                    progress_callback(0, 100, "OCS: Nenhum computador encontrado ou conexão falhou")
        except Exception:
            ocs_cache = {}
            if progress_callback:
                progress_callback(0, 100, "OCS: Erro na conexão")
        
        # Gerar lista de IPs
        ips = self.generate_ip_list()
        total = len(ips)
        
        if progress_callback:
            progress_callback(0, total, f"Escaneando {total} IPs...")
        
        # Escanear com ThreadPool
        max_workers = self.scan_config.get('max_workers', 30)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.scan_single_ip, ip, unifi_clients, ocs_cache): ip 
                for ip in ips
            }
            
            for future in as_completed(futures):
                if self._cancel_requested:
                    break
                    
                try:
                    info = future.result()
                    results.append(info)
                    
                    if info.status == IPStatus.FREE:
                        free_ips.add(info.ip_address)
                    else:
                        occupied_ips.add(info.ip_address)
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, f"Escaneado: {info.ip_address}")
                        
                except Exception as e:
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, f"Erro: {futures[future]}")
        
        # Ordenar por último octeto do IP
        results.sort(key=lambda x: int(x.ip_address.split('.')[-1]))
        
        self._is_scanning = False
        
        if complete_callback:
            complete_callback(results, free_ips, occupied_ips)
        
        return results, free_ips, occupied_ips
    
    def cancel_scan(self):
        """Cancela scan em andamento"""
        self._cancel_requested = True
    
    @property
    def is_scanning(self) -> bool:
        """Retorna se há scan em andamento"""
        return self._is_scanning
    
    # ==================== Atualização de Status ====================
    
    def update_status(
        self,
        ip_list: List[IPInfo],
        progress_callback: Callable[[int, int], None] = None
    ) -> List[IPInfo]:
        """
        Atualiza apenas o status (online/offline) dos IPs ocupados via ping.
        Mais rápido que scan completo.
        """
        occupied = [ip for ip in ip_list if ip.status == IPStatus.OCCUPIED]
        total = len(occupied)
        completed = 0
        
        max_workers = self.scan_config.get('max_workers', 30)
        timeout = self.scan_config.get('ping_timeout', 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.ping_ip, ip.ip_address, timeout): ip
                for ip in occupied
            }
            
            for future in as_completed(futures):
                ip_info = futures[future]
                try:
                    is_online = future.result()
                    # Mantém como OCCUPIED se responder ao ping
                    # (status não muda para FREE, apenas confirma que está ocupado)
                except Exception:
                    pass
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        return ip_list