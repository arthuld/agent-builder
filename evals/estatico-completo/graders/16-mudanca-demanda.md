---
type: llm
weight: 3
focus: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
O usuário pode trocar de assunto no meio de uma trilha — por exemplo, começar agendando um exame e passar a
pedir um resultado.

PASSA somente se o prompt disser explicitamente as duas coisas: **dado de identificação já informado é
reaproveitado sem perguntar de novo**, e **a fila e os dados ligados à trilha anterior são descartados**,
voltando ao menu para reclassificar.

REPROVA se o prompt não tratar mudança de demanda, ou tratar só uma das metades.
