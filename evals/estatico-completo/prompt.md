---
model: claude-opus-5-5
max_turns: 80
timeout_seconds: 1200
runs: 3
allowed_tools: [Read, Glob, Grep]
tags: [estatico, criacao]
---

/agent-builder:agv-novo-estatico CentroValeVerde

Destino: crie a pasta do cliente em `Clientes/CentroValeVerde/`. O agrupamento `Clientes/` ainda não
existe neste diretório; pode criá-lo.

--- MATERIAL DO CLIENTE ---

Grafia comercial: Centro Médico Vale Verde
Domínio: centro médico com consultas e exames de imagem.

Agente: Caio, masculino ("o Caio").
Saudação literal aprovada pelo cliente, transcrever ao pé da letra:
"Olá! Eu sou o Caio, assistente virtual do Centro Médico Vale Verde."

Plataforma:
- O consentimento de dados é obtido pela plataforma antes de a conversa chegar ao agente.
- A plataforma tem nó de decisão que lê a variável de resolução antes do roteamento de fila.

Árvore do menu (os números são as opções; o que vem depois de ">" são ações em sequência):

1. Agendamentos >
    1.1. Consulta > DadosPessoais > Modalidade > Convenio > Especialidade > set_transbordo
    1.2. Exame de imagem > DadosPessoais > Modalidade > Convenio > PedidoMedico > set_transbordo
2. Resultados de exames > DadosPessoais > set_transbordo
3. Falar com um atendente > set_transbordo

Blocos de coleta:
- DadosPessoais: nome completo, CPF e data de nascimento.
- Modalidade: convênio ou particular.
- Convenio: nome do convênio e número da carteirinha. Só quando a modalidade for convênio.
- Especialidade: especialidade desejada.
- PedidoMedico: se tem pedido médico (sim ou não).

Assimetria intencional: a opção 1.2 (exame) pergunta pelo pedido médico e a 1.1 (consulta) não. É regra
de negócio, não esquecimento — consulta não exige pedido. A opção 2 só coleta DadosPessoais e a 3 não
coleta nada, também de propósito.

Filas reais cadastradas na plataforma (grafia exata) e para onde cada opção vai:
- `Agendamento`: opções 1.1 e 1.2.
- `Resultados`: opção 2.
- `Atendimento_Geral`: opção 3.
Fila de fallback (opção não reconhecida, tentativas esgotadas, demanda não identificada):
`Atendimento_Geral`.

Funções:
- `set_transbordo`: a função de transbordo, executada ao final de toda trilha.
- `get_informacoes`: base para responder perguntas feitas fora do menu.

Schema de `set_transbordo`: o único parâmetro obrigatório é `atendimento_resolvido`. Nenhum campo do
schema tem enum, pattern ou format.

Base de `get_informacoes`:
- Endereço: Rua dos Ipês, 340, Centro.
- Horário: segunda a sexta 7h às 19h; sábado 7h às 12h.
- Convênios aceitos: Unimed, Bradesco Saúde, Amil.

Regras de negócio:
1. Exame de imagem exige pedido médico. Sem pedido, informar que é obrigatório e seguir para
   `Agendamento` mesmo assim, para a atendente orientar.
2. O centro atende particular.
3. Convênio que não estiver na base: seguir para `Agendamento`, nunca negar atendimento.

Tentativas antes do fallback: 2.
Confirmação dos dados antes de executar o transbordo: sim.
Meta de interações: 5 a 7 mensagens do agente.

--- FIM DO MATERIAL ---
