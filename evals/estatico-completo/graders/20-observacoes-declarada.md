---
type: regex
weight: 2
pattern: '__IA_OBSERVACOES__'
match: contains
target: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
A variável de observações é padrão em todo agente (R5): o prompt a define.
