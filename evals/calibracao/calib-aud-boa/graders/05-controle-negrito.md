---
type: llm
weight: 2
---

**Defeito-controle.** A resposta aponta o negrito de dois asteriscos no conteúdo que vira prompt.

Em `config/agente.md`, a regra de formatação diz *"Destaque textual com `**negrito**`"* — e o WhatsApp só
interpreta um asterisco de cada lado, então `**` aparece literal na tela do paciente. A regra ensina a
sintaxe errada no próprio enunciado.

Este grader não testa nenhum critério novo: é defeito que a versão anterior da skill já pegava. Serve para
provar que o auditor **leu os arquivos**, em vez de responder a partir do enunciado da tarefa. Se os outros
graders passarem e este falhar, a corrida não é confiável.
