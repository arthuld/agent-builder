---
type: regex
weight: 1
pattern: 'IA_[A-Z_]*(TELEFONE|CELULAR)'
match: not_contains
target: { source: file, path: "Clientes/ClinicaBoaVista/config/variaveis.md" }
---
O telefone do contato já vem da plataforma em `__CONTATO__` (R5a): não vira variável de coleta `IA_`.
Procura só o nome de variável, porque o dicionário pode citar a palavra "telefone" ao descrever `__CONTATO__`.
