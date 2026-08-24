---
name: agv-novo-clinux
description: Use somente quando o usuário pedir explicitamente a criação de um novo agente virtual de autoagendamento com integração ao sistema clinux-genesis, nomeando o cliente. Não usar para auditar, documentar ou editar agente que já existe.
argument-hint: "[cliente] [dados]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion
metadata:
  version: "1.0.0"
---

# Criar Agente de Autoagendamento — Clinux

Cria a pasta do cliente `$ARGUMENTS` a partir do **modelo de referência da categoria** — o cliente Clinux já
montado que existir no workspace. Localize-o pela busca do bloco *Onde criar a pasta do cliente*; se houver
mais de um, pergunte qual usar como referência. Não havendo nenhum, diga isso e pare: sem modelo não há de
onde derivar os invariantes desta categoria.

**Não escreva um agente do zero.** No Clinux não existe base de conhecimento estática: unidade, convênio,
exame, preço e horário são **consultas diretas a endpoints**, iguais em qualquer cliente do mesmo sistema. O
que varia entre dois clientes Clinux é um punhado de parâmetros e as regras de negócio próprias. Escrever um
segundo fluxo com estrutura própria só cria divergência entre duas instalações do mesmo módulo.

**Leia `invariantes-clinux.md`, nesta pasta, antes de escrever qualquer arquivo.** Ali estão as regras que
custaram uma auditoria de 30 defeitos para descobrir, cada uma com o motivo. Regra sem o motivo é regra que a
próxima revisão "melhora" e reintroduz o defeito.

---

## Onde criar a pasta do cliente

**Não assuma convenção de pastas.** Resolva pelo disco: busque o padrão `**/config/agente.md` por caminho
de arquivo (no Claude Code, a ferramenta `Glob`). Cada resultado é um cliente já montado, e a pasta dele é o
diretório **dois níveis acima** do arquivo.

| Estado | Ação |
| --- | --- |
| Encontrou pasta(s) de cliente | Criar ao lado. Havendo mais de um agrupamento (por modelo, por categoria), **perguntar em qual** |
| Não encontrou nada | **Perguntar onde criar.** Não inventar `Agentes Virtuais/` nem qualquer outra árvore |

A linha `destino.pasta` da ficha do Passo 0 recebe essa resposta, e é a mais bloqueante de todas: sem ela,
**não escreva arquivo nenhum** — todos moram dentro dessa pasta, então não existe "escrever o que não depende
dela". Não vale criar na raiz do diretório de trabalho "por não ter onde mais": isso é inventar árvore com
outro nome.

## Passo 0 — Perguntar o que falta. **Antes** de escrever.

Esta é a razão de a skill existir. Um agente sem ela produz a estrutura certa (o modelo de referência ensina)
e depois **inventa os dados do cliente**: assume o gênero pelo nome do agente, herda o ENUM de omnitag de
outro cliente "como proposta", reescreve a saudação por conta própria, e só lista as pendências no fim,
depois de já ter decidido.

**Herdar regra de negócio de outro cliente é o erro mais caro desta skill.** Estrutura se herda; regra de
negócio, nunca.

### Índice de função não é endpoint

A plataforma registra **funções por índice**, e o índice é independente do endpoint por trás dele. O mesmo
endpoint do Clinux pode ser registrado sob **mais de um índice**, e índices diferentes podem apontar para
endpoints diferentes. É esse mecanismo que resolve os dois casos que o modelo de referência não exemplifica.

**Consulta ganha índice próprio.** Se o escopo inclui consultas, a trilha tem suas próprias funções
numeradas. Cada uma pode reusar o endpoint da trilha de exames ou apontar para outro — **isso é decisão do
cliente e você precisa perguntar**, uma a uma. Não deduza que "consulta = mesmo endpoint" nem o contrário.

**Cada fila é uma função.** Não existe parâmetro `fila_atendimento`: a fila vai **no nome da função**, e
múltiplas filas significam **múltiplas funções de transbordo** — uma por fila. É o mesmo padrão dos agentes
de pré-agendamento (`set_transbordo_agendamento`, `set_transbordo_geral`). Perguntar quantas
filas, o nome exato de cada uma, e **qual gatilho leva a qual** — sem esse critério o agente tem duas portas
e nenhuma regra para escolher.

**O que continua fora do alcance:** o *conteúdo comportamental* da trilha de consulta — escolha de
especialidade e de médico — não existe no modelo de referência. Registrar os índices é uma coisa; escrever a
trilha é outra. Com escopo incluindo consulta, escreva a trilha de exames, registre os índices de consulta
que o cliente informar, e **reporte a trilha comportamental como pendência**. Não improvise etapa de médico.

**Armadilha do escopo maior: a negação não se herda.** Na referência, cada menção a um serviço fora do escopo
existe **para negá-lo** — a lista de exames não realizados inclui `Consultas` e `Fisioterapia`. Copiar isso
para um cliente que **presta** aquele serviço não deixa lacuna: produz **recusa ativa de um serviço real**,
com o agente dizendo ao paciente que a clínica não faz o que ela faz. Ao derivar para escopo maior, **não
copie os trechos de negação** do serviço que o cliente presta. Sem tratamento é ruim; recusa errada é pior.

**Requisito que você não pode implementar ainda continua sendo requisito.** Pergunte e registre — o critério
de separação entre filas, por exemplo — mesmo que a implementação dependa de configuração na plataforma.

### A ficha de parâmetros é obrigatória, e vem antes de tudo

Levante o que veio por qualquer dos dois caminhos válidos: **texto colado no próprio comando** e/ou arquivos
em `$ARGUMENTS/origem/` — pasta que num cliente novo costuma **não existir ainda**. Nenhum dos dois é
obrigatório; a ausência de ambos não é erro, só significa que mais linhas caem em `[PERGUNTAR]`. Vindo o
material colado no comando, salve-o verbatim em `origem/especificacao-agente-[NomeCliente].md`, criando a
pasta. **Preencha e exiba a
ficha abaixo antes de escrever qualquer arquivo**. Toda linha tem de ter um valor ou a marca `[PERGUNTAR]`.

```
FICHA DE PARÂMETROS — <cliente>
  cliente.grafia_comercial ....... 
  agente.nome .................... 
  agente.genero .................. 
  agente.saudacao_literal ........ 
  transbordo.filas ............... 
  transbordo.funcoes_por_fila .... 
  omnitag.enum ................... 
  escopo ......................... 
  funcoes.inventario ............. 
  funcoes.indices_consulta ....... 
  negocio.exames_nao_realizados .. 
  negocio.pedido_obrigatorio ..... 
  negocio.preparo_em_escopo ...... 
  negocio.reagendamento .......... 
  negocio.lgpd_upstream .......... 
  default.corte_turno ............ 13:00
  default.limite_caracteres ...... 200
  default.teto_lista ............. 5
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

Reexiba a ficha preenchida no relatório final (Passo 3), com a origem de cada valor: informado, lido de
`origem/`, ou default.

### Bloqueantes — sem estes o arquivo nasce com dado inventado

| Dado | Por que não se deduz |
| --- | --- |
| **Grafia comercial do cliente** | Aparece na primeira mensagem que todo paciente lê. Não inventar acento, espaço ou caixa. |
| **Nome e gênero do agente** | Gênero não se deduz do nome. E ter nome próprio de pessoa cria uma borda: perguntado se é humano, o agente confirma que é assistente virtual. |
| **Texto literal da saudação** | É transcrito ao pé da letra. Se o cliente não tiver um, propor e pedir aprovação — não assumir a de outro cliente. |
| **Fila(s) de transbordo** | O modelo pressupõe uma fila única de agendamento. Havendo mais de uma, muda o desenho da função de transbordo. |
| **ENUM de `OMNITAG`** | Os valores são por cliente. Herdar de outro grava classificação errada em silêncio — a estatística fica plausível e falsa. |
| **Escopo** | Exames (módulo AAGE), consultas (AAGC) ou ambos. Consultas trazem trilha de especialidade e médico, e outras funções. |
| **Inventário real de funções** | Quais estão de fato configuradas na plataforma. Autocadastro contratado? Preço exibido para particular? Cada "não" remove função e muda uma etapa. |
| **Funções de transbordo, uma por fila** | A fila vai no nome da função, não em parâmetro. Precisa do índice e do nome de cada uma, **e do gatilho que leva a cada fila** — duas portas sem critério de escolha é pior que uma. Perguntar também o que **mais** muda por fila: profundidade da coleta antes de transbordar, e o que aparece no card. Filas diferentes costumam querer coisas diferentes. |
| **Índices da trilha de consulta** | Só quando o escopo inclui consulta. Quais índices, e **para cada um**: reusa o endpoint da trilha de exames ou aponta para outro? Não deduzir nem um nem outro. |

### Regras de negócio — perguntar sempre, nunca herdar

| Pergunta | Efeito no prompt |
| --- | --- |
| **Exames que a clínica NÃO realiza** | Vira uma lista nominal no prompt e a **única** autorização para dizer "não realizamos". Sem lista, o agente não pode negar nada — retorno vazio de função não serve como negação (ver invariantes). |
| **Pedido médico é obrigatório?** | Se sim: trava de gravação, variável obrigatória, e o caminho "sem pedido" precisa de desfecho definido. |
| **Preparo está em escopo?** | O padrão da categoria é **fora**: nenhuma função devolve preparo, e preparo errado faz o paciente perder o exame. Só entra se o cliente contratou e você souber em qual retorno vem. |
| **Reagendamento e cancelamento** | Repasse com coleta mínima (padrão) ou o agente executa? Executar exige funções que o módulo não tem. |
| **Consentimento LGPD** | O padrão da categoria é tratado **a montante**: o agente não tem etapa de consentimento. Confirmar. |

### O que **parece** default e é regra de negócio

Quatro valores que um agente assume sem perceber, porque são plausíveis e há um único exemplo no repositório.
Todos ficam `[PERGUNTAR]`:

| Assunção tentadora | Por que não é default |
| --- | --- |
| "Sofia é nome feminino, logo gênero feminino" | Gênero é escolha do cliente, não inferência do nome. |
| "escopo = exames, porque é o único modelo que existe" | O repositório ter um só exemplo não é evidência sobre este cliente. |
| "fila única de agendamento" | A referência tem uma só, mas o padrão da plataforma é **uma função por fila**. Perguntar quantas, e o gatilho de cada. |
| "LGPD a montante, porque é o padrão da categoria" | É padrão **a confirmar**, não default silencioso. |

### Com default — assumir e informar no relatório final

| Dado | Default |
| --- | --- |
| Corte de turno | `13:00` — manhã `07:00`–`12:59`, tarde `13:00`–`18:00` |
| Limite de caracteres por mensagem | 200, com exceção para o resumo de confirmação e as listas de opções |
| Teto de itens em lista | 5, com paginação por "Outras opções" |
| Emojis | 😊 🏥 ✅ 📋 📅 📍 💳 |
| Delimitador de variável | `__NOME_DA_VARIAVEL__` |

---

## Passo 1 — Derivar do modelo

```
<pasta do cliente>/
├── config/
│   ├── agente.md              ← 4 seções = os 4 campos da tela
│   ├── variaveis.md           ← o contrato de parâmetros dos endpoints
│   └── clienteinfo.json       ← card do atendente no transbordo
├── ferramentas/
│   ├── manuais/               ← 1 .md por função, exatamente 2 campos cada
│   └── exemplos-de-dialogo.md ← documentação; não vai para a plataforma
├── origem/                    ← material bruto do cliente
└── relatorios/                ← nasce com o primeiro relatório
```

**Sem `ferramentas/dados/` e sem `ferramentas/schemas/`.** Não há base estática nem JSON Schema a versionar.
Não criar pasta "para depois".

### O que copia praticamente inteiro

- **Os 12 manuais.** Nenhum cita nome de cliente. Ajustar só o que o inventário de funções do Passo 0 mudou.
- **`clienteinfo.json`.** Só tokens de variável, zero conteúdo de cliente.
- **A espinha do `agente.md`:** Regra Geral de Dados, Regra Geral de Retorno de Função, Tabela de Etapas,
  etapas 1–6, trilha de repasse, Regra de Falha Técnica, Regra de Tentativas, e as 4 seções de segurança.
- **As notas de sistema do `variaveis.md`:** proibição de renomear, formato de data, nenhum valor de reserva
  em campo obrigatório.

### O que **não** copia

- **Regra de negócio do outro cliente:** ENUM de omnitag, lista de exames não realizados, obrigatoriedade do
  pedido. Vem do Passo 0 ou fica pendente.
- **Histórico de correção do outro cliente:** notas de "normalização aplicada nesta revisão", variáveis fora
  de uso que existem no registro *dele*, datas de decisão. Cliente novo não tem esse passado.
- **Nomes de exemplo** de unidade, convênio e exame nos diálogos: trocá-los por chute sobre o cliente novo
  planta dado inventado num arquivo de referência. Manter e marcar como fictícios.
- **A pasta `origem/` como baseline de prompt.** Num cliente novo não existe prompt de produção anterior.

### Numeração das funções

`1_` a `N_` **na ordem do fluxo, sem lacuna**. Cliente novo nasce numerado certo — numeração por ordem de
criação, com lacunas, foi a origem direta de dois defeitos críticos na referência.

Nos textos, citar função sempre pelo **nome completo**, nunca pelo prefixo solto (`` `7_` ``). Referência
curta sobrevive a renumeração apontando para a função errada, e não dá erro visível.

---

## Passo 2 — Verificação mecânica

Rodar **todas** antes de entregar. Estas checagens já pegaram defeito real em revisão humana.

```bash
# 1. Toda função citada tem manual, e todo manual é citado
# 2. Nenhuma referência curta `N_` — só nome completo
# 3. Todo manual com exatamente 2 seções: Objetivo da função / Condições de execução
# 4. Todo token do clienteinfo.json tem variável declarada
# 5. clienteinfo.json é JSON válido e os arrays de rótulo/token têm o mesmo tamanho
# 6. Nenhuma variável declarada em uso que o prompt e o card não citem
# 7. Cada "não realiza" no prompt está ancorado na lista de exclusão ou na proibição do retorno vazio
# 8. Nenhum nome próprio de OUTRO cliente vazou:  grep -ri "ultramed\|nome-do-cliente-anterior"
```

Medir o **bloco sempre-ativo** com `tiktoken` (encoding `o200k_base`): os 4 campos de prompt mais o
*Objetivo da função* e as *Condições de execução* de cada função. É o que a plataforma reenvia a cada turno.

**Cliente novo não tem "antes".** O comparável é o sempre-ativo do modelo de referência: medir os dois e
esperar **paridade**, não economia. Regra explícita custa mais que dado: na
referência, uma lista de 24 exames custou 120 tokens e as regras em volta dela custaram quase 1.000. Se
estourar, o corte é em **prosa de justificativa**, nunca em regra — o racional vai para o relatório, onde não
é pago por turno.

---

## Passo 3 — Relatório final: pendências e pontos importantes

Fechar exibindo, nesta ordem:

1. **Tree criada**, com contagem de funções e de variáveis.
2. **Parâmetros usados** — o que veio de você, o que veio de `origem/`, e o que assumiu por default.
3. **Pendências, separadas por quem resolve:**
   - *Bloqueiam a homologação:* dado de cliente que ficou faltando, e o que exatamente não pode ser
     validado sem ele.
   - *Ação de plataforma:* variáveis a criar antes de colar os campos, funções a renomear, permissões WEB a
     liberar no Clinux (o que não estiver liberado não retorna, e o agente lê como "não há opção").
   - *Dúvida aberta que não bloqueia.*
4. **Pontos importantes** — as decisões que mudam comportamento e que alguém vai questionar depois. No
   mínimo: escopo assumido, desfecho de quem não tem pedido médico, preparo dentro ou fora, o que acontece
   com exame fora da lista de exclusão, e o custo medido do sempre-ativo.
5. **Medição de token**, antes × depois, com o número real — não a estimativa.

**Nunca fechar dizendo "pronto" com pendência de dado de cliente aberta.** Diga o que está pronto para colar,
o que está pronto como documento interno, e o que não sobe até fechar pendência.
