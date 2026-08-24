---
name: agv-relatorio-homolog
description: Use somente quando o usuário pedir explicitamente o relatório resumido de entrega para teste (homologação) de um cliente, com o atalho de teste e as pendências que bloqueiam a validação. Não usar para criar nem auditar agente.
argument-hint: "[cliente]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash
metadata:
  version: "2.0.0"
---

# Relatório de Homologação (Resumido)

Gera o relatório de **liberação para teste** de `$ARGUMENTS`: comunica que a configuração foi concluída e
está disponível para validação em homologação. Destinado a anexo em chamado, lido por terceiros.

## Esta skill é autocontida

O modelo do relatório está inteiro aqui — não há arquivo de template externo a consultar. Se existir um e ele
**contradisser** este arquivo, pare e diga qual é a divergência.

**Registro:** formal e impessoal. Sem emoji, sem interjeição, sem primeira pessoa.
**Extensão-alvo:** 1 a 2 páginas. Conteúdo excedente pertence ao relatório de produção.

## Localizar o cliente

**Não há caminho fixo.** Descubra a pasta do cliente procurando aquela que contém `config/agente.md`:

```bash
find . -type d -name "$ARGUMENTS" | while read -r d; do [ -f "$d/config/agente.md" ] && echo "$d"; done
```

Mais de um resultado: confirme qual antes de seguir. Nenhum resultado: diga isso e pare — não invente
caminho nem assuma uma convenção de pastas.

---

## Passo 1 — Ler a configuração

Leia `config/agente.md`, `config/variaveis.md`, `config/clienteinfo.json` e `ferramentas/manuais/*.md`.
Extraia: nome do agente · modelo de fluxo · escopo e limites · menu e saudação · variáveis · blocos de
coleta · trilhas e filas · funções de consulta.

## Passo 2 — Obter o atalho de teste

O **atalho de teste** é o dado operacional mais importante do documento: sem ele o cliente não inicia a
validação. Se não estiver na configuração nem no material de origem, **pergunte** — não escreva o relatório
com o campo vazio nem invente um formato.

## Passo 3 — Levantar as pendências que bloqueiam o teste

Toda configuração que dependa de ação **fora do repositório** é pendência: criação de variável na
plataforma, ajuste de JSON Schema, atualização de descrição de função registrada na API, criação de fila,
reapontamento de filtro.

**Pendência é impedimento, não recomendação.** Enquanto ela existir, a validação não reflete a configuração
entregue.

## Passo 4 — Separar pendência de decisão deliberada

São coisas diferentes e hoje se confundem quando aparecem como itens da mesma lista:

| | O que é | Onde entra |
| --- | --- | --- |
| **Pendência** | Falta algo, e isso impede a validação | Seção 3 do relatório |
| **Decisão deliberada** | Está assim de propósito, e alguém vai questionar | Seção 9 do relatório |

*"O agente não valida convênio"* é decisão, não falha — se aparecer entre as pendências, o cliente vai
cobrar a correção de algo que foi combinado.

## Passo 5 — Escrever, nesta ordem

A ordem existe para quem lê **para agir**: veredito, o que bloqueia, e só depois o detalhe.

### 1 · Bloco de identificação

```markdown
# Relatório de Homologação — Agente Virtual [Nome]

| Campo | Conteúdo |
| :--- | :--- |
| **Cliente** | [Razão social ou nome fantasia] |
| **Agente** | [Nome do agente] |
| **Ambiente** | Homologação |
| **Atalho de teste** | `@[atalho]` |
| **Modelo de fluxo** | Interação livre / Estático por menu numerado |
| **Chamado** | [número ou referência] |
| **Data** | DD/MM/AAAA |
| **Revisão** | v1 |
| **Responsável técnico** | [nome] |
```

### 2 · Veredito — três linhas, no máximo

Antes de qualquer detalhe. Responde o que o leitor quer saber em dez segundos:

```markdown
## Veredito

- **O que o agente faz:** [uma linha]
- **Situação:** configuração concluída no repositório · [N] pendências de plataforma em aberto
- **Pode testar?** [Sim / Somente após os itens da seção 3]
```

Sem isto, o leitor monta essa conclusão sozinho lendo o documento inteiro.

### 3 · Pendências de Plataforma

**Vem antes do detalhe, não no rodapé.** É a única seção acionável do relatório; enterrá-la no fim produz
teste falho e reabertura indevida de chamado.

Uma linha por item: o que falta · quem executa · o que não pode ser validado enquanto isso.

**Vedado declarar "pronto para testes" sem qualificação.** Havendo pendência, a redação é:

> *"A configuração no repositório está concluída. A validação em homologação refletirá o comportamento
> entregue após a execução dos [N] itens relacionados nesta seção."*

### 4 · Escopo da entrega

Um parágrafo impessoal: o que foi configurado, sob qual modelo, e **os limites de atuação**.

Declarar o que o agente **não** executa importa mais que enumerar o que executa — evita validação conduzida
com expectativa fora de escopo.

> *"O agente foi configurado sob fluxo estático por menu numerado, com cinco opções e oito trilhas. Não
> realiza agendamento nem confirma horário: qualifica a solicitação, valida os dados coletados e encaminha o
> atendimento à fila correspondente para conclusão pela equipe."*

### 5 · Menu e Saudação

Opções numeradas como são exibidas ao usuário. Saudação transcrita **literalmente**.
Fluxo de interação livre: substituir por *Classificação da Demanda* — como o agente decide a trilha.

### 6 · Variáveis de Contexto

Duas listas: coletadas do usuário e preenchidas pelo agente. Sinalizar as que exigem criação na plataforma.
Forma de runtime — `__IA_CAMPO__`, com os sublinhados — em bloco de código quando a relação for para cópia.

### 7 · Blocos de Coleta

Tabela: bloco · dados coletados · trilhas que o utilizam. Só para fluxos com blocos reutilizáveis.

### 8 · Trilhas e Roteamento

Tabela: trilha · fila de destino · variável de resolução.

**Acrescente uma coluna de motivo onde a decisão não for óbvia.** A tabela diz *o quê* e nunca *por quê* —
"demanda X → fila Y" sem motivo vira a mesma discussão na próxima revisão. Não em toda linha: só onde
alguém questionaria.

### 9 · Decisões Deliberadas

O que está assim **de propósito** e alguém vai questionar. Uma linha cada, com o motivo.
Se não houver nenhuma, escreva "nenhuma" — a seção vazia é informação.

### 10 · Bases de Conhecimento

Uma linha por função de consulta, indicando o conteúdo carregado.

### 11 · Validações Executadas

Relação objetiva das verificações realizadas.

Encerrar com: `Elaborado por [nome] em DD/MM/AAAA.`

## Passo 6 — Salvar e reportar

Salvar em `<pasta do cliente>/relatorios/Relatorio_Homologacao_$ARGUMENTS.md`, criando `relatorios/` se não
existir.

**Controle de revisão dentro do documento.** Nova versão atualiza o campo *Revisão* do bloco de
identificação. **Nunca criar arquivo novo com sufixo** (`_FINAL`, `_v2`, ` copy`): duplicar arquivo impede
identificar a versão vigente.

---

## O que NÃO entra neste relatório

Detalhamento de arquitetura — contextos, tomadas de decisão, omnitags, integrações e lógica de transbordo
passo a passo. Isso é objeto do relatório de produção.

## Common Mistakes

| Erro | Correção |
| --- | --- |
| Pendências no rodapé | Vêm na seção 3, antes do detalhe. É a única seção acionável |
| "Pronto para testes" com pendência aberta | Use a redação qualificada da seção 3 |
| Decisão deliberada listada como pendência | Separar: pendência é falta, decisão é escolha |
| Tabela de trilhas sem motivo | Uma linha de motivo onde a decisão não é óbvia |
| Atalho de teste vazio ou inventado | Perguntar. Sem ele o cliente não começa |
| Detalhar arquitetura aqui | Pertence ao relatório de produção |
| Criar arquivo `_v2` | Atualizar o campo Revisão do mesmo arquivo |
| Emoji ou primeira pessoa | Registro formal e impessoal; o documento vai para chamado |

## Changelog

- **2.0.0** — Autocontida: o modelo do relatório, que vivia em arquivo de template separado, foi inlinado —
  fonte única, sem risco de skill e template divergirem. Caminho fixo de pasta substituído por descoberta
  estrutural. Quatro mudanças de conteúdo, vindas da leitura de uma saída real (11 linhas de tabela, 19
  itens de lista, zero parágrafo de prosa): veredito de três linhas na abertura; pendências promovidas do
  rodapé para a seção 3; coluna de motivo na tabela de trilhas; e separação entre pendência e decisão
  deliberada, que antes se confundiam na mesma lista.
- **1.0.0** — Versão inicial, com modelo em arquivo de template externo.
