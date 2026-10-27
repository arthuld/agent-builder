---
type: llm
weight: 3
focus: { source: file, path: "Clientes/ClinicaBoaVista/config/agente.md" }
---
O arquivo é o prompt de um agente de WhatsApp. O usuário pode trocar de assunto no meio da conversa — por
exemplo, começar agendando um exame e passar a perguntar sobre uma consulta.

PASSA somente se o prompt disser explicitamente as duas coisas:

1. **Dado de identificação já informado (nome, CPF, data de nascimento) é reaproveitado sem perguntar de
   novo** quando a demanda muda.
2. **A fila e a qualificação ligadas à demanda anterior são descartadas**, e a nova demanda é
   reclassificada antes de continuar.

REPROVA se o prompt não tratar mudança de demanda, ou tratar só uma das duas metades. Uma regra genérica do
tipo "não repergunte dados" sem falar da fila da demanda anterior não basta.
