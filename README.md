# 🌐 IP Scanner Pro

Aplicação desktop moderna para monitoramento e varredura de IPs em redes locais. Integra com UniFi Controller e OCS Reports para identificação automática de dispositivos.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

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

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👤 Autor

**Lucas Veríssimo**
- Desenvolvedor @ Empresa
- Estudante de Engenharia de Sistemas @ UNIMONTES

---

⭐ Se este projeto foi útil, considere dar uma estrela!
