# 🌐 IP Scanner Pro

[Leia em Português](#-ip-scanner-pro-pt)

Modern desktop application for monitoring and scanning IPs in local networks. Integrates with UniFi Controller and OCS Reports for automatic device identification.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-green.svg)
![License](https://img.shields.io/badge/License-View--Only-red.svg)

> ⚠️ **Repository made available for portfolio purposes only.** The code can
> be viewed, but **cannot** be copied, downloaded, used, or
> reused in other projects. See the [License](#-license) section and the
> [`LICENSE`](./LICENSE) file.

## ✨ Features

- 🔍 **IP Scanning** - Scans configurable IP ranges
- 🔄 **UniFi Integration** - Queries UniFi Controller clients
- 📋 **OCS Integration** - Gets information from OCS Reports
- 📡 **Auto Ping** - Checks connectivity status
- 🎨 **Modern Interface** - Figma-inspired design with dark/light theme
- ✨ **Visual Effect** - Blinking rows to indicate status
- 🔧 **Configurable** - IP ranges, exclusions, and auto-update

## 📸 Preview

```
┌──────────────────────────────────────────────────────────────┐
│  🌐 IP Scanner Pro                           [⚙️ Config]     │
├──────────────────────────────────────────────────────────────┤
│  📡 Scan Configuration                                       │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 203.0.113.1-254│  │ 100-199      │  │ 🔍 Start        │  │
│  └────────────────┘  └──────────────┘  └──────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Total    │ │ Occupied │ │ Free     │ │ Utiliz.  │        │
│  │   154    │ │   89     │ │   65     │ │  57.8%   │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├──────────────────────────────────────────────────────────────┤
│  STATUS  │ IP ADDRESS  │ NAME          │ MAC             ...│
│  🟢 OCCUP│ 203.0.113.5 │ PC-SALES-01   │ AA:BB:CC:DD:EE:FF │
│  🔵 FREE │ 203.0.113.6 │ N/A           │ N/A               │
│  🟢 OCCUP│ 203.0.113.7 │ PRINTER-HR    │ 11:22:33:44:55:66 │
└──────────────────────────────────────────────────────────────┘
```

## 🏗️ MVC Architecture

```
ip_scanner/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   ├── __init__.py
│   └── settings.py         # Global settings and themes
└── app/
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   └── ip_scanner_model.py  # Scanning logic
    ├── views/
    │   ├── __init__.py
    │   ├── components.py        # UI Components
    │   └── main_window.py       # Main window
    ├── controllers/
    │   ├── __init__.py
    │   └── scan_controller.py   # Action controls
    └── utils/
        └── __init__.py
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the project**
```bash
cd ip_scanner
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **(Optional) Configure your credentials**
```bash
# Copy the template and edit with your real network values.
# The config/user_settings.json file is in .gitignore and does not go to the repository.
cp config/user_settings.example.json config/user_settings.json
```
Without this file, the application uses the default (fictional) values from `config/settings.py`
and credentials can be filled out via the interface itself (⚙️ Settings).

4. **Run the application**
```bash
python main.py
```

## ⚙️ Configuration

### IP Range
In the interface, configure the desired IP range:
- `203.0.113.1-254` - Scans from .1 to .254
- `203.0.113.2-99` - Scans specific range

### Range Exclusion
To exclude IPs from the scan (e.g., collector range):
- `100-199` - Excludes IPs from .100 to .199
- `100-199, 250-254` - Multiple ranges

### Advanced Settings
Click on ⚙️ **Settings** to define:
- UniFi Controller Credentials
- OCS Reports Credentials

### Configuration File
Settings are saved in `config/user_settings.json` (not versioned).
Use `config/user_settings.example.json` as a template:

```json
{
    "unifi": {
        "host": "https://192.0.2.1:8443",
        "username": "example_user",
        "password": "example_password"
    },
    "ocs": {
        "base_url": "http://198.51.100.245/ocsreports",
        "username": "example_user",
        "password": "example_password"
    },
    "scan": {
        "ip_base": "203.0.113",
        "start_ip": 2,
        "end_ip": 253,
        "exclude_ranges": [[100, 199]]
    }
}
```

> The example addresses use documentation reserved ranges
> (RFC 5737). Replace with real values only in your local `user_settings.json`.

## 🎨 Themes

The application supports two themes:
- 🌙 **Dark Theme** (default) - Modern dark mode interface
- ☀️ **Light Theme** - Light mode interface

Toggle using the "Dark Theme" switch in the header.

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|--------|------|
| `F5` | Start scan |
| `Esc` | Cancel scan |
| `Ctrl+F` | Focus search field |

## 📊 IP Status

| Status | Description |
|--------|-----------|
| 🟢 OCCUPIED | IP in use (found in UniFi, OCS or responds to ping) |
| 🔵 FREE | IP available (not found in any source) |

## 🔧 Technologies Used

- **CustomTkinter** - Modern graphical interface
- **Requests** - HTTP requests
- **Threading** - Parallel processing
- **Concurrent.futures** - Thread pool for ping

## 📝 License

This repository is **not open source**. It is publicly available
only for portfolio/technical demonstration purposes.

- ✅ Allowed: viewing the code via the GitHub interface.
- ❌ Prohibited: copying, downloading, cloning for reuse, using, modifying, executing
  or redistributing this code, in whole or in part, without prior written authorization
  from the author.

All rights reserved. See the full terms in
[`LICENSE`](./LICENSE).

## 👤 Author

**Lucas Veríssimo**
- Developer @ Company
- Systems Engineering Student @ UNIMONTES

---

⭐ If this project was useful, consider giving it a star!

---

<a name="-ip-scanner-pro-pt"></a>
# 🌐 IP Scanner Pro (PT)

[Read in English](#-ip-scanner-pro)

Aplicação desktop moderna para monitoramento e varredura de IPs em redes locais. Integra com UniFi Controller e OCS Reports para identificação automática de dispositivos.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-green.svg)
![License](https://img.shields.io/badge/License-View--Only-red.svg)

> ⚠️ **Repositório disponibilizado apenas para portfólio.** O código pode
> ser visualizado, mas **não** pode ser copiado, baixado, usado ou
> reaproveitado em outros projetos. Veja a seção [Licença](#-licença) e o
> arquivo [`LICENSE`](./LICENSE).

## ✨ Funcionalidades

- 🔍 **Varredura de IPs** - Escaneia faixas de IP configuráveis
- 🔄 **Integração UniFi** - Consulta clientes do UniFi Controller
- 📋 **Integração OCS** - Obtém informações do OCS Reports
- 📡 **Ping automático** - Verifica status de conectividade
- 🎨 **Interface moderna** - Design inspirado no Figma com tema escuro/claro
- ✨ **Efeito visual** - Linhas piscando para indicar status
- 🔧 **Configurável** - Faixas de IP, exclusões e auto-atualização

## 📸 Preview

```
┌──────────────────────────────────────────────────────────────┐
│  🌐 IP Scanner Pro                           [⚙️ Config]     │
├──────────────────────────────────────────────────────────────┤
│  📡 Configuração de Varredura                                │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 203.0.113.1-254│  │ 100-199      │  │ 🔍 Iniciar      │  │
│  └────────────────┘  └──────────────┘  └──────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Total    │ │ Ocupados │ │ Livres   │ │ Utiliz.  │        │
│  │   154    │ │   89     │ │   65     │ │  57.8%   │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├──────────────────────────────────────────────────────────────┤
│  STATUS  │ IP ADDRESS  │ NAME          │ MAC             ...│
│  🟢 OCUP │ 203.0.113.5 │ PC-VENDAS-01  │ AA:BB:CC:DD:EE:FF │
│  🔵 LIVRE│ 203.0.113.6 │ N/A           │ N/A               │
│  🟢 OCUP │ 203.0.113.7 │ IMPRESSORA-RH │ 11:22:33:44:55:66 │
└──────────────────────────────────────────────────────────────┘
```

## 🏗️ Arquitetura MVC

```
ip_scanner/
├── main.py                 # Ponto de entrada
├── requirements.txt        # Dependências
├── config/
│   ├── __init__.py
│   └── settings.py         # Configurações globais e temas
└── app/
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   └── ip_scanner_model.py  # Lógica de varredura
    ├── views/
    │   ├── __init__.py
    │   ├── components.py        # Componentes de UI
    │   └── main_window.py       # Janela principal
    ├── controllers/
    │   ├── __init__.py
    │   └── scan_controller.py   # Controle de ações
    └── utils/
        └── __init__.py
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone ou baixe o projeto**
```bash
cd ip_scanner
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **(Opcional) Configure suas credenciais**
```bash
# Copie o template e edite com os valores reais da sua rede.
# O arquivo config/user_settings.json esta no .gitignore e nao vai para o repositorio.
cp config/user_settings.example.json config/user_settings.json
```
Sem esse arquivo, a aplicação usa os valores padrão (fictícios) de `config/settings.py`
e as credenciais podem ser preenchidas pela própria interface (⚙️ Configurações).

4. **Execute a aplicação**
```bash
python main.py
```

## ⚙️ Configuração

### Faixa de IP
Na interface, configure a faixa de IP desejada:
- `203.0.113.1-254` - Escaneia do .1 ao .254
- `203.0.113.2-99` - Escaneia faixa específica

### Exclusão de Faixas
Para excluir IPs do scan (ex: faixa de coletores):
- `100-199` - Exclui IPs de .100 a .199
- `100-199, 250-254` - Múltiplas faixas

### Configurações Avançadas
Clique em ⚙️ **Configurações** para definir:
- Credenciais do UniFi Controller
- Credenciais do OCS Reports

### Arquivo de Configuração
As configurações são salvas em `config/user_settings.json` (não versionado).
Use `config/user_settings.example.json` como modelo:

```json
{
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
        "exclude_ranges": [[100, 199]]
    }
}
```

> Os endereços de exemplo usam as faixas reservadas para documentação
> (RFC 5737). Substitua pelos valores reais apenas no seu `user_settings.json` local.

## 🎨 Temas

A aplicação suporta dois temas:
- 🌙 **Tema Escuro** (padrão) - Interface dark mode moderna
- ☀️ **Tema Claro** - Interface light mode

Alterne usando o switch "Tema Escuro" no cabeçalho.

## ⌨️ Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `F5` | Iniciar varredura |
| `Esc` | Cancelar varredura |
| `Ctrl+F` | Focar campo de busca |

## 📊 Status dos IPs

| Status | Descrição |
|--------|-----------|
| 🟢 OCUPADO | IP em uso (encontrado no UniFi, OCS ou responde a ping) |
| 🔵 LIVRE | IP disponível (não encontrado em nenhuma fonte) |

## 🔧 Tecnologias Utilizadas

- **CustomTkinter** - Interface gráfica moderna
- **Requests** - Requisições HTTP
- **Threading** - Processamento paralelo
- **Concurrent.futures** - Pool de threads para ping

## 📝 Licença

Este repositório **não é open source**. Ele é disponibilizado publicamente
apenas para fins de portfólio/demonstração técnica.

- ✅ Permitido: visualizar o código pela interface do GitHub.
- ❌ Proibido: copiar, baixar, clonar para reuso, usar, modificar, executar
  ou redistribuir este código, no todo ou em parte, sem autorização prévia
  e por escrito do autor.

Todos os direitos são reservados. Veja os termos completos em
[`LICENSE`](./LICENSE).

## 👤 Autor

**Lucas Veríssimo**
- Desenvolvedor @ Empresa
- Estudante de Engenharia de Sistemas @ UNIMONTES

---

⭐ Se este projeto foi útil, considere dar uma estrela!
