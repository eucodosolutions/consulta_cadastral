# Assistente de Consulta Cadastral - Simples Nacional

Solução de automação ponta a ponta desenvolvida em Python para integrar uma interface web de processamento, extração de dados da Receita Federal (via ReceitaWS), orquestração de notificações por e-mail e persistência robusta em banco de dados utilizando Supabase (PostgreSQL).

## Tecnologias Utilizadas

- Interface de Usuário: Streamlit
- Integração de Dados: Requests (Integração de APIs REST)
- Banco de Dados: Supabase (PostgreSQL nativo via API supabase-py)
- Manipulação de Dados: Pandas
- Controle de Ambiente: Python-dotenv
- Disparo de E-mails: smtplib (nativo Python)

## Pré-requisitos

- Python 3.10 ou superior
- Conta no Supabase com um projeto criado
- Conta de e-mail configurada com senha de aplicativo para acesso SMTP

## Instalação e Configuração

1. Clone o repositório ou baixe os arquivos.
2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Certifique-se de ter um arquivo `.env` preenchido com as credenciais da sua conta Supabase, bem como os dados de SMTP.

5. Crie as tabelas no Supabase:
Acesse o SQL Editor no painel do seu projeto Supabase e execute o script contido em `docs/ddl.sql`.

## Como Executar

Inicie a aplicação utilizando o Streamlit:
```bash
streamlit run main.py
```
O sistema estará disponível automaticamente no navegador padrão no endereço `http://localhost:8501`.

## Arquitetura e Decisões de Design
Consulte o documento de arquitetura detalhado localizado em `docs/architecture.md`.
