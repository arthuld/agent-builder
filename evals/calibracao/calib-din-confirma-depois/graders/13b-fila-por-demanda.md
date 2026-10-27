---
type: llm
weight: 3
focus: { source: file, path: "Clientes/ClinicaBoaVista/config/agente.md" }
---
O arquivo é o prompt de um agente de WhatsApp. Julgue uma única coisa: **a fila de cada demanda.**

| Demanda | Fila esperada |
| --- | --- |
| Agendar exame | `Agendamento` |
| Convênio que não consta na base | `Agendamento` |
| Fora do escopo, ou demanda não identificada | `Atendimento_Geral` |
| Dúvida resolvida pela base | em branco (é o desenho, não é defeito) |

PASSA se cada demanda da tabela recebe a fila indicada, em qualquer lugar do prompt — tabela de
classificação, cabeçalho de trilha ou bloco de confirmação valem igualmente.

REPROVA se alguma demanda da tabela fica sem fila ou recebe fila diferente da indicada.

Não julgue execução da função, confirmação nem nenhum outro aspecto. Cite o trecho que decidiu o voto.
