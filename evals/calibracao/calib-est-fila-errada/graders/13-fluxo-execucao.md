---
type: llm
weight: 3
focus: { source: file, path: "Clientes/CentroValeVerde/config/agente.md" }
---
O arquivo é o prompt de um agente de WhatsApp com menu numerado. As folhas do menu são 1.1 (consulta),
1.2 (exame), 2 (resultados) e 3 (atendente). Há também perguntas feitas fora do menu, respondidas pela base.

PASSA somente se as três condições valerem:

1. **Toda folha termina executando `set_transbordo`**, e a pergunta fora do menu, quando o usuário não
   quer mais nada, também termina executando a função. Reprova trilha que encerra só com texto, ou que
   anuncia a transferência sem executar.
2. **Cada folha vai para a fila certa:** 1.1 e 1.2 → `Agendamento`; 2 → `Resultados`;
   3 → `Atendimento_Geral`; e existe fallback para `Atendimento_Geral`.
3. **Onde houve coleta, a leitura de volta dos dados vem antes da execução**, e a execução acontece no
   turno em que o usuário confirma.

NÃO são defeito: a opção 3 executar direto sem confirmação (não coletou nada); a pergunta fora do menu
resolvida executar com a fila em branco; reconfirmar só o item que o usuário corrigiu; esgotadas as
tentativas, executar sem leitura de volta.

Cite o trecho que decidiu o voto.
