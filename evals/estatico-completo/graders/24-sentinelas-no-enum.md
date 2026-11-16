---
type: regex
weight: 2
pattern: 'Não se aplica'
match: contains
target: { source: file, path: "Clientes/CentroValeVerde/ferramentas/manuais/set_transbordo.md" }
---
O briefing dá ao campo `pedido_medico` um enum só com `Sim` e `Não`. Como a trilha de consulta não pede o
pedido médico, o campo recebe `"Não se aplica"` — e o manual de transbordo precisa declarar as sentinelas
aceitas no enum, em vez de afrouxar o campo para texto livre.
