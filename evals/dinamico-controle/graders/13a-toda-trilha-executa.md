---
type: llm
weight: 3
focus: { source: file, path: "Clientes/ClinicaBoaVista/config/agente.md" }
---
O arquivo é o prompt de um agente de WhatsApp. Julgue uma única coisa:

**Todo caminho da conversa termina executando a função `set_transbordo`** — inclusive o da dúvida que o
agente resolve sozinho pela base.

PASSA se cada caminho (agendamento, dúvida resolvida, repasse de demanda fora do escopo, tentativas
esgotadas) termina com a instrução de executar `set_transbordo`.

REPROVA se algum caminho encerra só com texto, ou se o prompt manda anunciar a transferência sem executar a
função.

Não julgue filas, confirmação nem nenhum outro aspecto. Cite o trecho que decidiu o voto.
