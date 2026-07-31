# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec para IP Scanner Pro
Gera em: dist/IP Scanner Pro/
Execute: pyinstaller ip_scanner.spec --noconfirm
"""

import os
import sys
import importlib

block_cipher = None
PROJECT_ROOT = os.path.abspath('.')

# Localizar customtkinter (obrigatorio para temas/assets)
ctk_path = os.path.dirname(importlib.import_module('customtkinter').__file__)

# Localizar reportlab (fontes internas)
rl_path = os.path.dirname(importlib.import_module('reportlab').__file__)

# Icone (se existir)
icon_path = os.path.join(PROJECT_ROOT, 'resources', 'icon', 'icon.ico')
if not os.path.exists(icon_path):
    icon_path = None

a = Analysis(
    ['main.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        # customtkinter assets (temas, imagens internas)
        (ctk_path, 'customtkinter'),
        # reportlab fonts (Helvetica, etc.)
        (os.path.join(rl_path, 'fonts'), os.path.join('reportlab', 'fonts')),
        # Resources do projeto (icone, etc.)
        (os.path.join(PROJECT_ROOT, 'resources'), 'resources'),
    ],
    hiddenimports=[
        # === Projeto ===
        'app',
        'app.models',
        'app.models.ip_scanner_model',
        'app.views',
        'app.views.main_window',
        'app.views.components',
        'app.controllers',
        'app.controllers.scan_controller',
        'config',
        'config.settings',
        # === UI ===
        'customtkinter',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # === Rede ===
        'requests',
        'urllib3',
        'urllib3.util',
        'urllib3.util.retry',
        'urllib3.util.ssl_',
        'urllib3.contrib',
        'certifi',
        'charset_normalizer',
        'idna',
        # === PDF (reportlab) ===
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.colors',
        'reportlab.lib.units',
        'reportlab.lib.styles',
        'reportlab.lib.enums',
        'reportlab.platypus',
        'reportlab.platypus.tables',
        'reportlab.platypus.paragraph',
        'reportlab.platypus.flowables',
        'reportlab.platypus.doctemplate',
        'reportlab.platypus.frames',
        'reportlab.pdfbase',
        'reportlab.pdfbase.pdfmetrics',
        'reportlab.pdfbase.ttfonts',
        'reportlab.pdfbase._fontdata',
        'reportlab.pdfbase.pdfdoc',
        'reportlab.pdfbase.pdfutils',
        'reportlab.graphics',
        'reportlab.graphics.shapes',
        'reportlab.rl_config',
        # === CSV (stdlib) ===
        'csv',
        # === Outros stdlib usados ===
        'subprocess',
        'platform',
        'threading',
        'concurrent.futures',
        'dataclasses',
        'enum',
        'json',
        'pathlib',
        're',
        'datetime',
        # === PIL (usado internamente pelo reportlab) ===
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy',
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx',
        'notebook', 'pytest', 'sphinx', 'IPython',
        '_tkinter_finder',
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IP Scanner Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='IP Scanner Pro',
)
