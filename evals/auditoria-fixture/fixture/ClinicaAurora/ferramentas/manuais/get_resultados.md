## 1. Descrição da Função (OpenAI Function Calling)

Retorna os canais de acesso ao resultado de exames e o prazo de liberação. Acionar quando o paciente
perguntar como acessar o resultado dele.

---

## 2. Diretrizes de Prompt (System Instructions)

```markdown
FUNÇÃO: get_resultados
# CONTRATO DE RETORNO
- canais: onde o paciente retira o resultado.
- prazo_dias_uteis_min / max: janela de liberação.
# APLICAÇÃO
- Responder só o canal perguntado.
```

---

## 3. Exemplos Práticos de Diálogos

### Cenário 1: acesso ao resultado

> **Paciente:** *"Como pego meu resultado?"*
>
> **Agente:** *"Me informa o protocolo do pedido, por favor."*
