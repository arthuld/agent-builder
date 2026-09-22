---
name: agv-novo-dinamico
description: Use somente quando o usuário pedir explicitamente a criação de um novo agente virtual de interação livre (dinâmico), nomeando o cliente. Não usar para auditar, documentar ou editar agente que já existe.
argument-hint: "[cliente] [dados]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
metadata:
  version: "2.0.0"
---

# Criar Agente Virtual de Pré-Atendimento

Cria a configuração completa de um agente virtual conversacional de pré-atendimento para o cliente
`$ARGUMENTS`: um assistente que atende por WhatsApp, classifica a demanda, coleta os dados necessários e
entrega o atendimento a uma fila humana.

## Esta skill é autocontida

Tudo que ela precisa está neste arquivo. **Não** consulte convenções externas, arquivos de instrução do
repositório, nem a configuração de outro cliente. Não existe "cliente de referência" a imitar: os formatos
da seção **Passo 2** são a referência, e são completos.

Isso é deliberado. A skill precisa produzir o mesmo resultado dentro deste repositório e fora dele, em outro
sistema, sem nada instalado ao lado.

Se houver convenções externas disponíveis e elas **contradisserem** este arquivo, pare e diga qual é a
divergência. Não escolha em silêncio.

## O modelo alvo

O agente gerado roda em **`gpt-5.4-nano`**, com `reasoning_effort` em `none` — o default da família, que a
plataforma não expõe. Quatro consequências valem para tudo que vem abaixo:

- **Saída fechada sempre que couber.** Enum no schema, template literal, tabela de decisão. Modelo pequeno
  erra menos escolhendo de uma lista do que redigindo livremente.
- **Toda borda escrita.** Modelo pequeno não infere o passo que falta — improvisa. Borda não escrita é
  comportamento inventado, e é a causa mais frequente de "o agente ignorou a regra".
- **Prompt um pouco mais longo e mais explícito** que o de um modelo maior. Aqui token e assertividade
  deixam de apontar na mesma direção: feche as bordas primeiro, meça depois, corte por último.
- **Markdown para estruturar, nada de XML.** Para o nano a doc **não prescreve formato de prompt
  nenhum** — o que ela exige é *ter* estrutura (`Generic instructions without structure` está na
  lista do que evitar). Markdown entrega isso pelo menor custo: medido nos agentes existentes, trocar
  os headers por tags XML custa **+217 tokens por turno por agente**, +5% do campo, sem ganho
  documentado. E o serviço que o XML prestaria — delimitar onde um bloco começa e termina — a
  plataforma já presta, porque os 4 campos são entradas separadas. Os blocos XML dos exemplos da
  documentação são orquestração multi-etapa do modelo frontier: o oposto do que o nano recebeu como
  orientação. Se um campo só fica legível com scaffolding pesado, o problema não é o formato — é que o
  campo está largo demais para o nano. Estreitar, não re-sintaxar.

Medição de token: `tiktoken`, encoding `o200k_base`.

**Se o modelo mudar, revise esta seção antes de tudo** — as escolhas de escrita abaixo derivam dela, e um
modelo maior torna várias delas desnecessárias.

## O contrato do runtime

Metade dos defeitos deste tipo de agente nasce de escrever uma regra num lugar que o modelo nunca lê. Esta
tabela decide **onde** cada coisa se escreve:

| Artefato | Campo da plataforma | Chega ao modelo |
| --- | --- | --- |
| As 4 seções de `agente.md` | Perfil · Diretrizes · Conduta · Segurança | **sempre-ativo** |
| §1 do manual | **Objetivo da Função** | **sempre-ativo** |
| §2 do manual | **Condições de Execução** | **sempre-ativo** |
| Schema da função — nome, parâmetros, `description` de cada um | cadastro da função | **sempre-ativo** |
| JSON de `ferramentas/dados/` | retorno da função | só no turno da chamada |
| Card do atendente | outro módulo | **nunca** — é a tela da atendente humana |
| `origem/`, `relatorios/` | — | **nunca** |

Sempre-ativo é pago em **todos** os turnos, inclusive naqueles em que nenhuma função é chamada. Duas
consequências que contrariam o instinto:

- **O manual inteiro é sempre-ativo.** Não existe "deixar a regra na §2 para não pagar" — a §2 custa
  exatamente como a §1. O que a §2 ganha é organização, não desconto.
- **O arquivo de dados não é.** Arquivo grande é barato; função a mais é cara. A conta está na R26.

## Ordem de execução

Passo 0 (ficha) → Regras → Passo 1 (origem) → Passo 2 (escrita) → Passo 3 (proibições) → Passo 4
(verificação) → Passo 5 (relatório).

**Leia as Regras Invioláveis antes de escrever qualquer arquivo.** Cada uma vem com o motivo. O motivo não é
enfeite: regra sem motivo é regra que a próxima revisão "simplifica", reintroduzindo o defeito que ela
existia para evitar.

---

## Onde criar a pasta do cliente

**Não assuma convenção de pastas.** Resolva pelo disco: busque o padrão `**/config/agente.md` por caminho
de arquivo (no Claude Code, a ferramenta `Glob`).
Cada resultado é um cliente já montado, e a pasta dele é o diretório **dois níveis acima** do arquivo — de
`X/Y/Cliente/config/agente.md`, a pasta do cliente é `X/Y/Cliente` e o agrupamento é `X/Y`.

| Estado | Ação |
| --- | --- |
| Encontrou pasta(s) de cliente | Criar ao lado. Havendo mais de um agrupamento (por modelo, por categoria), **perguntar em qual** |
| Não encontrou nada | **Perguntar onde criar.** Não inventar `Agentes Virtuais/` nem qualquer outra árvore |

A linha `destino.pasta` da ficha do Passo 0 recebe essa resposta, e é a mais bloqueante de todas: sem ela,
**não escreva arquivo nenhum** — todos moram dentro dessa pasta, então não existe "escrever o que não depende
dela". Não vale criar na raiz do diretório de trabalho "por não ter onde mais": isso é inventar árvore com
outro nome.

# Passo 0 — A ficha de parâmetros. **Antes** de escrever.

Esta é a razão de a skill existir. Um agente sem ela produz uma estrutura plausível e **inventa os dados do
cliente**: assume o gênero pelo nome do agente, redige a saudação por conta própria, presume o escopo, e só
lista as pendências no fim — depois de já ter decidido.

**Herdar regra de negócio de outro cliente é o erro mais caro desta skill.** Formato se reaproveita; regra de
negócio, nunca.

## A ficha é obrigatória e vem antes de tudo

Levante o que veio no comando e em `$ARGUMENTS/origem/`, e **preencha e exiba a ficha abaixo antes de
escrever qualquer arquivo**. Toda linha tem valor ou a marca `[PERGUNTAR]`.

```
FICHA DE PARÂMETROS — <cliente>
  cliente.grafia_comercial ........
  cliente.dominio .................
  agente.nome .....................
  agente.genero ...................
  agente.saudacao_literal .........
  plataforma.trata_consentimento ..
  plataforma.no_decisao_resolucao .
  transbordo.filas ................
  escopo.incluido .................
  escopo.excluido .................
  trilhas .........................
  funcoes.inventario ..............
  variaveis.origem ................
  negocio.regra_1..N ..............
  fluxo.confirma_antes_executar ... Sim
  fluxo.meta_interacoes ........... 5 a 7 mensagens do agente
  default.teto_lista .............. 5
  default.limite_secao1 ........... 950 caracteres
```

**Havendo qualquer `[PERGUNTAR]`, a próxima ação é perguntar ao usuário** — todas as perguntas em um bloco
só, não uma por vez (no Claude Code, a ferramenta `AskUserQuestion`). Não comece a escrever "enquanto isso".

Sem resposta depois de perguntar: escreva os arquivos que **não** dependem do dado e deixe o dependente de
fora, listando-o como pendência. Nunca preencha a linha com palpite nem com valor de outro cliente — a ficha
existe para tornar a lacuna **visível**, e um valor inventado nela derrota a ficha.

**Se não houver como perguntar** — execução automatizada, ou runtime sem mecanismo de pergunta — a regra é a
mesma, nunca mais frouxa: pare, entregue a ficha com as linhas em aberto e as perguntas que faria, e não
escreva o que depende delas. *Motivo: a ausência da ferramenta de perguntar não é permissão para decidir no
lugar do usuário. É justamente o caso em que decidir sozinho não é visto por ninguém.*

Reexiba a ficha preenchida no relatório final, com a origem de cada valor: informado, lido de `origem/`, ou
default.

## Bloqueantes — sem estes o arquivo nasce com dado inventado

| Dado | Por que não se deduz |
| --- | --- |
| **Grafia comercial do cliente** | Aparece na primeira mensagem que todo usuário lê. Não inventar acento, espaço ou caixa. Nome de pasta não é grafia comercial. |
| **Domínio de negócio** | Define se há limite de aconselhamento obrigatório (saúde, jurídico, financeiro) e qual terminologia usar. |
| **Nome e gênero do agente** | Gênero não se deduz do nome. A concordância do prompt inteiro depende disso. |
| **Texto literal da saudação** | É transcrito ao pé da letra. Se o cliente não tiver uma, proponha e peça aprovação — nunca assuma. |
| **Filas de transbordo** | São os nomes reais cadastrados na plataforma. Grafia divergente é transbordo perdido, e o erro não aparece em teste de conversa. |
| **Escopo incluído e excluído** | O que o cliente **não** faz é o que autoriza o agente a dizer "não atendemos". Sem lista explícita, o agente não pode negar nada. |
| **Inventário de funções** | Quais funções vão de fato existir. Cada uma a menos remove uma etapa do fluxo. |
| **Cada regra de negócio** | Obrigatoriedade de documento, exigência de pedido médico, quem pode agendar, o que exige atendente. Nunca herdar de outro cliente. |

## Duas perguntas sobre a plataforma de destino

Estas separam uma regra de domínio de uma premissa da plataforma. São o que torna a skill portátil.

**`plataforma.trata_consentimento`** — a plataforma obtém o consentimento de dados **antes** de a conversa
chegar ao agente?

- **Sim** → não escrever bloco de consentimento. Ele seria custo pago em todo turno duplicando controle que
  já existe a montante.
- **Não** → incluir o bloco de consentimento (formato em 2.2), com frase curta antes do primeiro dado
  pessoal e encerramento cordial **sem transbordo** se o usuário recusar o consentimento em si — não há
  atendimento a entregar.

Nunca decidir isso por conta própria: as duas configurações existem, e a errada ou vaza coleta sem
consentimento, ou paga por um bloco redundante.

**`plataforma.no_decisao_resolucao`** — a plataforma tem um nó de decisão que lê a variável de resolução
**antes** do roteamento de fila?

- **Sim** → na trilha de informação resolvida, a fila fica **em branco**; a plataforma desvia e encerra.
- **Não** → o ENUM de filas precisa de um valor de encerramento (ex: `Finalizacao_Atendimento`), senão o
  atendimento resolvido fica sem destino.

Os dois desenhos existem. Deduzir errado quebra em silêncio: o atendimento simplesmente não é entregue.

## Com default — assumir e informar no relatório

| Dado | Default |
| --- | --- |
| Confirmação dos dados antes de executar o transbordo | Sim |
| Meta de interações até finalizar ou transferir | 5 a 7 mensagens do agente |
| Modalidade fora de convênio (particular) | Disponível — assumir que sim e confirmar no relatório |
| Teto de itens por lista numerada | 5, com paginação por "Outras opções" |
| Limite da descrição de função | 950 caracteres (**teto**, não alvo — o usual fica em 600–850) |
| Tentativas antes do transbordo por falha | 2 |
| Delimitador de variável | `__NOME_DA_VARIAVEL__` |
| Formato de data | `DD/MM/AAAA` |

---

# Regras Invioláveis

Numeradas para referência **dentro desta skill**. Não cite estes números nos arquivos gerados — eles não
significam nada fora daqui.

## Variáveis

**R1 — Padrão de nome.** Toda variável de contexto usa `__IA_CAMPO__`, dois underscores de cada lado, caixa
alta, sem acento. Se o material de origem nomear fora do padrão (`IA_CPF`, `campo_ia`, `paciente_nome`),
normalize e **registre a normalização** numa nota no topo do dicionário de variáveis.
*Motivo:* a plataforma interpola pelo token exato. Nome divergente não gera erro — chega vazio ao painel do
atendente.
**Única exceção:** a coluna **Variável** do dicionário traz o nome **sem** os `__` (`IA_CAMPO`), porque é ali que a plataforma registra o campo. Em todo o resto — prompt, card, referências cruzadas — o token vai com os underscores.

**R2 — Quatro colunas, sempre.** O dicionário de variáveis tem exatamente: `Variável | Descrição | Regra de
Validação | Funções`. A coluna de validação carrega obrigatoriedade, formato ou ENUM completo, e o fallback.
*Motivo:* é o único lugar onde a lógica de cada campo fica escrita uma vez. Descrição sem regra de validação
vira decisão do modelo em runtime.

**R3 — Toda variável declarada precisa de algo que a preencha.** Declarar e definir fallback não basta.
Duas categorias, com verificações diferentes:
- *Variáveis de coleta* (nome, documento, data, item de interesse): basta o passo de coleta em prosa. Não
  precisam do token no prompt — exigi-lo só engorda o custo sempre-ativo.
- *Variáveis de controle* (fila, resolução, classificação da demanda): **precisam ser nomeadas
  explicitamente pelo token**, porque nenhum passo de coleta as alimenta. Só instrução direta faz o modelo
  preenchê-las. Ausência aqui é bug, não estilo.

**R4 — Variável de roteamento obrigatória.** Todo agente que aciona transbordo declara uma variável de fila
e a define **antes** de chamar a função. Proibido acionar transbordo com fila em branco quando existe
atendente de destino.
*Motivo:* transbordo sem fila cai em lugar nenhum, e o usuário fica esperando.

**R5 — Não declare variável de observações livres.** Os sinais que não cabem em campo dedicado — demanda
fora do escopo, item que o cliente não oferece, falha de triagem, demanda não identificada — já chegam ao
atendente pelo **otto resumo**, função predefinida da plataforma.
*Motivo:* uma variável de observações reimplementa capacidade nativa e paga token em todo turno, porque cada
ponto do prompt que a alimenta é sempre-ativo. Mesma razão pela qual não existe função de leitura de
carteirinha: o modelo já lê imagem.

**R6 — Três estados de ausência, nunca o mesmo texto.**
- `"Não Informado"` — o usuário **recusou explicitamente** um dado já perguntado.
- `"Não coletado"` — o transbordo foi acionado por **falha de triagem** ou repasse simples, **antes** de o
  dado ter sido perguntado.
- `"Não se aplica"` — o bloco da trilha em curso **deliberadamente não pergunta** esse dado.

*Motivo:* o atendente age diferente em cada caso. Um único texto para os três apaga a diferença, e "não se
aplica" lido como recusa faz o atendente cobrar um dado que ninguém deveria ter pedido.

## Fluxo

**R7 — Organizar em trilhas, não em esteira linear.** Classifique a demanda logo após a saudação e siga uma
das três:
- **Ação/transbordo** — qualificação completa + coleta → fila correspondente.
- **Informação** — o agente responde pela base, pergunta se há mais alguma coisa e **encerra como
  resolvido**, sem fila.
- **Repasse simples** — demanda fora do escopo que exige ação humana: **coleta mínima** (só o nome) e
  transbordo, **sem** triagem completa. A demanda em si o otto resumo entrega.

*Motivo:* não coletar dado desnecessário para o que só será repassado, e não acionar humano para o que o
agente resolve sozinho.

**R7a — Modalidade de pagamento é classificação, não coleta opcional.** Quando o domínio tiver convênio,
plano ou carteirinha, o agente pergunta **primeiro** qual é a modalidade — convênio ou particular — e só
então segue para os dados dela. Particular é uma **variação da trilha**, com os campos que se aplicam a
ela; os campos de convênio ficam `"Não se aplica"`. Assuma que o atendimento particular existe e confirme
no relatório: praticamente todo prestador atende particular.
*Motivo:* sem essa bifurcação, quem não tem convênio cai no laço de tentativas e termina registrado como
`"Não Informado"` — que a R6 define como **recusa explícita**. O atendente recebe "recusou informar o
convênio" sobre alguém que simplesmente não tem um, e vai cobrar um dado que ninguém deveria ter pedido.

**R8 — Fallback de classificação.** Se a variável de entrada que traz a demanda chegar vazia ou com valor
fora do ENUM esperado, defina o que fazer — nunca deixe essa borda implícita. Padrão: perguntar o mínimo
(normalmente só o nome) e transferir para a fila geral.
*Motivo:* é a borda mais frequente em produção e a que ninguém testa.

**R9 — O transbordo é o handoff único.** **Toda** trilha executa a função de transbordo, inclusive a de
informação resolvida. A variável de resolução decide o que a plataforma faz **depois** da chamada — ela não
decide se a função roda.
*Motivo:* escrever "dúvida sanada → encerrar sem acionar a função" deixa a automação de encerramento e as
tags de relatório sem gatilho: o atendimento nunca é entregue, e o número nunca fecha.
*Única exceção:* recusa de consentimento antes de qualquer coleta — não há atendimento a entregar.
*Consequência no schema:* se a trilha de informação não coleta nada, **só a variável de resolução pode ser
`required`** — nem o nome. Nome obrigatório faz toda dúvida resolvida falhar em silêncio.

Executar é uma ação; anunciar não realiza. Esta formulação vai **literalmente** no prompt gerado:

> Toda trilha termina obrigatoriamente com a execução da função de transbordo. *Executar a função é uma
> ação — anunciar a transferência em texto não a realiza.*

*Motivo:* é o ponto de falha nº 1 em produção. O paciente sai da conversa acreditando que foi transferido, e
não foi. Template literal porque modelo pequeno reproduz frase fixa melhor do que obedece a descrição.

*A mensagem de transferência não é do agente.* Quem envia o texto de encerramento ou de transferência é a
**plataforma**, depois da chamada, derivando-o das variáveis preenchidas. Por isso o prompt fica proibido de
conter despedida, aviso de transferência ou frase de encerramento. O que o agente faz no último turno é o
que a ficha definir em `fluxo.confirma_antes_executar`: com `Sim` (default), ele lê de volta o que coletou,
aguarda a confirmação do usuário e **então** executa.
*Motivo:* medido em produção — um prompt obrigava o literal *"Vou transferir você para a nossa equipe
agora"* antes de **todo** transbordo, inclusive na trilha de dúvida resolvida, que encerra sem fila. O
usuário saía informado de que falaria com alguém que nunca viria. E como o texto estava escrito em três
lugares do config, as três versões já divergiam entre si.

**R10 — Tentativas antes de desistir.** Defina o número de tentativas (padrão 2) após o qual o agente para
de insistir num dado, aciona o transbordo e marca os campos não perguntados como `"Não coletado"`.
*Motivo:* sem limite, o agente entra em laço com quem não vai responder.

**R10a — Falha de ferramenta tem escada própria.** Erro ou timeout **não** é retorno vazio, e os dois não
podem ter o mesmo tratamento. Escreva no prompt gerado:

> Refazer a **mesma** chamada 1× no mesmo turno, em silêncio. Persistindo, informar instabilidade e seguir
> **sem** transbordar. Transbordar só quando a **mesma** operação acumular 3 falhas.

*Motivo:* sem esta regra a borda fica implícita, e modelo pequeno diante de borda implícita improvisa — em
geral anunciando ao usuário um problema técnico que não sabe descrever, ou transbordando na primeira falha.

**R10b — Precedência entre regras, declarada.** O prompt tem quatro campos, e eles podem se contradizer em
caso de borda. Declare a ordem uma vez, em Regras de Segurança:

> Havendo conflito entre duas regras, vence a de Regras de Segurança. Nunca escolher em silêncio.

*Motivo:* é a única borda que o próprio prompt cria. Sem ordem declarada, o modelo resolve o empate por
proximidade no texto — e a regra de segurança é a que está mais longe do fluxo.

**R10c — Nenhum passo repergunta o que a conversa já resolveu.** Duas formas, as duas medidas em produção.
A cláusula vai **na linha do passo**, não no cabeçalho do fluxo:

> Dado que o usuário já informou espontaneamente é preenchido **sem perguntar** — inclusive a demanda
> declarada na primeira mensagem.
> Lista de opções mostra **apenas as que se aplicam** ao item já identificado. Opção única se confirma, não
> se oferece em lista.

*Motivo:* a regra genérica no topo do fluxo **não basta**. Medida num agente que a tinha escrita: ele
reperguntou se era agendamento ou dúvida depois de o usuário abrir com *"quero agendar uma acupuntura"*, e
ofereceu três unidades para um serviço que só existe em uma — o usuário reclamou, e o agente repetiu a mesma
lista. O modelo lê o passo que está executando, não o parágrafo de abertura da seção.

**R10d — Mudança de demanda reclassifica, e invalida o que não se aplica.** O usuário pode trocar de
assunto depois de a trilha ter começado. Escreva no prompt gerado o que sobrevive e o que morre:

> Mudando a demanda, reclassificar antes de continuar. Dado de identificação já informado é reaproveitado
> **sem perguntar de novo**. Dado ligado à demanda anterior — fila, item de interesse, qualificação — é
> descartado, e perguntado de novo só se a nova demanda precisar dele.

*Motivo:* sem isso a nova demanda herda a fila e a qualificação da antiga, e o transbordo entrega um caso
coerente com a conversa errada. É pior do que faltar dado: o atendente não tem como perceber.

## Funções

**R11 — Descrição da função ≤ 950 caracteres.** É o texto registrado na API. Sem saudação, sem "esta função
serve para". Duas coisas: o que ela retorna e em qual intenção do usuário acioná-la. Feche delimitando o que
ela **não** decide, quando houver função vizinha que decide.
*Motivo:* é pago em 100% dos turnos. E função sem fronteira declarada é chamada no lugar da vizinha.

**R12 — Nunca chamar função com parâmetro deduzido.** Faltando um dado obrigatório, o agente **retém a
chamada** e pergunta. Nunca supor documento, convênio, unidade, item ou qualquer parâmetro não informado
explicitamente.
*Motivo:* parâmetro inventado retorna dado de outra pessoa ou vazio, e os dois viram resposta errada com
cara de certa.

**R12a — Só colete dado que tem finalidade no caminho em curso.** Antes de acrescentar um passo de coleta,
aponte quem consome o dado: um parâmetro de função, ou um campo que o atendente recebe no card. Sem
consumidor, o passo não existe. Em particular, separe **orientação geral** ("como faço para acessar X",
"quais são os canais") de **consulta individual** ("qual é o meu X"): a primeira não precisa de
identificador nenhum.
*Motivo:* medido em produção — um agente pedia documento para uma função que devolvia só canais e prazos
genéricos, iguais para todo mundo. O dado não alimentava nada, e a função passava a parecer uma consulta
autenticada que ela não fazia.

**R12b — Toda sentinela usada no prompt consta do `enum` do parâmetro.** Campo com `enum`, `pattern` ou
`format` que recebe `"Não coletado"` sem tê-lo na lista faz a plataforma **descartar a chamada em
silêncio** — o sintoma é "o agente chega na função e não faz nada". A correção é acrescentar a sentinela ao
`enum`, **nunca** afrouxar o campo para texto livre: em modelo pequeno o enum é a única restrição
estrutural disponível, e schema afrouxado para acomodar sentinela é defeito.
*Exceção — ENUM fechado por natureza.* Alguns campos não aceitam sentinela, tipicamente a fila de
transbordo, cujos valores são as filas reais do cliente. Para esses, declare **qual valor real do ENUM vale
como fallback** quando o dado não foi coletado, e diga explicitamente que o campo não aceita sentinela.
Deixar isso implícito produz o pior defeito possível: a transferência é descartada sem erro visível.

**R13 — Responder só o subconjunto perguntado.** Ao processar o retorno de uma função que carrega uma base
grande, responda **apenas** com o que foi perguntado. Nunca cole a base inteira na conversa.
*Motivo:* base inteira na tela faz o
modelo misturar itens que ninguém perguntou.

**R14 — Tolerância fuzzy só dentro da mesma entidade.** Quando uma função valida um dado informado pelo
usuário contra uma base, a tolerância cobre variações da **mesma** entidade: caixa, acento, abreviação
clara, nome popular. Nunca aproximar duas entidades diferentes por soarem parecidas. Em dúvida, **falhar
fechado** — tratar como não localizado e perguntar.
*Motivo:* aproximar dois itens diferentes agenda a pessoa para a coisa errada, e ninguém percebe até ela
chegar lá.

**R15 — Duas seções no manual, com o nome do campo da plataforma.** Todo manual de função tem exatamente
`## 1. Objetivo da Função` · `## 2. Condições de Execução` — os nomes dos dois campos onde o texto é
colado, como já acontece com as quatro seções do prompt. Nunca uma terceira, e nunca uma seção de
especificação técnica (JSON Schema): isso é artefato de documentação, não de configuração.
*Motivo:* a seção nomeada pelo campo de destino elimina a dúvida de onde cada texto vai. E não existe
terceira porque não existe um terceiro campo para colá-la.

**R16 — As duas seções do manual são sempre-ativas.** §1 e §2 são campos da plataforma, pagos em **todos**
os turnos junto com o schema da função — não só quando a função é chamada.
*Motivo:* a versão anterior desta regra afirmava o contrário, que a §2 era documentação fora do alcance do
modelo. Sob essa premissa, toda medição de sempre-ativo feita nestes agentes subestimou o custo por uma §2
inteira vezes o número de funções, e regra escrita na §2 parecia gratuita. Não é: custa como a §1.
*Consequência:* regra que vale para o fluxo inteiro vai no prompt principal e **não** se repete na §2;
regra que só vale ao ler o retorno daquela função vai na §2 e **não** se repete no prompt. Duplicar entre
os dois paga duas vezes e produz deriva (R19).

## Dados

**R17 — Higiene do JSON de base.** Chaves com nome semântico claro, nunca nome de coluna de sistema legado
do cliente. Sem `null`, sem chave vazia, sem metadado que não serve ao atendimento. Números e booleanos
tipados, não encapsulados em string. Indentado e legível — **não minificar**, a plataforma já minifica no
envio e estes arquivos são revisados por humanos.

**R18 — Sentinela explícita, nunca valor ambíguo.** Nunca deixe um valor que o modelo leia com o sentido
**oposto** ao pretendido. Lista vazia `[]` é lida como "**nenhum**", não como "todos". Quando o significado
for "todos" ou "não se aplica", use sentinela explícita (`["Todos"]`) e documente a leitura na §2 do manual
daquela função.
*Motivo:* o caso clássico. `[]` em "convênios atendidos" faz o agente negar cobertura que existe.

**R19 — Um assunto, um arquivo dono.** O mesmo fato nunca aparece em dois JSONs, nem duplicado verbatim
entre o prompt e um manual.
*Motivo:* o custo não é token — é deriva. A próxima correção é aplicada num lado só, e as duas versões
passam a se contradizer em silêncio.

**R20 — Regra geral de dados, declarada uma vez.** No topo das diretrizes, uma única regra: *todo dado
factual vem da função no momento da chamada; nunca memorizar, supor ou reproduzir no prompt*. Cada regra
seguinte só aponta **qual função** consultar, sem repetir a ressalva.
*Motivo:* repetir "não memorizar" em cada item multiplica o custo sempre-ativo sem adicionar instrução.

## Conduta, segurança e plataforma

**R21 — Perguntas em blocos relacionados, dentro de uma meta de interações.** O agente agrupa numa mensagem
só as perguntas do mesmo assunto — os dados de identificação numa lista, a qualificação em outra — em vez de
uma pergunta por mensagem. A ficha define a meta de mensagens do agente, da saudação até executar o
transbordo (default **5 a 7**), e o fluxo escrito precisa caber nela.
*Motivo:* a cobrança do WhatsApp passou a ser por mensagem. Uma pergunta por mensagem multiplica o custo de
canal e alonga o atendimento sem ganhar precisão — bloco relacionado é respondido de uma vez.
*Limite:* bloco não é formulário. Passando de 4 ou 5 itens, ou misturando assuntos que o usuário
responderia em momentos diferentes, parta em dois. O teto de itens por lista do contrato de saída continua
valendo dentro do bloco.

**R22 — Limite de atuação em domínio regulado.** Domínio de saúde, jurídico ou financeiro exige uma regra
explícita de "Sem aconselhamento [domínio]" nas regras de segurança, **mesmo que o cliente não peça**. Uma
clínica nunca indica exame, diagnóstico, preparo ou tratamento a partir de sintoma relatado.
*Motivo:* a ausência dessa instrução no material do cliente não significa que ela é dispensável — significa
que ninguém pensou nisso.

**R23 — Agrupar em subtítulos a partir de 5 itens.** Seções de conduta ou segurança com 5+ itens ganham
subtítulos `###` temáticos, em vez de uma lista única.

**R24 — Negrito com um único asterisco.** Toda instrução de destaque textual nas mensagens ao usuário
especifica `*texto*`, nunca `**texto**`.
*Motivo:* o WhatsApp só interpreta um asterisco. `**` aparece literal na tela, poluindo a mensagem.
*Exceção:* o card do atendente (arquivo de contexto) é markdown de painel, não mensagem — ali `**` é
correto.

**R25 — Proibido citar caminho ou nome de arquivo no conteúdo do prompt.** O prompt principal e as descrições
de função nunca citam pasta, nome de arquivo do projeto, nem número de seção. Referências cruzadas se
resolvem inline (repetindo a regra curta) ou pelo nome do campo da plataforma.
*Motivo:* o usuário e o modelo não têm "arquivos" como referência, e citar estrutura interna vaza processo
interno numa conversa com o público.

**R26 — Consciência de custo.** O bloco sempre-ativo é pago em **todos** os turnos: as 4 seções do prompt,
mais **§1 + §2 + schema de cada função**. Nasce enxuto: sem dado que a função retorna, sem prosa de
justificativa, sem regra escrita duas vezes. Quando precisar cortar, corte **redundância e verbosidade**,
nunca regra: o racional vai para o relatório, onde não é pago por turno.

O **arquivo de dados** que a função retorna não entra nesse bloco — é pago só no turno da chamada. Daí a
conta de desenho, que tem dois lados e precisa dos dois:

- **Fundir economiza** uma §1 + §2 + schema por turno, em todos os turnos da conversa.
- **Fundir custa** carregar o JSON da outra função em toda chamada isolada. A plataforma devolve o
  **arquivo cheio** — não há filtro por parâmetro. Fundir uma base pequena numa grande faz toda consulta à
  pequena pagar as duas.

Regra prática: **funda** quando as duas forem quase sempre acionadas juntas **e** a menor for pequena;
**mantenha separada** quando uma for raramente acionada (carga preguiçosa) **ou** quando as duas bases
forem grandes. Não force a fusão: assunto genuinamente distinto merece função própria. Partir um arquivo
grande em duas funções piora os dois lados — paga mais uma §1, §2 e schema em todo turno, e não reduz o
retorno.

**R27 — Quatro campos, quatro seções.** A tela de configuração da plataforma tem quatro campos separados —
Perfil do Agente Virtual, Diretrizes de Atendimento, Regras de Conduta, Regras de Segurança — e o arquivo de
prompt é colado **campo a campo**, não como arquivo único. Por isso a numeração `## 1.`–`## 4.` é fixa e
nunca ganha uma quinta seção.

---

# Passo 1 — Ler o material do cliente

**O material do cliente chega por dois caminhos, e os dois valem:** arquivos na pasta `origem/` do cliente,
e/ou texto colado no próprio comando que invocou esta skill. Nenhum dos dois é obrigatório e nenhum tem
precedência — o que existir é fonte primária. *Motivo: exigir `origem/` faria a skill marcar `[PERGUNTAR]` em
linha cujo dado está à vista no comando.*

**Se o material vier colado no comando**, extraia dele só o nome do cliente para nomear a pasta, e salve o
restante verbatim em `origem/especificacao-agente-[NomeCliente].md`, criando a pasta `origem/` se não existir.
A partir daí trate esse arquivo como fonte primária.

Leia **todos** os arquivos que existirem em `$ARGUMENTS/origem/`. Extraia:

- Domínio de negócio e terminologia do setor
- Serviços ou produtos oferecidos, e o que explicitamente **não** é oferecido
- Públicos-alvo e perfis de usuário
- Canais de contato e URLs oficiais
- Dados de identificação a coletar
- Filas de atendimento humano mencionadas, com a grafia usada pelo cliente
- Regras de negócio declaradas (o que exige documento, o que exige humano, quem pode ser atendido)

`origem/` vazia ou ausente não é impedimento: significa que quase toda linha da ficha vira `[PERGUNTAR]`.

---

# Passo 2 — Escrever. Os formatos são estes.

Não há cliente de referência a consultar. Os esqueletos abaixo são a referência completa.

## 2.1 Árvore

```
[NomeCliente]/
├── config/
│   ├── agente.md
│   ├── variaveis.md
│   └── clienteinfo.json
├── ferramentas/
│   ├── dados/           get_*.json
│   └── manuais/         get_*.md + a função de transbordo
├── origem/              (já existente, ou criada no Passo 1)
└── relatorios/          (nasce com o primeiro relatório)
```

Sem pasta de schemas. Sem pasta criada "para depois".

## 2.2 `config/agente.md`

Cabeçalho, parágrafo de abertura, e as quatro seções separadas por `---`. Emoji no `###` é a convenção
visual; mantenha.

```markdown
# 🤖 Configurações do Agente Virtual

Este documento consolida as diretrizes de personalidade, regras operacionais, de conduta e segurança para
[o/a] **[Agente]**, assistente virtual oficial [do/da] **[Cliente]**.

---

## 1. Perfil do Agente Virtual

### 📋 Descrição do Papel
### 👥 Público-Alvo
### ✨ Características (Personalidade e Tom de Voz)

---

## 2. Diretrizes de Atendimento

### ⚠️ Regras Críticas
### 📌 Regra Geral de Dados
### 🚦 Classificação da Demanda
### 🅰️ Trilha A — [Ação]
### 🅱️ Trilha B — [Informação]
### 🅲 Trilha C — Repasse Simples
### ✅ Confirmação dos Dados
### 🧯 Bordas
### 🔢 Regra de Tentativas e Transbordo

---

## 3. Regras de Conduta

### 📐 Formato da Resposta
### ✍️ Linguagem e Formato
### 🤝 Tom e Acolhimento
### 🎯 Limites de Escopo

---

## 4. Regras de Segurança

### 🔎 Transparência e Confidencialidade
### 🩺 Sem Aconselhamento [Domínio]
### 🔐 Proteção de Dados
### 🛡️ Limites de Atuação
```

**O que vai em cada bloco obrigatório:**

- **Regras Críticas** — de 3 a 5 travas, no topo do campo, antes de qualquer fluxo. São as regras cuja
  violação é binária e cara: o que o agente jamais confirma, o que jamais deduz, e o template literal de
  execução (R9). Nada de tom, nada de formato, nada que dependa de julgamento.
  *Motivo:* o campo de Diretrizes é o mais longo e o mais consultado. Trava enterrada no meio dele compete
  com trinta linhas de fluxo; trava no topo é a primeira coisa que o modelo lê ao entrar no campo.
- **Regra Geral de Dados** — a declaração única de R20. Vem logo depois das travas.
- **Classificação da Demanda** — como o agente decide a trilha, o ENUM de motivos, e o fallback de R8.
  Costuma ser uma tabela `Demanda | Motivo | Trilha | Fila`.
- **Trilha A** — a coleta completa, passo a passo, com o que perguntar e em que ordem, fechando com a fila e
  a chamada do transbordo.
- **Trilha B** — quais funções respondem o quê, a pergunta de fechamento ("posso ajudar em mais alguma
  coisa?") e o encerramento com resolução positiva. **Ainda executa o transbordo** (R9).
- **Trilha C** — coleta mínima, fila e transbordo. Uma linha explícita proibindo a coleta completa aqui.
- **Confirmação dos Dados** — o que o agente lê de volta antes de executar o transbordo, e o que faz se o
  usuário corrigir algum item. Presente quando `fluxo.confirma_antes_executar = Sim` (default). Termina
  executando a função **no mesmo turno** da confirmação: o agente não espera um segundo "sim" depois de
  executar, e não escreve despedida nenhuma (R9).
- **Bordas** — tabela `situação | ação`, com **uma linha por borda**: retorno vazio de função, falha técnica
  (R10a), dado que o usuário não dá (R10b não; ver Tentativas), e conflito entre regras (R10b). Tabela, não
  prosa: a borda tem que ser encontrável por varredura visual, não por leitura.
- **Regra de Tentativas e Transbordo** — o limite de R10 e o que fica `"Não coletado"`.
- **Formato da Resposta** — o contrato de saída, em 4 a 6 linhas: como as perguntas se agrupam em blocos
  relacionados e qual é a meta de interações (R21), teto de itens em lista, se numera, se usa emoji, e qual
  mensagem é template literal.
  *Motivo:* é o passo que mais falta nos agentes existentes. Sem contrato, o modelo escolhe o formato a cada
  turno, e modelo pequeno escolhe mal com frequência.
- **Linguagem e Formato** — tom da escrita e a regra do asterisco único (R24). Não repetir aqui o que já
  está no contrato de saída.
- **Sem Aconselhamento [Domínio]** — obrigatório em domínio regulado (R22).

**Blocos condicionais, conforme a ficha:**

- `### 🔐 Consentimento` — **só** se `plataforma.trata_consentimento = Não`. Frase curta antes do primeiro
  dado pessoal, aguardar resposta, e encerramento cordial sem transbordo se o usuário recusar.
- `### 💳 Modalidade de Pagamento` — **só** se o domínio tiver convênio ou plano (R7a). A bifurcação
  convênio × particular e quais campos se aplicam a cada uma.
- Blocos de escopo, urgência ou exceção próprios do domínio.

## 2.3 `config/variaveis.md`

Duas notas em blockquote, depois a tabela. Nesta ordem.

```markdown
# Variáveis de Contexto — [Agente] ([Cliente])

> **Normalização de nomenclatura.** [De onde vieram os nomes e o que foi renomeado — ou a declaração de que
> o material de origem não definia nomes próprios e todo o padrão foi criado a partir dos campos descritos
> em linguagem natural.]

> **Nota sobre valores de ausência.** Três situações distintas deixam uma variável sem dado real, e **nunca**
> podem usar o mesmo texto:
> - `"Não Informado"` — o usuário **recusou explicitamente** um dado que já foi perguntado.
> - `"Não coletado"` — o transbordo foi acionado por **falha de triagem** ou repasse simples, **antes** de o
>   dado ter sido perguntado.
> - `"Não se aplica"` — o bloco de coleta da trilha em curso **deliberadamente não pergunta** esse dado.
>
> Nunca inventar ou deduzir um valor para viabilizar a chamada da função.

| Variável | Descrição | Regra de Validação | Funções |
| --- | --- | --- | --- |
| `IA_CAMPO` | [o que é] | Obrigatório/Opcional. Formato ou ENUM completo. Fallback. | `nome_funcao` → parâmetro `nome_param` |
```

Na coluna **Variável** o nome vai **sem** os underlines duplos — é assim que a plataforma registra o campo. Os
`__` são delimitadores de interpolação e permanecem em todo o resto: prompt, `clienteinfo.json` e as
referências cruzadas dentro das outras colunas.

**Núcleo canônico de controle.** Estas três existem em todo agente; as de coleta se acrescentam a elas:

| Variável | Papel |
| --- | --- |
| `__IA_MOTIVO_CONTATO__` | Classifica a demanda logo após a saudação; determina trilha e fila |
| `__IA_ATENDIMENTO_FILA__` | Fila humana de destino; obrigatória sempre que a resolução for negativa |
| `__IA_ATENDIMENTO_RESOLVIDO__` | Único parâmetro obrigatório em toda chamada de transbordo |

A coluna de validação é onde mora a lógica: ENUM completo, condição de obrigatoriedade por trilha, sentinela
aceita no `enum` do parâmetro (R12b) e fallback. Descrição sem validação é campo sem regra.

Acrescente, no rodapé, uma nota de aplicação com o que a plataforma precisa saber: variáveis a cadastrar,
comportamento do nó de decisão de resolução, e o que muda se ele não existir.

## 2.4 `config/clienteinfo.json`

Array com um objeto. `nome` é a variável de destaque do card do atendente, em negrito duplo — aqui `**` é
correto (R24, exceção).

Cada bloco tem `titulo` e um `informacoes` com **dois arrays de mesmo tamanho**: rótulos legíveis primeiro,
tokens depois, pareados por índice. Tamanhos diferentes desalinham o card em silêncio.

```json
[
    {
        "nome": "**__IA_MOTIVO_CONTATO__**",
        "informacoes": [
            {
                "titulo": "Informações do Paciente",
                "informacoes": [
                    ["Nome Completo", "CPF", "Data de Nascimento"],
                    ["__IA_PACIENTE_NOME__", "__IA_PACIENTE_CPF__", "__IA_PACIENTE_DATA_NASCIMENTO__"]
                ]
            },
            {
                "titulo": "Resumo do Atendimento",
                "informacoes": [
                    ["Resolvido pel[o/a] [Agente]", "Fila"],
                    ["__IA_ATENDIMENTO_RESOLVIDO__", "__IA_ATENDIMENTO_FILA__"]
                ]
            }
        ]
    }
]
```

Blocos típicos: "Informações do [Usuário]" e "Resumo do Atendimento". Um terceiro só quando o fluxo
justificar. Indentação de 4 espaços. Adapte o rótulo do usuário ao domínio (paciente, cliente, segurado).

## 2.5 `ferramentas/manuais/*.md`

Exatamente duas seções, separadas por `---`, nomeadas pelo campo da plataforma onde cada uma é colada.
**As duas são sempre-ativas** (R16).

````markdown
## 1. Objetivo da Função

[Prosa corrida, ≤ 950 caracteres. Sem saudação, sem "esta função serve para". Duas coisas: o que retorna e
em qual intenção do usuário acioná-la. Fechar delimitando o que ela NÃO decide, quando houver função
vizinha que decida.]

---

## 2. Condições de Execução

```markdown
================================================================
FUNÇÃO: nome_da_funcao
================================================================
# CONTRATO DE RETORNO
- [campo]: [o que é, e a armadilha de leitura]

# LEITURA DOS CAMPOS
- [como interpretar cada campo; o que nunca inferir de uma ausência]
- [semântica de qualquer sentinela usada no JSON]

# APLICAÇÃO
- [o que esta função responde e o que ela NÃO responde]
- [tolerância fuzzy só na mesma entidade; em dúvida, perguntar]
- [responder só o subconjunto perguntado, nunca colar a base inteira]
- [nunca inventar valor que não conste no retorno]
```
````

**Detalhes que não são óbvios:**

- **Não existe seção de exemplos.** Não há um terceiro campo na plataforma para colá-la, e exemplo que o
  modelo não recebe não ensina nada ao agente — só cria uma segunda versão da regra, que a revisão seguinte
  corrige de um lado só. Os casos de teste vão para a matriz de homologação (Passo 5).
- **A §2 custa o mesmo que a §1** (R16). Escreva nela só o que é específico de ler o retorno **desta**
  função. O que vale para o fluxo inteiro vai no prompt principal, uma vez.
- A função de transbordo é a única sem JSON correspondente, e sua §2 é a mais longa: carrega a tabela de
  filas, a regra de resolução e a lista completa de parâmetros.

## 2.6 `ferramentas/dados/*.json`

```json
{
    "assunto": [
        {
            "nome": "[item]",
            "campo_semantico": "[valor tipado corretamente]",
            "lista_relacionada": ["Todos"]
        }
    ]
}
```

Aplicam-se R17, R18 e R19. Quando o JSON usar uma sentinela ou tiver uma convenção de leitura não óbvia, a
regra correspondente vai na §2 do manual daquela função — o JSON sozinho não ensina a lê-lo.

## 2.7 Nomenclatura de funções

`get_*` para consulta, mais uma função de transbordo. Nome descritivo do assunto, não do arquivo de origem
do cliente. Nos textos, cite a função sempre pelo **nome completo** — referência curta sobrevive a
renomeação apontando para a função errada, e não dá erro visível.

Um cliente típico tem de **3 a 5** funções `get_*`, mais o transbordo. Acima disso, verifique se não é
fragmentação de um mesmo assunto (R19) antes de aceitar — mas não force a fusão: assunto genuinamente
distinto merece função própria.

*Por que o número importa:* cada função paga **§1 + §2 + schema** no sempre-ativo, em todo turno; o arquivo
de dados dela, só no turno da chamada. A conta dos dois lados — quando fundir compensa e quando não — está
na R26. Partir um arquivo grande em duas funções **piora** o custo.

---

# Passo 3 — Proibido

- **Herdar regra de negócio de outro cliente.** Formato se reaproveita; regra de negócio, nunca.
- **Preencher linha da ficha** com palpite, com default não declarado, ou com valor de outro cliente.
- **Inventar** nome de convênio, serviço, profissional, unidade, fila ou URL.
- **Citar caminho de pasta, nome de arquivo ou número de seção** dentro do que vira prompt (R25).
- **Hardcodar no prompt** dado que uma função retorna (R20, R26).
- **Criar uma quinta seção `##`** no prompt principal (R27), ou uma terceira seção no manual (R15).
- **Escrever despedida, aviso de transferência ou frase de encerramento** no conteúdo de prompt. Essa
  mensagem é enviada pela plataforma depois da chamada, não pelo agente (R9).
- **Deduzir o gênero do agente** pelo nome.
- **Usar retorno vazio de função como negação.** Vazio significa "não veio", não "não existe". A única
  autorização para negar é uma lista de exclusão explícita, informada pelo cliente.
- **Minificar** os JSONs de base (R17).

---

# Passo 4 — Verificação mecânica

Rodar **todas** antes de entregar.

```
1.  Toda variável declarada tem algo no prompt que a preencha
    (controle: buscar o token nomeado; coleta: basta o passo em prosa)
2.  Todo token do card do atendente tem variável declarada no dicionário
3.  Os arrays de rótulo e de token têm o mesmo tamanho, bloco a bloco
4.  O card do atendente é JSON válido
5.  Nenhum `**` como instrução de destaque no conteúdo de prompt
6.  Descrição de cada função ≤ 950 caracteres
7.  Todo manual com exatamente 2 seções: `1. Objetivo da Função` e `2. Condições de Execução`
8.  Nenhum caminho, nome de arquivo ou `§N` no conteúdo de prompt
9.  Nenhum `[]` ou `null` nos JSONs de base
10. Nenhuma tabela ou regra duplicada verbatim entre o prompt e um manual
11. O prompt principal tem exatamente 4 seções `##`
12. Nenhum nome próprio de outro cliente em lugar nenhum
13. Toda função citada no prompt tem manual, e todo manual é citado
14. Toda trilha termina acionando a função de transbordo (R9)
15. O bloco Regras Críticas existe, é a primeira coisa das Diretrizes, e tem de 3 a 5 itens
16. A formulação literal de execução (R9) aparece verbatim no prompt
17. O bloco Bordas cobre as quatro: retorno vazio, falha técnica, dado não obtido, conflito entre regras
18. Existe bloco de Formato da Resposta em Regras de Conduta
19. Toda sentinela usada no prompt consta do `enum` do parâmetro correspondente, ou o parâmetro não tem
    `enum`. Sentinela fora do enum faz a chamada ser descartada em silêncio (R12b)
20. Nenhuma despedida, aviso de transferência ou frase de encerramento no conteúdo de prompt (R9)
21. O caminho mais longo do fluxo cabe na meta de interações da ficha — conte as mensagens do agente da
    saudação até o transbordo (R21)
22. Havendo convênio ou plano no domínio, existe a bifurcação de modalidade e o caminho particular (R7a)
23. Todo passo de coleta tem consumidor nomeado: parâmetro de função ou campo do card (R12a)
```

Meça o **bloco sempre-ativo** — as 4 seções do prompt mais **§1 + §2 + schema de cada função**. É o que a
plataforma reenvia a cada turno. Meça o **texto final**, o que vai ser colado na plataforma, nunca um
rascunho: rascunho não conferido contra esta checklist já subestimou o resultado em 22 pontos percentuais,
porque o que ele "economizava" era precisão que precisou voltar. Reporte o número medido, não estimado.

Os itens 15 a 23 existem porque o agente roda em modelo pequeno: são as lacunas que fazem um `nano`
improvisar. Vários deles aumentam o token em vez de reduzir. É deliberado.

---

# Passo 5 — Relatório final

Fechar exibindo, nesta ordem:

1. **Tree criada**, com contagem de funções e de variáveis.
2. **A ficha reexibida**, com a origem de cada valor: informado por você, lido de `origem/`, ou default.
3. **Pendências, separadas por quem resolve:**
   - *Bloqueiam a homologação:* dado de cliente que faltou, e o que exatamente não pode ser validado sem ele.
   - *Ação de plataforma:* variáveis a cadastrar, funções a registrar, filas a criar com a grafia exata,
     permissões a liberar.
   - *Dúvida aberta que não bloqueia.*
4. **Pontos importantes** — as decisões que mudam comportamento e que alguém vai questionar depois. No
   mínimo: escopo assumido, o que acontece com demanda fora da lista de exclusão, se o consentimento entrou
   ou não e por quê, e o comportamento na trilha resolvida.
5. **Custo do sempre-ativo**, medido.
6. **A matriz de homologação**, escrita em `relatorios/homologacao.md` do cliente — uma linha por caso, no
   formato `cenário | resultado esperado`. Cobre no mínimo: cada trilha até o desfecho; classificação vazia
   ou fora do ENUM (R8); o caminho particular (R7a); o usuário que já abre dando vários dados (R10c);
   mudança de demanda no meio da conversa (R10d); recusa de um dado (R10); falha de ferramenta (R10a); e o
   desfecho resolvido **versus** transferido (R9). É o arquivo que a equipe usa para testar, e não vai para
   a plataforma.

**Nunca fechar dizendo "pronto" com pendência de dado de cliente aberta.** Diga o que está pronto para colar
na plataforma, o que está pronto como documento interno, e o que não sobe até a pendência fechar.

---

## Changelog

- **2.0.0** — **Corrigido o contrato do runtime: a §2 do manual é sempre-ativa.** A R16 afirmava o
  contrário — que §2 e §3 eram documentação fora do alcance do modelo. São dois campos da plataforma,
  `Objetivo da Função` e `Condições de Execução`, pagos em todo turno junto com o schema; toda medição de
  sempre-ativo feita sob a premissa antiga subestimou o custo por uma §2 vezes o número de funções. Daí
  vêm: a tabela do contrato do runtime, a §3 removida (não há campo para ela, e exemplo que o modelo não
  recebe só produz uma segunda versão da regra), os manuais renomeados pelos campos de destino, e a conta
  de fusão de funções com os dois lados na R26. Outras mudanças de comportamento: a mensagem de
  transferência é da plataforma e o prompt fica proibido de escrevê-la (R9); confirmação dos dados antes de
  executar vira bloco padrão; perguntas passam a ser agrupadas em blocos relacionados com meta de
  interações, por causa da cobrança por mensagem do WhatsApp (R21, que substitui a regra de mascaramento —
  removida, porque o documento fica no histórico da plataforma e é coletado sob consentimento); bifurcação
  de modalidade de pagamento com caminho particular explícito (R7a); coleta só com consumidor nomeado
  (R12a); sentinela declarada no enum promovida de item de checklist a regra (R12b); e reclassificação na
  mudança de demanda (R10d). O Passo 5 passa a emitir a matriz de homologação.
- **1.2.0** — **Formato declarado: markdown para estruturar, nunca XML.** A documentação oficial não
  prescreve formato de prompt para o `gpt-5.4-nano` — o que ela exige é *ter* estrutura. Medido: trocar
  os headers por tags XML custaria +217 tokens por turno por agente (+5% do campo), sem ganho
  documentado, e o que o XML resolveria — delimitar blocos — a plataforma já resolve, porque os 4 campos
  são entradas separadas. A regra existe para impedir que a próxima revisão "melhore" o prompt para os
  blocos XML dos exemplos da documentação, que são orquestração multi-etapa do modelo frontier.
- **1.1.0** — Adequação ao `gpt-5.4-nano`. Modelo alvo declarado, com as consequências de escrita que derivam dele. Acrescentados os três blocos que faltavam no prompt gerado — **Regras Críticas** no topo das Diretrizes, **Bordas** e **Formato da Resposta** — e as regras de borda que não existiam: falha técnica com escada própria e precedência entre regras declarada. Motivo: a orientação oficial do nano pede tarefa estreita, saída fechada e nenhuma borda implícita; borda não escrita é comportamento inventado. Acrescentada a formulação literal de execução (R9), que já existia no modelo estático e é o ponto de falha nº 1. Corrigido o número típico de funções, que estava desatualizado frente ao corpus real.
- **1.0.0** — Versão inicial. Deriva da `/novo-agente`, com três mudanças de fundo: ficha de parâmetros
  obrigatória antes da escrita; regras e formatos inlined, sem dependência externa nem cliente de
  referência; consentimento e comportamento de resolução viram perguntas sobre a plataforma de destino, em
  vez de premissas fixas.
