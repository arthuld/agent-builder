---
type: llm
weight: 2
focus: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
Ao exibir o submenu de "Agendamentos", o usuário deve ver as opções numeradas a partir de 1 (1 e 2), com
o título da categoria acima — e não "1.1" e "1.2". O código interno da trilha (1.1, 1.2) é usado só para
preencher parâmetros e na tabela interna, nunca exibido no chat.

PASSA se o prompt manda exibir o submenu com numeração recomeçando em 1 e proíbe mostrar o código interno
ao usuário. REPROVA se o submenu for exibido como "1.1 / 1.2", ou se nada disser sobre isso.
