---
model: claude-opus-5-5
max_turns: 60
timeout_seconds: 1200
runs: 3
allowed_tools: [Read, Glob, Grep]
tags: [comparacao]
---

Aplique as correções aprovadas do plano abaixo na configuração do agente virtual.

A pasta do cliente está em `ClinicaAurora/`, no diretório de trabalho. O plano de correção da auditoria
está em `ClinicaAurora/relatorios/plano-correcao.md`.

Aprovo os itens 1 e 2. O item 3 fica para depois: não aplique.
