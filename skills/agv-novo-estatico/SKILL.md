---
name: agv-novo-estatico
description: Use somente quando o usuário pedir explicitamente a criação de um novo agente virtual estático, de fluxo em menus numerados que ainda responde pergunta fora do menu, nomeando o cliente. Não usar para auditar, documentar ou editar agente que já existe.
argument-hint: "[cliente] [dados]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
metadata:
  version: "3.0.0"
---

# Criar Agente Virtual Estático (Fluxo por Menu)

Cria a configuração completa de um agente de pré-atendimento **estático** para o cliente `$ARGUMENTS`: o
atendimento é uma árvore de menus numerados, cada folha coleta apenas o que aquela demanda exige, e toda
trilha termina na função de transbordo.

## Esta skill é autocontida

Tudo que ela precisa está neste arquivo. **Não** consulte convenções externas, arquivos de instrução do
repositório, nem a configuração de outro cliente. Se houver convenções externas disponíveis e elas
**contradisserem** este arquivo, pare e diga qual é a divergência — não escolha em silêncio.

## O modelo alvo

O agente gerado roda em **`gpt-5.4-nano`**, com `reasoning_effort` em `none` — o default da família, que a
plataforma não expõe. Quatro consequências valem para tudo que vem abaixo:

- **Saída fechada sempre que couber.** Enum no schema (R21), template literal (R15), tabela de decisão.
  Modelo pequeno erra menos escolhendo de uma lista do que redigindo livremente.
- **Toda borda escrita.** Modelo pequeno não infere o passo que falta — improvisa. Borda não escrita é
  comportamento inventado.
- **Prompt um pouco mais longo e mais explícito** que o de um modelo maior. Feche as bordas primeiro, meça
  depois, corte por último.
- **Markdown para estruturar, nada de XML.** Para o nano a doc **não prescreve formato de prompt
  nenhum** — o que ela exige é *ter* estrutura (`Generic instructions without structure` está na
  lista do que evitar). Markdown entrega isso pelo menor custo: medido nos agentes existentes, trocar
  os headers por tags XML custa **+217 tokens por turno por agente**, +5% do campo, sem ganho
  documentado. E o serviço que o XML prestaria — delimitar onde um bloco começa e termina — a
  plataforma já presta, porque os 4 campos são entradas separadas. Os blocos XML dos exemplos da
  documentação são orquestração multi-etapa do modelo frontier: o oposto do que o nano recebeu como
  orientação. Se um campo só fica legível com scaffolding pesado, o problema não é o formato — é que o
  campo está largo demais para o nano. Estreitar, não re-sintaxar.

O fluxo em menu joga a favor aqui: entrada de dígito e trilha em tabela são mais fáceis para um modelo
pequeno do que classificação semântica aberta. **O que não joga a favor é o estado** — saber em qual menu
está, contar tentativas, e distinguir escolha de opção de pergunta fora do menu a cada turno. Onde houver
escolha entre resolver por estado ou por tabela, escolha a tabela.

Medição de token: `tiktoken`, encoding `o200k_base`.

**Se o modelo mudar, revise esta seção antes de tudo.**

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

Sempre-ativo é pago em **todos** os turnos, inclusive naqueles em que nenhuma função é chamada. **O manual
inteiro é sempre-ativo**: não existe "deixar a regra na §2 para não pagar". O arquivo de dados, não —
arquivo grande é barato, função a mais é cara.

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
  fluxo.confirma_antes_executar .... Sim
  fluxo.meta_interacoes ............ 5 a 7 mensagens do agente
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
| **Parâmetros `required` do schema** | Ver R21: campo com `enum`/`pattern`/`format` rejeita a sentinela e a chamada é descartada sem erro visível. A saída é declarar a sentinela no `enum`, não afrouxar o campo. |
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
| Confirmação dos dados antes de executar o transbordo | Sim |
| Meta de interações até finalizar ou transferir | 5 a 7 mensagens do agente |
| Modalidade fora de convênio (particular) | Disponível — assumir que sim e confirmar no relatório |
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
**Única exceção:** a coluna **Variável** do dicionário traz o nome **sem** os `__` (`IA_CAMPO`), porque é ali que a plataforma registra o campo. Em todo o resto — prompt, card, referências cruzadas — o token vai com os underscores.

**R2 — Quatro colunas, sempre.** O dicionário de variáveis tem exatamente estas colunas, nesta ordem:
`Variável | Descrição | Regra de Validação | Funções`. A coluna de validação carrega obrigatoriedade,
formato ou ENUM completo, e o fallback.
*Motivo:* é o único lugar onde a lógica de cada campo fica escrita uma vez. Descrição sem regra de validação
vira decisão do modelo em runtime.

**R3 — Toda variável declarada precisa de algo que a preencha.** Declarar e definir fallback não basta.
- *Variáveis de coleta* (nome, documento, data, convênio): basta o bloco de coleta em prosa.
- *Variáveis de controle* (fila, resolução, trilha): **precisam ser nomeadas explicitamente pelo
  token**, porque nenhum bloco de coleta as alimenta. Ausência aqui é bug, não estilo.

**R4 — Variável de roteamento obrigatória.** Declare uma variável de fila e defina-a **antes** de chamar o
transbordo. Proibido acionar transbordo com fila em branco quando existe atendente de destino.
*Motivo:* transbordo sem fila cai em lugar nenhum, e o usuário fica esperando.

**R5 — Não declare variável de observações livres.** Sinais sem campo dedicado — demanda fora do escopo,
tentativas esgotadas, opção não reconhecida, convênio sem cobertura — já chegam ao atendente pelo **otto
resumo**, função predefinida da plataforma.
*Motivo:* reimplementar capacidade nativa paga token em todo turno, porque cada ponto do prompt que alimenta
a variável é sempre-ativo.

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
fallback.

**R13 — Pergunta fora do menu tem tratamento próprio.** O usuário pode perguntar qualquer coisa a qualquer
momento. Responda pela base, pergunte *"Posso ajudar em algo mais?"* e bifurque na variável de resolução:
resposta negativa encerra como resolvido; resposta positiva ou nova demanda retoma o menu.
*Motivo:* é o que torna o fluxo estático utilizável — sem isso o agente ignora a pergunta e repete o menu.

**R14 — Fallback de roteamento.** Defina o destino de opção não reconhecida, tentativas esgotadas e demanda
não identificada. Nunca deixe essa borda implícita — é a mais frequente em produção e a que ninguém testa.

**R14a — Falha de ferramenta tem escada própria.** Erro ou timeout **não** é retorno vazio, e os dois não
podem ter o mesmo tratamento. Escreva no prompt gerado:

> Refazer a **mesma** chamada 1× no mesmo turno, em silêncio. Persistindo, informar instabilidade e seguir
> **sem** transbordar. Transbordar só quando a **mesma** operação acumular 3 falhas.

*Motivo:* sem esta regra a borda fica implícita, e modelo pequeno diante de borda implícita improvisa — em
geral transbordando na primeira falha, ou anunciando ao usuário um erro técnico que não sabe descrever.

**R14b — Retorno vazio não é negação.** Função que volta sem itens significa "não veio", não "não existe".
A **única** autorização para dizer que o cliente não oferece algo é uma lista de exclusão explícita,
informada pelo cliente e escrita no prompt.
*Motivo:* negar com base em vazio produz recusa de um serviço real, e o usuário desiste de um atendimento
que a empresa presta. É a regra que falta com mais frequência.

**R14c — Precedência entre regras, declarada.** O prompt tem quatro campos, e eles podem se contradizer em
caso de borda. Declare a ordem uma vez, em Regras de Segurança:

> Havendo conflito entre duas regras, vence a de Regras de Segurança. Nunca escolher em silêncio.

*Motivo:* é a única borda que o próprio prompt cria. Sem ordem declarada, o modelo resolve o empate por
proximidade no texto — e a regra de segurança é a que está mais longe do fluxo.

**R13a — Modalidade de pagamento é um bloco próprio, antes do bloco de convênio.** Quando o domínio tiver
convênio ou plano, a trilha pergunta **primeiro** a modalidade — convênio ou particular — e só entra no
bloco de convênio se a resposta for convênio. Em particular, os campos de convênio ficam `"Não se aplica"`.
Assuma que o atendimento particular existe e confirme no relatório: praticamente todo prestador atende
particular.
*Motivo:* sem esse bloco, quem não tem convênio esgota as tentativas da R12 e termina registrado como
`"Não Informado"` — que a R6 define como **recusa explícita**. O atendente recebe "recusou informar o
convênio" sobre alguém que simplesmente não tem um.

## Encerramento — o ponto de falha nº 1

**R14d — Nenhum passo repergunta o que a conversa já resolveu.** A cláusula vai **na linha do passo**, não
no cabeçalho:

> Dado que o usuário já informou espontaneamente é preenchido **sem perguntar** — inclusive quando a
> primeira mensagem já aponta a opção do menu.
> Lista de **coleta** (unidades, turnos, valores de um campo) mostra só o que se aplica ao item já
> identificado; opção única se confirma, não se oferece em lista.

Isso **não** vale para o menu da árvore: ali a numeração é contrato (R10) e filtrar deslocaria os números.

*Motivo:* a regra genérica no topo do fluxo não basta. Medida num agente que a tinha: reperguntou o motivo
que a primeira mensagem já declarava, e ofereceu três unidades para um serviço que só existe em uma. O
modelo lê o passo que executa, não o parágrafo de abertura.

**R14e — Mudança de demanda reclassifica, e invalida o que não se aplica.** O usuário pode pedir outra
coisa depois de a trilha ter começado. Escreva no prompt gerado o que sobrevive e o que morre:

> Mudando a demanda, voltar ao menu e reclassificar antes de continuar. Dado de identificação já informado
> é reaproveitado **sem perguntar de novo**. Dado ligado à trilha anterior — fila, item de interesse,
> bloco de qualificação — é descartado, e perguntado de novo só se a nova trilha precisar dele.

*Motivo:* sem isso a nova trilha herda a fila e a qualificação da antiga, e o transbordo entrega um caso
coerente com a conversa errada. É pior do que faltar dado: o atendente não tem como perceber.

**R15 — Executar é uma ação; anunciar não realiza.** Toda trilha termina com a **execução** da função de
transbordo. **Proibido escrever "vou te transferir" / "estou te encaminhando" sem executar a função na mesma
resposta.**

A formulação que funciona em produção, e que deve aparecer no prompt gerado, é esta — use-a literalmente:

> Toda trilha do menu termina obrigatoriamente com a execução da função de transbordo. *Executar a função é
> uma ação — anunciar a transferência em texto não a realiza.*

*A mensagem de transferência não é do agente.* Quem envia o texto de encerramento ou de transferência é a
**plataforma**, depois da chamada, derivando-o das variáveis preenchidas. O prompt fica proibido de conter
despedida, aviso de transferência ou frase de encerramento — o último turno do agente é a confirmação da
R18, seguida da execução.

**R16 — O transbordo é o handoff único.** **Toda** trilha executa a função, inclusive a de informação
resolvida. A variável de resolução decide o que a plataforma faz **depois** da chamada — ela não decide se a
função roda.
*Motivo:* "dúvida sanada → encerrar sem acionar a função" deixa a automação de encerramento e as tags de
relatório sem gatilho: o atendimento nunca é entregue.
*Única exceção:* recusa de consentimento antes de qualquer coleta.

**R17 — Falta de dado não bloqueia a execução.** O que a trilha não coleta vai como sentinela (R6). Fila
indefinida nunca justifica não transferir — o fallback resolve.

**R18 — Trilha com coleta confirma e executa; trilha sem coleta executa direto.** Com
`fluxo.confirma_antes_executar = Sim` (default), a trilha que coletou dados lê de volta o que coletou, pede
**uma** confirmação, e executa a função no turno em que a confirmação chega. Com `Não`, o resumo é
informativo e a execução acontece na mesma resposta do resumo. Trilha sem coleta executa imediatamente após
a escolha da opção.
*Motivo:* dado errado só é descoberto pela atendente humana, depois de a transferência já ter custado. A
confirmação é a única checagem antes disso.

**R19 — Duas armadilhas de redação que produzem exatamente este defeito.** Evitar no prompt **e** nos
manuais:

1. **Esperar um "sim" que ninguém trata.** A confirmação da R18 é **uma**, e vem **antes** da execução.
   Pedir confirmação *depois* de a função já ter rodado deixa o agente parado num estado que nenhum passo
   seguinte resolve. Uma confirmação, antes; nunca duas, nunca depois.
2. **Descrever a fala em vez do ato.** *"Informe que o atendimento está sendo encaminhado"* ensina o agente a
   emitir a frase e encerrar o turno. Toda instrução tem que ser sobre executar a função.

**R20 — Cada proibição vem com a saída correspondente.** Cercar o transbordo só de proibições (*"proibido
transferir sem X"*, *"proibido sem Y"*) faz o modelo ler a transferência como ação de risco e hesitar.

## Funções e schema

**R21 — A sentinela entra no `enum`; não se afrouxa o schema para caber nela.** Se o parâmetro declara
`enum`, `pattern` ou `format` e o agente manda `"Não coletado"`, a chamada **viola o schema e é descartada
em silêncio** — o sintoma é *"o agente chega na função e não faz nada"*.

A saída é **declarar as sentinelas como valores válidos**, não remover a restrição:

```json
"pedido_medico": { "type": "string",
                   "enum": ["Sim", "Não", "Não Informado", "Não coletado"] }
```

Só os campos realmente universais da árvore podem ser `required`. Os condicionais continuam opcionais — mas
**opcional não é o mesmo que sem restrição de valor**. **Registre o enum no manual da função de transbordo.**

*Motivo:* o conjunto de valores já era finito; só não estava declarado. Trocar o enum por string livre
resolve o descarte e cria um problema maior: devolve ao modelo um campo aberto onde ele pode escrever
qualquer coisa. Num agente que roda em modelo pequeno, o enum é a única restrição estrutural disponível —
a plataforma não expõe `allowed_tools`, `reasoning_effort` nem modo strict. Desarmá-lo é abrir mão do
último controle que não depende de o modelo obedecer.

*Se o formulário de função não aceitar `enum`:* aí sim o campo é string livre, e a compensação vai para o
prompt — a lista de valores válidos escrita literalmente no bloco da trilha, com a sentinela incluída.
Registre essa limitação no relatório final; ela muda o que se pode esperar do agente.

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

**R24a — Só colete dado que tem finalidade na trilha em curso.** Todo campo de um bloco de coleta precisa
de um consumidor nomeado: um parâmetro da função, ou um campo que o atendente recebe no card. Sem
consumidor, o campo sai do bloco. Em particular, separe **orientação geral** ("como faço para acessar X",
"quais são os canais") de **consulta individual** ("qual é o meu X"): a primeira não precisa de
identificador nenhum.
*Motivo:* medido em produção — um agente pedia documento para uma função que devolvia só canais e prazos
genéricos, iguais para todo mundo. O dado não alimentava nada, e a função passava a parecer uma consulta
autenticada que ela não fazia.

**R25 — Duas seções no manual, com o nome do campo da plataforma.** Todo manual de função tem exatamente
`## 1. Objetivo da Função` · `## 2. Condições de Execução` — os nomes dos dois campos onde o texto é colado,
como já acontece com as quatro seções do prompt. Nunca uma terceira, e nunca seção de especificação técnica.
*Motivo:* a seção nomeada pelo campo de destino elimina a dúvida de onde cada texto vai. E não existe
terceira porque não existe um terceiro campo para colá-la.

**R26 — As duas seções do manual são sempre-ativas.** §1 e §2 são campos da plataforma, pagos em **todos**
os turnos junto com o schema da função — não só quando a função é chamada.
*Motivo:* a versão anterior desta regra afirmava o contrário, que a §2 era documentação fora do alcance do
modelo. Sob essa premissa, toda medição de sempre-ativo subestimou o custo por uma §2 inteira vezes o número
de funções, e regra escrita na §2 parecia gratuita. Não é: custa como a §1.
*Consequência:* regra que vale para o fluxo inteiro vai no prompt principal e **não** se repete na §2;
regra que só vale ao ler o retorno daquela função vai na §2 e **não** se repete no prompt. Duplicar entre
os dois paga duas vezes e produz deriva (R29).

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

**R27a1 — Menos funções é mais barato que arquivos menores.** O sempre-ativo paga a **descrição** de cada
função em todo turno; o **arquivo** que ela retorna, não. Funda o que é sempre chamado no mesmo trecho do
fluxo numa função só, e mantenha separada apenas a que é raramente acionada. Partir um arquivo grande em
duas funções piora o custo, porque paga mais uma descrição em todo turno.
*Motivo:* a intuição puxa para o lado errado — enxugar JSON parece economia e quase não é; cortar uma função
é economia permanente.

**R27b — Responder só o subconjunto perguntado.** Ao processar o retorno de uma função que carrega uma base
grande, responda **apenas** com o que foi perguntado. Nunca cole a base inteira na conversa.
*Motivo:* base inteira na tela faz o
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

**R30 — Perguntas em blocos relacionados, dentro de uma meta de interações.** O bloco de coleta é emitido
como **uma** mensagem com a lista dos campos pedidos, não como uma pergunta por mensagem. A ficha define a
meta de mensagens do agente, da saudação até executar o transbordo (default **5 a 7**), e a trilha mais
longa da árvore precisa caber nela.
*Motivo:* a cobrança do WhatsApp passou a ser por mensagem. Uma pergunta por mensagem multiplica o custo de
canal e alonga o atendimento sem ganhar precisão — bloco relacionado é respondido de uma vez.
*Limite:* bloco não é formulário. Passando de 4 ou 5 campos, parta em dois. E isto não vale para o menu: ali
a escolha é uma por vez, porque a numeração é contrato (R10).

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

### ⚠️ Regras Críticas
### 📌 Regra geral de dados
### 🧭 Fluxo Estático — Menu Principal
### 🧭 Submenus
### 🧱 Blocos de Coleta
### 🗺️ Tabela de Trilhas (opção → coleta → fila)
### ✅ Encerramento Obrigatório da Trilha (ação, não mensagem)
### 🔁 Regra de Navegação e Tentativas
### ❓ Perguntas Fora do Menu
### 🧯 Bordas

---

## 3. Regras de Conduta

### 📐 Formato da Resposta
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
blocos de borda próprios do domínio (ex: convênio sem cobertura → seguir pela trilha particular, R13a).

**Os três blocos que existem por causa do modelo pequeno:**

- **Regras Críticas** — de 3 a 5 travas, no topo do campo, antes do menu. São as de violação binária e cara:
  o que o agente jamais confirma, o que jamais deduz, e a formulação literal de execução (R15). Nada de tom,
  nada de formato, nada que dependa de julgamento.
  *Motivo:* Diretrizes é o campo mais longo. Trava enterrada no meio dele compete com a árvore inteira de
  menus; trava no topo é a primeira coisa lida ao entrar no campo.
- **Bordas** — tabela `situação | ação`, uma linha por borda: retorno vazio (R14b), falha técnica (R14a),
  tentativas esgotadas (R12), conflito entre regras (R14c). Tabela, não prosa: a borda tem que ser
  encontrável por varredura visual.
- **Formato da Resposta** — o contrato de saída, em 4 a 6 linhas: como o bloco de coleta se emite em uma
  mensagem só e qual é a meta de interações (R30), teto de itens em lista, se numera, se usa emoji, e qual
  mensagem é template literal.
  *Motivo:* sem contrato, o modelo escolhe o formato a cada turno — e modelo pequeno escolhe mal com
  frequência. Não repetir aqui o que já estiver em Linguagem e Formato.

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
**Bloco Modalidade** — convênio ou particular; vem **antes** do Bloco Convenio (R13a)
**Bloco Convenio** — nome do convênio; só quando a modalidade for convênio
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
| `IA_CAMPO` | [o que é] | Obrigatório/Opcional. Formato ou ENUM completo. Fallback. | `nome_funcao` → parâmetro `nome_param` |
```

Na coluna **Variável** o nome vai **sem** os underlines duplos — é assim que a plataforma registra o campo. Os
`__` são delimitadores de interpolação e permanecem em todo o resto: prompt, `clienteinfo.json` e as
referências cruzadas dentro das outras colunas.

**Núcleo canônico de controle** — presente em todo agente estático:

| Variável | Papel |
| --- | --- |
| `__IA_TRILHA__` | Código + rótulo da opção percorrida |
| `__IA_ATENDIMENTO_FILA__` | Fila humana de destino |
| `__IA_ATENDIMENTO_RESOLVIDO__` | Único parâmetro obrigatório em toda chamada de transbordo |

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
                    ["Trilha", "Resolvido", "Fila"],
                    ["__IA_TRILHA__", "__IA_ATENDIMENTO_RESOLVIDO__", "__IA_ATENDIMENTO_FILA__"]
                ]
            }
        ]
    }
]
```

## 2.6 Manual da função de transbordo

Duas seções (R25), **as duas sempre-ativas** (R26). A §2 deste manual é a mais longa: carrega a tabela de
filas, a regra de resolução, a lista completa de parâmetros e — obrigatoriamente — **a nota de
compatibilidade de sentinela com o schema (R21)**.

````markdown
## 1. Objetivo da Função

[Prosa corrida, ≤ 950 caracteres. O que a função faz e em qual momento acioná-la.]

---

## 2. Condições de Execução

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
````

**Não existe seção de exemplos.** Não há um terceiro campo na plataforma para colá-la, e exemplo que o
modelo não recebe não ensina nada ao agente — só cria uma segunda versão da regra, que a revisão seguinte
corrige de um lado só. Os casos de teste vão para a matriz de homologação (Passo 5).

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
- **Pedir uma segunda confirmação, ou confirmar depois de executar a função** (R19.1).
- **Escrever despedida, aviso de transferência ou frase de encerramento** no conteúdo de prompt. Essa
  mensagem é enviada pela plataforma depois da chamada, não pelo agente (R15).
- **Exibir código interno de trilha** ao usuário (R11).
- **Citar caminho de pasta ou arquivo** no conteúdo do prompt (R34).
- **Criar uma quinta seção `##`** no prompt (R36) ou uma terceira no manual (R25).
- **Deduzir o gênero do agente** pelo nome.

---

# Passo 4 — Verificação mecânica

```
1.  Toda folha da árvore virou linha da Tabela de Trilhas, com fila definida
2.  Nenhuma trilha coleta dado além do que a tabela declara
3.  Fila de fallback definida para opção não reconhecida e tentativas esgotadas
4.  Seção de encerramento presente, com a formulação "ação, não mensagem"
5.  Nenhuma instrução pede uma segunda confirmação nem confirmação depois da execução (R19.1)
6.  Nenhuma instrução descreve a fala de transferência sem a execução
7.  Toda sentinela usada no prompt consta do `enum` do parâmetro, ou o parâmetro não tem `enum` (R21).
    Schema afrouxado para acomodar sentinela é defeito, não solução
8.  Variável de resolução com regra de preenchimento em 100% dos caminhos
9.  Toda variável declarada tem algo que a preencha; as de controle pelo token
10. Todo token do card tem variável declarada, e os arrays têm o mesmo tamanho
11. O card é JSON válido
12. Numeração de submenu reinicia em 1
13. Código interno de trilha nunca exibido, sempre preenchido
14. Nenhum `**` como instrução de destaque no conteúdo de prompt
15. §1 de cada função ≤ 950 caracteres; todo manual com exatamente 2 seções, `1. Objetivo da Função` e
    `2. Condições de Execução`
16. Nenhum caminho, nome de arquivo ou `§N` no conteúdo de prompt
17. O prompt tem exatamente 4 seções `##`
18. Nenhum nome próprio de outro cliente
19. O bloco Regras Críticas existe, é a primeira coisa das Diretrizes, e tem de 3 a 5 itens
20. O bloco Bordas cobre as quatro: retorno vazio (R14b), falha técnica (R14a), tentativas esgotadas (R12),
    conflito entre regras (R14c)
21. Existe bloco de Formato da Resposta em Regras de Conduta
22. Nenhuma despedida, aviso de transferência ou frase de encerramento no conteúdo de prompt (R15)
23. A trilha mais longa cabe na meta de interações da ficha — conte as mensagens do agente da saudação até
    o transbordo (R30)
24. Havendo convênio ou plano no domínio, existe o Bloco Modalidade antes do Bloco Convenio (R13a)
25. Todo campo de bloco de coleta tem consumidor nomeado: parâmetro de função ou campo do card (R24a)
```

Meça o **bloco sempre-ativo** — as 4 seções do prompt mais **§1 + §2 + schema de cada função**. Meça o
**texto final**, o que vai ser colado na plataforma, nunca um rascunho: rascunho não conferido contra esta
checklist já subestimou o resultado em 22 pontos percentuais, porque o que ele "economizava" era precisão
que precisou voltar. Reporte o número medido, não estimado.

Os itens 19 a 25 existem porque o agente roda em modelo pequeno: são as lacunas que fazem um `nano`
improvisar. Vários deles aumentam o token em vez de reduzir. É deliberado.

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
6. **A matriz de homologação**, escrita em `relatorios/homologacao.md` do cliente — uma linha por caso, no
   formato `cenário | resultado esperado`. Cobre no mínimo: cada folha da árvore até o desfecho; opção
   inválida e tentativas esgotadas; o caminho particular (R13a); o usuário que já abre declarando a opção
   (R14d); mudança de demanda no meio da conversa (R14e); falha de ferramenta (R14a); e o desfecho
   resolvido **versus** transferido (R16). É o arquivo que a equipe usa para testar, e não vai para a
   plataforma.

**Nunca fechar dizendo "pronto" com pendência de dado de cliente aberta.** Diga o que está pronto para colar,
o que está pronto como documento interno, e o que não sobe até a pendência fechar.

---

## Changelog

- **3.0.0** — **Corrigido o contrato do runtime: a §2 do manual é sempre-ativa.** A R26 afirmava o
  contrário — que §2 e §3 eram documentação fora do alcance do modelo. São dois campos da plataforma,
  `Objetivo da Função` e `Condições de Execução`, pagos em todo turno junto com o schema; toda medição de
  sempre-ativo feita sob a premissa antiga subestimou o custo. Daí vêm: a tabela do contrato do runtime, a
  §3 removida, os manuais renomeados pelos campos de destino, e a R19 reduzida a duas armadilhas — a
  terceira ("exemplo que contradiz a regra é few-shot e vence a regra") deixou de existir junto com a §3, e
  sua premissa estava errada de todo modo, porque exemplo de manual nunca chegou ao modelo. Outras mudanças
  de comportamento: a mensagem de transferência é da plataforma e o prompt fica proibido de escrevê-la
  (R15); a R18 passa a **pedir** uma confirmação antes de executar, e a R19.1 protege apenas o defeito real
  — confirmação depois da execução, ou uma segunda confirmação; perguntas passam a ser agrupadas em blocos
  relacionados com meta de interações, por causa da cobrança por mensagem do WhatsApp (R30, que substitui a
  regra de mascaramento — removida, porque o documento fica no histórico da plataforma e é coletado sob
  consentimento); Bloco Modalidade antes do Bloco Convenio, com caminho particular explícito (R13a); coleta
  só com consumidor nomeado (R24a); e reclassificação na mudança de demanda (R14e). O Passo 5 passa a
  emitir a matriz de homologação.
- **2.2.0** — **Formato declarado: markdown para estruturar, nunca XML.** A documentação oficial não
  prescreve formato de prompt para o `gpt-5.4-nano` — o que ela exige é *ter* estrutura. Medido: trocar
  os headers por tags XML custaria +217 tokens por turno por agente (+5% do campo), sem ganho
  documentado, e o que o XML resolveria — delimitar blocos — a plataforma já resolve, porque os 4 campos
  são entradas separadas. A regra existe para impedir que a próxima revisão "melhore" o prompt para os
  blocos XML dos exemplos da documentação, que são orquestração multi-etapa do modelo frontier.
- **2.1.0** — Adequação ao `gpt-5.4-nano`. Modelo alvo declarado, com as consequências de escrita que derivam dele. Acrescentados os três blocos que faltavam no prompt gerado — **Regras Críticas** no topo das Diretrizes, **Bordas** e **Formato da Resposta** — e as regras de borda que não existiam: falha técnica com escada própria e precedência entre regras declarada. Motivo: a orientação oficial do nano pede tarefa estreita, saída fechada e nenhuma borda implícita; borda não escrita é comportamento inventado. **R21 reescrita**: a sentinela passa a ser declarada no `enum` do parâmetro, em vez de o schema ser afrouxado para acomodá-la. Com a plataforma sem `allowed_tools`, `reasoning_effort` nem modo strict, o enum é a única restrição estrutural disponível — desarmá-lo era abrir mão do último controle que não depende de o modelo obedecer.
- **2.0.0** — Reescrita autocontida. Antes, 14 regras eram citadas por número de um documento externo; numa
  medição com esse documento fora de alcance, **6 delas viraram buraco** — a taxonomia de trilhas e os
  limites de domínio foram pulados, o fallback de roteamento ficou sem destino, e o formato de quatro colunas
  do dicionário de variáveis teve de ser **adivinhado**. Agora todas estão inlinadas com numeração própria e
  o motivo junto. Acrescentada a ficha de parâmetros do Passo 0: a versão anterior produzia boas perguntas e
  assumia mesmo assim, listando na frase seguinte "o que eu assumiria por conta própria, e é chute".
  Acrescentados os esqueletos literais de cada arquivo gerado.
- **1.0.0** — Versão inicial.
