---
name: agv-novo-estatico
description: Use somente quando o usuário pedir explicitamente a criação de um novo agente virtual estático, de fluxo em menus numerados que ainda responde pergunta fora do menu, nomeando o cliente. Não usar para auditar, documentar ou editar agente que já existe.
argument-hint: "[cliente] [dados]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
metadata:
  version: "2.0.0"
---

# Criar Agente Virtual Estático (Fluxo por Menu)

Cria a configuração completa de um agente de pré-atendimento **estático** para o cliente `$ARGUMENTS`: o
atendimento é uma árvore de menus numerados, cada folha coleta apenas o que aquela demanda exige, e toda
trilha termina na função de transbordo.

## Esta skill é autocontida

Tudo que ela precisa está neste arquivo. **Não** consulte convenções externas, arquivos de instrução do
repositório, nem a configuração de outro cliente. Se houver convenções externas disponíveis e elas
**contradisserem** este arquivo, pare e diga qual é a divergência — não escolha em silêncio.

## O estático é o dinâmico mais uma camada de menu

A diferença entre este modelo e o conversacional é **apenas como a demanda é classificada**: aqui o usuário
escolhe um número em vez de descrever o que quer. Tudo depois disso é igual — mesma coleta, mesma função de
transbordo, mesmas variáveis, mesmo encerramento. O agente **não valida nada**: ele preenche as variáveis
corretamente e entrega; a validação acontece fora do fluxo dele.

Por isso: se algo aqui parecer específico do estático mas na verdade valer para os dois modelos, ele vale
para os dois. A camada estática é a árvore, os blocos de coleta, a tabela de trilhas, a navegação e o
tratamento de pergunta fora do menu.

## Ordem de execução

Passo 0 (ficha) → Regras → Passo 1 (origem e árvore) → Passo 2 (escrita) → Passo 3 (proibições) →
Passo 4 (verificação) → Passo 5 (relatório).

**Leia as Regras Invioláveis antes de escrever qualquer arquivo.** Cada uma vem com o motivo. Regra sem
motivo é regra que a próxima revisão "simplifica", reintroduzindo o defeito que ela existia para evitar.

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

Um agente sem esta ficha faz o que uma medição real mostrou: **pergunta bem e assume mesmo assim**. Produz
oito boas perguntas sobre filas, assimetria e schema — e na frase seguinte lista "o que eu assumiria por
conta própria, e é chute". Perguntar sem bloquear não impede a invenção.

**A ficha existe para bloquear.** Toda linha tem valor ou a marca `[PERGUNTAR]`, e **qualquer `[PERGUNTAR]`
obriga a perguntar antes de prosseguir**.

```
FICHA DE PARÂMETROS — <cliente>
  cliente.grafia_comercial .........
  cliente.dominio ..................
  agente.nome ......................
  agente.genero ....................
  agente.saudacao_literal ..........
  menu.arvore ......................
  menu.acao_por_opcao ..............
  menu.blocos_de_coleta ............
  menu.fila_por_trilha .............
  menu.assimetria_intencional ......
  transbordo.funcao ................
  transbordo.filas_enum ............
  transbordo.fila_fallback .........
  schema.parametros_required .......
  schema.tem_enum_ou_pattern .......
  plataforma.trata_consentimento ...
  plataforma.no_decisao_resolucao ..
  negocio.regra_1..N ...............
  default.tentativas ............... 2
  default.mascara_documento ........ ***.***.XXX-XX
  default.teto_lista ............... 5
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
| **Árvore de opções** | É o insumo que define o modelo. Sem ela não há fluxo estático a construir — pare e peça. |
| **Ação de cada opção** | O que vem depois de `>` são ações em sequência, não opções. Deduzir a ação inverte o fluxo. |
| **Fila real por trilha** | Rótulo em prosa ("equipe de agendamento", "financeiro") **não é** identificador. Transbordo com fila inválida quebra o roteamento em silêncio. |
| **Fila de fallback** | Destino de opção não reconhecida e de tentativas esgotadas. Sem ele, o agente fica preso no menu. |
| **Parâmetros `required` do schema** | Ver R31: campo com `enum`/`pattern`/`format` rejeita a sentinela e a chamada é descartada sem erro visível. |
| **Grafia comercial do cliente** | Aparece na primeira mensagem que todo usuário lê. Não inventar acento, espaço ou caixa. |
| **Nome e gênero do agente** | Gênero não se deduz do nome. A concordância do prompt inteiro depende disso. |
| **Texto literal da saudação** | É transcrito ao pé da letra. Se o cliente não tiver uma, proponha e peça aprovação — nunca assuma. |
| **Assimetria entre trilhas irmãs** | Ver R29. Confirmar antes de "consertar": pode ser regra de negócio real. |
| **Cada regra de negócio** | Obrigatoriedade de documento, quem pode ser atendido, o que exige humano. Nunca herdar de outro cliente. |

## Duas perguntas sobre a plataforma de destino

Separam regra de domínio de premissa da plataforma. São o que torna a skill portátil.

**`plataforma.trata_consentimento`** — a plataforma obtém o consentimento de dados **antes** de a conversa
chegar ao agente?

- **Sim** → não escrever bloco de consentimento; seria custo pago em todo turno duplicando controle que já
  existe a montante.
- **Não** → incluir o bloco, com frase curta antes do primeiro dado pessoal e encerramento cordial **sem
  transbordo** se o usuário recusar o consentimento em si — não há atendimento a entregar.

**`plataforma.no_decisao_resolucao`** — a plataforma tem um nó de decisão que lê a variável de resolução
**antes** do roteamento de fila?

- **Sim** → na trilha de informação resolvida a fila fica **em branco**; a plataforma desvia e encerra.
- **Não** → o ENUM de filas precisa de um valor de encerramento (ex: `Finalizacao_Atendimento`).

Os dois desenhos existem. Deduzir errado quebra em silêncio: o atendimento não é entregue.

## Com default — assumir e informar no relatório

| Dado | Default |
| --- | --- |
| Tentativas inválidas antes do fallback | 2 |
| Máscara de documento exibido no chat | `***.***.XXX-XX` |
| Teto de itens por lista | 5 |
| Formato de data | `DD/MM/AAAA` |
| Delimitador de variável | `__NOME_DA_VARIAVEL__` |

---

# Regras Invioláveis

Numeradas para referência **dentro desta skill**. Não cite estes números nos arquivos gerados — eles não
significam nada fora daqui.

## Variáveis

**R1 — Padrão de nome.** Toda variável de contexto usa `__IA_CAMPO__`, dois underscores de cada lado, caixa
alta, sem acento. Se o material de origem nomear fora do padrão, normalize e **registre a normalização**
numa nota no topo do dicionário.
*Motivo:* a plataforma interpola pelo token exato. Nome divergente não gera erro — chega vazio ao painel do
atendente.

**R2 — Quatro colunas, sempre.** O dicionário de variáveis tem exatamente estas colunas, nesta ordem:
`Variável | Descrição | Regra de Validação | Funções`. A coluna de validação carrega obrigatoriedade,
formato ou ENUM completo, e o fallback.
*Motivo:* é o único lugar onde a lógica de cada campo fica escrita uma vez. Descrição sem regra de validação
vira decisão do modelo em runtime.

**R3 — Toda variável declarada precisa de algo que a preencha.** Declarar e definir fallback não basta.
- *Variáveis de coleta* (nome, documento, data, convênio): basta o bloco de coleta em prosa.
- *Variáveis de controle* (fila, resolução, trilha, observações): **precisam ser nomeadas explicitamente pelo
  token**, porque nenhum bloco de coleta as alimenta. Ausência aqui é bug, não estilo.

**R4 — Variável de roteamento obrigatória.** Declare uma variável de fila e defina-a **antes** de chamar o
transbordo. Proibido acionar transbordo com fila em branco quando existe atendente de destino.
*Motivo:* transbordo sem fila cai em lugar nenhum, e o usuário fica esperando.

**R5 — Variável de observações livres.** Texto livre, curto e opcional, para sinais sem campo dedicado:
demanda fora do escopo, tentativas esgotadas, opção não reconhecida, convênio sem cobertura.
*Motivo:* sem ela esses sinais morrem na instrução e nunca chegam ao atendente.

**R6 — Três estados de ausência, nunca o mesmo texto.**
- `"Não Informado"` — o usuário **recusou explicitamente** um dado já perguntado.
- `"Não coletado"` — a trilha **não pergunta** esse dado.
- `"Não se aplica"` — o bloco da trilha em curso deliberadamente não pede.

*Motivo:* num fluxo estático a maioria das trilhas não coleta a maioria dos campos, então este é o caso
comum, não a exceção. O atendente age diferente em cada um.

**R7 — Variável de trilha.** Declare uma variável que registre qual opção o usuário percorreu (código +
rótulo). É o que permite medir o menu depois.

## Fluxo estático

**R8 — A árvore é o insumo obrigatório.** Formato típico:

```
1. Categoria >
    1.1. Ação > BlocoDeColeta > BlocoDeColeta > funcao_transbordo
    1.2. Ação > BlocoDeColeta > funcao_transbordo
2. Categoria > funcao_transbordo
```

Os **números são as opções de menu**. O que vem depois de `>` são **ações executadas em sequência**, não
opções. Categoria sem subitens é folha: escolha da opção → transbordo direto, sem coleta.
Sem árvore, pare e peça. Não há fluxo estático a construir.

**R9 — Não normalizar assimetria por conta própria.** Se uma trilha coleta diferente das irmãs (ex: `1.3`
pede pedido médico e `1.1`/`1.2` não), **pergunte se é intencional antes de "consertar"**.
*Motivo:* assimetria quase sempre é regra de negócio real. Uniformizar por estética apaga a regra e ninguém
percebe até o atendente receber o dado errado.

**R10 — Numeração de submenu reinicia em 1.** Ao exibir um submenu, mostre `1`, `2`, `3` com o título da
categoria acima — não `1.1`, `1.2`.
*Motivo:* o usuário digita o que vê. Exibir `1.1` faz metade digitar `1` e a outra metade `1.1`.

**R11 — Código interno de trilha nunca é exibido.** `1.1`, `2.3` não aparecem no chat, **mas são sempre
preenchidos** nos parâmetros. A regra de confidencialidade não pode impedir o preenchimento.

**R12 — Navegação e tentativas.** O número é interpretado no contexto do menu que está na tela. Aceite
também atalho por texto livre quando reconhecível. Após N tentativas inválidas (padrão 2), vá para a fila de
fallback registrando o motivo em observações.

**R13 — Pergunta fora do menu tem tratamento próprio.** O usuário pode perguntar qualquer coisa a qualquer
momento. Responda pela base, pergunte *"Posso ajudar em algo mais?"* e bifurque na variável de resolução:
resposta negativa encerra como resolvido; resposta positiva ou nova demanda retoma o menu.
*Motivo:* é o que torna o fluxo estático utilizável — sem isso o agente ignora a pergunta e repete o menu.

**R14 — Fallback de roteamento.** Defina o destino de opção não reconhecida, tentativas esgotadas e demanda
não identificada. Nunca deixe essa borda implícita — é a mais frequente em produção e a que ninguém testa.

## Encerramento — o ponto de falha nº 1

**R15 — Executar é uma ação; anunciar não realiza.** Toda trilha termina com a **execução** da função de
transbordo. **Proibido escrever "vou te transferir" / "estou te encaminhando" sem executar a função na mesma
resposta.**

A formulação que funciona em produção, e que deve aparecer no prompt gerado, é esta — use-a literalmente:

> Toda trilha do menu termina obrigatoriamente com a execução da função de transbordo. **Executar a função é
> uma ação — anunciar a transferência em texto não a realiza.**

**R16 — O transbordo é o handoff único.** **Toda** trilha executa a função, inclusive a de informação
resolvida. A variável de resolução decide o que a plataforma faz **depois** da chamada — ela não decide se a
função roda.
*Motivo:* "dúvida sanada → encerrar sem acionar a função" deixa a automação de encerramento e as tags de
relatório sem gatilho: o atendimento nunca é entregue.
*Única exceção:* recusa de consentimento antes de qualquer coleta.

**R17 — Falta de dado não bloqueia a execução.** O que a trilha não coleta vai como sentinela (R6). Fila
indefinida nunca justifica não transferir — o fallback resolve.

**R18 — Trilha com coleta exibe o resumo e executa na mesma resposta.** Trilha sem coleta executa
imediatamente após a escolha da opção.

**R19 — Três armadilhas de redação que produzem exatamente este defeito.** Evitar no prompt **e** nos
manuais:

1. **Resumo pedindo confirmação.** *"Exibir os dados para confirmação"* faz o agente parar e esperar um
   segundo "sim" que nunca é tratado. Diga explicitamente que o resumo é informativo, não é pedido de
   autorização.
2. **Descrever a fala em vez do ato.** *"Informe que o atendimento está sendo encaminhado"* ensina o agente a
   emitir a frase e encerrar o turno. Toda instrução tem que ser sobre executar a função.
3. **Exemplo que contradiz a regra.** Um diálogo com *"Confirma para mim:"* é few-shot e **vence a regra
   escrita acima dele**. Revise os exemplos dos manuais contra as regras.

**R20 — Cada proibição vem com a saída correspondente.** Cercar o transbordo só de proibições (*"proibido
transferir sem X"*, *"proibido sem Y"*) faz o modelo ler a transferência como ação de risco e hesitar.

## Funções e schema

**R21 — Sentinela precisa ser compatível com o JSON Schema.** Se o schema registrado na API declara o
parâmetro com `enum`, `pattern` ou `format`, a sentinela `"Não coletado"` **viola o schema e a chamada é
descartada em silêncio** — o sintoma é *"o agente chega na função e não faz nada"*.
Só os campos realmente universais da árvore podem ser `required`; os condicionais precisam ser string livre,
sem restrição de formato. **Registre isso no manual da função de transbordo.**

**R22 — Distinguir argumento de função e variável de contexto.** Instruir o agente a preencher um argumento
que não existe no schema é outra causa de chamada descartada. Se não estiver claro, **pergunte** — não
deduza.

**R23 — Descrição da função ≤ 950 caracteres.** É o texto registrado na API, pago em 100% dos turnos. Sem
saudação, sem "esta função serve para". Duas coisas: o que ela faz e em qual intenção acioná-la.
*Motivo:* função sem fronteira declarada é chamada no lugar da vizinha.

**R24 — Nunca chamar função com parâmetro deduzido.** Faltando dado obrigatório, o agente **retém a chamada**
e pergunta. Nunca supor documento, convênio ou qualquer parâmetro não informado.
*Motivo:* parâmetro inventado retorna dado de outra pessoa ou vazio, e os dois viram resposta errada com
cara de certa.

**R25 — Três seções no manual, exatamente.** `## 1. Descrição da Função` · `## 2. Diretrizes de Prompt` ·
`## 3. Exemplos Práticos de Diálogos`. Nunca uma quarta, e nunca seção de especificação técnica.

**R26 — §2 e §3 do manual não chegam ao modelo.** São documentação. Tudo que o agente precisa em runtime
tem que estar no prompt principal.
*Motivo:* regra deixada só na §2 é lacuna funcional silenciosa — parece configurada e não está.

## Dados, conduta e plataforma

**R27 — Regra geral de dados, declarada uma vez.** No topo das diretrizes: *todo dado factual vem da função
no momento da chamada; nunca memorizar, supor ou reproduzir no prompt*. Cada regra seguinte só aponta qual
função consultar.
*Motivo:* repetir "não memorizar" em cada item multiplica o custo sempre-ativo sem adicionar instrução. E
endereço ou horário chumbado no prompt fica desatualizado sem ninguém perceber.

**R27a — Higiene do JSON de base.** Chaves com nome semântico claro, nunca nome de coluna de sistema legado
do cliente. Sem `null`, sem chave vazia, sem metadado que não serve ao atendimento. Números e booleanos
tipados, não encapsulados em string. Indentado e legível — **não minificar**, a plataforma já minifica no
envio e estes arquivos são revisados por humanos.

**R27b — Responder só o subconjunto perguntado.** Ao processar o retorno de uma função que carrega uma base
grande, responda **apenas** com o que foi perguntado. Nunca cole a base inteira na conversa.
*Motivo:* o retorno persiste no histórico e é reenviado a cada turno seguinte. E base inteira na tela faz o
modelo misturar itens que ninguém perguntou.

**R27c — Tolerância fuzzy só dentro da mesma entidade.** Quando uma função valida um dado informado pelo
usuário contra uma base, a tolerância cobre variações da **mesma** entidade: caixa, acento, abreviação
clara, nome popular. Nunca aproximar duas entidades diferentes por soarem parecidas. Em dúvida, **falhar
fechado** — tratar como não localizado e perguntar.
*Motivo:* aproximar dois itens diferentes agenda a pessoa para a coisa errada, e ninguém percebe até ela
chegar lá.

**R28 — Sentinela explícita, nunca valor ambíguo.** Lista vazia `[]` é lida como "**nenhum**", não como
"todos". Quando o significado for "todos", use `["Todos"]` e documente a leitura na §2 do manual.
*Motivo:* o caso clássico — `[]` em "convênios atendidos" faz o agente negar cobertura que existe.

**R29 — Um assunto, um arquivo dono.** O mesmo fato nunca aparece em dois JSONs, nem duplicado verbatim
entre o prompt e um manual.
*Motivo:* o custo não é token — é deriva. A próxima correção é aplicada num lado só e as duas versões se
contradizem em silêncio.

**R30 — Mascarar documento exibido de volta** (`***.***.XXX-XX`).

**R31 — Limite de atuação em domínio regulado.** Saúde, jurídico ou financeiro exigem regra explícita de
"Sem aconselhamento [domínio]" nas regras de segurança, **mesmo que o cliente não peça**. Uma clínica nunca
indica exame, diagnóstico, preparo ou tratamento a partir de sintoma relatado.
*Motivo:* a ausência disso no material do cliente não significa que é dispensável — significa que ninguém
pensou nisso.

**R32 — Agrupar em subtítulos a partir de 5 itens.** Seções de conduta ou segurança com 5+ itens ganham
subtítulos `###` temáticos.

**R33 — Negrito com um único asterisco.** Toda instrução de destaque nas mensagens ao usuário especifica
`*texto*`, nunca `**texto**`.
*Motivo:* o WhatsApp só interpreta um asterisco; `**` aparece literal na tela.
*Exceção:* o card do atendente é markdown de painel, não mensagem — ali `**` é correto.

**R34 — Proibido citar caminho ou nome de arquivo no conteúdo do prompt.** O prompt e as descrições de função
nunca citam pasta, arquivo do projeto ou número de seção. Referências se resolvem inline ou pelo nome do
campo da plataforma.
*Motivo:* o usuário e o modelo não têm "arquivos" como referência, e citar estrutura interna vaza processo
interno numa conversa com o público.

**R35 — Consciência de custo.** O prompt principal mais as descrições de função são pagos em **todos** os
turnos. Nasce enxuto: sem dado que a função retorna, sem prosa de justificativa, sem regra escrita duas
vezes.

**R36 — Quatro campos, quatro seções.** A tela da plataforma tem quatro campos separados — Perfil,
Diretrizes de Atendimento, Regras de Conduta, Regras de Segurança — e o prompt é colado **campo a campo**.
A numeração `## 1.`–`## 4.` é fixa e nunca ganha uma quinta seção.

---

# Passo 1 — Ler o material do cliente e interpretar a árvore

**O material do cliente chega por dois caminhos, e os dois valem:** arquivos na pasta `origem/` do cliente,
e/ou texto colado no próprio comando que invocou esta skill. Nenhum dos dois é obrigatório e nenhum tem
precedência — o que existir é fonte primária. *Motivo: exigir `origem/` faria a skill marcar `[PERGUNTAR]` em
linha cujo dado está à vista no comando.*

**Se o material vier colado no comando**, extraia dele só o nome do cliente para nomear a pasta, e salve o
restante verbatim em `origem/especificacao-agente-[NomeCliente].md`, criando a pasta `origem/` se não existir.
A partir daí trate esse arquivo como fonte primária.

Leia **todos** os arquivos que existirem em `$ARGUMENTS/origem/`. Extraia: domínio · serviços · público-alvo ·
terminologia · dados de identificação coletados · **a árvore de opções** · **os nomes reais das filas**.

Compare a lista de serviços com as opções do menu. **Serviço que aparece na lista e não no menu é pergunta,
não decisão sua** — pode ser omissão do cliente ou escopo deliberado.

Não vindo o dado por nenhum dos dois caminhos, a linha vira `[PERGUNTAR]` — mas só então.

---

# Passo 2 — Escrever. Os formatos são estes.

## 2.1 Árvore de arquivos

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

## 2.2 `config/agente.md`

Quatro seções `##` separadas por `---`. A camada estática entra em `## 2`, entre a regra geral de dados e o
encerramento. Emoji no `###` é a convenção visual.

```markdown
# 🤖 Configurações do Agente Virtual

Este documento consolida as diretrizes de personalidade, regras operacionais, de conduta e segurança para
[o/a] **[Agente]**, assistente virtual oficial [do/da] **[Cliente]**.

---

## 1. Perfil do Agente Virtual

### 📋 Descrição do Papel
### ✨ Características (Personalidade e Tom de Voz)
### 👥 Público-Alvo

---

## 2. Diretrizes de Atendimento

### 📌 Regra geral de dados
### 🧭 Fluxo Estático — Menu Principal
### 🧭 Submenus
### 🧱 Blocos de Coleta
### 🗺️ Tabela de Trilhas (opção → coleta → fila)
### ✅ Encerramento Obrigatório da Trilha (ação, não mensagem)
### 🔁 Regra de Navegação e Tentativas
### ❓ Perguntas Fora do Menu

---

## 3. Regras de Conduta

### ✍️ Linguagem e Formato
### 💬 Tom e Acolhimento

---

## 4. Regras de Segurança

### 🔒 Consentimento e Proteção de Dados
### 📋 Coleta Condicionada à Trilha
### 🔀 Roteamento e Fechamento
### 🚫 Limites de Atuação
### 🌐 Fonte Única de Verdade
### 🤐 Transparência e Confidencialidade
```

Blocos condicionais, conforme a ficha: `### 🔒 Consentimento` só se a plataforma **não** tratar upstream;
blocos de borda próprios do domínio (ex: convênio sem cobertura → oferecer particular ou atendente).

## 2.3 Menu, blocos e tabela de trilhas

**Menu principal** — uma opção por linha, numeração exibida a partir de 1:

```markdown
Escolha uma opção digitando o número:

*1* — [Categoria]
*2* — [Categoria]
*3* — [Folha, vai direto ao transbordo]
```

**Submenu** — título da categoria acima, numeração **reiniciando em 1** (R10).

**Blocos de coleta** — nomeados, definidos uma vez e reutilizados pelas trilhas:

```markdown
**Bloco DadosPessoais** — nome completo · telefone · data de nascimento
**Bloco Convenio** — nome do convênio, ou "Particular"
```

**Tabela de Trilhas** — uma linha por folha da árvore, sem exceção:

```markdown
| Opção | Coleta | Fila |
| --- | --- | --- |
| `1.1` [rótulo] | DadosPessoais + Convenio | `[fila real]` |
| `3` [rótulo] | — | `[fila real]` |
| Fallback — opção não reconhecida | — | `[fila de fallback]` |
```

## 2.4 `config/variaveis.md`

Duas notas em blockquote, depois a tabela de **exatamente quatro colunas**. Nesta ordem.

```markdown
# Variáveis de Contexto — [Agente] ([Cliente])

> **Normalização de nomenclatura.** [De onde vieram os nomes e o que foi renomeado — ou a declaração de que
> o material de origem não definia nomes próprios.]

> **Nota sobre valores de ausência.** Três situações distintas deixam uma variável sem dado real, e **nunca**
> podem usar o mesmo texto:
> - `"Não Informado"` — o usuário **recusou explicitamente** um dado já perguntado.
> - `"Não coletado"` — a trilha **não pergunta** esse dado.
> - `"Não se aplica"` — o bloco da trilha em curso deliberadamente não pede.
>
> Nunca inventar valor para viabilizar a chamada da função.

| Variável | Descrição | Regra de Validação | Funções |
| --- | --- | --- | --- |
| `__IA_CAMPO__` | [o que é] | Obrigatório/Opcional. Formato ou ENUM completo. Fallback. | `nome_funcao` → parâmetro `nome_param` |
```

**Núcleo canônico de controle** — presente em todo agente estático:

| Variável | Papel |
| --- | --- |
| `__IA_TRILHA__` | Código + rótulo da opção percorrida |
| `__IA_ATENDIMENTO_FILA__` | Fila humana de destino |
| `__IA_ATENDIMENTO_RESOLVIDO__` | Único parâmetro obrigatório em toda chamada de transbordo |
| `__IA_OBSERVACOES__` | Texto livre para sinais sem campo dedicado |

No rodapé, uma nota de aplicação: variáveis a cadastrar na plataforma, comportamento do nó de decisão de
resolução, e o que muda se ele não existir.

## 2.5 `config/clienteinfo.json`

Array com um objeto. `nome` é a variável de destaque do card, em negrito duplo — aqui `**` é correto (R33).
Cada bloco tem `titulo` e um `informacoes` com **dois arrays de mesmo tamanho**: rótulos primeiro, tokens
depois, pareados por índice. Tamanhos diferentes desalinham o card em silêncio.

```json
[
    {
        "nome": "**__IA_TRILHA__**",
        "informacoes": [
            {
                "titulo": "Informações do Paciente",
                "informacoes": [
                    ["Nome Completo", "Telefone", "Data de Nascimento"],
                    ["__IA_PACIENTE_NOME__", "__IA_PACIENTE_TELEFONE__", "__IA_PACIENTE_DATA_NASCIMENTO__"]
                ]
            },
            {
                "titulo": "Resumo do Atendimento",
                "informacoes": [
                    ["Trilha", "Resolvido", "Fila", "Observações"],
                    ["__IA_TRILHA__", "__IA_ATENDIMENTO_RESOLVIDO__", "__IA_ATENDIMENTO_FILA__", "__IA_OBSERVACOES__"]
                ]
            }
        ]
    }
]
```

## 2.6 Manual da função de transbordo

Três seções (R25). A §2 deste manual é a mais longa: carrega a tabela de filas, a regra de resolução, a lista
completa de parâmetros e — obrigatoriamente — **a nota de compatibilidade de sentinela com o schema (R21)**.

````markdown
## 1. Descrição da Função (OpenAI Function Calling)

[Prosa corrida, ≤ 950 caracteres. O que a função faz e em qual momento acioná-la.]

---

## 2. Diretrizes de Prompt (System Instructions)

```markdown
================================================================
FUNÇÃO: nome_da_funcao
================================================================
# QUANDO EXECUTAR
- Ao final de toda trilha, sem exceção. Executar é ação, não mensagem.

# PARÂMETROS
- [param]: [origem, obrigatoriedade, sentinela aceita]

# COMPATIBILIDADE DE SCHEMA
- Campos condicionais são string livre, sem enum/pattern/format — a sentinela
  "Não coletado" precisa ser um valor válido, senão a chamada é descartada em silêncio.
```

---

## 3. Exemplos Práticos de Diálogos

### Cenário 1: [trilha com coleta]

> **Usuário:** *"[escolha]"*
>
> **Agente:** *"[resumo informativo]"*  → e executa a função na mesma resposta
>
> ❌ **Errado:** pedir confirmação depois do resumo e esperar um novo "sim".
````

## 2.7 `ferramentas/dados/*.json`

Objeto de topo por assunto, indentado, **nunca minificado**. Chaves semânticas, sem `null` nem chave vazia,
números e booleanos tipados. Sentinela explícita onde o sentido é "todos" (R28).

---

# Passo 3 — Proibido

- **Herdar regra de negócio de outro cliente.** Formato se reaproveita; regra de negócio, nunca.
- **Preencher linha da ficha** com palpite ou valor de outro cliente.
- **Normalizar assimetria** entre trilhas irmãs sem confirmar (R9).
- **Usar rótulo em prosa como nome de fila** ("equipe de agendamento" não é identificador).
- **Escrever a fala de transferência** sem a execução da função (R15, R19).
- **Pedir confirmação depois do resumo** (R19.1).
- **Exibir código interno de trilha** ao usuário (R11).
- **Citar caminho de pasta ou arquivo** no conteúdo do prompt (R34).
- **Criar uma quinta seção `##`** no prompt (R36) ou uma quarta no manual (R25).
- **Deduzir o gênero do agente** pelo nome.

---

# Passo 4 — Verificação mecânica

```
1.  Toda folha da árvore virou linha da Tabela de Trilhas, com fila definida
2.  Nenhuma trilha coleta dado além do que a tabela declara
3.  Fila de fallback definida para opção não reconhecida e tentativas esgotadas
4.  Seção de encerramento presente, com a formulação "ação, não mensagem"
5.  Nenhum exemplo de diálogo pede confirmação depois do resumo
6.  Nenhuma instrução descreve a fala de transferência sem a execução
7.  Sentinelas documentadas e compatíveis com o JSON Schema (R21)
8.  Variável de resolução com regra de preenchimento em 100% dos caminhos
9.  Toda variável declarada tem algo que a preencha; as de controle pelo token
10. Todo token do card tem variável declarada, e os arrays têm o mesmo tamanho
11. O card é JSON válido
12. Numeração de submenu reinicia em 1
13. Código interno de trilha nunca exibido, sempre preenchido
14. Nenhum `**` como instrução de destaque no conteúdo de prompt
15. §1 de cada função ≤ 950 caracteres; todo manual com exatamente 3 seções
16. Nenhum caminho, nome de arquivo ou `§N` no conteúdo de prompt
17. O prompt tem exatamente 4 seções `##`
18. Nenhum nome próprio de outro cliente
```

---

# Passo 5 — Relatório final

1. **Tree criada**, com contagem de trilhas, funções e variáveis.
2. **A Tabela de Trilhas completa**, para conferência do cliente.
3. **A ficha reexibida**, com a origem de cada valor: informado, lido de `origem/`, ou default.
4. **Pendências, separadas por quem resolve:**
   - *Bloqueiam a homologação:* dado de cliente que faltou, e o que não pode ser validado sem ele.
   - *Ação de plataforma:* variáveis a cadastrar, função a registrar, filas a criar com a grafia exata,
     campos do schema a ajustar.
   - *Dúvida aberta que não bloqueia.*
5. **Pontos importantes** — as decisões que alguém vai questionar depois: assimetrias mantidas e por quê,
   serviços que ficaram fora do menu, se o consentimento entrou, e o comportamento na trilha resolvida.

**Nunca fechar dizendo "pronto" com pendência de dado de cliente aberta.** Diga o que está pronto para colar,
o que está pronto como documento interno, e o que não sobe até a pendência fechar.

---

## Changelog

- **2.0.0** — Reescrita autocontida. Antes, 14 regras eram citadas por número de um documento externo; numa
  medição com esse documento fora de alcance, **6 delas viraram buraco** — a taxonomia de trilhas e os
  limites de domínio foram pulados, o fallback de roteamento ficou sem destino, e o formato de quatro colunas
  do dicionário de variáveis teve de ser **adivinhado**. Agora todas estão inlinadas com numeração própria e
  o motivo junto. Acrescentada a ficha de parâmetros do Passo 0: a versão anterior produzia boas perguntas e
  assumia mesmo assim, listando na frase seguinte "o que eu assumiria por conta própria, e é chute".
  Acrescentados os esqueletos literais de cada arquivo gerado.
- **1.0.0** — Versão inicial.
