---
type: llm
weight: 3
focus: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
No briefing, a opção 1.2 (exame de imagem) pergunta se o usuário tem pedido médico, e a opção 1.1
(consulta) **não** pergunta. É regra de negócio deliberada.

PASSA se o prompt mantém essa diferença: a trilha do exame coleta o pedido médico e a da consulta não.

REPROVA se a consulta também pedir pedido médico, ou se o exame deixar de pedir. Uniformizar as duas
trilhas apaga a regra do cliente.
