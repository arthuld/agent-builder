# Changelog — agv-auditoria

- **3.2.0** — **Retorno vazio deixou de ser julgado ao contrário da criação, e a auditoria passou a conhecer
  três regras que a criação ganhou.** A tabela de categorias dizia que, em Base de conhecimento, vazio "pode
  indicar ausência na base", e o critério de negativa ancorada era só de agente Integrado; as skills de
  criação dizem que vazio nunca autoriza negar, em nenhuma categoria. Um agente era criado sob a regra e
  auditado sem ela — o mesmo padrão das versões 2.2.0 e 3.1.0. O critério agora vale nas duas, com a base
  declarada autoritativa pelo cliente tratada como decisão deliberada. Critérios novos, espelhando a criação:
  conjunto finito declarado como `enum` (o formulário de função aceita, confirmado); telefone do contato não
  coletado, porque a plataforma o entrega em `__CONTATO__`; variável de observações definida uma única vez; e cabeçalho `FUNÇÃO: nome` no topo da §2, que a criação
  deixou de escrever por ser pago em todo turno.
  Passo 0 corrigido: os comandos assumiam a pasta do cliente sem dizer, e o segundo sinal de categoria
  procurava `__X__` solto, que também casa em agente Integrado. Modelo alvo alinhado às skills de criação. O
  changelog saiu do `SKILL.md` para este arquivo.

- **3.1.0** — **Fila em branco na trilha resolvida deixou de ser reportada como defeito.** O critério "toda
  demanda tem destino" tratava "trilha sem fila" como violação sem exceção, contradizendo as skills de
  criação, em que a trilha de informação resolvida executa o transbordo com a fila em branco por desenho. A
  regra de decisão deliberada, só enunciada, não vencia o critério explícito: medido na suíte de evals, o
  auditor classificou essa fila como Crítica em 4 de 6 execuções, com base numa inferência sobre o schema da
  plataforma. Agora o critério traz a exceção, a regra de decisão deliberada diz onde procurar o registro de
  intenção, inferência sobre schema vai para "o que não foi possível julgar", e o plano ganha a seção
  obrigatória *Decisões deliberadas mantidas*.
- **3.0.0** — **Corrigido o contrato do runtime, e com ele sete critérios.** A §2 do manual é sempre-ativa —
  é o campo `Condições de Execução` da plataforma —, e não documentação como as skills afirmavam. Entram a
  tabela do contrato do runtime e a declaração do modelo alvo, que a auditoria não tinha: ela julgava sem
  saber para qual modelo o prompt fora escrito, a mesma lacuna que a 2.2.0 fechou para o formato XML.
  **Dois critérios foram invertidos:** pedir confirmação dos dados antes de executar era classificado como
  defeito e é o comportamento correto — o defeito real, preservado, é confirmar *depois* da execução ou
  pedir uma segunda confirmação; e "exemplo de diálogo é few-shot e vence a regra" saiu, porque exemplo de
  manual nunca chegou ao modelo e a seção de exemplos deixou de existir. **Um critério foi removido:** o
  mascaramento de documento, que o cliente descontinuou. Entram critérios para despedida escrita no prompt,
  blocos de perguntas relacionadas com meta de interações, mudança de demanda, modalidade de pagamento,
  coleta sem consumidor, e a conta de fusão de funções com os dois lados. A contagem de seções deixou de
  distinguir as categorias — as duas têm 2 — e virou achado de migração.
- **2.2.0** — Critério de formato de prompt: markdown estrutura, nunca XML. A regra e a medição (+217 tokens por turno por agente) já existiam nas skills de criação desde a adequação ao gpt-5.4-nano, mas não haviam chegado à auditoria — um agente podia ser criado sob a regra e auditado sem ela. Baseline com 3 repetições sobre um cliente-fixture cujo prompt inteiro era XML: **0 de 3** apontaram o formato, e **3 de 3** acharam o defeito-controle plantado na mesma seção, provando que auditaram e que a lacuna era de critério, não de atenção.
- **2.1.0** — Passo 0: determinar a categoria do agente antes de aplicar critério. Metade dos critérios só vale para agentes com base de conhecimento, e aplicá-los a um agente integrado produzia ruído de alta gravidade. Corrigido um **falso negativo silencioso**: a checagem de variável ausente do card ancorava o regex em `IA_`, e num agente integrado — onde as variáveis são nomes de parâmetro de endpoint — os dois lados voltavam vazios e a verificação passava sem ter verificado nada. Critério de sentinela alinhado à R21 do modelo estático.
- **2.0.0** — Autocontida e estruturada. Antes eram 934 palavras de prosa com **dois cabeçalhos** e 15 regras
  citadas por número de um documento externo. Numa medição com esse documento fora de alcance, a skill ainda
  achou 22 defeitos — porque trazia glosa inline —, mas em 5 regras a glosa era insuficiente e o auditor
  **observou sem julgar**: *"sei que exige mascaramento de CPF, não sei o formato"*. Agora cada verificação
  traz o critério de violação junto, as cinco dimensões viraram tabelas, e o Passo 3 acrescenta as
  verificações mecânicas que pegaram defeito real.
- **1.0.0** — Versão inicial.
