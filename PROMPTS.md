# Registro Cronológico de Prompts

**Hackathon Kanastra 2026 – Desafio Portal Antecipe FIDC**
**Equipe:** Cúpula
**Data:** 24 de outubro de 2026

Todos os prompts abaixo estão em ordem cronológica, cada um acompanhado da descrição do que foi feito com a resposta (item 4.1.2 do edital).

---

## 01. [09:54] Contexto do desafio

**Prompt:**
> Vou copiar uma mensagem, guarde ela em sua memoria, e me espere novas instruções. Hackathon Antecipe: dataset para os participantes O desafio: portal Antecipe O problema: uma pequena empresa vendeu a prazo e quer o dinheiro hoje. Ela "vende" essas notas para o fundo, mas o fundo só pode comprar o que cumpre regras: prazo máximo, valor mínimo, sacado (quem vai pagar) não pode estar concentrado demais, CNPJ ativo etc. O que os times constroem: Design: a jornada da empresa, do upload das notas até ver quanto vai receber e por que algumas foram recusadas. O desafio de UX é explicar a recusa de forma clara. Front: upload de lote (CSV), tabela com status por nota e simulação do valor líquido (valor de face menos o desconto). Back: API que valida cada recebível contra critérios de elegibilidade configuráveis e calcula o preço de compra com uma taxa de desconto simples. Arquitetura: como modelar um motor de regras que o gestor do fundo altere sem deploy, e como garantir que o mesmo recebível não seja vendido duas vezes (idempotência e duplicidade). Arquivos Dados para o desafio Antecipe. Baixe os dois arquivos abaixo: Estoque: a carteira já comprada por 18 fundos, com cerca de 100 mil linhas (um único CSV, estoque_antecipe.csv, dentro do zip). Validadores: a configuração das regras do ANTECIPE FIDC. Cada validador tem um codigo, a chave ativo (só os ativos valem) e os parametros. estoque_antecipe_100k.zip 2.32 MiB validadores_antecipe.json 1.44 KiB Requisitos mínimos de entrega Prazo: até as 18h de sábado. Projetos enviados depois não são avaliados. Repositório com o código, com acesso liberado para os jurados. README com o passo a passo para rodar a aplicação do zero: dependências, comandos e variáveis de ambiente. Linguagem, framework e infraestrutura são livres. Aplicação funcionando, com: upload de um CSV de notas no mesmo formato do arquivo de exemplo (separador ;, decimal com vírgula, datas dd/mm/aaaa); regras lidas do validadores_antecipe.json, sem valores fixos no código; resultado de cada nota: aprovada ou recusada e, se recusada, o motivo, explicado de um jeito que a empresa entenda; valor líquido de cada nota aprovada e o total a receber; a mesma validação disponível pela tela e por uma API. Relatório curto (pode estar no README): o que o time construiu, as tecnologias usadas, as principais decisões e o que ficou de fora. Histórico dos prompts de IA usados durante o projeto (exportado ou em arquivo de texto). Apresentação aos jurados: o time mostra a solução funcionando e responde perguntas. Formato do CSV Separador ;, decimal com vírgula, datas dd/mm/aaaa, UTF-8, cabeçalho na primeira linha. Data-base dos dados: @Thursday. Coluna Significado NOME_FUNDO, DOC_FUNDO Fundo que comprou a nota NOME_CEDENTE, DOC_CEDENTE Empresa que vendeu a nota NOME_SACADO, DOC_SACADO Cliente que vai pagar a nota NU_DOCUMENTO Número da nota no sistema do cedente (cada empresa numera do seu jeito) TIPO_RECEBIVEL Duplicata, Duplicata de Serviço, Cheque, CCB ou Nota Comercial VALOR_NOMINAL Valor de face, em reais DATA_VENCIMENTO_ORIGINAL Data de vencimento DATA_AQUISICAO Data em que o fundo comprou a nota

**O que foi feito com a resposta:** A IA entendeu o que é o trabalho e como ele funciona para instruir os participantes em como dar continuidade.

---

## 02. [10:03] Planejamento do projeto como consultor de TI

**Prompt:**
> Bom para começar, primeiro Aja como um consultor de TI, pense que sou um cliente seu, e acabei de enviar o meu desafio, mensagem enviada acima.
>
> O seu trabalho é me fornecer o melhor caminho possivel para a conclusão dessa desasfio. A principal questão aqui: é o tempo, o trabalho deve ser concluído em até 6 horas.
>
> Então com base no texto do desafio enviado primeiro. Monte um PLANEJAMENTO sobre a sucessão do que deve ser feito, o passo a passo.
>
> O que deve ser montado e pensado primeiro.
> O nosso grupo possuí três integrantes, então monte o planejamento, de forma que o trabalho fique bem distribuido entre os participantes.
> IMPORTANTÍSSIMO:
>
> Para fazer tudo o que se pede, aqui vai algumas caracteristicas sobre nosso grupo:
>
> Somos estudantes de Sistema de Informação do segundo período, então nosso conhecimento se limita praticamente à LINGUAGEM C.
> Pense nisso, e monte o planejamento com base nessa linguagem.
>
> Sabemos que no decorrer do projeto, deveremos fazer algo que foge do nosso escopo de conhecimento, então tudo que voce segerir pense que DEVE SER FEITO NA LINGUAGEM C, OU QUE SEJA O MAIS FACIL DE SER EXECUTADO NA LINGUAGEM C.
>
> Pense com calma, não diga nada que voce não tenha certeza.
>
> Tem alguma pergunta que voce acha necessario me fazer, antes de prosseguir?

**O que foi feito com a resposta:** A IA dividiu o trabalho em horas, etapas e função de cada participante do grupo.

---

## 03. [10:23] Identificação de componentes e estruturação do ambiente

**Prompt:**
> circula esse icone nessa imagem

**Objetivo técnico:** Localizar os elementos operacionais no ambiente de desenvolvimento (Chromebook/Linux) para abrir o terminal nativo, compilar rotinas em C e gerenciar arquivos do repositório Git.

**Resposta da IA:** Mapeamento visual das coordenadas da interface, apontando o terminal de linha de comando (`>_`), o editor web do GitHub e o atalho de navegação da raiz do projeto.

**O que foi feito com a resposta:** O terminal local foi aberto para inicialização das rotinas de compilação GCC e estruturação das pastas `/src` e `/frontend` no repositório.

---

## 04. [10:35] Interface web e jornada do usuário (Design e UX)

**Prompt:**
> eu vou fazer a parte do html

**Objetivo técnico:** Criar uma interface web voltada à experiência do tomador de crédito (PME), com upload de lotes em CSV, métricas executivas financeiras (valor de face vs. valor líquido com desconto simples) e listagem de títulos, com foco no critério de 25 pontos em Design e UX.

**Resposta da IA:** Código estruturado para `index.html` com layout escuro moderno, área de arrastar e soltar (drag & drop) para CSV, cards de resumo de elegibilidade e tabela com categorização de status e motivos explicativos amigáveis de recusa.

**O que foi feito com a resposta:** O arquivo foi adicionado ao repositório via commit no GitHub, criando a base visual para simulação das regras de negócio do FIDC Antecipe.

---

## 05. [10:49] Servidor local e validação de renderização web

**Prompts:**
> como faço pra abrir o site desse codigo pra ver como que ta ficando o layout

> na opção 2, a partir daqui, como posso ver o layout

**Objetivo técnico:** Executar um servidor de teste em ambiente local no terminal Linux para validação visual em tempo real, sem dependências externas.

**Resposta da IA:** Instruções passo a passo para sincronização via `git pull` e inicialização de servidor HTTP nativo com `python3 -m http.server 8080`, acessível em `http://localhost:8080`.

**O que foi feito com a resposta:** Execução do comando no terminal e abertura do navegador para verificação da diagramação e da responsividade dos componentes.

---

## 06. [10:55] Motor de validação em C, idempotência e filosofia Unix

**Prompts:**
> vou fazer pelo compilador normal msm

> eu quero usar compilador externo mesmo, depois eu copio o codigo para o github

**Objetivo técnico:** Desenvolver o núcleo do motor de regras de antecipação com alta performance em C, priorizando complexidade O(1) para idempotência contra a base de 100 mil títulos (`estoque_antecipe.csv`), logs estruturados sem vazamento de dados do CSV e segregação de tarefas (filosofia Unix).

**Resposta da IA:** Implementação de `main.c` com tabela hash (algoritmo djb2) para detecção instantânea de duplicidade, cálculo de taxa de desconto simples por prazo, logs estruturados em JSON via `stderr` (sem expor dados sensíveis do CSV) e mensagens claras de recusa.

**O que foi feito com a resposta:** O código foi testado no compilador GCC com a flag de otimização `-O3` e usado como referência de arquitetura de alta escala para processar lotes de até 500 mil linhas.

---

## 07. [10:58] Diagnóstico de falha de renderização e separação do front-end (HTML/CSS/JS)

**Prompts:**
> vamos pro codigo, e agora

> e na parte do css e do js?

**Objetivo técnico:** Resolver o travamento de visualização externa causado por bloqueio de rede corporativa e a quebra de sintaxe decorrente da tradução automática do navegador, separando o projeto em camadas limpas (HTML semântico, estilos CSS puros e script JS reativo).

**Resposta da IA:** Diagnóstico das regras de tradução que alteraram seletores CSS essenciais (`:root`, `header`, `display`), fornecimento do código modularizado em 3 camadas e configuração de botões de teste interativo via CodePen/JSFiddle com dados simulados do regulamento Antecipe.

**O que foi feito com a resposta:** O layout foi testado e validado no CodePen, com verificação da renderização dos cards e da tabela de recusas ao acionar a rotina de demonstração.

---

## 08. [11:15] Decisão arquitetural do back-end (de Java para Python)

**Prompt:**
> o back end vai ser em python, assim, substitui java?

**Objetivo técnico:** Avaliar a viabilidade de usar Python (FastAPI/Flask) no back-end sob os critérios do edital: produtividade em um evento de 1 dia, leitura rápida de CSVs em memória com sets/hash maps e simplicidade de execução para o README eliminatório.

**Resposta da IA:** Confirmação de que o edital não impõe restrição de linguagem, apontando os ganhos em velocidade de desenvolvimento, facilidade de implementar logs sem dados sensíveis e manutenção do motor de regras sem redeploy via JSON.

**O que foi feito com a resposta:** O time alinhou a arquitetura do back-end em Python e manteve o front-end em HTML/CSS/JS, eliminando o overhead de configuração.

---

## 09. [11:30] Contrato de integração e especificação técnica

**Prompts:**
> entao agora eu vou aguardar eles fazerem o codigo em python, esse codigo que eles fizerem em python da certinho com esse meu layout front end ou eu vou ter que esperar o codigo deles ficarem pronto e ter que adaptar os meus pra dar certo?

> http://localhost:8000/api/analisar-lote falta so esse url pra conectar o front e o back certo?

> me passa todos os nomes, requisitos e etc que devem ter no codigo em python pra conseguir fazer a conexao entre o meu codigo front e o back

**Objetivo técnico:** Estabelecer um contrato formal de interface entre front-end e back-end (endpoint POST multipart, esquema JSON de resposta com `resumo` e `itens`, habilitação de CORS e regras de negócio do edital) para permitir desenvolvimento paralelo e integração imediata.

**Resposta da IA:** Especificação completa com contrato de dados, nomes de campos (`totalNotas`, `totalBruto`, `totalLiquido`, `totalRecusadas`, `motivoRecusa`), requisitos de escalabilidade em O(1), modelo sem redeploy via validadores JSON e geração de um documento técnico compartilhado no Google Drive (`Especificacao_Integracao_Antecipe_Kanastra`).

**O que foi feito com a resposta:** A especificação foi repassada formalmente aos desenvolvedores do back-end em Python para garantir conformidade de payloads e headers antes da subida da API.

---

## 10. [11:55] JavaScript unificado de produção com fallback resiliente

**Prompt:**
> com isso tudo, me mande agora o codigo java script atualizado para so colar dps os url e outros ngc do back em python

**Objetivo técnico:** Consolidar o código JavaScript (`script.js`) com isolamento de variáveis de ambiente (`API_URL` e `FILE_FIELD_NAME`), suporte a upload por arrastar e soltar, consumo assíncrono via `fetch`, fallback para dados simulados em caso de indisponibilidade da API e exibição amigável de diagnósticos de recusa (25 pontos de UX).

**Resposta da IA:** Script JS final desacoplado, com a função `enviarLoteParaBackend`, gerenciamento de estados visuais ("Processando lote...") e montagem dinâmica da tabela e dos cartões de resumo.

**O que foi feito com a resposta:** O código foi integrado ao front-end, mantendo a interface totalmente testável e preparada para conexão assim que o time de back-end subir a rota `POST /api/analisar-lote`.
