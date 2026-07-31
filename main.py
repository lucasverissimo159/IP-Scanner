#!/usr/bin/env python3
"""
IP Scanner Pro
Aplicação desktop para monitoramento de IPs em tempo real

Autor: Lucas Veríssimo
Versão: 1.0.0
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Função principal da aplicação"""
    try:
        # Verificar dependências
        check_dependencies()
        
        # Importar e iniciar aplicação
        from app.views import MainWindow
        
        app = MainWindow()
        app.mainloop()
        
    except ImportError as e:
        show_dependency_error(e)
        sys.exit(1)
    except Exception as e:
        show_error(e)
        sys.exit(1)


def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    missing = []
    
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import urllib3
    except ImportError:
        missing.append("urllib3")
    
    if missing:
        raise ImportError(
            f"Dependências não encontradas: {', '.join(missing)}\n"
            f"Execute: pip install {' '.join(missing)}"
        )


def show_dependency_error(error):
    """Exibe erro de dependência"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Erro de Dependência",
            f"Algumas dependências não estão instaladas:\n\n{error}\n\n"
            "Execute no terminal:\n"
            "pip install customtkinter requests urllib3"
        )
        root.destroy()
    except:
        print(f"ERRO: {error}")


def show_error(error):
    """Exibe erro genérico"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro", f"Ocorreu um erro:\n\n{error}")
        root.destroy()
    except:
        print(f"ERRO: {error}")


if __name__ == "__main__":
    main()
