---
type: regex
weight: 2
pattern: '^(?=[\s\S]*\bAgendamento\b)(?=[\s\S]*\bResultados\b)(?=[\s\S]*\bAtendimento_Geral\b)'
target: { source: file, path: "Clientes/CentroValeVerde/config/variaveis.md" }
---
