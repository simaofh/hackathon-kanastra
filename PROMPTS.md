# Registro Cronológico de Prompts

**Hackathon Kanastra 2026 – Desafio Portal Antecipe FIDC**
**Equipe:** Cúpula
**Data:** 24 de outubro de 2026

Todos os prompts abaixo estão em ordem cronológica, resumindo a construção do projeto desde o planejamento até o refinamento final de interface e escalabilidade, com as respectivas ações implementadas no código (item 4.1.2 do edital).

---

## 01. Contexto do desafio

**Prompt:**

> "Vou copiar uma mensagem, guarde ela em sua memoria... O desafio: portal Antecipe O problema: uma pequena empresa vendeu a prazo e quer o dinheiro hoje... Back: API que valida cada recebível..."
> **O que foi feito com a resposta:** A IA internalizou as regras de negócio do FIDC, os critérios de avaliação e o formato dos dados para guiar tecnicamente o desenvolvimento.

## 02. Planejamento do projeto como consultor de TI

**Prompt:**

> "Aja como um consultor de TI... monte o planejamento com base nessa linguagem [C]... o trabalho deve ser concluído em até 6 horas."
> **O que foi feito com a resposta:** A IA dividiu o fluxo de trabalho em blocos de horas, definindo as etapas e a responsabilidade de cada um dos três membros do grupo.

## 03. Identificação de componentes e estruturação do ambiente

**Prompt:**

> "circula esse icone nessa imagem"
> **O que foi feito com a resposta:** Mapeamento visual das ferramentas no ambiente (Chromebook/Linux), permitindo a inicialização do terminal local e configuração do Git.

## 04. Interface web e jornada do usuário (Design e UX)

**Prompt:**

> "eu vou fazer a parte do html"
> **O que foi feito com a resposta:** Criação da estrutura base em `index.html` com layout escuro, área de drag & drop para CSV, cards de métricas e tabela de recusas com foco em UX.

## 05. Servidor local e validação de renderização web

**Prompt:**

> "como faço pra abrir o site desse codigo pra ver como que ta ficando o layout"
> **O que foi feito com a resposta:** Inicialização de um servidor HTTP nativo no terminal Linux para validação de responsividade do layout em tempo real.

## 06. Motor de validação, idempotência e filosofia Unix

**Prompt:**

> "vou fazer pelo compilador normal msm / eu quero usar compilador externo mesmo"
> **O que foi feito com a resposta:** Estruturação da lógica de detecção de duplicidades em O(1) e logs blindados contra vazamento de dados, servindo de base arquitetural.

## 07. Separação do front-end (HTML/CSS/JS)

**Prompt:**

> "e na parte do css e do js?"
> **O que foi feito com a resposta:** Modularização limpa da interface em 3 camadas, resolvendo falhas de renderização e permitindo testes interativos via CodePen.

## 08. Decisão arquitetural do back-end (Python)

**Prompt:**

> "o back end vai ser em python, assim, substitui java?"
> **O que foi feito com a resposta:** Transição validada para Python (Flask) visando maior produtividade no evento, leitura otimizada de CSVs e aderência aos requisitos de execução do edital.

## 09. Contrato de integração e especificação técnica

**Prompt:**

> "me passa todos os nomes, requisitos e etc que devem ter no codigo em python pra conseguir fazer a conexao entre o meu codigo front e o back"
> **O que foi feito com a resposta:** Definição do contrato da API (endpoint, payload JSON, CORS), permitindo o desenvolvimento do front e back em paralelo.

## 10. JavaScript unificado e fallback resiliente

**Prompt:**

> "com isso tudo, me mande agora o codigo java script atualizado para so colar dps os url..."
> **O que foi feito com a resposta:** Integração do `script.js` com a API, incluindo gerenciamento de estado ("Processando lote...") e renderização dinâmica da tabela.

## 11. Integração Front/Back e Escalabilidade de Banco de Dados

**Prompt:**

> "cara, estava usando o claude pra linkar os códigos do front e do back e acabou o limite dele... corrija tudo e qualquer divergência nos códigos, de maneira que não tenha nenhum erro."
> **O que foi feito com a resposta:** A IA (via Gemini) unificou o contrato JSON entre `script.js` e a API em Flask. Foi implementado o `executemany` (Bulk Insert) no SQLite e cache no Python para garantir o processamento em $O(1)$ de lotes com até 500 mil linhas.

## 12. Motor de Regras Dinâmico (Sem Redeploy)

**Prompt:**

> "dentro do projeto era preciso ter um filtro para o usuário conseguir adaptar os limites maximos e minimos... 1. Criar um pop-up na tela principal... 3. criar um endpoint pra isso no backend"
> **O que foi feito com a resposta:** Construção dos endpoints `GET` e `POST` em `/api/configuracoes` e de um Modal no front-end. A alteração permitiu a edição do `validadores.json` pela tela da aplicação, atualizando as regras do FIDC em tempo real sem novo deploy.

## 13. Refinamento de UX/UI para Padrão Fintech

**Prompt:**

> "considerando o meu codigo css e html, o que vc indicaria que deixaria mais bonito o layout da pagina, e mais dinamico e profissional também..."
> **O que foi feito com a resposta:** O layout foi modernizado com elementos de dashboard financeiro, ganhando uma barra de liquidez de carteira, pílulas de filtros interativas (Todas/Aprovadas/Recusadas) e destaque visual das recusas.

## 14. Adaptação Visual e High-Contrast Light Mode

**Prompt:**

> "use a formatação de design da kanastra link... seguinte, tira o filtro... tira as escritas da kanastra e os emoji, quero fundo claro igual no site"
> **O que foi feito com a resposta:** A UI foi refinada para um tema claro limpo (#F7FAF8), combinando tipografia elegante (Inter) com os tons de verde institucionais. Foram removidos emojis e referências de marca diretas para manter a neutralidade e o profissionalismo.

## 15. Correção Final de UX (Tabela Vazia)

**Prompt:**

> "no quadrado onde ta a frase Nenhum lote carregado... troque o branco de quando o mause nao esta em cima pelo mesmo cinza de quando esta o mause em cima"
> **O que foi feito com a resposta:** O arquivo `style.css` foi ajustado fixando a cor de fundo (`background-color`) da classe `.empty-state`, garantindo que a linha informativa de tabela vazia permaneça com destaque visual contínuo.
