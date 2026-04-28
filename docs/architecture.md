# Documentação de Arquitetura

O sistema foi desenhado com o conceito de separação de preocupações (Separation of Concerns), utilizando uma estrutura limpa baseada em módulos independentes. O objetivo é garantir que a aplicação seja um projeto de software resiliente e de fácil manutenção.

## Componentes

### 1. Interface (Streamlit)
Localizada em `main.py`. Utiliza os recursos nativos do Streamlit para fornecer uma interface web moderna. O módulo gerencia a interação do usuário, processa uploads de planilhas de forma transparente e fornece feedback contínuo sobre o status do processamento. A injeção de JavaScript assegura persistência de estado e máscaras de input.

### 2. Motor de Extração (Scraper/API)
Localizado em `app/scraper/`.
- **Estratégia de Integração:** Em vez de depender de automação de navegador complexa e instável, o projeto utiliza consultas diretas à API pública da ReceitaWS via HTTP (biblioteca `requests`).
- **Desempenho e Resiliência:** Esta abordagem reduz drásticamente o tempo de resposta e o uso de recursos, garantindo alta disponibilidade. Exceções customizadas tratam dados inválidos e falhas de conexão de forma sistemática como regras de negócio.

### 3. Orquestrador e Serviços
Localizado em `app/services/`.
- **Orquestrador (`orchestrator.py`):** Atua como a ponte entre a Interface, o Extrator e o Banco de Dados. Gerencia o fluxo de execução, incluindo formatação de dados em lote, início de cronômetros e controle transacional dos processamentos. Garante que todo evento tenha seu status corretamente atualizado ("sucesso" ou "falha").
- **Mailer (`mailer.py`):** Módulo autônomo responsável pelo disparo automático do relatório final via protocolo SMTP com anexo gerado em memória, desacoplando o envio de e-mails da interface primária.

### 4. Persistência (Supabase)
Localizada em `app/db/`.
- **Arquitetura Serverless:** O uso do Supabase minimiza a necessidade de infraestrutura local. A biblioteca `supabase-py` faz requisições via API REST de forma rápida e segura, evitando overhead de gerenciamento de conexões de banco tradicionais.
- **Tabela `logs_execucao`:** Adota o uso do campo `metadados` como JSONB para proporcionar flexibilidade nos logs (Observabilidade). Em vez de colunas dinâmicas, o contexto arbitrário de cada operação é registrado na estrutura JSON.
- **Tabela `consultar_simples_nacional`:** Armazena o registro processado e validado, atrelando-se indiretamente aos logs de execução através das datas de processamento e dos metadados.
