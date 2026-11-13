# Changelog — agv-novo-dinamico

- **2.1.0** — **Variável de observações volta, definida uma única vez; telefone do contato deixa de ser
  coletado.** A R5 proibia a variável de observações e a prática a criava: três dos quatro agentes mais
  recentes a tinham, a pedido do usuário. Agora ela é padrão — um informativo breve para o atendente —,
  definida em um único ponto do prompt, com teto de tamanho e restrita ao que foi dito ou retornado, que é o
  que impede tanto o custo espalhado da versão antiga quanto o resumo inventado. A R5a registra que a
  plataforma já entrega o número em `__CONTATO__`. Correções de consistência: a ficha ganha a linha
  `destino.pasta`, que o texto citava e o bloco não trazia; R12 passa a declarar o escopo (função de
  consulta retém, transbordo nunca), porque escritas como dois absolutos as duas regras colidem no prompt
  gerado; o cabeçalho `FUNÇÃO: nome` sai do template da §2, onde era pago em todo turno; referência truncada
  no bloco Bordas corrigida. O modelo alvo passa a dizer que o `reasoning_effort` é o default do modelo, fora
  do nosso controle, e registra a saída do `gpt-5.4-nano` da API em 01/04/2027. O changelog saiu do
  `SKILL.md` para este arquivo: era lido a cada invocação sem orientar nada.

- **2.0.0** — **Corrigido o contrato do runtime: a §2 do manual é sempre-ativa.** A R16 afirmava o
  contrário — que §2 e §3 eram documentação fora do alcance do modelo. São dois campos da plataforma,
  `Objetivo da Função` e `Condições de Execução`, pagos em todo turno junto com o schema; toda medição de
  sempre-ativo feita sob a premissa antiga subestimou o custo por uma §2 vezes o número de funções. Daí
  vêm: a tabela do contrato do runtime, a §3 removida (não há campo para ela, e exemplo que o modelo não
  recebe só produz uma segunda versão da regra), os manuais renomeados pelos campos de destino, e a conta
  de fusão de funções com os dois lados na R26. Outras mudanças de comportamento: a mensagem de
  transferência é da plataforma e o prompt fica proibido de escrevê-la (R9); confirmação dos dados antes de
  executar vira bloco padrão; perguntas passam a ser agrupadas em blocos relacionados com meta de
  interações, por causa da cobrança por mensagem do WhatsApp (R21, que substitui a regra de mascaramento —
  removida, porque o documento fica no histórico da plataforma e é coletado sob consentimento); bifurcação
  de modalidade de pagamento com caminho particular explícito (R7a); coleta só com consumidor nomeado
  (R12a); sentinela declarada no enum promovida de item de checklist a regra (R12b); e reclassificação na
  mudança de demanda (R10d). O Passo 5 passa a emitir a matriz de homologação.
- **1.2.0** — **Formato declarado: markdown para estruturar, nunca XML.** A documentação oficial não
  prescreve formato de prompt para o `gpt-5.4-nano` — o que ela exige é *ter* estrutura. Medido: trocar
  os headers por tags XML custaria +217 tokens por turno por agente (+5% do campo), sem ganho
  documentado, e o que o XML resolveria — delimitar blocos — a plataforma já resolve, porque os 4 campos
  são entradas separadas. A regra existe para impedir que a próxima revisão "melhore" o prompt para os
  blocos XML dos exemplos da documentação, que são orquestração multi-etapa do modelo frontier.
- **1.1.0** — Adequação ao `gpt-5.4-nano`. Modelo alvo declarado, com as consequências de escrita que derivam dele. Acrescentados os três blocos que faltavam no prompt gerado — **Regras Críticas** no topo das Diretrizes, **Bordas** e **Formato da Resposta** — e as regras de borda que não existiam: falha técnica com escada própria e precedência entre regras declarada. Motivo: a orientação oficial do nano pede tarefa estreita, saída fechada e nenhuma borda implícita; borda não escrita é comportamento inventado. Acrescentada a formulação literal de execução (R9), que já existia no modelo estático e é o ponto de falha nº 1. Corrigido o número típico de funções, que estava desatualizado frente ao corpus real.
- **1.0.0** — Versão inicial. Deriva da `/novo-agente`, com três mudanças de fundo: ficha de parâmetros
  obrigatória antes da escrita; regras e formatos inlined, sem dependência externa nem cliente de
  referência; consentimento e comportamento de resolução viram perguntas sobre a plataforma de destino, em
  vez de premissas fixas.
