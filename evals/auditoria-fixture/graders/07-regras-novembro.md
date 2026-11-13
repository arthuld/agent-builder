---
type: llm
weight: 2
---

A resposta encontra os três defeitos acrescentados com as regras de 11/2026. Conte quantos aparecem:

1. **Telefone do contato coletado.** A Trilha A pede o telefone e há uma variável para ele, mas a
   plataforma já entrega o número de quem está na conversa (`__CONTATO__`). Conta como acerto apontar que o
   dado é desnecessário porque a plataforma já o tem.
2. **Sem variável de observações.** Não existe `__IA_OBSERVACOES__` (ou equivalente) — o informativo breve
   que o atendente lê para continuar o atendimento.
3. **Cabeçalho `FUNÇÃO: nome` no topo da §2 dos manuais.** É pago em todo turno, uma vez por função, e a
   plataforma já sabe de qual função o campo é.

Nota: 1.0 com os três; 0.5 com dois; 0 com um ou nenhum.

**Não** conta como acerto uma recomendação genérica de "revisar as variáveis".
