# Hackathon Kanastra - Cúpula

Portal Antecipe: a empresa envia um lote de notas (CSV) e vê, nota a nota, se foi aprovada ou recusada, o motivo da recusa em linguagem clara, o desconto, o valor líquido de cada nota aprovada e o total a receber. As regras do fundo podem ser alteradas pela própria tela, sem mexer no código.

## Tecnologias

- **Back-end:** Python 3.10+, Flask 3.0.3, Flask-CORS 4.0.1
- **Banco local:** SQLite (módulo `sqlite3`, já vem com o Python)
- **Front-end:** HTML, CSS e JavaScript puros (sem build, sem Node)

## Pré-requisitos

- Python 3.10 ou superior (`python --version`)
- `pip`
- Um navegador (Chrome, Firefox...)

Não é preciso Docker, Node nem banco de dados instalado.

## Como rodar do zero

**1. Clone o repositório e entre na pasta**

```bash
git clone https://github.com/simaofh/hackathon-kanastra.git
cd hackathon-kanastra
```

**2. (Recomendado) Crie um ambiente virtual**

```bash
python -m venv venv
```

Ative-o:

- Linux / macOS: `source venv/bin/activate`
- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Windows (cmd): `venv\Scripts\activate.bat`

> Em alguns sistemas o comando é `python3` em vez de `python`.

**3. Instale as dependências**

```bash
pip install -r backend/requirements.txt
```

**4. Confira os arquivos de dados**

| Arquivo | Onde fica | Obrigatório? |
|---|---|---|
| Regras do fundo (`validadores_antecipe.json` do desafio) | `backend/validadores.json` | Já vem no repositório |
| `estoque_antecipe.csv` (carteira já comprada, ~100 mil linhas) | `backend/data/estoque_antecipe.csv` | Recomendado |

O arquivo de regras é procurado em `backend/` com um destes nomes, nesta ordem: `validadores_antecipe_3.json`, `validadores.json`, `config.json`, `config`.

O estoque **não** é versionado (dados do evento). Baixe o `estoque_antecipe_100k.zip` da página do desafio, descompacte e coloque o CSV em `backend/data/` (crie a pasta `data` se não existir). Sem ele a aplicação funciona, mas a checagem de notas já compradas só considera o que foi processado pela própria aplicação, e o limite de concentração usa uma carteira de referência fixa (veja "O que ficou de fora").

**5. Inicie a aplicação**

```bash
cd backend
python app.py
```

O terminal mostra os logs. Deixe-o aberto.

**6. Abra no navegador**

<http://localhost:8000>

A mesma porta serve a tela e a API.

**7. Teste rápido**

Na tela, clique em **"Mesa de Antecipação"** e envie o arquivo `exemplos/lote_exemplo.csv` (dados fictícios no formato do desafio). O resultado esperado, com as regras originais e sem estoque carregado, é:

| Nota | Resultado | Motivo |
|---|---|---|
| EX-001 | Aprovada | Líquido R$ 14.700,00 |
| EX-002 | Aprovada | Líquido R$ 17.280,00 |
| EX-003 | Recusada | Valor de face abaixo do mínimo |
| EX-004 | Recusada | Prazo (251 dias) acima do máximo de 180 |
| EX-005 | Recusada | Sacado com situação cadastral INAPTA |
| EX-006 | Recusada | Tipo de recebível "Cheque" não aceito |
| EX-007 | Recusada | Título já vencido |
| EX-002 (repetida) | Recusada | Nota duplicada |
| EX-008 | Recusada | CNPJ do sacado inválido (13 dígitos) |
| EX-009 | Aprovada | Líquido R$ 21.150,47 |

Totais: **10 notas, 7 recusadas, total a receber R$ 53.130,47**. O botão **"Simular Lote Demonstração"** mostra dados de exemplo sem usar o back-end.

### Variáveis de ambiente

Nenhuma. O código não lê variáveis de ambiente nem usa segredos (o arquivo `.env.example` só documenta isso).

### Começar do zero de novo

As notas aprovadas ficam salvas em `backend/database.db`, e enviar o mesmo arquivo duas vezes recusa tudo como duplicado (é a garantia de que a mesma nota não é vendida duas vezes). Para repetir um teste, use o botão **"Limpar Cache de Testes"** da tela, ou pare o servidor e apague `backend/database.db`.

## Como usar a tela

- **Início:** atalhos para enviar um lote, configurar as regras, rodar a demonstração e limpar o cache de testes.
- **Mesa de Antecipação:** upload do lote (clique ou arraste), cards com totais, tabela por nota com busca por empresa ou ID e filtro Todos / Aprovados / Recusados. Cada recusa mostra o motivo.
- **Validadores do Fundo:** edição das regras (ligar/desligar, limites, taxa de desconto). Ao salvar, o arquivo de regras é reescrito, o cache de testes é limpo e o último lote é processado de novo. **"Restaurar Padrões"** volta às regras originais do desafio.

## Regras aplicadas

Lidas do arquivo de regras a cada lote (os nomes são os `codigo` do JSON):

| Regra | O que faz | Estado original |
|---|---|---|
| `CNPJ_SACADO_VALIDO` | Recusa se o CNPJ do sacado não tem 14 dígitos | Ativa |
| `SITUACAO_CADASTRAL_SACADO` | Aceita só as situações listadas (ex.: ATIVA) | Ativa |
| `TIPO_RECEBIVEL` | Aceita só Duplicata e Duplicata de Serviço | Ativa |
| `VALOR_MINIMO` | Valor de face mínimo (R$ 100,00) | Ativa |
| `NAO_VENCIDA` | Recusa nota com vencimento anterior à aquisição | Ativa |
| `PRAZO_MAXIMO` | Prazo máximo até o vencimento (180 dias) | Ativa |
| `CONCENTRACAO_MAXIMA_SACADO` | Limite de 10% da carteira por sacado, agrupado pela raiz do CNPJ | Ativa |
| `PRAZO_MINIMO` | Prazo mínimo (30 dias) | Desativada |
| `CONCENTRACAO_MAXIMA_CEDENTE` | Limite de 8% da carteira por cedente | Desativada |

Além dessas, a duplicidade sempre é checada.

**Preço de compra:** desconto simples, `valor × (taxa mensal ÷ 100) × (dias ÷ base_dias)`, com taxa de 2% ao mês e base de 30 dias (campo `precificacao` do JSON). Valor líquido = valor de face − desconto.

## Como usar a API

A mesma validação da tela está disponível por API:

```bash
curl -F "lote=@exemplos/lote_exemplo.csv" http://localhost:8000/api/analisar-lote
```

| Rota | O que faz |
|---|---|
| `POST /api/analisar-lote` | Valida um lote. Corpo `multipart/form-data` com o CSV no campo `lote` |
| `GET /api/configuracoes` (ou `/api/validadores`) | Devolve as regras atuais em JSON |
| `POST /api/configuracoes` (ou `/api/validadores`) | Grava novas regras (JSON no mesmo formato) e limpa o cache de testes |
| `POST /api/configuracoes/reset` | Restaura as regras originais |
| `POST /api/limpar-cache` | Apaga as notas aprovadas guardadas no banco e volta ao estoque original |

- **Formato do CSV:** separador `;`, decimal com vírgula, datas `dd/mm/aaaa`, UTF-8, cabeçalho na primeira linha. Colunas lidas: `NU_DOCUMENTO`, `DOC_CEDENTE`, `NOME_SACADO`, `DOC_SACADO`, `TIPO_RECEBIVEL`, `VALOR_NOMINAL`, `DATA_VENCIMENTO_ORIGINAL`, `DATA_AQUISICAO` e, opcionalmente, `SITUACAO_CADASTRAL_SACADO`. O prazo é calculado como vencimento menos aquisição.
- **Resposta de `/api/analisar-lote` (200):**

```json
{
  "resumo": {
    "totalNotas": 10,
    "totalBruto": "R$ 112.380,50",
    "totalLiquido": "R$ 53.130,47",
    "totalRecusadas": 7
  },
  "itens": [
    {
      "id": "EX-001",
      "sacado": "Distribuidora Aurora Ltda",
      "valorFace": "R$ 15.000,00",
      "prazo": "30 dias",
      "desconto": "R$ 300,00 (2.00%)",
      "valorLiquido": "R$ 14.700,00",
      "status": "APROVADO",
      "motivoRecusa": null
    }
  ]
}
```

Os totais consideram o lote inteiro; a lista `itens` traz as primeiras 500 notas, para a resposta e a tela continuarem rápidas com lotes grandes. Erros devolvem `{"erro": "mensagem"}` com status 400.

## Estrutura do projeto

```
hackathon-kanastra/
├── README.md             manual e relatório
├── PROMPTS.md            registro cronológico dos prompts de IA
├── .env.example          (sem variáveis; só documenta isso)
├── .gitignore            impede subir segredos, CSVs, logs e banco
├── exemplos/
│   └── lote_exemplo.csv  lote fictício para teste
├── backend/
│   ├── app.py            rotas Flask (API, configuração das regras e entrega do front)
│   ├── motor.py          leitura do CSV, regras de elegibilidade e cálculo do desconto
│   ├── banco.py          persistência em SQLite
│   ├── validadores.json  regras do fundo (editáveis pela tela ou pelo arquivo)
│   ├── requirements.txt  dependências
│   └── data/             estoque_antecipe.csv (não versionado)
└── frontend/
    ├── index.html        tela
    ├── css/style.css     estilo
    └── js/script.js      upload, regras, filtros e exibição dos resultados
```

## Relatório curto

**O que construímos.** Um portal em que a empresa envia um lote em CSV e recebe, por nota, aprovada ou recusada, com o motivo explicado, o desconto, o valor líquido e o total a receber. A tela e a API usam a mesma validação, e o gestor do fundo altera as regras sem deploy.

**Principais decisões**

- **Regras fora do código:** as regras e a taxa de desconto são lidas do arquivo de regras a cada lote. O gestor edita pela tela (ou pelo arquivo) e a mudança vale no lote seguinte, sem reiniciar.
- **Idempotência em O(1):** a identidade da nota é cedente + número do documento (cada empresa numera do seu jeito). As chaves ficam em um conjunto em memória, carregado do estoque e do banco ao iniciar.
- **Persistência:** as notas aprovadas são gravadas em SQLite em lote (`executemany`) e recarregadas ao iniciar, então a garantia de "não vender duas vezes" sobrevive a reinícios.
- **Escalabilidade:** processamento linha a linha com estruturas em memória, cache de datas e agrupamento por raiz de CNPJ em dicionário. A resposta traz totais completos e só as primeiras 500 notas, e a tela filtra e busca nessa amostra.
- **Explicação da recusa:** cada regra tem uma mensagem própria com o valor e o limite envolvidos (ex.: "Prazo de vencimento (251 dias) ultrapassa o limite máximo de 180 dias").
- **Logs e credenciais:** logs em linha única `EVENT=... CHAVE=valor`, só com eventos, contagens e tipos de erro, nunca com conteúdo do CSV. Não há segredos no repositório e o `.gitignore` bloqueia CSVs, logs e o banco local.
- **Front sem dependências:** HTML, CSS e JavaScript puros, servidos pelo próprio Flask na mesma porta da API.

**O que ficou de fora**

- A validação de CNPJ confere só a quantidade de dígitos (14), não os dígitos verificadores.
- A situação cadastral vem da coluna `SITUACAO_CADASTRAL_SACADO` do lote; se a coluna não existir, a nota é tratada como ATIVA. O arquivo de situação cadastral da organização não é consultado.
- A concentração por sacado usa o valor total do estoque (todos os fundos do CSV) como carteira. Sem o estoque carregado, usa uma carteira de referência de R$ 1.000.000, fixa no código.
- Datas ilegíveis fazem a nota assumir prazo de 30 dias, e valores ilegíveis viram R$ 0,00 (recusa por valor mínimo), em vez de uma recusa específica.
- As rotas de configuração e de limpeza de cache não têm autenticação (foram pensadas para demonstração e testes).

## Registro de prompts

Todos os prompts de IA usados no projeto estão em [`PROMPTS.md`](PROMPTS.md), em ordem cronológica, com a descrição do que foi feito com cada resposta.
