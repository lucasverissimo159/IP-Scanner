"""
Configurações globais da aplicação IP Scanner
"""

import sys
import os
import json
from pathlib import Path


def _get_base_dir() -> Path:
    """
    Retorna o diretório base correto:
    - Executável PyInstaller (frozen): pasta onde o .exe está
    - Desenvolvimento: raiz do projeto (dois níveis acima deste arquivo)
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def _get_config_dir() -> Path:
    """
    Retorna o diretório de configurações por usuário:
    - Frozen (exe): %APPDATA%/IP Scanner Pro/  (cada usuário tem o seu)
    - Dev: <raiz_do_projeto>/config/
    """
    if getattr(sys, 'frozen', False):
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            return Path(appdata) / "IP Scanner Pro"
        # Fallback: ao lado do exe
        return Path(sys.executable).parent / "config"
    return Path(__file__).parent.parent / "config"


# Diretórios
BASE_DIR   = _get_base_dir()
CONFIG_DIR = _get_config_dir()
ASSETS_DIR = BASE_DIR / "app" / "assets"

# Arquivo de configurações persistentes
SETTINGS_FILE = CONFIG_DIR / "user_settings.json"

# Configurações padrão
DEFAULT_SETTINGS = {
    "unifi": {
        "host": "https://192.0.2.1:8443",
        "username": "usuario_exemplo",
        "password": "senha_exemplo"
    },
    "ocs": {
        "base_url": "http://198.51.100.245/ocsreports",
        "username": "usuario_exemplo",
        "password": "senha_exemplo"
    },
    "scan": {
        "ip_base": "203.0.113",
        "start_ip": 2,
        "end_ip": 253,
        "exclude_ranges": [[100, 199]],  # Faixa dos coletores
        "ping_timeout": 1,
        "max_workers": 30
    },
    "interface": {
        "auto_refresh": True,
        "refresh_interval": 10,  # 10 segundos
        "blink_interval": 800,    # milissegundos
        "theme": "light"
    },
    "proxy": {
        "enabled": False,
        "host": "",              # ex: http://proxy.empresa.com:3128
        "username": "",
        "password": "",
        "bypass_local": True     # ignora proxy para IPs locais (192.168.x.x, 10.x.x.x)
    }
}

# Cores dos temas (claro e escuro)
COLORS = {
    "light": {
        "bg_primary": "#f0f4f8",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#e2e8f0",
        "bg_card": "#ffffff",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "accent_dark": "#1e40af",
        "text_primary": "#1e293b",
        "text_secondary": "#64748b",
        "text_muted": "#94a3b8",
        "border": "#cbd5e1",
        "success": "#16a34a",
        "success_bg": "#dcfce7",
        "success_light": "#22c55e",
        "danger": "#dc2626",
        "danger_bg": "#fee2e2",
        "danger_light": "#ef4444",
        "warning": "#ea580c",
        "warning_bg": "#ffedd5",
        "info": "#0284c7",
        "info_bg": "#e0f2fe",
        "free": "#7c3aed",
        "free_bg": "#ede9fe",
        "free_blink": "#c4b5fd",
        "occupied": "#16a34a",
        "occupied_bg": "#dcfce7",
        "occupied_blink": "#86efac",
        "header_bg": "#e2e8f0",
        "row_even": "#ffffff",
        "row_odd": "#f8fafc",
        "row_hover": "#f1f5f9",
        "scrollbar": "#cbd5e1",
        "scrollbar_hover": "#94a3b8"
    },
    "dark": {
        "bg_primary": "#0f172a",
        "bg_secondary": "#1e293b",
        "bg_tertiary": "#334155",
        "bg_card": "#1e293b",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "accent_dark": "#1d4ed8",
        "text_primary": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "border": "#334155",
        "success": "#4ade80",
        "success_bg": "#14532d",
        "success_light": "#86efac",
        "danger": "#f87171",
        "danger_bg": "#7f1d1d",
        "danger_light": "#fca5a5",
        "warning": "#fb923c",
        "warning_bg": "#7c2d12",
        "info": "#38bdf8",
        "info_bg": "#0c4a6e",
        "free": "#a78bfa",
        "free_bg": "#2e1065",
        "free_blink": "#7c3aed",
        "occupied": "#4ade80",
        "occupied_bg": "#14532d",
        "occupied_blink": "#16a34a",
        "header_bg": "#1e293b",
        "row_even": "#1e293b",
        "row_odd": "#0f172a",
        "row_hover": "#334155",
        "scrollbar": "#334155",
        "scrollbar_hover": "#475569"
    }
}


def save_settings(settings):
    """Salva configurações no arquivo, criando a pasta config se necessário."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def load_settings():
    """
    Carrega configurações do arquivo.
    Se o arquivo não existir (primeira execução), cria a pasta config
    e grava o user_settings.json com os valores padrão automaticamente.
    """
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
                # Merge com padrões para garantir todas as chaves
                merged = DEFAULT_SETTINGS.copy()
                for key, value in user_settings.items():
                    if isinstance(value, dict) and key in merged:
                        merged[key].update(value)
                    else:
                        merged[key] = value
                return merged
        except Exception:
            # Arquivo corrompido — regrava com os padrões
            defaults = DEFAULT_SETTINGS.copy()
            save_settings(defaults)
            return defaults

    # Primeira execução: cria a pasta config e o arquivo com os padrões
    defaults = DEFAULT_SETTINGS.copy()
    save_settings(defaults)
    return defaults


def get_colors(theme="light"):
    """Retorna as cores do tema solicitado (light ou dark)"""
    return COLORS.get(theme, COLORS["light"])