---
model: claude-opus-5-5
max_turns: 80
timeout_seconds: 1200
runs: 3
allowed_tools: [Read, Glob, Grep]
tags: [dinamico, criacao, negativo]
---

/agent-builder:agv-novo-dinamico ClinicaBoaVista

--- MATERIAL DO CLIENTE ---

Grafia comercial: Clínica Boa Vista
Domínio: clínica de diagnóstico por imagem.

Agente: Lia, feminino ("a Lia").
Saudação literal aprovada pelo cliente, transcrever ao pé da letra:
"Olá! Sou a Lia, assistente virtual da Clínica Boa Vista. Em que posso ajudar?"

Plataforma:
- O consentimento de dados é obtido pela plataforma antes de a conversa chegar ao agente.
- A plataforma tem nó de decisão que lê a variável de resolução antes do roteamento de fila.

Filas reais cadastradas na plataforma (grafia exata): `Agendamento`, `Atendimento_Geral`.

Escopo incluído: ultrassonografia, raio-x, tomografia e mamografia.
Escopo excluído: consultas médicas, exames laboratoriais (sangue, urina) e ressonância magnética.

Trilhas:
- A, agendamento de exame: coleta completa e transbordo para `Agendamento`.
- B, dúvida sobre convênios aceitos ou sobre unidades e horários: o agente responde pela base e encerra
  como resolvido.
- C, demanda fora do escopo (consulta, laboratório, ressonância, resultado de exame, qualquer outra):
  só o nome e transbordo para `Atendimento_Geral`.

Funções que vão existir:
- `get_convenios`: lista de convênios aceitos.
- `get_unidades`: unidades, endereços e horários.
- `set_transbordo`: a função de transbordo.

Base de `get_convenios`: Unimed, Bradesco Saúde, SulAmérica, Amil. Todos cobrem todos os exames do escopo.

Base de `get_unidades`:
- Unidade Centro, Rua das Acácias, 120. Segunda a sexta 7h às 19h; sábado 7h às 12h.
- Unidade Norte, Avenida Brasil, 2500. Segunda a sexta 7h às 18h.
As duas unidades fazem todos os exames do escopo.

Dados que a atendente precisa receber no agendamento: nome completo, CPF, data de nascimento, modalidade
(convênio ou particular), nome do convênio e número da carteirinha quando for convênio, exame desejado,
unidade de preferência, e se tem pedido médico.

Variáveis: o material não define nomes; crie no padrão da plataforma.

Regras de negócio:
1. Todo exame exige pedido médico. Sem pedido, informar que é obrigatório e transbordar para
   `Agendamento` mesmo assim, para a atendente orientar.
2. Menor de 18 anos só realiza exame acompanhado do responsável legal. O agente informa; não coleta dado
   do responsável.
3. Convênio que não estiver na base: transbordar para `Agendamento`, nunca negar atendimento.
4. A clínica atende particular.

Confirmação dos dados antes de executar o transbordo: sim.
Meta de interações: 5 a 7 mensagens do agente.

--- FIM DO MATERIAL ---
