"""
Controller: Gerencia a comunicação entre Model e View
"""

import threading
from typing import List, Set, Callable, Optional
from app.models import IPScannerModel, IPInfo, IPStatus
from config import load_settings, save_settings


class ScanController:
    """
    Controller principal para operações de scan.
    Gerencia threads e comunicação entre Model e View.
    """
    
    def __init__(self):
        self.settings = load_settings()
        self.model = IPScannerModel(
            unifi_config=self.settings.get('unifi', {}),
            ocs_config=self.settings.get('ocs', {}),
            scan_config=self.settings.get('scan', {}),
            proxy_config=self.settings.get('proxy', {})
        )
        
        self._scan_thread: Optional[threading.Thread] = None
        self._results: List[IPInfo] = []
        self._free_ips: Set[str] = set()
        self._occupied_ips: Set[str] = set()
        
        # Callbacks para a View
        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_complete: Optional[Callable[[List[IPInfo], Set[str], Set[str]], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def reload_settings(self):
        """Recarrega configurações do arquivo"""
        self.settings = load_settings()
        self.model.configure(
            unifi_config=self.settings.get('unifi', {}),
            ocs_config=self.settings.get('ocs', {}),
            scan_config=self.settings.get('scan', {}),
            proxy_config=self.settings.get('proxy', {})
        )
    
    def update_settings(self, section: str, values: dict):
        """Atualiza uma seção das configurações"""
        if section in self.settings:
            self.settings[section].update(values)
        else:
            self.settings[section] = values
        save_settings(self.settings)
        self.reload_settings()
    
    def get_setting(self, section: str, key: str = None):
        """Obtém valor de configuração"""
        if key:
            return self.settings.get(section, {}).get(key)
        return self.settings.get(section, {})
    
    def start_scan(self):
        """Inicia scan em thread separada"""
        if self.model.is_scanning:
            return
        
        self._scan_thread = threading.Thread(target=self._run_scan, daemon=True)
        self._scan_thread.start()
    
    def _run_scan(self):
        """Executa o scan (chamado pela thread)"""
        try:
            self._results, self._free_ips, self._occupied_ips = self.model.scan_all(
                progress_callback=self._on_progress,
                complete_callback=self._on_complete
            )
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
    
    def _on_progress(self, current: int, total: int, message: str):
        """Callback interno de progresso"""
        if self.on_progress:
            self.on_progress(current, total, message)
    
    def _on_complete(self, results: List[IPInfo], free_ips: Set[str], occupied_ips: Set[str]):
        """Callback interno de conclusão"""
        self._results = results
        self._free_ips = free_ips
        self._occupied_ips = occupied_ips
        
        if self.on_complete:
            self.on_complete(results, free_ips, occupied_ips)
    
    def cancel_scan(self):
        """Cancela scan em andamento"""
        self.model.cancel_scan()
    
    def get_results(self) -> List[IPInfo]:
        """Retorna resultados do último scan"""
        return self._results
    
    def get_free_ips(self) -> Set[str]:
        """Retorna IPs livres do último scan"""
        return self._free_ips
    
    def get_occupied_ips(self) -> Set[str]:
        """Retorna IPs ocupados do último scan"""
        return self._occupied_ips
    
    def get_statistics(self) -> dict:
        """Retorna estatísticas do último scan"""
        total = len(self._results)
        free = len(self._free_ips)
        occupied = len(self._occupied_ips)
        
        return {
            "total": total,
            "free": free,
            "occupied": occupied,
            "free_percent": (free / total * 100) if total > 0 else 0,
            "occupied_percent": (occupied / total * 100) if total > 0 else 0
        }
    
    def filter_results(
        self,
        status_filter: str = "all",
        search_term: str = ""
    ) -> List[IPInfo]:
        """
        Filtra resultados baseado em critérios.
        
        Args:
            status_filter: "all", "free", "occupied"
            search_term: Texto para buscar em nome, IP, MAC
        """
        filtered = self._results.copy()
        
        # Filtro de status
        if status_filter == "free":
            filtered = [ip for ip in filtered if ip.status == IPStatus.FREE]
        elif status_filter == "occupied":
            filtered = [ip for ip in filtered if ip.status == IPStatus.OCCUPIED]
        
        # Filtro de busca
        if search_term:
            search_lower = search_term.lower()
            filtered = [
                ip for ip in filtered
                if (search_lower in ip.ip_address.lower() or
                    search_lower in ip.name.lower() or
                    search_lower in ip.mac.lower() or
                    search_lower in ip.manufacturer.lower())
            ]
        
        return filtered
    
    def parse_ip_range(self, ip_range_str: str) -> dict:
        """
        Converte string de faixa de IP para configuração.
        Exemplos:
            "203.0.113.1-254" -> {"ip_base": "203.0.113", "start_ip": 1, "end_ip": 254}
            "203.0.113.1" -> {"ip_base": "203.0.113", "start_ip": 1, "end_ip": 254}
        """
        try:
            parts = ip_range_str.strip().split('.')
            
            if len(parts) != 4:
                raise ValueError("IP inválido")
            
            ip_base = '.'.join(parts[:3])
            last_part = parts[3]
            
            if '-' in last_part:
                start_str, end_str = last_part.split('-')
                start_ip = int(start_str)
                end_ip = int(end_str)
            else:
                # Se só passar um IP, assume range de 1 a 254
                start_ip = 1
                end_ip = 254
            
            # Validações
            if not (0 <= start_ip <= 255 and 0 <= end_ip <= 255):
                raise ValueError("Octeto fora do range")
            if start_ip > end_ip:
                start_ip, end_ip = end_ip, start_ip
            
            return {
                "ip_base": ip_base,
                "start_ip": start_ip,
                "end_ip": end_ip
            }
            
        except Exception as e:
            raise ValueError(f"Formato de IP inválido: {e}")
    
    @property
    def is_scanning(self) -> bool:
        """Verifica se há scan em andamento"""
        return self.model.is_scanning