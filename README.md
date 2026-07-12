# Smart Report Converter

Sistema de automação desenvolvido em Python para conversão de arquivos TXT
de folha de pagamento/consignado em relatórios Excel estruturados, com
interface web (Flask), progresso em tempo real e geração de múltiplas abas
formatadas.

## Funcionalidades

- ✔ Upload de arquivo `.txt` via drag-and-drop ou seleção manual
- ✔ Conversão assíncrona (background thread) com progresso em tempo real via Server-Sent Events
- ✔ Geração de planilha Excel com 3 abas: `ABA_1`, `DESCONTADOS` e `NAO_DESCONTADOS`
- ✔ Formatação automática de valores monetários e datas
- ✔ Escolha de pasta e nome de saída
- ✔ Logging estruturado em arquivo (`logs/app.log`)

## Tecnologias

- Python 3.11+
- Flask
- Pandas
- OpenPyXL

## Arquitetura

```
Upload do .txt
      │
      ▼
Thread em background (converter.py)
      │
      ├─► Leitura e parsing (Pandas)
      ├─► Cálculo de valores financeiros
      ├─► Formatação de datas
      └─► Geração do .xlsx (OpenPyXL)
      │
      ▼
Progresso via SSE (/progresso/<job_id>)
      │
      ▼
Download do resultado (/download/<job_id>)
```

## Estrutura do projeto

```
smart-report-converter/
├── app/
│   ├── __init__.py       # Application factory
│   ├── config.py         # Configurações via variáveis de ambiente
│   ├── jobs.py           # Estado em memória do progresso das conversões
│   ├── converter.py      # Lógica de conversão TXT -> XLSX
│   ├── routes.py         # Rotas (index, converter, progresso, download)
│   └── templates/
│       └── index.html
├── logs/                  # Logs da aplicação (gerado automaticamente)
├── run.py                 # Ponto de entrada
├── requirements.txt
├── .env.example
└── .gitignore
```

## Como rodar localmente

```bash
# 1. Criar e ativar um ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. (opcional) configurar variáveis de ambiente
copy .env.example .env     # Windows
cp .env.example .env       # Linux/Mac

# 4. Rodar a aplicação
python run.py
```

Acesse http://localhost:5000

## Layout esperado do arquivo TXT de entrada

Arquivo delimitado por `;`, sem cabeçalho, codificação `latin1`, com pelo
menos 18 colunas. As colunas usadas no processamento (índices 0-based):
`1, 2, 3, 7, 8, 9, 10, 11, 12, 14, 17` (CPF, MASP, nome, código, número do
contrato, nome do convênio, valores, data de lançamento e desconto, etc.).

## Mudanças em relação à versão original

- **Correção de segurança**: a rota de download antes aceitava um caminho
  de arquivo arbitrário via query string (`/download?path=...`), o que
  permitiria, em tese, ler qualquer arquivo acessível ao processo do
  servidor. Agora o download é feito por `job_id` (`/download/<job_id>`),
  e o caminho real do arquivo nunca é exposto nem controlado pelo cliente.
- **Sanitização de nomes de arquivo**: tanto o nome do `.txt` enviado
  quanto o nome do `.xlsx` de saída agora passam por `secure_filename`,
  evitando caracteres problemáticos ou tentativas de path traversal.
- **Tratamento de erros**: se o TXT não tiver o número de colunas
  esperado, a aplicação avisa isso de forma clara em vez de quebrar com
  um erro genérico do Pandas.
- **Logging**: erros de conversão agora ficam registrados com stack trace
  completo em `logs/app.log`, mas o usuário final vê apenas uma mensagem
  amigável.
- **Organização em módulos**: HTML movido para `templates/`, lógica de
  conversão isolada em `converter.py`, rotas em `routes.py`.

## Limitações conhecidas / próximos passos

- O progresso das conversões é guardado em memória (`app/jobs.py`). Como
  é uma aplicação local/pessoal, isso é suficiente; não use com múltiplos
  workers (`gunicorn -w 4`) sem migrar esse estado para algo compartilhado.
- Não há autenticação — qualquer pessoa com acesso à URL pode enviar
  arquivos e converter. Adequado para uso local/pessoal; se for expor a
  aplicação na internet, adicione autenticação antes.
- Não há testes automatizados ainda — próximo passo natural seria
  `pytest` cobrindo a lógica de `converter.py`.

> Sistema de automação desenvolvido em Python para conversão de arquivos
> TXT em relatórios Excel estruturados, com processamento assíncrono e
> feedback de progresso em tempo real via interface web feita em Flask.
