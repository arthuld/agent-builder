# Changelog — agv-novo-estatico

- **3.2.0** — **Verificador único e teto de escopo**, iguais aos da dinâmica 2.2.0: o `verificar.py` no
  Passo 4, `Bash` em `allowed-tools`, e a parada antes de escrever quando o inventário passa de 10 funções.
- **3.1.0** — **O template do manual de transbordo deixou de contradizer a R21, e `"Não coletado"` voltou a
  ter sentido próprio.** O bloco `COMPATIBILIDADE DE SCHEMA` do template ainda mandava escrever "campos
  condicionais são string livre" — o remédio antigo, que a R21 passou a classificar como defeito —, e como o
  template é o texto que se copia, a regra perdia para ele. A R6 definia `"Não coletado"` e `"Não se aplica"`
  com o mesmo sentido ("a trilha não pergunta"), diferente do modelo dinâmico e da auditoria: dois rótulos
  com uma definição fazem o modelo escolher ao acaso e o atendente ler errado. O exemplo de `enum` da R21 passou a listar as três sentinelas — faltava `"Não se aplica"`, justamente a
  mais comum num fluxo estático. Confirmado que o formulário de
  função aceita `enum`, saiu a alternativa de string livre da R21. Mesmas mudanças da dinâmica 2.1.0:
  variável de observações padrão, definida uma única vez (R5); telefone do contato fora da coleta, porque a
  plataforma o entrega em `__CONTATO__` (R5a) — saiu do bloco e do card de exemplo; linha `destino.pasta` na
  ficha; escopo declarado em R17 e R24; cabeçalho `FUNÇÃO: nome` fora do template da §2. R27a1 e R35
  alinhadas ao contrato do runtime: o sempre-ativo é §1 + §2 + schema, e a conta de fusão tem dois lados. O
  changelog saiu do `SKILL.md` para este arquivo.

- **3.0.0** — **Corrigido o contrato do runtime: a §2 do manual é sempre-ativa.** A R26 afirmava o
  contrário — que §2 e §3 eram documentação fora do alcance do modelo. São dois campos da plataforma,
  `Objetivo da Função` e `Condições de Execução`, pagos em todo turno junto com o schema; toda medição de
  sempre-ativo feita sob a premissa antiga subestimou o custo. Daí vêm: a tabela do contrato do runtime, a
  §3 removida, os manuais renomeados pelos campos de destino, e a R19 reduzida a duas armadilhas — a
  terceira ("exemplo que contradiz a regra é few-shot e vence a regra") deixou de existir junto com a §3, e
  sua premissa estava errada de todo modo, porque exemplo de manual nunca chegou ao modelo. Outras mudanças
  de comportamento: a mensagem de transferência é da plataforma e o prompt fica proibido de escrevê-la
  (R15); a R18 passa a **pedir** uma confirmação antes de executar, e a R19.1 protege apenas o defeito real
  — confirmação depois da execução, ou uma segunda confirmação; perguntas passam a ser agrupadas em blocos
  relacionados com meta de interações, por causa da cobrança por mensagem do WhatsApp (R30, que substitui a
  regra de mascaramento — removida, porque o documento fica no histórico da plataforma e é coletado sob
  consentimento); Bloco Modalidade antes do Bloco Convenio, com caminho particular explícito (R13a); coleta
  só com consumidor nomeado (R24a); e reclassificação na mudança de demanda (R14e). O Passo 5 passa a
  emitir a matriz de homologação.
- **2.2.0** — **Formato declarado: markdown para estruturar, nunca XML.** A documentação oficial não
  prescreve formato de prompt para o `gpt-5.4-nano` — o que ela exige é *ter* estrutura. Medido: trocar
  os headers por tags XML custaria +217 tokens por turno por agente (+5% do campo), sem ganho
  documentado, e o que o XML resolveria — delimitar blocos — a plataforma já resolve, porque os 4 campos
  são entradas separadas. A regra existe para impedir que a próxima revisão "melhore" o prompt para os
  blocos XML dos exemplos da documentação, que são orquestração multi-etapa do modelo frontier.
- **2.1.0** — Adequação ao `gpt-5.4-nano`. Modelo alvo declarado, com as consequências de escrita que derivam dele. Acrescentados os três blocos que faltavam no prompt gerado — **Regras Críticas** no topo das Diretrizes, **Bordas** e **Formato da Resposta** — e as regras de borda que não existiam: falha técnica com escada própria e precedência entre regras declarada. Motivo: a orientação oficial do nano pede tarefa estreita, saída fechada e nenhuma borda implícita; borda não escrita é comportamento inventado. **R21 reescrita**: a sentinela passa a ser declarada no `enum` do parâmetro, em vez de o schema ser afrouxado para acomodá-la. Com a plataforma sem `allowed_tools`, `reasoning_effort` nem modo strict, o enum é a única restrição estrutural disponível — desarmá-lo era abrir mão do último controle que não depende de o modelo obedecer.
- **2.0.0** — Reescrita autocontida. Antes, 14 regras eram citadas por número de um documento externo; numa
  medição com esse documento fora de alcance, **6 delas viraram buraco** — a taxonomia de trilhas e os
  limites de domínio foram pulados, o fallback de roteamento ficou sem destino, e o formato de quatro colunas
  do dicionário de variáveis teve de ser **adivinhado**. Agora todas estão inlinadas com numeração própria e
  o motivo junto. Acrescentada a ficha de parâmetros do Passo 0: a versão anterior produzia boas perguntas e
  assumia mesmo assim, listando na frase seguinte "o que eu assumiria por conta própria, e é chute".
  Acrescentados os esqueletos literais de cada arquivo gerado.
- **1.0.0** — Versão inicial.
