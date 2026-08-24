---
name: agv-relatorio-prod
description: Use somente quando o usuário pedir explicitamente o relatório completo de arquitetura (versão final, produção) de um cliente — fluxos, variáveis, filas, funções, omnitags e lógica de transbordo. Não usar para criar nem auditar agente.
argument-hint: "[cliente]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash
metadata:
  version: "2.0.0"
---

# Relatório de Produção (Completo)

Gera a **documentação técnica de versão final** de `$ARGUMENTS`, para anexo em chamado de entrega e consulta
posterior em manutenção. Registra a arquitetura do agente após homologação aprovada.

**Finalidade:** responder *"como esta configuração opera"* sem que o leitor precise abrir os arquivos do
repositório — inclusive meses depois, por alguém que não participou da implementação.

## Esta skill é autocontida

O modelo do relatório está inteiro aqui — não há arquivo de template externo a consultar. Se existir um e ele
**contradisser** este arquivo, pare e diga qual é a divergência.

**Registro:** formal e impessoal. Sem emoji, sem interjeição, sem primeira pessoa.
**Extensão-alvo:** a exigida pela arquitetura. Completude prevalece sobre concisão.

## Localizar o cliente

**Não há caminho fixo.** Descubra a pasta do cliente procurando aquela que contém `config/agente.md`:

```bash
find . -type d -name "$ARGUMENTS" | while read -r d; do [ -f "$d/config/agente.md" ] && echo "$d"; done
```

Mais de um resultado: confirme qual antes de seguir. Nenhum resultado: diga isso e pare — não invente
caminho nem assuma uma convenção de pastas.

---

## Passo 1 — Ler toda a configuração

`config/agente.md`, `config/variaveis.md`, `config/clienteinfo.json`, todos os
`ferramentas/manuais/*.md` e os `ferramentas/dados/*.json`. O relatório de produção documenta a arquitetura
inteira; leitura parcial produz documento que não substitui abrir os arquivos.

## Passo 2 — Reunir as decisões deliberadas

Toda escolha **não dedutível dos arquivos** precisa da justificativa junto, senão volta como questionamento
ou é revertida em manutenção — reintroduzindo o problema que a decisão resolvia. Procure por:

- Enum com grafia própria (caixa alta, sem acento, nome comercial) e a consequência de normalizá-lo
- Coleta assimétrica entre trilhas — dado exigido num bloco e dispensado em bloco equivalente
- Dado deliberadamente fora de escopo
- Correção aplicada sobre texto do cliente (erro de digitação em enum, endereço, URL)
- Sentinela explícita onde o valor significa "todos" ou "não se aplica"

## Passo 3 — Reunir as travas, não só os caminhos

Documentação restrita ao fluxo bem-sucedido não permite diagnosticar incidente em produção. Levante: o que o
agente **não** afirma na ausência de dado · o que não deduz · o comportamento quando o dado falta (sentinela,
fallback, encaminhamento) · limite de tentativas e consequência do esgotamento · limites de domínio.

## Passo 4 — Escrever, nesta ordem

### 1 · Bloco de identificação e histórico

```markdown
# Relatório de Configuração — Agente Virtual [Nome]

| Campo | Conteúdo |
| :--- | :--- |
| **Cliente** | [Razão social ou nome fantasia] |
| **Agente** | [Nome do agente] |
| **Ambiente** | Produção |
| **Atalho de teste** | `@[atalho]` |
| **Modelo de fluxo** | Interação livre / Estático por menu numerado |
| **Chamado** | [número ou referência] |
| **Data** | DD/MM/AAAA |
| **Revisão** | v1 |
| **Responsável técnico** | [nome] |

## Histórico de Revisões

| Revisão | Data | Alteração |
| :--- | :--- | :--- |
| v1 | DD/MM/AAAA | Emissão inicial. |
```

O histórico é **obrigatório** aqui. Substitui versionar por nome de arquivo, prática que impede identificar
a versão vigente.

### 2 · Veredito — três linhas, no máximo

Antes de qualquer detalhe. É o que um leitor futuro precisa saber antes de decidir se vai ler o resto:

```markdown
## Veredito

- **O que o agente faz:** [uma linha]
- **O que ele deliberadamente não faz:** [uma linha]
- **Limitações que afetam operação:** [N] itens registrados na seção 4
```

### 3 · Limitações Conhecidas

**Promovida para perto do topo.** Dado não fornecido pelo cliente · validação executada na plataforma e não
pelo modelo · campo que invariavelmente chega vazio ao atendente · comportamento dependente de configuração
externa ao repositório.

Omitir esta seção transfere a limitação para descoberta em produção. Enterrá-la no rodapé de um documento
longo tem o mesmo efeito prático.

### 4 · Fluxos e Navegação

Um item por contexto, interação ou tomada de decisão, com **Tipo** e **Ação/Lógica**. Nas tomadas de
decisão, identificar a variável analisada e o resultado produzido por cada valor.

### 5 · Argumentos de Coleta (Variáveis)

Tabela: `Variável | Regra de Validação e Comportamento | Obrigatoriedade`.

Registrar comportamento efetivo, não apenas formato. *"Exigido por digitação mesmo havendo carteirinha
anexada"* tem valor documental; *"campo texto"* não tem.

### 6 · Contextos e Filas

Tabela: destino · comportamento · gatilho. Identificar expressamente qual valor corresponde a encerramento
automático e qual corresponde a fila humana.

Relacionar também os valores do enum **não alcançados por nenhum fluxo**, com a justificativa. Valor
inalcançável não documentado é lido como omissão e reintroduzido em manutenção futura.

### 7 · Instruções de Sistema (Funções)

Tabela: função e objetivo. Uma linha por função de consulta e uma para a de transbordo. Descrever o papel da
função no fluxo, não o conteúdo do arquivo de dados.

### 8 · Omnitags (Métricas)

Agrupar por Fluxo, Serviço Demandado e Serviço Realizado. Identificar as etiquetas dinâmicas que recebem
valor de variável.

### 9 · Lógica de Decisão e Transbordo

Sequência numerada. Contemplar processamento de imagem quando aplicável, os cenários de transbordo e o de
encerramento automático.

### 10 · Integrações de API

Só quando o fluxo consultar ou gravar em sistema externo. Tabela: endpoint e objetivo no fluxo.

### 11 · Decisões Técnicas Registradas

**Seção obrigatória.** É o que diferencia este relatório do resumido. Cada decisão do Passo 2 com a
justificativa ao lado — sem ela, a decisão volta como questionamento.

### 12 · Limites de Atuação e Travas

**Seção obrigatória.** O material do Passo 3.

## Passo 5 — Regra de leitura

**Cada seção abre com uma linha em itálico delimitando seu escopo.** Permite localizar a seção pertinente
sem ler o documento inteiro — é o que torna um documento longo consultável.

Variáveis na forma de runtime: `__IA_CAMPO__`.

## Passo 6 — Salvar e reportar

Salvar em `<pasta do cliente>/relatorios/Relatorio_Producao_$ARGUMENTS.md`, criando a pasta se não existir.

Se já existir relatório final, **não sobrescrever em silêncio** — mostrar o que muda e confirmar. Nova versão
acrescenta linha ao Histórico de Revisões e atualiza o campo *Revisão*. **Nunca criar arquivo com sufixo**
(`_FINAL`, `_v2`, ` copy`).

---

## Common Mistakes

| Erro | Correção |
| --- | --- |
| Limitações no rodapé de um documento longo | Seção 3, perto do topo. Enterrada equivale a omitida |
| Documentar só o caminho feliz | As travas são o que permite diagnosticar incidente |
| Decisão sem justificativa | Volta como questionamento ou é revertida em manutenção |
| Omitir valor de enum não alcançado | É lido como omissão e reintroduzido depois |
| Seção sem a linha de escopo em itálico | O documento deixa de ser consultável por seção |
| Descrever o conteúdo do JSON em vez do papel da função | O leitor quer saber o que a função faz no fluxo |
| Criar arquivo `_v2` | Acrescentar linha ao Histórico de Revisões |
| Sobrescrever relatório final em silêncio | Mostrar o diff e confirmar |

## Changelog

- **2.0.0** — Autocontida: o modelo, que vivia em arquivo de template separado, foi inlinado — fonte única,
  sem risco de skill e template divergirem. Caminho fixo substituído por descoberta estrutural. Removidos os
  exemplos que apontavam para arquivos de cliente e de `Utilitários/`, que não acompanham a publicação da
  skill. Duas mudanças de conteúdo: veredito de três linhas na abertura, e Limitações Conhecidas promovida
  do rodapé para a seção 3. As outras duas propostas — motivo junto da decisão e separação entre decisão e
  pendência — já existiam aqui nas seções de Decisões Técnicas e Limites de Atuação.
- **1.0.0** — Versão inicial, com modelo em arquivo de template externo.
