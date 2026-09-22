## 1. Descrição da Função (OpenAI Function Calling)

Retorna os convênios aceitos pela clínica e os exames cobertos por cada um. Acionar quando o paciente
informar o convênio e for preciso validar a cobertura do exame pedido.

---

## 2. Diretrizes de Prompt (System Instructions)

```markdown
FUNÇÃO: get_convenios
# CONTRATO DE RETORNO
- convenios: lista de convênios aceitos, com os exames cobertos de cada um.
# APLICAÇÃO
- Tolerância a variação de grafia só dentro do mesmo convênio.
- Convênio ausente da lista: não afirmar cobertura nem negar em definitivo.
```

---

## 3. Exemplos Práticos de Diálogos

### Cenário 1: convênio aceito

> **Paciente:** *"Tenho Saude Total, cobre ultrassom?"*
>
> **Agente:** *"Cobre sim. Vou transferir você para a nossa equipe agora."*
