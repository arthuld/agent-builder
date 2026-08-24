---
name: agv-novo-dinamico
description: Use somente quando o usuário pedir explicitamente a criação de um novo agente virtual de interação livre (dinâmico), nomeando o cliente. Não usar para auditar, documentar ou editar agente que já existe.
argument-hint: "[cliente] [dados]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
metadata:
  version: "1.0.0"
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
  default.mascara_cpf ............. ***.***.XXX-XX
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
| Máscara de documento exibido no chat | `***.***.XXX-XX` (últimos 5 dígitos visíveis) |
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

**R2 — Quatro colunas, sempre.** O dicionário de variáveis tem exatamente: `Variável | Descrição | Regra de
Validação | Funções`. A coluna de validação carrega obrigatoriedade, formato ou ENUM completo, e o fallback.
*Motivo:* é o único lugar onde a lógica de cada campo fica escrita uma vez. Descrição sem regra de validação
vira decisão do modelo em runtime.

**R3 — Toda variável declarada precisa de algo que a preencha.** Declarar e definir fallback não basta.
Duas categorias, com verificações diferentes:
- *Variáveis de coleta* (nome, documento, data, item de interesse): basta o passo de coleta em prosa. Não
  precisam do token no prompt — exigi-lo só engorda o custo sempre-ativo.
- *Variáveis de controle* (fila, resolução, classificação da demanda, observações): **precisam ser nomeadas
  explicitamente pelo token**, porque nenhum passo de coleta as alimenta. Só instrução direta faz o modelo
  preenchê-las. Ausência aqui é bug, não estilo.

**R4 — Variável de roteamento obrigatória.** Todo agente que aciona transbordo declara uma variável de fila
e a define **antes** de chamar a função. Proibido acionar transbordo com fila em branco quando existe
atendente de destino.
*Motivo:* transbordo sem fila cai em lugar nenhum, e o usuário fica esperando.

**R5 — Variável de observações livres.** Declare uma variável de texto livre, curta e opcional, para os
sinais que não cabem em nenhum campo dedicado: demanda fora do escopo, item solicitado que o cliente não
oferece, falha de triagem, demanda não identificada.
*Motivo:* sem ela, esses sinais morrem na instrução e nunca chegam ao atendente humano.

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
- **Repasse simples** — demanda fora do escopo que exige ação humana: **coleta mínima** (só o nome + a
  demanda em observações) e transbordo, **sem** triagem completa.

*Motivo:* não coletar dado desnecessário para o que só será repassado, e não acionar humano para o que o
agente resolve sozinho.

**R8 — Fallback de classificação.** Se a variável de entrada que traz a demanda chegar vazia ou com valor
fora do ENUM esperado, defina o que fazer — nunca deixe essa borda implícita. Padrão: perguntar o mínimo
(normalmente só o nome), registrar em observações e transferir para a fila geral.
*Motivo:* é a borda mais frequente em produção e a que ninguém testa.

**R9 — O transbordo é o handoff único.** **Toda** trilha executa a função de transbordo, inclusive a de
informação resolvida. A variável de resolução decide o que a plataforma faz **depois** da chamada — ela não
decide se a função roda.
*Motivo:* escrever "dúvida sanada → encerrar sem acionar a função" deixa a automação de encerramento e as
tags de relatório sem gatilho: o atendimento nunca é entregue, e o número nunca fecha.
*Única exceção:* recusa de consentimento antes de qualquer coleta — não há atendimento a entregar.
*Consequência no schema:* se a trilha de informação não coleta nada, **só a variável de resolução pode ser
`required`** — nem o nome. Nome obrigatório faz toda dúvida resolvida falhar em silêncio.

**R10 — Tentativas antes de desistir.** Defina o número de tentativas (padrão 2) após o qual o agente para
de insistir num dado, aciona o transbordo e marca os campos não perguntados como `"Não coletado"`.
*Motivo:* sem limite, o agente entra em laço com quem não vai responder.

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

**R13 — Responder só o subconjunto perguntado.** Ao processar o retorno de uma função que carrega uma base
grande, responda **apenas** com o que foi perguntado. Nunca cole a base inteira na conversa.
*Motivo:* o retorno persiste no histórico e é reenviado a cada turno seguinte. E base inteira na tela faz o
modelo misturar itens que ninguém perguntou.

**R14 — Tolerância fuzzy só dentro da mesma entidade.** Quando uma função valida um dado informado pelo
usuário contra uma base, a tolerância cobre variações da **mesma** entidade: caixa, acento, abreviação
clara, nome popular. Nunca aproximar duas entidades diferentes por soarem parecidas. Em dúvida, **falhar
fechado** — tratar como não localizado e perguntar.
*Motivo:* aproximar dois itens diferentes agenda a pessoa para a coisa errada, e ninguém percebe até ela
chegar lá.

**R15 — Três seções no manual, exatamente.** Todo manual de função tem `## 1. Descrição da Função` ·
`## 2. Diretrizes de Prompt` · `## 3. Exemplos Práticos de Diálogos`. Nunca uma quarta, e nunca uma seção de
especificação técnica (JSON Schema) — isso é artefato de documentação, não de configuração.

**R16 — §2 e §3 do manual não chegam ao modelo.** São documentação e área de estágio. Tudo que o agente
precisa saber em runtime tem que estar no prompt principal.
*Motivo:* regra deixada só na §2 é lacuna funcional silenciosa — parece configurada e não está.

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

**R21 — Mascarar documento exibido de volta.** Documentos de identificação ecoados no chat vão mascarados
(`***.***.XXX-XX`).

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

**R26 — Consciência de custo.** O bloco sempre-ativo — o prompt principal mais as descrições de função — é
pago em **todos** os turnos. Nasce enxuto: sem dado que a função retorna, sem prosa de justificativa, sem
regra escrita duas vezes. Quando precisar cortar, corte **redundância e verbosidade**, nunca regra: o
racional vai para o relatório, onde não é pago por turno.

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

### 📌 Regra Geral de Dados
### 🚦 Classificação da Demanda
### 🅰️ Trilha A — [Ação]
### 🅱️ Trilha B — [Informação]
### 🅲 Trilha C — Repasse Simples
### 🔢 Regra de Tentativas e Transbordo

---

## 3. Regras de Conduta

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

- **Regra Geral de Dados** — a declaração única de R20. Primeira coisa das diretrizes.
- **Classificação da Demanda** — como o agente decide a trilha, o ENUM de motivos, e o fallback de R8.
  Costuma ser uma tabela `Demanda | Motivo | Trilha | Fila`.
- **Trilha A** — a coleta completa, passo a passo, com o que perguntar e em que ordem, fechando com a fila e
  a chamada do transbordo.
- **Trilha B** — quais funções respondem o quê, a pergunta de fechamento ("posso ajudar em mais alguma
  coisa?") e o encerramento com resolução positiva. **Ainda executa o transbordo** (R9).
- **Trilha C** — coleta mínima, registro da demanda em observações, fila e transbordo. Uma linha explícita
  proibindo a coleta completa aqui.
- **Regra de Tentativas e Transbordo** — o limite de R10 e o que fica `"Não coletado"`.
- **Linguagem e Formato** — tamanho de mensagem, listas numeradas com teto, emojis, e a regra do asterisco
  único (R24).
- **Sem Aconselhamento [Domínio]** — obrigatório em domínio regulado (R22).

**Blocos condicionais, conforme a ficha:**

- `### 🔐 Consentimento` — **só** se `plataforma.trata_consentimento = Não`. Frase curta antes do primeiro
  dado pessoal, aguardar resposta, e encerramento cordial sem transbordo se o usuário recusar.
- `### ✅ Confirmação dos Dados` — se o cliente quiser o resumo lido de volta antes da transferência.
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
| `__IA_CAMPO__` | [o que é] | Obrigatório/Opcional. Formato ou ENUM completo. Fallback. | `nome_funcao` → parâmetro `nome_param` |
```

**Núcleo canônico de controle.** Estas quatro existem em todo agente; as de coleta se acrescentam a elas:

| Variável | Papel |
| --- | --- |
| `__IA_MOTIVO_CONTATO__` | Classifica a demanda logo após a saudação; determina trilha e fila |
| `__IA_ATENDIMENTO_FILA__` | Fila humana de destino; obrigatória sempre que a resolução for negativa |
| `__IA_ATENDIMENTO_RESOLVIDO__` | Único parâmetro obrigatório em toda chamada de transbordo |
| `__IA_OBSERVACOES__` | Texto livre para sinais sem variável dedicada |

A coluna de validação é onde mora a lógica: ENUM completo, condição de obrigatoriedade por trilha, regra de
máscara e fallback. Descrição sem validação é campo sem regra.

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
                    ["Resolvido pel[o/a] [Agente]", "Fila", "Observações"],
                    ["__IA_ATENDIMENTO_RESOLVIDO__", "__IA_ATENDIMENTO_FILA__", "__IA_OBSERVACOES__"]
                ]
            }
        ]
    }
]
```

Blocos típicos: "Informações do [Usuário]" e "Resumo do Atendimento". Um terceiro só quando o fluxo
justificar. Indentação de 4 espaços. Adapte o rótulo do usuário ao domínio (paciente, cliente, segurado).

## 2.5 `ferramentas/manuais/*.md`

Exatamente três seções, separadas por `---`.

````markdown
## 1. Descrição da Função (OpenAI Function Calling)

[Prosa corrida, ≤ 950 caracteres. Sem saudação, sem "esta função serve para". Duas coisas: o que retorna e
em qual intenção do usuário acioná-la. Fechar delimitando o que ela NÃO decide, quando houver função
vizinha que decida.]

---

## 2. Diretrizes de Prompt (System Instructions)

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

---

## 3. Exemplos Práticos de Diálogos

### Cenário 1: [nome do caso]

> **Usuário:** *"[fala]"*
>
> **Agente:** *"[resposta]"*

### Cenário 2: [caso com o erro clássico]

> **Usuário:** *"[fala]"*
>
> **Agente:** *"[resposta correta]"*
>
> ❌ **Errado:** [o que não fazer, e o defeito que produz]
````

**Detalhes que não são óbvios:**

- **§2 e §3 não chegam ao modelo** (R16). Se uma regra precisa valer em runtime, ela tem que estar no prompt
  principal também.
- Nos diálogos da §3, o negrito das falas do agente usa **um** asterisco — os exemplos são o que a equipe
  copia para testar.
- Pelo menos um cenário com `❌ **Errado:**`. O exemplo negativo é o que impede a regra de ser "simplificada"
  na revisão seguinte.
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

Um cliente típico tem de 2 a 4 funções `get_*`. Mais que isso costuma ser fragmentação de um mesmo assunto,
o que viola R19.

---

# Passo 3 — Proibido

- **Herdar regra de negócio de outro cliente.** Formato se reaproveita; regra de negócio, nunca.
- **Preencher linha da ficha** com palpite, com default não declarado, ou com valor de outro cliente.
- **Inventar** nome de convênio, serviço, profissional, unidade, fila ou URL.
- **Citar caminho de pasta, nome de arquivo ou número de seção** dentro do que vira prompt (R25).
- **Hardcodar no prompt** dado que uma função retorna (R20, R26).
- **Criar uma quinta seção `##`** no prompt principal (R27), ou uma quarta seção no manual (R15).
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
7.  Todo manual com exatamente 3 seções, numeradas 1 → 2 → 3
8.  Nenhum caminho, nome de arquivo ou `§N` no conteúdo de prompt
9.  Nenhum `[]` ou `null` nos JSONs de base
10. Nenhuma tabela ou regra duplicada verbatim entre o prompt e um manual
11. O prompt principal tem exatamente 4 seções `##`
12. Nenhum nome próprio de outro cliente em lugar nenhum
13. Toda função citada no prompt tem manual, e todo manual é citado
14. Toda trilha termina acionando a função de transbordo (R9)
```

Meça o **bloco sempre-ativo** — as 4 seções do prompt mais a descrição de cada função. É o que a plataforma
reenvia a cada turno. Reporte o número medido, não estimado.

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

**Nunca fechar dizendo "pronto" com pendência de dado de cliente aberta.** Diga o que está pronto para colar
na plataforma, o que está pronto como documento interno, e o que não sobe até a pendência fechar.

---

## Changelog

- **1.0.0** — Versão inicial. Deriva da `/novo-agente`, com três mudanças de fundo: ficha de parâmetros
  obrigatória antes da escrita; regras e formatos inlined, sem dependência externa nem cliente de
  referência; consentimento e comportamento de resolução viram perguntas sobre a plataforma de destino, em
  vez de premissas fixas.
