---
type: regex
weight: 3
pattern: 'Olá!\s+Eu\s+sou\s+o\s+Caio,\s+assistente\s+virtual\s+do\s+Centro\s+Médico\s+Vale\s+Verde\.'
target: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
Controle: a saudação literal do briefing aparece ao pé da letra. Espaço entre palavras aceita quebra
de linha: o arquivo pode quebrar a frase em duas linhas sem mudar o texto. Se este reprovar, a rodada não vale.
