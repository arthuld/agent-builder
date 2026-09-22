# Suíte de evals

Transforma em regressão repetível o que antes era subagente ad-hoc refeito à mão a cada mudança.

## Rodar

```bash
claude plugin eval . --allow-tools Bash --trust-plugin
```

`--allow-tools Bash` não é opcional: a auditoria roda verificações mecânicas em shell, e sem o grant o caso
aborta antes do primeiro turno. `--trust-plugin` pula o prompt de confiança de primeira execução.

Uma passada barata, para validar formato de caso ou grader novo, sem pagar o braço de ablação:

```bash
claude plugin eval . --runs 1 --ablation none --allow-tools Bash --trust-plugin --no-publish
```

Por padrão a ferramenta roda **dois braços**: com o plugin e sem. O delta entre eles é a medida do que a
skill acrescenta, e é exatamente o braço de controle que este repositório já aplicava à mão. Três runs por
caso por braço, então ~6 execuções de agente por caso.

Resultados vão para `evals/results/`, que é gitignored.

## Os casos

| Caso | O que prova |
|---|---|
| `auditoria-fixture` | A `agv-auditoria` encontra os defeitos que os critérios da v2.0.0 introduziram, sem inventar defeito onde a configuração está certa |

## Como um caso é montado

`prompt.md` é a tarefa, no frontmatter os limites (`max_turns`, `allowed_tools`, `runs`, `tags`).
`graders/*.md` são os critérios, um arquivo por critério, com `weight` no frontmatter.

Dois tipos em uso:

- `type: llm` — um modelo julga a resposta contra o critério escrito. O critério precisa dizer o que conta
  como acerto **e** o que não conta; grader vago vira nota aleatória.
- `type: tool_used` com `tool: Skill` — verifica que a skill foi acionada de fato, não só mencionada. É
  indicador de que o plugin disparou, e a ferramenta o trata como `with-only`: no braço sem plugin ele não
  entra na nota.

## Dois graders que não testam critério nenhum

Valem tanto quanto os outros, e por razões opostas:

**`05-controle-negrito`** é o defeito-controle. Cobre uma regra que a versão anterior da skill já pegava, e
existe só para provar que o auditor **leu os arquivos** em vez de responder a partir do enunciado. Se os
outros passarem e este falhar, a corrida não é confiável e a nota não significa nada.

**`06-sem-falso-positivo`** cobra o contrário: que três decisões deliberadas do cliente **não** sejam
reportadas como defeito. Auditoria que classifica decisão deliberada como bug faz o cliente corrigir o que
estava certo, e nenhum grader de cobertura pega isso — quanto mais o auditor reporta, melhor ele parece.

## O fixture

`auditoria-fixture/fixture/ClinicaAurora` é um cliente **fictício**, escrito para esta suíte, com sete
defeitos plantados e um de controle. Nenhum dado de cliente real entra aqui: este repositório é público.
