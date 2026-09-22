---
type: llm
weight: 2
---

A resposta aponta que os manuais estão fora do padrão de seções.

Conta como acerto se disser **qualquer uma** destas coisas sobre `ferramentas/manuais/*.md`:

- os três manuais têm 3 seções quando o esperado são 2; ou
- os rótulos das seções estão desatualizados (`Descrição da Função`, `Diretrizes de Prompt`,
  `Exemplos Práticos de Diálogos`) e deveriam ser `Objetivo da Função` e `Condições de Execução`; ou
- a seção de exemplos não tem campo correspondente na plataforma e por isso não chega ao modelo.

Ganha ponto extra, mas não é obrigatório, se notar que a §2 é sempre-ativa e que por isso a tabela de
filas duplicada entre `config/agente.md` e a §2 de `set_transbordo.md` custa token, não só deriva.

**Não** conta como acerto uma observação genérica de que "os manuais poderiam ser melhorados".
