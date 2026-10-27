---
type: regex
weight: 3
pattern: 'Olá!\s+Sou\s+a\s+Lia,\s+assistente\s+virtual\s+da\s+Clínica\s+Boa\s+Vista\.\s+Em\s+que\s+posso\s+ajudar\?'
target: { source: file, path: "Clientes/ClinicaBoaVista/config/agente.md" }
---
Controle: a saudação literal do briefing aparece ao pé da letra. Espaço entre palavras aceita quebra
de linha: o arquivo pode quebrar a frase em duas linhas sem mudar o texto. Prova que a skill rodou sobre o briefing,
e não respondeu com um modelo genérico. Se este reprovar, a rodada inteira não vale.
