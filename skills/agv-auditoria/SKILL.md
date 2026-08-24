---
name: agv-auditoria
description: Use somente quando o usuário pedir explicitamente a auditoria ou revisão de um agente virtual já criado, nomeando o cliente. Propõe um plano de correção e não aplica alterações. Não usar para criar agente novo.
argument-hint: "[cliente]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
metadata:
  version: "2.0.0"
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

Por isso cada linha das tabelas abaixo traz **o que verificar** e **o que conta como violação**. Sem os dois,
o achado não é acionável e vira discussão.

## Localizar o cliente

**Não há caminho fixo.** Descubra a pasta do cliente procurando aquela que contém `config/agente.md`:

```bash
find . -type d -name "$ARGUMENTS" | while read -r d; do [ -f "$d/config/agente.md" ] && echo "$d"; done
```

Mais de um resultado: confirme qual antes de seguir. Nenhum: diga isso e pare.

---

## Passo 1 — Ler tudo antes de julgar qualquer coisa

`config/agente.md` · `config/variaveis.md` · `config/clienteinfo.json` · todos os
`ferramentas/manuais/*.md` · todos os `ferramentas/dados/*.json`.

**Auditoria parcial produz achado falso.** Metade dos defeitos deste tipo de agente é contradição *entre*
arquivos — o prompt diz uma coisa e o manual diz outra. Só se enxerga lendo os dois.

---

## Passo 2 — As cinco dimensões, com critério

### Fluxo

| Verificar | Violação |
| --- | --- |
| Toda trilha termina executando a função de transbordo | Trilha que encerra sem executar. **Única exceção:** recusa de consentimento antes de qualquer coleta |
| A trilha de informação resolvida **também** executa | "Dúvida sanada → encerrar sem acionar" — deixa a automação de fechamento sem gatilho |
| Instrução manda **executar**, não anunciar | "Informe que está sendo encaminhado" sem a execução na mesma resposta |
| Resumo antes do transbordo é informativo | "Exibir para confirmação" — o agente para e espera um segundo "sim" que ninguém trata |
| Exemplo de diálogo concorda com a regra | Diálogo com "Confirma para mim:" — few-shot vence regra escrita acima dele |
| Toda demanda tem destino | Valor de intenção sem trilha, ou trilha sem fila |
| Fallback de intenção não reconhecida existe | Borda implícita: nada define o que fazer com valor vazio ou fora do ENUM |
| Trilha de repasse coleta o mínimo | Triagem cadastral completa para demanda que só será repassada |

### Lógica

| Verificar | Violação |
| --- | --- |
| Toda variável declarada tem algo que a preencha | Variável em `variaveis.md` sem passo de coleta nem menção no prompt. **Controle** (fila, resolução, trilha, observações) precisa do token nomeado; **coleta** basta em prosa |
| Variável e card batem | Token em `variaveis.md` ausente do `clienteinfo.json`, ou o inverso — chega vazia ao atendente |
| Arrays do card pareados | Rótulos e tokens com tamanhos diferentes no mesmo bloco — desalinha em silêncio |
| Grafia de fila consistente | Mesma fila escrita diferente entre `agente.md`, `variaveis.md` e o manual de transbordo. **Comparar entre os arquivos do cliente**, nunca contra uma lista padrão — o cliente pode ter filas próprias |
| Sentinela compatível com o schema | Campo condicional com `enum`/`pattern`/`format` recebendo `"Não coletado"` — a chamada é descartada **em silêncio** |
| Só o universal é `required` | Campo que trilhas sem coleta não preenchem marcado como obrigatório |
| Função anunciada existe na base | Prompt cita serviço, exame ou item que o `get_*` não retorna |
| Tolerância fuzzy limitada à mesma entidade | Aproximação entre entidades diferentes (Tomografia/Angiotomografia). Em dúvida, falhar fechado |
| Sem valor ambíguo nos dados | `[]` onde o sentido é "todos" — é lido como "nenhum". Sentinela explícita (`["Todos"]`) |
| Sem curinga que anula proibição | Item tipo `"Outros"` que autoriza afirmar disponibilidade do que o prompt proíbe |

### Segurança

| Verificar | Violação |
| --- | --- |
| Documento mascarado ao ecoar no chat | CPF exibido inteiro. **Formato: `***.***.XXX-XX`** — últimos 5 dígitos visíveis. Ausente ou em outro formato é violação |
| Três estados de ausência distintos | Mesmo texto para os três. `"Não Informado"` = recusou o que foi perguntado · `"Não coletado"` = nunca foi perguntado · `"Não se aplica"` = a trilha deliberadamente não pede |
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
| Regra geral de dados declarada uma vez | Repetição de "não memorizar" a cada item, ou duas declarações do mesmo princípio |
| Sem duplicação entre prompt e manual | Tabela ou regra verbatim nos dois. O custo não é token, é **deriva**: a próxima correção vai num lado só |
| Um assunto, um arquivo dono | Mesmo fato em dois JSONs de dados |
| Descrição de função ≤ 950 caracteres | §1 acima do teto — é pago em 100% dos turnos |
| Manual com exatamente 3 seções | Quarta seção, tipicamente "Tool Specification"/JSON Schema. Ela desloca a numeração e joga as diretrizes para fora do lugar esperado |
| Prompt com exatamente 4 seções `##` | Quinta seção — a tela da plataforma tem quatro campos, e a quinta não tem onde ser colada |
| Sem caminho de arquivo no prompt | `config/agente.md`, `§2` ou nome de pasta citados no conteúdo que vira prompt |

---

## Passo 3 — Verificações mecânicas

Rode, não estime. Cada uma já pegou defeito real:

```bash
# seções do prompt (esperado 4)
grep -c '^## ' config/agente.md

# manuais fora do padrão de 3 seções
for f in ferramentas/manuais/*.md; do echo "$(grep -c '^## ' "$f") $f"; done

# seção de schema que não deveria existir
grep -rl 'Tool Specification' ferramentas/manuais/

# variável declarada e ausente do card
comm -23 <(grep -oE '__IA_[A-Z_]+__' config/variaveis.md | sort -u) \
         <(grep -oE '__IA_[A-Z_]+__' config/clienteinfo.json | sort -u)

# negrito duplo no que vira prompt
grep -c '\*\*' config/agente.md

# caminho de arquivo citado no prompt
grep -nE 'config/|ferramentas/|§[0-9]' config/agente.md

# valor ambíguo nos dados
grep -n '\[\]\|null' ferramentas/dados/*.json

# card é JSON válido
python -c "import json;json.load(open('config/clienteinfo.json',encoding='utf-8'))"
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

**Achado ≠ observação.** Se você não tem o critério para julgar, é observação — diga isso em vez de reportar
como violação. Auditoria que classifica dúvida como defeito faz o cliente corrigir o que estava certo.

**Decisão deliberada não é defeito.** Antes de reportar, verifique se há registro de que é intencional. Uma
assimetria entre trilhas costuma ser regra de negócio, não descuido.

---

## Passo 5 — Entregar o plano

Ordenado do mais grave para o menos. Cada item com:

1. **O defeito**, em uma frase
2. **Arquivo e evidência** — a linha, a contagem, o trecho
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
| Achado sem efeito em produção | "Viola a convenção" não move ninguém; "o atendente recebe vazio" move |
| Aplicar a correção | Esta skill propõe. A aplicação é pedida depois |

## Changelog

- **2.0.0** — Autocontida e estruturada. Antes eram 934 palavras de prosa com **dois cabeçalhos** e 15 regras
  citadas por número de um documento externo. Numa medição com esse documento fora de alcance, a skill ainda
  achou 22 defeitos — porque trazia glosa inline —, mas em 5 regras a glosa era insuficiente e o auditor
  **observou sem julgar**: *"sei que exige mascaramento de CPF, não sei o formato"*. Agora cada verificação
  traz o critério de violação junto, as cinco dimensões viraram tabelas, e o Passo 3 acrescenta as
  verificações mecânicas que pegaram defeito real.
- **1.0.0** — Versão inicial.
