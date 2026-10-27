---
type: regex
weight: 2
pattern: '(vou|irei) (te |lhe )?(transferir|encaminhar)|transferindo (você|voce)|estou (te |lhe )?encaminhando|um momento, por favor|até logo|tenha um (ótimo|bom) dia'
flags: i
match: not_contains
target: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
