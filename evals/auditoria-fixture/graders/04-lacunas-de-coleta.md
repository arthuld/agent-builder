---
type: llm
weight: 3
---

A resposta encontra as lacunas de coleta. São quatro, plantadas de propósito. Conte quantas aparecem:

1. **Particular sem caminho.** A Trilha A exige convênio, a base só tem convênios nomeados, e quem não tem
   plano esgota as tentativas e é gravado como `"Não Informado"` — que o próprio `variaveis.md` define como
   *recusou explicitamente*.
2. **Sem confirmação antes de executar.** Nenhuma trilha lê de volta os dados coletados antes de acionar
   `set_transbordo`.
3. **Protocolo sem consumidor.** A Trilha C coleta o protocolo para `get_resultados`, mas essa função
   devolve só canais e prazo genéricos, iguais para qualquer paciente — nada indexado por protocolo.
4. **Mudança de demanda.** Nada define o que acontece quando o paciente troca de assunto no meio; a nova
   demanda herda fila e dados da anterior.

Nota: 1.0 com três ou quatro; 0.5 com duas; 0 com uma ou nenhuma.
