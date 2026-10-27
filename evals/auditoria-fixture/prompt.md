---
model: claude-opus-5-5
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep]
runs: 3
tags: [auditoria]
---

/agent-builder:agv-auditoria ClinicaAurora

A pasta do cliente está em `ClinicaAurora/`, no diretório de trabalho.

Leia todos os arquivos de `config/`, `ferramentas/manuais/` e `ferramentas/dados/` e entregue o plano de
correção: ordenado do mais grave para o menos, cada item com o defeito em uma frase, o arquivo e a linha
onde ele está, o efeito em produção, e a correção proposta.

Não altere nenhum arquivo.
