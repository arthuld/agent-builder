---
type: regex
weight: 2
pattern: '__IA_OBSERVACOES__[\s\S]*__IA_OBSERVACOES__'
match: not_contains
target: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
A variável de observações é citada em **um** ponto só do prompt (R5). Uma segunda menção — tipicamente na trilha de repasse — é o padrão que custava 92 tokens por turno.
