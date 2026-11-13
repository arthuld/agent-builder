---
type: regex
weight: 1
pattern: '__IA_OBSERVACOES__[^\n]{0,200}[0-9]{2,4} caracteres|[0-9]{2,4} caracteres[^\n]{0,200}__IA_OBSERVACOES__'
match: contains
target: { source: file, path: "Clientes/ClinicaBoaVista/config/agente.md" }
---
A definição da variável de observações traz teto de tamanho em caracteres, na mesma linha (R5).
