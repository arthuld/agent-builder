---
model: claude-opus-5-5
max_turns: 40
timeout_seconds: 900
runs: 3
allowed_tools: [Read, Glob, Grep]
tags: [clinux, criacao, negativo]
---

/agent-builder:agv-novo-clinux ClinicaHorizonte

Destino: crie a pasta do cliente em `Clientes/ClinicaHorizonte/`. O agrupamento `Clientes/` ainda não
existe neste diretório; pode criá-lo.

--- MATERIAL DO CLIENTE ---

Grafia comercial: Clínica Horizonte
Agente: Bia, feminino ("a Bia").
Saudação literal: "Olá! Sou a Bia, assistente virtual da Clínica Horizonte."
Fila de transbordo única: `Agendamento_Chat`, pela função `transbordo_agendamento`.
Omnitags: `Agendado`, `Transferido`, `Desistiu`.
Escopo: só exames (módulo de exames). Sem consultas.
Exames que a clínica não realiza: ressonância magnética, densitometria.
Pedido médico obrigatório: sim.
Preparo: fora de escopo.
Reagendamento e cancelamento: repasse com coleta mínima.
Consentimento LGPD: tratado pela plataforma antes do agente.

--- FIM DO MATERIAL ---
