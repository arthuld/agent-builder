# Invariantes do Auto Agendamento Clinux

Regras que valem para **qualquer** cliente Clinux, cada uma com o motivo. O motivo não é enfeite: regra sem
motivo é regra que a próxima revisão "simplifica" e reintroduz o defeito que ela existia para evitar. Todas
saíram de defeito observado em produção ou de auditoria.

---

## 1. Nome de variável é proibido mudar

Os nomes (`EMPRESA_ID`, `PLANO_ID`, `CPF_DIGITADO`, `PROCEDIMENTOS_GRUPO_ID`…) **são** os nomes dos
parâmetros nos endpoints do Clinux. Não há camada de tradução: o que está no registro é o que vai na
requisição.

**Por que importa:** renomear — inclusive para o padrão `__IA_CAMPO__` da Regra 4 do projeto, usado no Pré
Agendamento — quebra a chamada **em silêncio**. Parâmetro que o Clinux não reconhece não gera erro: devolve
**vazio**, e o agente reporta vazio ao paciente como se não houvesse resultado.

A Regra 4 **não se aplica** a esta categoria. Só nome de **função** entra em discussão de renomeação.

**Apagar tem o mesmo risco.** Variável fora de uso no prompt fica declarada e intacta: pode estar ligada a um
nó de fluxo estático ou a uma campanha, e variável sem uso **não custa token** — não entra no sempre-ativo.

**Interpolação:** `__NOME_DA_VARIAVEL__`, dois underscores de cada lado, nos campos de prompt e no
`clienteinfo.json`. Diferente do Pré Agendamento, aqui os underscores são **sintaxe**, não parte do nome. Não
tente deduzir isso do Pré Agendamento: lá o nome já contém os underscores, então as duas leituras produzem a
mesma string e nada distingue uma da outra.

---

## 2. Índice de função é registro, não endpoint

A plataforma registra funções por **índice**. O índice é o identificador do registro; o endpoint do Clinux é
o que está por trás dele. Os dois são independentes:

- O **mesmo endpoint** pode ser registrado sob **vários índices**.
- **Índices diferentes** podem apontar para **endpoints diferentes**.

Duas consequências que mudam o desenho, e que não se deduzem olhando o modelo de referência:

**Cada fila de transbordo é uma função própria.** Não existe parâmetro `fila_atendimento` — a fila vai **no
nome da função**. Cliente com três filas tem três funções de transbordo. É o mesmo padrão dos agentes de Pré
Agendamento deste workspace (`set_transbordo_agendamento`, `set_transbordo_geral`).

**Consequência que importa mais que o registro:** com mais de uma fila, o prompt precisa do **gatilho de
cada uma** — qual situação leva a qual fila. Duas portas sem critério de escolha é pior que uma porta: o
agente escolhe por conta e o atendimento cai na fila errada, em silêncio.

**A trilha de consulta tem índices próprios.** Escopo com consulta não reaproveita os índices de exame:
ganha os seus. Cada um pode reusar o endpoint da trilha de exames ou apontar para outro — é decisão do
cliente, perguntada função a função, nunca deduzida.

**Registrar o índice não é escrever a trilha.** O comportamento da trilha de consulta — escolha de
especialidade, escolha de médico, disponibilidade por médico versus por especialidade — não está no modelo de
referência. Registrar índices é configuração; escrever a trilha exige material que só existe quando o
primeiro cliente com consulta for montado.

---

## 3. Retorno vazio não é falha, e não é negação

Três estados distintos, três tratamentos:

| Estado | Tratamento |
| --- | --- |
| **Não respondeu** (erro/timeout) | Retry silencioso 1× no mesmo turno → mensagem de instabilidade, continuar sem transbordar → transbordo só na **3ª** falha da mesma operação. |
| **Respondeu com 0 itens** | **Não é erro.** Seguir o tratamento de vazio da etapa. |
| **Respondeu com N itens** | Ver *Regra Geral de Retorno de Função*. |

**Por que vazio nunca autoriza dizer "a clínica não realiza":** no Clinux, item que não está **liberado para
agendamento web** simplesmente não retorna. Vazio significa "não veio liberado", não "não existe". Negar com
base nele produz recusa errada e faz o paciente desistir de um atendimento que a clínica presta.

A **única** autorização para negar é uma lista nominal de exclusão no prompt, informada pelo cliente.

---

## 4. Regra Geral de Retorno de Função — declarada uma vez

Vale para unidade, plano, exame e horário. **Nenhuma etapa tem tratamento próprio** — foi a duplicação por
função que produziu o defeito mais visível em produção.

| Retorno | Comportamento |
| --- | --- |
| **1 item, sem busca por texto** (a clínica tem uma unidade só) | Não há escolha a fazer: informar e **emendar a próxima pergunta na mesma mensagem**. Proibido numerar, proibido perguntar "qual você prefere?", proibido pedir OK. |
| **1 item, vindo de busca por texto** (plano, exame) | Informar pelo nome exato retornado e pedir **só a confirmação**. Proibido numerar. |
| **2 ou mais** | Lista numerada, uma por linha, teto de 5, excedente em "Outras opções". |
| **0 itens** | Ver *Retorno vazio não é falha, e não é negação*. |
| **Item já informado pelo paciente**, retorno com 1 correspondente | Não perguntar de novo. |

**Por que:** numerar uma lista de um item e perguntar a preferência quando não há alternativa é a
inconsistência que os clientes reportam. Vem de escrever "1 ou mais itens → apresente numerado" num manual e
"confirme o item" no fluxo — duas instruções para o mesmo passo.

---

## 5. Parâmetro malformado se disfarça de indisponibilidade

Sem camada de validação de schema, valor no formato errado **não** volta como erro: o endpoint responde
**vazio**. E vazio o agente lê, por regra, como "não há resultado" — então um bug de parâmetro vira
"não há vaga", indistinguível de agenda cheia para o paciente e para quem analisa a conversa depois.

Consequências:
- **Formato é regra, não preferência.** Chat sempre `DD/MM/AAAA`; a data desejada vai ao endpoint em
  `AAAA-MM-DD`; a conversão é do agente. Nunca um terceiro formato em circulação.
- **Nenhum valor de reserva em campo obrigatório.** Não existem as sentinelas `"Não Informado"` /
  `"Não coletado"` do Pré Agendamento. Faltando o dado real, o agente **retém a chamada** e pergunta.
- **O único teste que separa as duas causas** é informar uma data com vaga **já conferida no Clinux**. Se o
  agente disser que não há vaga num dia que a agenda tem, é formato de parâmetro. Esse teste não se
  improvisa: exige conferir a agenda antes.

---

## 6. A data é piso, não dia exato

A consulta de disponibilidade retorna o que há **a partir** da data informada, podendo incluir dias
posteriores.

- Dizer sempre *"a partir de [data]"*, nunca *"no dia [data]"* — afirmar que não há vaga num dia específico é
  dado que a função não devolveu.
- **Vazio → refazer uma vez sem janela de horário**, mesma data-piso. Cobre o turno oposto e qualquer hora de
  uma vez, numa chamada em vez de duas.
- **Ainda vazio → não oferecer data posterior.** Sendo piso, nada depois dela tem vaga também: a pergunta
  oferece ao paciente uma escolha que não existe. Transbordar. Data **anterior** só se ele propuser.

---

## 7. Chamada única para vários exames

Havendo mais de um exame, **todos** os IDs numa só chamada de disponibilidade, separados por vírgula. Nunca
uma chamada por exame.

**Por que:** horários buscados isoladamente não combinam entre si. O paciente escolheria três horários
incompatíveis e terminaria com os exames em dias diferentes sem saber.

Cada **conjunto** de IDs de agenda retornado é **uma** opção de horário, que atende todos os exames juntos.
Nunca apresentar IDs de um mesmo conjunto como opções separadas. Guardar na **mesma ordem** dos IDs de
procedimento.

---

## 8. Ação, não mensagem

Recebido o aceite do resumo, **executar** a gravação naquele turno.

**Por que é a falha mais grave do fluxo:** anunciar o agendamento sem executar a chamada faz o paciente sair
da conversa acreditando que tem um horário reservado que não existe — e a vaga segue aberta para outra
pessoa. Só aparece no dia, no balcão.

A mensagem de sucesso vem **depois** do retorno, com os dados que a função devolveu. E dois turnos são
obrigatórios entre escolher o horário e gravar: resumo → aceite → gravação.

---

## 9. Identificação: o telefone já vem da plataforma

O contato é injetado. O agente **nunca** pede número de telefone, e o **único** número que o paciente digita
no fluxo é o CPF.

Ordem: busca silenciosa pelo contato no turno da saudação → CPF (só se a busca não resolver) → cadastro (só
se o CPF também não resolver).

**Por que a ordem importa:** ofertar cadastro antes de tentar o CPF cria cadastro duplicado para paciente que
existe com outro telefone.

**Não classificar dígitos.** Regra do tipo "11 dígitos = CPF, 10 = telefone" está errada: celular brasileiro
com DDD tem 11 dígitos. Como o agente nunca pede telefone, a classificação não precisa existir — e sem ela o
defeito não existe.

**CPF digitado não se confirma.** Chamar direto; a confirmação é o **nome retornado** na resposta. CPF lido de
**imagem** é exceção e entra em confirmação consolidada: OCR troca dígito, digitação não.

---

## 10. Ler o contexto de entrada, e ler não dispensa validar

Pacientes abrem direto ao ponto ou enviando a foto do pedido médico. Varrer **texto e imagem** a cada
mensagem, apresentar **uma** confirmação consolidada, atrelar as variáveis só com o aceite.

- **Ler economiza a pergunta, nunca a chamada.** O que foi extraído ainda passa pela função da etapa —
  constar no pedido médico não significa que a clínica realize o exame.
- **Confirmar para quem é o exame.** O pedido pode ser de outra pessoa; nunca assumir o dono do número.
- **Ler o pedido não autoriza opinar sobre ele.** Lido apenas para extrair identificação e nome do exame.
  Proibido comentar, interpretar ou mencionar hipótese diagnóstica, CID, histórico ou medicação. Sem essa
  regra, dar visão ao agente abre caminho para aconselhamento médico.

---

## 11. Custo: o sempre-ativo são 4 campos + 2 por função

A plataforma reenvia a cada turno os 4 campos de prompt **e** os dois campos de cada função — *Objetivo da
função* e *Condições de execução*. Diferente do Pré Agendamento, onde a §2 do manual é documentação que não
chega ao modelo.

**Consequência:** o limite de 950 caracteres da Regra 7 cobre só o *Objetivo*, que é a menor metade. Numa
medição real, o *Objetivo* das 12 funções somou 508 tokens e as *Condições*, 2.303.

**Onde cada regra mora, para não pagar duas vezes:**

| Conteúdo | Lugar |
| --- | --- |
| Ordem do fluxo, travas, tratamento de retorno, política de falha, mensagens-modelo | **Diretrizes de atendimento**, uma vez |
| Trava daquela chamada, parâmetros e formato, a proibição própria daquela função | **Condições de execução** da função |
| Racional, justificativa, "por que esta regra existe" | **Relatório**, nunca no prompt |

Replicar o detalhe operacional por função inflou o sempre-ativo em **67%** na primeira tentativa da
referência. Não repetir `FUNÇÃO: nome` no topo do campo: a plataforma já sabe de qual função ele é.

**Esperar paridade, não economia.** De-duplicar libera orçamento; regra explícita consome mais do que a
de-duplicação libera. Um prompt menor costuma ser um prompt incompleto.

---

## 12. Preparo do exame: fora de escopo por padrão

Nenhuma função devolve preparo. O agente **não responde** preparo: a dúvida é demanda de repasse.

**Por que o padrão é o seguro:** preparo errado faz o paciente perder o exame. Proibido redigir, deduzir ou
repetir de memória orientação de jejum, medicação ou bexiga cheia. Só entra em escopo se o cliente contratou
e você souber em **qual retorno** o texto vem — e então é repassado **literalmente**.

---

## 13. Card do atendente: o mínimo para entender e continuar

`clienteinfo.json` serve **um** caso: o agente não conseguiu agendar e transbordou. Levar só o que o atendente
precisa para retomar de onde o paciente parou.

**Critérios de corte, com o motivo:**

- **Sem ID interno.** O atendente localiza o paciente pelo CPF, não por código.
- **Sem campo estruturalmente vazio no cenário do card.** O número do agendamento é o exemplo: se ele existe,
  não houve transbordo — o campo estaria vazio em 100% dos cards.
- **Sem anexo.** Quando o paciente envia, o arquivo já está visível na conversa.
- **O par digitado + localizado:** manter o **digitado**. No caso de falha mais comum — convênio não
  localizado — o campo localizado volta vazio, e é o digitado que carrega o que o paciente disse.
- **CPF completo, não mascarado.** A máscara vale para o chat, onde o paciente lê. O card é interno.
- **`RESUMO` é obrigatório antes de todo transbordo** e é o título do card. Sem ele o atendente recebe um
  cartão sem contexto justamente no atendimento que já falhou.

Estar declarada no registro de variáveis **não** significa entrar no card.

---

## 14. Consentimento LGPD: a montante

O consentimento é obtido **antes** do agente. O agente não tem, e não deve ganhar, etapa de consentimento — a
Regra 14 do projeto não se aplica a esta categoria. Confirmar por cliente, mas não reintroduzir por herança
do Pré Agendamento.
