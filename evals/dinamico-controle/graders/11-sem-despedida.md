---
type: regex
weight: 2
pattern: "(vou|irei) (te |lhe )?(transferir|encaminhar)|transferindo (você|voce)|um momento, por favor|até logo|tenha um (ótimo|bom) dia"
flags: i
match: not_contains
target: { source: file, path: "Clientes/ClinicaBoaVista/config/agente.md" }
---
Nenhuma despedida nem aviso de transferência escrito no prompt: essa mensagem é da plataforma.
