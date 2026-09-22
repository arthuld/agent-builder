# Variáveis de Contexto — Nina (Clínica Aurora)

> **Normalização.** O material do cliente não trazia nomes próprios; o padrão foi criado aqui.

> **Nota sobre valores de ausência.**
> - `"Não Informado"` — o paciente recusou explicitamente um dado já perguntado.
> - `"Não coletado"` — o transbordo foi acionado antes de o dado ser perguntado.
> - `"Não se aplica"` — a trilha deliberadamente não pergunta esse dado.

| Variável | Descrição | Regra de Validação | Funções |
| --- | --- | --- | --- |
| `IA_PACIENTE_NOME` | Nome completo | Obrigatório nas trilhas A e C. Texto livre. | `set_transbordo` -> `nome` |
| `IA_PACIENTE_CPF` | CPF do paciente | Obrigatório na trilha A. 11 dígitos. | `set_transbordo` -> `cpf` |
| `IA_CONVENIO_NOME` | Convênio do paciente | Obrigatório na trilha A. Validar com get_convenios. | `get_convenios` -> `convenio` |
| `IA_PROTOCOLO` | Protocolo do pedido | Obrigatório na trilha C. Texto livre. | `get_resultados` -> `identificador` |
| `IA_MOTIVO_CONTATO` | Classifica a demanda | Obrigatório. ENUM: Exame, Duvida, Resultado. | `set_transbordo` -> `motivo` |
| `IA_ATENDIMENTO_FILA` | Fila humana | Obrigatória quando resolvido for Não. Em branco quando Sim. ENUM: agendamento, resultados, atendimento_geral. Não aceita sentinela; fallback atendimento_geral. | `set_transbordo` -> `fila` |
| `IA_ATENDIMENTO_RESOLVIDO` | Resolvido pela Nina | Obrigatório. ENUM: Sim, Nao. | `set_transbordo` -> `resolvido` |
