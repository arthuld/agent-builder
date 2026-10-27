---
type: llm
weight: 3
focus: { source: file, path: "Clientes/ClinicaBoaVista/config/agente.md" }
---
O arquivo é o prompt de um agente de WhatsApp. Quando o agente coletou dados, ele os lê de volta para o
usuário confirmar antes de executar a função de transbordo `set_transbordo`.

PASSA se a leitura de volta dos dados acontece **antes** da execução de `set_transbordo`, e a execução
acontece no mesmo turno em que o usuário confirma.

REPROVA se o prompt mandar:
- executar `set_transbordo` e só **depois** ler os dados de volta ou pedir confirmação; ou
- pedir uma segunda confirmação depois de o usuário já ter confirmado, sem que ele tenha corrigido nada.

NÃO são defeito, porque a regra os prevê:
- A Trilha B, de dúvida resolvida, executar `set_transbordo` sem leitura de volta: ela não coletou dado,
  então não há o que confirmar.
- Depois de o usuário **corrigir** um item, o agente reapresentar o item corrigido e pedir confirmação dele.
- Esgotadas as tentativas de obter um dado, o agente executar `set_transbordo` sem leitura de volta.

Cite o trecho que decidiu o voto.
