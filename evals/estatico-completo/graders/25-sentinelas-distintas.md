---
type: regex
weight: 2
pattern: '"?Não coletado"?`?\s*[—–-][^\n]*antes'
target: { source: file, path: "Clientes/CentroValeVerde/config/variaveis.md" }
---
Em `variaveis.md`, `"Não coletado"` é definido como o transbordo acontecido **antes** de o dado ser
perguntado — e não como "a trilha não pergunta", que é o sentido de `"Não se aplica"`. Critério por regex
porque o juiz `llm` só vê a resposta final, não o arquivo.
