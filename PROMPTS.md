# Registro de PROMPTS

## 01. [09:54]
**Prompt:**  Vou copiar uma mensagem, guarde ela em sua memoria, e me espere novas instruções. Hackathon Antecipe: dataset para os participantes O desafio: portal Antecipe O problema: uma pequena empresa vendeu a prazo e quer o dinheiro hoje. Ela “vende” essas notas para o fundo, mas o fundo só pode comprar o que cumpre regras: prazo máximo, valor mínimo, sacado (quem vai pagar) não pode estar concentrado demais, CNPJ ativo etc. O que os times constroem: Design: a jornada da empresa, do upload das notas até ver quanto vai receber e por que algumas foram recusadas. O desafio de UX é explicar a recusa de forma clara. Front: upload de lote (CSV), tabela com status por nota e simulação do valor líquido (valor de face menos o desconto). Back: API que valida cada recebível contra critérios de elegibilidade configuráveis e calcula o preço de compra com uma taxa de desconto simples. Arquitetura: como modelar um motor de regras que o gestor do fundo altere sem deploy, e como garantir que o mesmo recebível não seja vendido duas vezes (idempotência e duplicidade). Arquivos Dados para o desafio Antecipe. Baixe os dois arquivos abaixo: Estoque: a carteira já comprada por 18 fundos, com cerca de 100 mil linhas (um único CSV, estoque_antecipe.csv, dentro do zip). Validadores: a configuração das regras do ANTECIPE FIDC. Cada validador tem um codigo, a chave ativo (só os ativos valem) e os parametros. estoque_antecipe_100k.zip 2.32 MiB validadores_antecipe.json 1.44 KiB Requisitos mínimos de entrega Prazo: até as 18h de sábado. Projetos enviados depois não são avaliados. Repositório com o código, com acesso liberado para os jurados. README com o passo a passo para rodar a aplicação do zero: dependências, comandos e variáveis de ambiente. Linguagem, framework e infraestrutura são livres. Aplicação funcionando, com: upload de um CSV de notas no mesmo formato do arquivo de exemplo (separador ;, decimal com vírgula, datas dd/mm/aaaa); regras lidas do validadores_antecipe.json, sem valores fixos no código; resultado de cada nota: aprovada ou recusada e, se recusada, o motivo, explicado de um jeito que a empresa entenda; valor líquido de cada nota aprovada e o total a receber; a mesma validação disponível pela tela e por uma API. Relatório curto (pode estar no README): o que o time construiu, as tecnologias usadas, as principais decisões e o que ficou de fora. Histórico dos prompts de IA usados durante o projeto (exportado ou em arquivo de texto). Apresentação aos jurados: o time mostra a solução funcionando e responde perguntas. Formato do CSV Separador ;, decimal com vírgula, datas dd/mm/aaaa, UTF-8, cabeçalho na primeira linha. Data-base dos dados: @Thursday. Coluna Significado NOME_FUNDO, DOC_FUNDO Fundo que comprou a nota NOME_CEDENTE, DOC_CEDENTE Empresa que vendeu a nota NOME_SACADO, DOC_SACADO Cliente que vai pagar a nota NU_DOCUMENTO Número da nota no sistema do cedente (cada empresa numera do seu jeito) TIPO_RECEBIVEL Duplicata, Duplicata de Serviço, Cheque, CCB ou Nota Comercial VALOR_NOMINAL Valor de face, em reais DATA_VENCIMENTO_ORIGINAL Data de vencimento DATA_AQUISICAO Data em que o fundo comprou a nota

**O que foi feito com a resposta:** A IA entendeu o que é o trabalho e como ele funciona para instruir nós participantes em como dar continuidade.


## 02. [10:03]

**Prompt:** Bom para começar, primeiro Aja como um consultor de TI, pense que sou um cliente seu, e acabei de enviar o meu desafio, mensagem enviada acima.

O seu trabalho é me fornecer o melhor caminho possivel para a conclusão dessa desasfio. A principal questão aqui: é o tempo, o trabalho deve ser concluído em até 6 horas.

Então com base no texto do desafio enviado primeiro. Monte um PLANEJAMENTO sobre a sucessão do que deve ser feito, o passo a passo.
- O que deve ser montado e pensado primeiro.
- O nosso grupo possuí três integrantes, então monte o planejamento, de forma que o trabalho fique bem distribuido entre os participantes.

IMPORTANTÍSSIMO:

Para fazer tudo o que se pede, aqui vai algumas caracteristicas sobre nosso grupo:
- Somos estudantes de Sistema de Informação do segundo período, então nosso conhecimento se limita praticamente à LINGUAGEM C.

Pense nisso, e monte o planejamento com base nessa linguagem.

Sabemos que no decorrer do projeto, deveremos fazer algo que foge do nosso escopo de conhecimento, então tudo que voce segerir pense que DEVE SER FEITO NA LINGUAGEM C, OU QUE SEJA O MAIS FACIL DE SER EXECUTADO NA LINGUAGEM C.

Pense com calma, não diga nada que voce não tenha certeza.

Tem alguma pergunta que voce acha necessario me fazer, antes de prosseguir?

**O que foi feito com a resposta:** Dividiu em horas, etapas e função de cada participante do grupo.
