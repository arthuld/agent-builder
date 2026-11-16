# Suíte de evals

Troca o teste em cliente real por clientes **inventados**, com critérios escritos uma vez. Mudou uma skill,
roda um comando, lê aprovado/reprovado por critério.

Nenhum dado de cliente real entra aqui: todo fixture e todo briefing foram escritos para esta suíte.

## Rodar

### No dia a dia — só a skill que mudou

Uma execução por caso, só com a skill. Dinâmica, estática ou clinux:

```bash
claude plugin eval . --tag dinamico --runs 1 --ablation none --allow-tools Write Edit --judge-model claude-sonnet-5-5 --trust-plugin --no-publish
```

Troque `--tag dinamico` por `estatico` ou `clinux`. Auditoria, que não escreve arquivo mas precisa do
scaffold:

```bash
claude plugin eval . --tag auditoria --runs 1 --ablation none --scaffold --judge-model claude-sonnet-5-5 --trust-plugin --no-publish
```

### Antes de publicar versão nova do plugin — completa

Três execuções por caso, todas as suítes, quatro de cada vez:

```bash
claude plugin eval . --tag dinamico estatico auditoria clinux --runs 3 --ablation none -j 4 --scaffold --allow-tools Write Edit --judge-model claude-sonnet-5-5 --threshold 0.9 --trust-plugin --no-publish
```

### Quando mudar um critério — calibração

```bash
claude plugin eval . --tag calibracao --runs 1 --ablation none -j 4 --scaffold --judge-model claude-sonnet-5-5 --trust-plugin --no-publish
```

Coloca no workspace arquivos **conhecidos** — um certo e vários estragados de propósito, cada um com um
defeito — e confere que cada critério aprova o certo e reprova o estragado. É a prova de que o critério
consegue falhar. Resultado esperado:

| Caso | Critério | Esperado |
| --- | --- | --- |
| `calib-din-certo` | 13b e 15 | aprova os dois |
| `calib-din-sem-execucao` | — | Sem critério desde 11/2026: o 13a, que cobria "toda trilha executa", foi retirado (ver abaixo) |
| `calib-din-confirma-depois` | 15 | **reprova** — executa antes de confirmar |
| `calib-din-fila-errada` | 13b | **reprova** — convênio fora da base vai para a fila errada |
| `calib-est-certo` | 13 | aprova |
| `calib-est-fila-errada` | 13 | **reprova** — a opção 2 vai para a fila errada |
| `calib-aud-fraca` | 02 a 07 | **reprova os seis** — auditoria genérica, com três falsos positivos e sem os critérios de 11/2026 |
| `calib-aud-boa` | 02 a 07 | **aprova todos**: auditoria real da v3.2.0. Prova que os critérios não reprovam uma resposta correta |

Se um caso que devia reprovar aprovar, o critério ficou leniente e a suíte não está provando nada.

### Por que cada opção

| Opção | Por quê |
| --- | --- |
| `--judge-model claude-sonnet-5-5` | **Obrigatória.** O juiz padrão é o `claude-haiku-4-5`, e ele reprova resposta correta sempre que o critério exige raciocinar sobre um texto longo inteiro: reprovou duas auditorias que continham todos os defeitos plantados, e os critérios de fluxo das duas skills de criação. Medido. Esquecer a opção traz os falsos negativos de volta |
| `--allow-tools Write Edit` | As skills de criação escrevem arquivos. **Nunca** `Bash`: no Windows a ferramenta recusa a rodada, porque não há sandbox para o terminal |
| `--scaffold` | A rodada começa num workspace vazio e não enxerga a pasta do caso. O `scaffold.sh` de cada caso copia o fixture para lá. Só roda o que está neste repositório |
| `--ablation none` | O braço sem plugin recebe um comando com barra que lá não existe, e responde que o comando não está instalado — não tenta a tarefa. A comparação automática não mede nada. A comparação real é o caso `dinamico-controle` (abaixo) |
| `--no-publish` | O relatório é publicado por padrão. Mesmo com cliente inventado, publicar é decisão, não efeito colateral |
| `--threshold` | Abaixo do limiar a rodada sai com erro. Ver o valor medido em [Custo e variação](#custo-e-variação) |

Resultados vão para `evals/results/`, que é gitignored.

## Os casos

| Caso | Tag | O que prova |
| --- | --- | --- |
| `dinamico-completo` | `dinamico` | Briefing completo → os arquivos certos, a saudação ao pé da letra, toda trilha executa o transbordo, cada demanda na fila certa, confirmação antes de executar, mudança de demanda tratada. Critérios 20 a 25: observações citada uma vez e com teto, sem cabeçalho `FUNÇÃO:`, sem "string livre", sem variável de telefone |
| `dinamico-sem-destino` | `dinamico` | Sem dizer onde criar a pasta, a skill para e não escreve nada |
| `estatico-completo` | `estatico` | O mesmo, mais o que é do menu: frase literal de execução, submenu recomeçando em 1, assimetria entre trilhas irmãs mantida. Critérios 20 a 25: observações citada uma vez e com teto, sem cabeçalho `FUNÇÃO:`, sem "string livre" no manual de transbordo, e `"Não coletado"` distinto de `"Não se aplica"` |
| `estatico-sem-destino` | `estatico` | Sem destino, para e não escreve nada |
| `clinux-sem-referencia` | `clinux` | Sem cliente Clinux de referência no disco, a skill para em vez de inventar o agente do zero |
| `auditoria-fixture` | `auditoria` | A auditoria encontra os defeitos plantados e não reporta decisão deliberada como defeito. O critério 07 cobre as regras de 11/2026: telefone do contato coletado, variável de observações ausente e cabeçalho `FUNÇÃO:` na §2 |
| `dinamico-teto` | `dinamico` | Com 12 funções no inventário, acima do teto de 10, a skill para antes de escrever e oferece as saídas |
| `fix-fixture` | `fix` | Com um plano de três itens e só dois aprovados, a correção aplica os dois, deixa o terceiro como estava e não mexe no que está fora do plano |
| `fix-controle` | `comparacao` | O mesmo pedido, sem a skill. Mede o que a skill acrescenta |
| `relatorio-homolog`, `relatorio-prod` | `relatorio` | Os dois relatórios saem no caminho certo, com veredito, e não declaram pronto um cliente com defeito |
| `dinamico-controle` | `comparacao` | O mesmo briefing e os mesmos critérios, **sem** a skill — só a estrutura de arquivos informada. Mede o que a skill acrescenta. Não roda no dia a dia |
| `calib-*` | `calibracao` | Prova que os critérios reprovam o que está errado |

## Sincronia entre as skills

```bash
python evals/sincronia.py
```

Não roda modelo nenhum e não custa nada. Confere que as regras repetidas em mais de uma skill continuam
dizendo a mesma coisa, que nenhuma regra revogada voltou, e que as cinco cópias do `verificar.py` são
idênticas. Rodar antes de todo commit que mexa em skill.

## Como um caso é montado

- `prompt.md` — a tarefa. No frontmatter: `model` (ID completo, nunca apelido, para troca de versão do
  modelo não parecer regressão), `max_turns`, `timeout_seconds`, `allowed_tools`, `runs`, `tags`.
- `graders/*.md` — um critério por arquivo, com `weight`.
- `case.yaml` + `scaffold.sh` — só quando o caso precisa de arquivo no workspace antes de começar.

Regras que custaram uma rodada para aprender:

- **A skill é invocada pelo comando com barra** (`/agent-builder:agv-novo-dinamico Cliente`). Elas têm
  `disable-model-invocation`, então pedido em linguagem natural não as dispara. O comando **não** registra
  chamada `Skill`, então `tool_used: Skill` não serve como prova de que rodou: a prova é um critério de
  controle pelo conteúdo (a saudação literal do briefing, ou a linha `destino.pasta`).
- **O destino vai explícito no prompt**, com nome de pasta só em ASCII. Workspace vazio faz a skill parar sem
  destino — corretamente —, e critério de arquivo precisa de caminho fixo.
- **`AskUserQuestion` fica fora de `allowed_tools`.** O briefing tem de responder todas as linhas da ficha;
  qualquer `[PERGUNTAR]` faz a skill escrever pela metade e o critério oscilar.
- **`timeout_seconds: 1200` e `max_turns: 80` nas skills de criação.** Os defaults (300 s, 10 turnos) matam o
  caso: uma execução leva 6 a 7 minutos e 12 a 16 turnos.

## Critérios

| Tipo | Uso | Custo |
| --- | --- | --- |
| `file_exists` | O arquivo nasceu. Aceita curinga, inclusive `**` com `exists: false` para "nada foi escrito" | grátis |
| `regex` | Checagem mecânica no conteúdo: contagem de seções, frase literal, ausência de despedida. O alvo `{ source: file, path }` **não aceita curinga** — um critério por arquivo | grátis |
| `llm` | Só onde o critério exige raciocinar sobre fluxo | pago |

- **Padrão de `regex` em YAML vai entre aspas simples.** Em aspas duplas, `\.` e `\s` são escapes inválidos
  e `\b` vira *backspace* — o padrão se corrompe sem erro.
- **Critério `llm` cobra o requisito, nunca uma forma de implementá-lo.** Dois critérios desta suíte
  nasceram cravando uma implementação ("a Trilha C vai para `Atendimento_Geral`") e reprovaram saídas
  corretas, que chegavam ao mesmo destino por outro caminho. Escreva o que conta como acerto, o que reprova,
  e o que **não** é defeito — as exceções que a própria skill prevê.
- **Critério `llm` é sim ou não.** O juiz vota passa ou falha, sem nota parcial. Um critério que junta
  três verificações com "tira 0,33 cada" reprova a resposta inteira na primeira leitura rigorosa de qualquer
  uma delas. Foi o que aconteceu com o antigo critério 06 da auditoria, hoje dividido em 06a, 06b e 06c: a
  mesma resposta reprovava junto e passava separada.
- **Mudou um critério, roda a calibração.** Critério reescrito depois de ver a saída só se justifica se
  continuar reprovando o que está errado.

## Critério retirado: 13a

O critério "toda trilha da dinâmica termina executando o transbordo" (13a) reprovou o arquivo **sabidamente
correto** da calibração em 13/11/2026, como já tinha acontecido em outubro, sem causa encontrada. Saiu da
régua. A garantia que ele dava fica parcial: a frase literal de execução é conferida pelo `verificar.py`, mas
um caminho que encerra só com texto não tem mais critério automático.

## Custo e variação

Medido na rodada de 13 a 16/11/2026, v2.5.0, juiz Sonnet. Custo em dólar é o que a CLI reporta; na
assinatura, sai da cota de uso.

| Caso | Custo por execução | Execuções | Resultado |
| --- | --- | --- | --- |
| `auditoria-fixture` | ~US$ 0,95 | 3 | 3 de 3 com nota 1 |
| `estatico-completo` | ~US$ 1,20 | 5 | 4 de 5 com nota 1; uma parou em 2 turnos sem escrever nada, sem causa registrada |
| `dinamico-completo` | ~US$ 1,90 | 3 | 3 de 3 depois de retirar o 13a |
| `dinamico-teto` | ~US$ 0,40 | 3 | 3 de 3 |
| `*-sem-destino`, `clinux-sem-referencia` | ~US$ 0,33 | 1 cada | todos com nota 1 |
| `fix-fixture` | ~US$ 0,30 | 3 | 3 de 3 |
| `relatorio-homolog`, `relatorio-prod` | ~US$ 0,45 | 5 e 3 | 4 de 5 e 3 de 3 |
| calibração inteira | ~US$ 1,70 | 1 | cada caso no resultado esperado |

A rodada completa com 3 execuções por caso custa por volta de **US$ 35** e estoura o limite de 5 horas da
assinatura no meio. Rode por partes, com `-j 2`.

**Limiar: `--threshold 0.9`.** Abaixo disso, algum critério reprovou de verdade numa execução. A execução do
estático que parou sem escrever nada fica abaixo do limiar, e deve ficar: é exatamente o tipo de falha que a
suíte existe para mostrar.

## Limites

- **Os critérios leem o texto da configuração gerada; não simulam conversa com o agente.** Erro que só aparece
  numa conversa ao vivo, e que não esteja visível no texto, esta suíte não pega.
- **Sem terminal.** As verificações em shell que as skills fazem por conta própria não rodam aqui — os
  critérios conferem o resultado de fora.
- **A clinux só tem o caso negativo.** O caso completo exigiria um cliente Clinux de referência no fixture, e
  o único que existe é real.
