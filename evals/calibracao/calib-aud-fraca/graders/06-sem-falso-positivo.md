---
type: llm
weight: 2
---

A resposta **não** reporta como defeito nenhuma destas três coisas, que estão corretas no cliente:

1. **Fundir `get_convenios` com `get_resultados`.** Elas servem trilhas diferentes (A e C) e não são
   acionadas juntas. Função raramente acionada é carga preguiçosa, e mantê-las separadas é o desenho certo.
2. **A fila em branco na Trilha B.** É decisão deliberada, documentada em `variaveis.md` (*"Em branco
   quando Sim"*), porque o nó de decisão da plataforma desvia e encerra. Apontar a *promessa de atendente*
   feita nessa trilha é outra coisa, e é acerto — o que não pode é chamar a fila vazia de bug.
3. **O `**` do `clienteinfo.json`.** O card do atendente é markdown de painel, não mensagem de WhatsApp;
   ali dois asteriscos é a sintaxe correta.

Nota 1.0 se nenhuma das três for reportada como defeito. Cada uma reportada tira 0.33.

Auditoria que classifica decisão deliberada como defeito faz o cliente corrigir o que estava certo.
