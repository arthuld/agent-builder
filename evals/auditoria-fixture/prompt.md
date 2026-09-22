---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Bash, Skill]
runs: 3
tags: [auditoria]
---

Audite o agente virtual do cliente `ClinicaAurora`, cuja pasta está em
`evals/auditoria-fixture/fixture/ClinicaAurora`. Use a skill `agv-auditoria` se ela estiver disponível.

Leia todos os arquivos de `config/`, `ferramentas/manuais/` e `ferramentas/dados/` e entregue o plano de
correção: ordenado do mais grave para o menos, cada item com o defeito em uma frase, o arquivo e a linha
onde ele está, o efeito em produção, e a correção proposta.

Não altere nenhum arquivo.
