---
type: llm
weight: 3
---

A resposta identifica que o prompt escreve a mensagem de transferência, que é responsabilidade da
plataforma.

Conta como acerto se apontar o literal *"Vou transferir você para a nossa equipe agora"* em
`config/agente.md` **e** pelo menos uma destas consequências:

- a Trilha B encerra com resolução positiva e fila em branco, então promete um atendente que não virá; ou
- quem envia a mensagem de encerramento depois da chamada é a plataforma, e o prompt duplica; ou
- a frase está escrita em mais de um arquivo e as versões vão divergir.

Peso alto: é o defeito que o paciente sente diretamente.
