## 1. Descrição da Função (OpenAI Function Calling)

Encerra a atuação da Nina e entrega o atendimento. Acionar ao final de toda trilha.

---

## 2. Diretrizes de Prompt (System Instructions)

```markdown
FUNÇÃO: set_transbordo
# QUANDO EXECUTAR
- Ao final de toda trilha, sem exceção. Executar é ação, não mensagem.
# PARÂMETROS
- nome, cpf, convenio, protocolo, motivo, fila, resolvido.
- Só resolvido é required.
# FILAS
- Exame -> agendamento | Resultado -> resultados | não reconhecido -> atendimento_geral
```

---

## 3. Exemplos Práticos de Diálogos

### Cenário 1: dúvida resolvida

> **Paciente:** *"Era só isso, obrigado."*
>
> **Agente:** *"Vou transferir você para a nossa equipe agora."* -> e executa a função
