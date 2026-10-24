# Hackathon Kanastra - Cúpula

Portal Antecipe: a empresa envia um lote de notas (CSV) e vê, nota a nota, se foi aprovada ou recusada, o motivo da recusa em linguagem clara, o valor líquido de cada nota aprovada e o total a receber.

## Tecnologias

- **Back-end:** Python 3.10+, Flask, Flask-CORS
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
| `validadores.json` (regras do FIDC, cópia do `validadores_antecipe.json` do desafio) | `backend/validadores.json` | Já vem no repositório |
| `estoque_antecipe.csv` (carteira já comprada, ~100 mil linhas) | `backend/data/estoque_antecipe.csv` | Recomendado |

O estoque **não** é versionado (dados do evento). Baixe o `estoque_antecipe_100k.zip` da página do desafio, descompacte e coloque o CSV em `backend/data/` (crie a pasta `data` se não existir). Sem ele a aplicação funciona, mas a checagem de notas já compradas e de concentração por sacado usa apenas o que foi processado pela própria aplicação.

**5. Inicie a aplicação**

```bash
cd backend
python app.py
```

O terminal mostra o log de inicialização. Deixe-o aberto.

**6. Abra no navegador**

<http://localhost:8000>

A mesma porta serve a tela e a API.

**7. Teste rápido**

Na tela, clique em **"Simular com Notas Exemplo"** (dados de demonstração) ou envie o arquivo `exemplos/lote_exemplo.csv` (dados fictícios no formato do desafio).

### Variáveis de ambiente

Nenhuma. O projeto não usa segredos nem chaves (o arquivo `.env.example` só documenta isso).

### Começar do zero de novo

As notas aprovadas ficam salvas em `backend/database.db`, e enviar o mesmo arquivo duas vezes recusa tudo como duplicado (é a garantia de que a mesma nota não é vendida duas vezes). Para repetir uma demonstração: pare o servidor, apague `backend/database.db` e inicie de novo.

## Como usar a API

A mesma validação da tela está disponível por API:

```bash
curl -F "lote=@exemplos/lote_exemplo.csv" http://localhost:8000/api/analisar-lote
```

- **Método e rota:** `POST /api/analisar-lote`
- **Corpo:** `multipart/form-data` com o arquivo CSV no campo `lote`
- **Formato do CSV:** separador `;`, decimal com vírgula, datas `dd/mm/aaaa`, UTF-8, cabeçalho na primeira linha
- **Resposta (200):**

```json
{
  "resumo": {
    "totalNotas": 7,
    "totalBruto": "R$ 84.200,50",
    "totalLiquido": "R$ 51.942,33",
    "totalRecusadas": 3
  },
  "itens": [
    {
      "id": "EX-001",
      "sacado": "Distribuidora Aurora Ltda",
      "valorFace": "R$ 15.000,00",
      "prazo": "29 dias",
      "desconto": "R$ 362,50 (2.42%)",
      "valorLiquido": "R$ 14.637,50",
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
│   ├── app.py            rotas Flask (API e entrega do front)
│   ├── motor.py          leitura do CSV, regras de elegibilidade e cálculo do desconto
│   ├── banco.py          persistência em SQLite
│   ├── validadores.json  regras do fundo (editáveis sem mexer no código)
│   └── requirements.txt  dependências
└── frontend/
    ├── index.html        tela
    ├── css/style.css     estilo
    └── js/script.js      upload, chamada à API e exibição dos resultados
```

## Relatório curto

**O que construímos.** Um portal em que a empresa envia um lote em CSV e recebe, por nota, aprovada ou recusada, com o motivo explicado, o desconto, o valor líquido e o total a receber. A tela e a API usam a mesma validação.

**Principais decisões**

- **Regras fora do código:** valor mínimo, prazo máximo, concentração por sacado e CNPJ ativo são lidos de `backend/validadores.json` a cada lote. Para mudar uma regra, o gestor edita o JSON, sem alterar código nem reiniciar.
- **Idempotência em O(1):** a identidade da nota é cedente + número do documento (cada empresa numera do seu jeito). As chaves ficam em um conjunto em memória, carregado do estoque e do banco ao iniciar.
- **Persistência:** as notas aprovadas são gravadas em SQLite em lote (`executemany`) e recarregadas ao iniciar, então a garantia de "não vender duas vezes" sobrevive a reinícios.
- **Escalabilidade:** processamento linha a linha com estruturas em memória; a resposta traz totais completos e só as primeiras 500 notas. Em teste local com 500 mil linhas, o lote foi processado e gravado em cerca de 8 segundos.
- **Logs e credenciais:** logs em linha única `EVENT=... CHAVE=valor`, só com eventos, contagens e tipos de erro, nunca com conteúdo do CSV. Não há segredos no repositório e o `.gitignore` bloqueia CSVs, logs e o banco local.
- **Front sem dependências:** HTML, CSS e JavaScript puros, servidos pelo próprio Flask na mesma porta da API.

**O que ficou de fora**

- A taxa de desconto (2,5% ao mês, desconto simples) está definida no código, e não no JSON de validadores.
- Validadores do JSON com códigos diferentes de valor mínimo, prazo máximo, concentração e CNPJ ativo não são aplicados.
- A checagem de CNPJ ativo só usa uma coluna de situação cadastral, se existir no CSV; não há consulta a base externa.
- O tipo de recebível (Duplicata, Cheque, CCB...) não é validado.
- Datas ilegíveis fazem a nota assumir prazo de 30 dias, em vez de ser recusada.
- Sem autenticação e sem painel para o gestor editar as regras (hoje a edição é no arquivo JSON).

## Registro de prompts

Todos os prompts de IA usados no projeto estão em [`PROMPTS.md`](PROMPTS.md), em ordem cronológica, com a descrição do que foi feito com cada resposta.
