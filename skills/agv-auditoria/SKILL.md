---
name: agv-auditoria
description: Use somente quando o usuário pedir explicitamente a auditoria ou revisão de um agente virtual já criado, nomeando o cliente. Propõe um plano de correção e não aplica alterações. Não usar para criar agente novo.
argument-hint: "[cliente]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
metadata:
  version: "3.0.0"
---

# Auditar Agente Virtual

Audita a configuração de um agente virtual em cinco dimensões — **Fluxo · Lógica · Segurança · Conduta ·
Eficiência** — e entrega um plano de correção aprovável.

**Diagnóstico e proposta. Não aplica.** A separação entre auditar e escrever é o que impede uma auditoria de
"consertar" um config correto para satisfazer um falso positivo.

## Esta skill é autocontida

Todos os critérios estão aqui. **Não** consulte convenções externas nem a configuração de outro cliente. Se
houver convenções externas e elas **contradisserem** este arquivo, pare e diga qual é a divergência.

## Cada regra tem critério de violação — julgue, não apenas observe

Uma medição real mostrou o defeito que esta versão corrige: sem o critério, o auditor sabe *que* algo deve
existir mas não *como* deve ser, então reporta como observação em vez de achado. Ele escreveu:

> *"Sei que exige mascaramento de CPF, não sei o formato. Verifiquei só presença/ausência."*

A regra de mascaramento não existe mais, mas o modo de falha é o mesmo em qualquer critério: sem o limiar
escrito junto, a verificação degrada para presença/ausência sem ninguém perceber.

Por isso cada linha das tabelas abaixo traz **o que verificar** e **o que conta como violação**. Sem os dois,
o achado não é acionável e vira discussão.

## O modelo alvo

Os agentes auditados aqui rodam em **`gpt-5.4-nano`**, com `reasoning_effort` em `none`. É a mesma premissa
sob a qual as skills de criação escrevem, e ela muda o que conta como defeito:

- **Borda não escrita é comportamento inventado.** Modelo pequeno não infere o passo que falta — improvisa.
  Uma borda implícita num agente frontier é folga; aqui é bug.
- **Saída fechada é controle.** Enum, template literal e tabela de decisão são as únicas restrições
  estruturais disponíveis — a plataforma não expõe `allowed_tools`, `reasoning_effort` nem modo strict.
  Afrouxar um enum para acomodar um valor é remover o último controle que não depende de o modelo obedecer.
- **Prompt mais explícito não é prompt inchado.** Não reporte como excesso a redundância que existe para
  fechar uma borda.

**Se o modelo mudar, revise esta seção antes de aplicar critério nenhum.**

## O contrato do runtime — o que chega ao modelo

Sem esta tabela não há como separar defeito de runtime de defeito apenas documental, e a auditoria reporta
os dois com a mesma gravidade:

| Artefato | Campo da plataforma | Chega ao modelo |
| --- | --- | --- |
| As 4 seções de `config/agente.md` | Perfil · Diretrizes · Conduta · Segurança | **sempre-ativo** |
| §1 do manual | **Objetivo da Função** | **sempre-ativo** |
| §2 do manual | **Condições de Execução** | **sempre-ativo** |
| Schema da função — nome, parâmetros, `description` de cada um | cadastro da função | **sempre-ativo** |
| JSON de `ferramentas/dados/` | retorno da função | só no turno da chamada |
| `config/clienteinfo.json` | outro módulo | **nunca** — é a tela da atendente humana |
| `origem/`, `relatorios/` | — | **nunca** |

Sempre-ativo é pago em **todos** os turnos, inclusive naqueles em que nenhuma função é chamada. **As duas
seções do manual são sempre-ativas**, e regra duplicada entre o prompt e a §2 custa token de verdade, não só
deriva. Uma medição feita sob a premissa antiga — a de que a §2 era documentação — subestima o custo do
agente por uma §2 inteira vezes o número de funções.

## Localizar o cliente

**Não há caminho fixo.** Descubra a pasta do cliente procurando aquela que contém `config/agente.md`:

```bash
find . -type d -name "$ARGUMENTS" | while read -r d; do [ -f "$d/config/agente.md" ] && echo "$d"; done
```

Mais de um resultado: confirme qual antes de seguir. Nenhum: diga isso e pare.

---

## Passo 0 — Determinar a categoria. **Antes** de aplicar critério nenhum.

Há dois tipos de agente neste workspace, e **metade dos critérios abaixo só vale para um deles**. Aplicar os
critérios errados produz ruído de alta gravidade num relatório que se vende por acionabilidade.

```bash
# Categoria: a presença da base estática é o sinal primário
ls ferramentas/dados/*.json 2>/dev/null | wc -l     # 0 => Integrado, >0 => Base de conhecimento

# confirmação pelo nome das variáveis
grep -oE '__[A-Z0-9_]+__' config/variaveis.md | head -3   # casou => Base de conhecimento
```

**Contar seções do manual não distingue mais as categorias** — as duas têm 2 seções, `Objetivo da Função` e
`Condições de Execução`, que são os nomes dos campos da plataforma. Manual com 3 seções, ou com os rótulos
antigos (`Descrição da Função`, `Diretrizes de Prompt`, `Exemplos Práticos de Diálogos`), é agente escrito
sob a convenção anterior: reportar como achado de migração, não como sinal de categoria.

| Sinal | **Base de conhecimento** | **Integrado** |
|---|---|---|
| `ferramentas/dados/*.json` | existe | **não existe** |
| Nome de variável | `__IA_CAMPO__` | **nome do parâmetro do endpoint** (`EMPRESA_ID`, `CPF_DIGITADO`) |
| Sentinelas de ausência | três estados obrigatórios | **proibidas** em campo obrigatório — retém a chamada e pergunta |
| Fim do caminho feliz | transbordo | **gravação no sistema** |
| Retorno vazio | pode indicar ausência na base | **nunca** indica ausência — só a lista de exclusão autoriza negar |

**Declare a categoria detectada no início do relatório.** Onde um critério estiver marcado *(só Base de
conhecimento)* abaixo, **não o aplique** a um agente Integrado — e vice-versa. Na dúvida sobre a categoria,
pergunte; não escolha em silêncio.

---

## Passo 1 — Ler tudo antes de julgar qualquer coisa

`config/agente.md` · `config/variaveis.md` · `config/clienteinfo.json` · todos os
`ferramentas/manuais/*.md` · todos os `ferramentas/dados/*.json` **quando existirem**.

**Auditoria parcial produz achado falso.** Metade dos defeitos deste tipo de agente é contradição *entre*
arquivos — o prompt diz uma coisa e o manual diz outra. Só se enxerga lendo os dois.

---

## Passo 2 — As cinco dimensões, com critério

### Fluxo

| Verificar | Violação |
| --- | --- |
| *(só Base de conhecimento)* Toda trilha termina executando a função de transbordo | Trilha que encerra sem executar. **Única exceção:** recusa de consentimento antes de qualquer coleta. Num agente **Integrado** o caminho feliz termina em **gravação**, não em transbordo — não reportar como violação |
| *(só Base de conhecimento)* A trilha de informação resolvida **também** executa | "Dúvida sanada → encerrar sem acionar" — deixa a automação de fechamento sem gatilho |
| Instrução manda **executar**, não anunciar | "Informe que está sendo encaminhado" sem a execução na mesma resposta |
| Resumo confirmado **uma vez**, antes de executar | O agente confirma os dados coletados e executa no turno em que a confirmação chega. **Violação:** transbordar sem confirmar nada; ou pedir uma segunda confirmação, ou confirmar **depois** de a função já ter rodado — aí ele para num estado que nenhum passo resolve |
| Nenhuma despedida ou aviso de transferência no prompt | "Vou transferir você para a nossa equipe agora" escrito no conteúdo de prompt. Quem envia a mensagem de encerramento ou transferência é a **plataforma**, depois da chamada, derivando-a das variáveis. Prompt que a escreve produz três defeitos: promete atendente na trilha resolvida, duplica a mensagem da plataforma, e diverge de si mesmo quando o texto aparece em mais de um lugar |
| Perguntas agrupadas em blocos relacionados | Uma pergunta por mensagem onde os campos pertencem ao mesmo bloco. A cobrança do WhatsApp é por mensagem: cada pergunta isolada é custo de canal sem ganho de precisão. **Exceção:** menu numerado, onde a escolha é uma por vez |
| Fluxo cabe na meta de interações | Caminho mais longo acima da meta declarada, ou meta não declarada. Contar as mensagens do agente da saudação até o transbordo |
| Mudança de demanda reclassifica | Nada define o que acontece quando o usuário troca de assunto no meio. A nova demanda herda fila, qualificação ou item de interesse da anterior, e o atendente recebe um caso coerente com a conversa errada |
| Modalidade de pagamento antes do convênio | Domínio com convênio ou plano sem bifurcação convênio × particular. Quem não tem convênio esgota as tentativas e é gravado como `"Não Informado"` — que significa **recusou informar**, não "não tem" |
| Toda demanda tem destino | Valor de intenção sem trilha, ou trilha sem fila |
| Fallback de intenção não reconhecida existe | Borda implícita: nada define o que fazer com valor vazio ou fora do ENUM |
| Trilha de repasse coleta o mínimo | Triagem cadastral completa para demanda que só será repassada |
| Passo não repergunta dado já dado | Passo de coleta sem cláusula própria de "se já informado, preencher sem perguntar". **Regra genérica no cabeçalho do fluxo não conta** — medida em produção: existia, e o agente ainda assim reperguntou se era agendamento ou dúvida depois de o usuário abrir com "quero agendar uma acupuntura" |
| Lista de opções filtrada pelo que se aplica | Instrução manda listar o conjunto fixo (as N unidades, todos os turnos) quando o item já identificado restringe o conjunto — ou o agente reabre como pergunta um fato que ele mesmo afirmou turnos antes. Oferece escolha que será negada depois, e o usuário percebe |

### Lógica

| Verificar | Violação |
| --- | --- |
| Toda variável declarada tem algo que a preencha | Variável em `variaveis.md` sem passo de coleta nem menção no prompt. **Controle** (fila, resolução, trilha) precisa do token nomeado; **coleta** basta em prosa |
| Variável e card batem | Token em `variaveis.md` ausente do `clienteinfo.json`, ou o inverso — chega vazia ao atendente |
| Arrays do card pareados | Rótulos e tokens com tamanhos diferentes no mesmo bloco — desalinha em silêncio |
| Grafia de fila consistente | Mesma fila escrita diferente entre `agente.md`, `variaveis.md` e o manual de transbordo. **Comparar entre os arquivos do cliente**, nunca contra uma lista padrão — o cliente pode ter filas próprias |
| Sentinela declarada no `enum` | Campo com `enum`/`pattern`/`format` recebendo `"Não coletado"` — a chamada é descartada **em silêncio**. A correção é acrescentar a sentinela ao `enum`, **não** trocar o campo por string livre: num agente que roda em modelo pequeno, o enum é a única restrição estrutural disponível. Schema afrouxado para acomodar sentinela é defeito |
| Só o universal é `required` | Campo que trilhas sem coleta não preenchem marcado como obrigatório |
| *(só Base de conhecimento)* Função anunciada existe na base | Prompt cita serviço, exame ou item que o `get_*` não retorna |
| *(só Integrado)* Toda negativa está ancorada | "Não realiza X" sem lista de exclusão explícita. Retorno vazio **não** autoriza negar: significa "não veio", não "não existe" |
| Tolerância fuzzy limitada à mesma entidade | Aproximação entre entidades diferentes (Tomografia/Angiotomografia). Em dúvida, falhar fechado |
| *(só Base de conhecimento)* Sem valor ambíguo nos dados | `[]` onde o sentido é "todos" — é lido como "nenhum". Sentinela explícita (`["Todos"]`) |
| Sem curinga que anula proibição | Item tipo `"Outros"` que autoriza afirmar disponibilidade do que o prompt proíbe |
| Todo dado coletado tem consumidor | Passo de coleta cujo dado não vira parâmetro de função nem campo do card. Separar **orientação geral** ("quais são os canais") de **consulta individual** ("qual é o meu resultado"): a primeira não precisa de identificador. Pedir documento para uma função que devolve o mesmo texto para todo mundo faz a função parecer uma consulta autenticada que ela não é |

### Segurança

| Verificar | Violação |
| --- | --- |
| *(só Base de conhecimento)* Três estados de ausência distintos | Mesmo texto para os três. `"Não Informado"` = recusou o que foi perguntado · `"Não coletado"` = nunca foi perguntado · `"Não se aplica"` = a trilha deliberadamente não pede |
| *(só Integrado)* Nenhuma sentinela em campo obrigatório | Valor de reserva em parâmetro de endpoint. O endpoint responde **vazio**, e o vazio vira "não há resultado" — o bug se disfarça de indisponibilidade. Faltando o dado real, o agente **retém a chamada** e pergunta |
| Consentimento antes do primeiro dado pessoal | Ausente **quando a plataforma não trata upstream**. A frase é curta, vem antes do primeiro dado, e aguarda resposta; recusa encerra cordialmente **sem transbordo**. "Justificar sob a ótica da LGPD" não é consentimento |
| Limite de atuação em domínio regulado | Saúde, jurídico ou financeiro sem regra de "sem aconselhamento [domínio]" — obrigatória mesmo que o cliente não peça |
| Nunca deduzir parâmetro | Instrução que permite supor documento, convênio ou item não informado |
| Confidencialidade não bloqueia preenchimento | Regra que impede preencher código interno nos parâmetros. Ele não é exibido, mas é sempre preenchido |
| Transparência sobre ser agente virtual | Nenhuma instrução sobre isso |

### Conduta

| Verificar | Violação |
| --- | --- |
| Negrito com um asterisco | Instrução usando `**texto**`. O WhatsApp só interpreta `*texto*`; `**` aparece literal. **Exceção:** o card do atendente é markdown de painel — ali `**` é correto |
| Formato interno coerente | Limite de caracteres por mensagem incompatível com listas verticais, emojis ou resumo longo exigidos na mesma seção |
| Saudação definida | Prompt exige "saudação institucional" que não está escrita em lugar nenhum |
| Seções agrupadas | Conduta ou segurança com 5+ itens em lista única, sem subtítulos temáticos |
| Personalidade com regra operacional | §1 declara um traço ("empática", "acolhedora") sem nenhuma regra em Conduta que o produza |

### Eficiência

| Verificar | Violação |
| --- | --- |
| Nenhum dado factual chumbado no prompt | Endereço, horário, preço ou lista que a função retorna, repetidos no sempre-ativo |
| Número de funções justificado pela conta dos dois lados | **Fundir economiza** uma §1 + §2 + schema por turno, em todos os turnos. **Fundir custa** carregar o JSON da outra em toda chamada isolada — a plataforma devolve o arquivo cheio, sem filtro por parâmetro. **Violação:** duas funções quase sempre acionadas juntas e ambas com base pequena, mantidas separadas; **ou** uma base grande fundida a uma pequena, fazendo toda consulta à pequena pagar as duas. Não reportar fusão de assunto genuinamente distinto: função raramente acionada é carga preguiçosa, e separá-la é o desenho certo |
| Descrição de função e de parâmetro sem conduta | Regra de comportamento na §1 ou na `description` de um parâmetro — sempre-ativo duplicando o prompt |
| Regra geral de dados declarada uma vez | Repetição de "não memorizar" a cada item, ou duas declarações do mesmo princípio |
| Sem duplicação entre prompt e manual | Tabela ou regra verbatim nos dois. Custa **token** — a §2 é sempre-ativa — e custa **deriva**: a próxima correção vai num lado só. Regra que vale para o fluxo inteiro fica no prompt; regra de leitura do retorno daquela função fica na §2 |
| *(só Base de conhecimento)* Um assunto, um arquivo dono | Mesmo fato em dois JSONs de dados |
| Descrição de função ≤ 950 caracteres | §1 acima do teto — é pago em 100% dos turnos. A §2 **não** tem teto duro, mas entra na medição do sempre-ativo |
| Manual com exatamente 2 seções, nomeadas pelos campos | `## 1. Objetivo da Função` · `## 2. Condições de Execução`, nas duas categorias. Seção a mais — tipicamente "Exemplos Práticos de Diálogos" ou "Tool Specification"/JSON Schema — não tem campo onde ser colada. Rótulo antigo é achado de migração |
| Prompt com exatamente 4 seções `##` | Quinta seção — a tela da plataforma tem quatro campos, e a quinta não tem onde ser colada |
| Sem caminho de arquivo no prompt | `config/agente.md`, `§2` ou nome de pasta citados no conteúdo que vira prompt |
| Markdown estrutura o prompt, nunca XML | Tags XML (`<perfil>`, `<etapa>`, `<regras>`, `<item>`) estruturando `config/agente.md` ou o bloco de diretrizes de um manual. Medido nos agentes existentes: trocar os headers markdown por tags custa **+217 tokens por turno por agente** (+5% do campo), sem ganho documentado — e o que o XML delimitaria, a plataforma já delimita, porque os 4 campos são entradas separadas. A documentação do modelo não prescreve formato; os blocos XML dos exemplos dela são orquestração multi-etapa de modelo frontier, não este caso |

---

## Passo 3 — Verificações mecânicas

Rode, não estime. Cada uma já pegou defeito real:

```bash
# seções do prompt (esperado 4) — as duas categorias
grep -c '^## ' config/agente.md

# manuais fora do padrão — esperado 2 nas duas categorias
for f in ferramentas/manuais/*.md; do echo "$(grep -c '^## ' "$f") $f"; done

# rótulo antigo de seção — achado de migração, não de categoria
grep -rln 'Descrição da Função\|Diretrizes de Prompt\|Exemplos Práticos' ferramentas/manuais/

# seção de schema que não deveria existir — as duas categorias
grep -rl 'Tool Specification' ferramentas/manuais/

# despedida ou aviso de transferência escrito no prompt — quem envia é a plataforma
grep -niE 'vou (te )?transferir|estou (te )?encaminhando|vou encerrar|ate logo|até logo' config/agente.md

# variável declarada e ausente do card — as duas categorias
# o regex NÃO pode ancorar em `IA_`: num agente Integrado as variáveis são
# nomes de parâmetro de endpoint, e ancorar em IA_ faz os dois lados voltarem
# vazios — a checagem passa sem ter verificado nada (falso negativo silencioso).
comm -23 <(grep -oE '^\| `_{0,2}[A-Z][A-Z0-9_]+_{0,2}`' config/variaveis.md | grep -oE '[A-Z][A-Z0-9_]+' | sed 's/_*$//' | sort -u) \
         <(grep -oE '[A-Z][A-Z0-9_]{2,}' config/clienteinfo.json | sed 's/_*$//' | sort -u)

# negrito duplo no que vira prompt — as duas categorias
grep -c '\*\*' config/agente.md

# caminho de arquivo citado no prompt — as duas categorias
grep -nE 'config/|ferramentas/|§[0-9]' config/agente.md

# formato do prompt: markdown, nunca XML — as duas categorias
# qualquer acerto aqui é violação: o conteúdo que vira prompt se estrutura
# com headers markdown, não com tags. Cobre o prompt e os manuais.
grep -nE '</?[a-zA-Z_][a-zA-Z0-9_-]*>' config/agente.md ferramentas/manuais/*.md

# valor ambíguo nos dados — SÓ Base de conhecimento
[ -d ferramentas/dados ] && grep -n '\[\]\|null' ferramentas/dados/*.json

# card é JSON válido — as duas categorias
python -c "import json;json.load(open('config/clienteinfo.json',encoding='utf-8'))"

# toda negativa do prompt está ancorada — SÓ Integrado
# (num agente Integrado, "não realiza" só pode vir de lista de exclusão explícita)
grep -nE 'não realiza|não atende|não oferece' config/agente.md
```

---

## Passo 4 — Classificar, e separar achado de observação

**Gravidade:**

| | Critério |
| --- | --- |
| **Crítico** | Quebra o atendimento em produção: chamada descartada, transbordo sem destino, dado sensível exposto |
| **Alto** | Produz resposta errada ou perde conversão: nega o que a clínica faz, afirma o que não pode |
| **Médio** | Custo, duplicação, inconsistência que ainda não quebrou |
| **Baixo** | Higiene |

**Procedência**, declarada ao lado da gravidade. São três, e elas não se misturam:

| | O que é | Como escrever |
| --- | --- | --- |
| **Observado** | Está no arquivo, e você cita a linha. Contradição entre dois arquivos entra aqui | "`agente.md:33` obriga X; `variaveis.md:18` exige Y" |
| **Inferido** | O arquivo permite o defeito, mas você não viu acontecer | "pode produzir", "fica indeterminado" — nunca "o agente faz" |
| **Reproduzido** | Alguém rodou e viu. Só use quando houver conversa, log ou teste | "medido em produção: o agente reperguntou..." |

*Motivo:* sem isso os três viram "Alto", e o cliente não sabe qual foi visto e qual foi deduzido. Risco
inferido relatado como incidente comprovado queima a credibilidade do relatório inteiro na primeira vez que
alguém confere.

**Achado ≠ observação.** Se você não tem o critério para julgar, é observação — diga isso em vez de reportar
como violação. Auditoria que classifica dúvida como defeito faz o cliente corrigir o que estava certo.

**Decisão deliberada não é defeito.** Antes de reportar, verifique se há registro de que é intencional. Uma
assimetria entre trilhas costuma ser regra de negócio, não descuido.

---

## Passo 5 — Entregar o plano

Ordenado do mais grave para o menos. Cada item com:

1. **O defeito**, em uma frase
2. **Arquivo e evidência** — a linha, a contagem, o trecho — com a **procedência**: observado, inferido ou
   reproduzido
3. **O efeito em produção** — o que o usuário ou o atendente sente
4. **A correção proposta**

Feche com o que **não** foi possível julgar por falta de critério ou de informação do cliente.

**Não aplique nenhuma alteração até confirmação explícita.** Depois do aceite, as correções são pedidas em
conversa — esta skill não escreve no cliente.

---

## Common Mistakes

| Erro | Correção |
| --- | --- |
| Auditar só o `agente.md` | Metade dos defeitos é contradição entre prompt e manual |
| Reportar observação como violação | Sem critério, é observação. Dizer isso é informação útil |
| Tratar assimetria como descuido | Costuma ser regra de negócio. Verificar antes |
| Comparar filas com uma lista padrão | Auditar a coerência **entre os arquivos do cliente** |
| Achado sem evidência | Linha, contagem ou trecho — senão vira discussão |
| Risco inferido escrito como incidente | Declarar a procedência. "Pode produzir" e "o agente faz" não são a mesma frase |
| Medir o sempre-ativo sem as §2 | As duas seções do manual são campos da plataforma. Fora da conta, o custo do agente sai subestimado |
| Achado sem efeito em produção | "Viola a convenção" não move ninguém; "o atendente recebe vazio" move |
| Aplicar a correção | Esta skill propõe. A aplicação é pedida depois |

## Changelog

- **3.0.0** — **Corrigido o contrato do runtime, e com ele sete critérios.** A §2 do manual é sempre-ativa —
  é o campo `Condições de Execução` da plataforma —, e não documentação como as skills afirmavam. Entram a
  tabela do contrato do runtime e a declaração do modelo alvo, que a auditoria não tinha: ela julgava sem
  saber para qual modelo o prompt fora escrito, a mesma lacuna que a 2.2.0 fechou para o formato XML.
  **Dois critérios foram invertidos:** pedir confirmação dos dados antes de executar era classificado como
  defeito e é o comportamento correto — o defeito real, preservado, é confirmar *depois* da execução ou
  pedir uma segunda confirmação; e "exemplo de diálogo é few-shot e vence a regra" saiu, porque exemplo de
  manual nunca chegou ao modelo e a seção de exemplos deixou de existir. **Um critério foi removido:** o
  mascaramento de documento, que o cliente descontinuou. Entram critérios para despedida escrita no prompt,
  blocos de perguntas relacionadas com meta de interações, mudança de demanda, modalidade de pagamento,
  coleta sem consumidor, e a conta de fusão de funções com os dois lados. A contagem de seções deixou de
  distinguir as categorias — as duas têm 2 — e virou achado de migração.
- **2.2.0** — Critério de formato de prompt: markdown estrutura, nunca XML. A regra e a medição (+217 tokens por turno por agente) já existiam nas skills de criação desde a adequação ao gpt-5.4-nano, mas não haviam chegado à auditoria — um agente podia ser criado sob a regra e auditado sem ela. Baseline com 3 repetições sobre um cliente-fixture cujo prompt inteiro era XML: **0 de 3** apontaram o formato, e **3 de 3** acharam o defeito-controle plantado na mesma seção, provando que auditaram e que a lacuna era de critério, não de atenção.
- **2.1.0** — Passo 0: determinar a categoria do agente antes de aplicar critério. Metade dos critérios só vale para agentes com base de conhecimento, e aplicá-los a um agente integrado produzia ruído de alta gravidade. Corrigido um **falso negativo silencioso**: a checagem de variável ausente do card ancorava o regex em `IA_`, e num agente integrado — onde as variáveis são nomes de parâmetro de endpoint — os dois lados voltavam vazios e a verificação passava sem ter verificado nada. Critério de sentinela alinhado à R21 do modelo estático.
- **2.0.0** — Autocontida e estruturada. Antes eram 934 palavras de prosa com **dois cabeçalhos** e 15 regras
  citadas por número de um documento externo. Numa medição com esse documento fora de alcance, a skill ainda
  achou 22 defeitos — porque trazia glosa inline —, mas em 5 regras a glosa era insuficiente e o auditor
  **observou sem julgar**: *"sei que exige mascaramento de CPF, não sei o formato"*. Agora cada verificação
  traz o critério de violação junto, as cinco dimensões viraram tabelas, e o Passo 3 acrescenta as
  verificações mecânicas que pegaram defeito real.
- **1.0.0** — Versão inicial.
