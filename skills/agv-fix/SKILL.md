---
name: agv-fix
description: Use somente quando o usuário pedir explicitamente para aplicar correções em um agente virtual já auditado, nomeando o cliente, e houver um plano de correção aprovado. Não usar para auditar, para criar agente novo, nem para "melhorar" configuração por conta própria.
argument-hint: "[cliente]"
arguments: [cliente]
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
metadata:
  version: "1.0.0"
---

# Aplicar Correções em Agente Virtual

Aplica, na configuração de `$ARGUMENTS`, **os itens que o usuário aprovou** de um plano de correção que já
existe. Fecha o ciclo auditar → corrigir.

## Esta skill não diagnostica

A auditoria propõe e não aplica; esta aplica e não propõe. A separação é deliberada e é o que impede uma
auditoria de "consertar" configuração correta para satisfazer um falso positivo.

Consequências, todas obrigatórias:

- **Sem plano aprovado, não escreva nada.** Não vale reconstruir o plano auditando agora.
- **Não acrescente achado.** Encontrando algo fora do plano enquanto lê, **anote e reporte no fim** — não
  corrija. Quem decide se aquilo é defeito é o usuário, com a auditoria na mão.
- **Não "aproveite para melhorar".** Renomear variável, enxugar prosa, reordenar seção, padronizar emoji:
  nada disso entra sem estar no plano. Diff que faz mais do que foi aprovado é diff que ninguém revisa.

*Motivo:* medido no comportamento destes agentes — a correção que ninguém pediu é a que volta como bug
duas semanas depois, e o usuário não tem como saber o que mudou porque o diff virou ruído.

## Esta skill é autocontida

Tudo que ela precisa está aqui. **Não** consulte convenções externas nem a configuração de outro cliente.
Havendo convenções externas que **contradigam** este arquivo, pare e diga qual é a divergência.

## Localizar o cliente

**Não há caminho fixo.** Descubra a pasta procurando aquela que contém `config/agente.md`:

```bash
find . -type d -name "$ARGUMENTS" | while read -r d; do [ -f "$d/config/agente.md" ] && echo "$d"; done
```

Mais de um resultado: confirme qual antes de seguir. Nenhum: diga isso e pare.

---

## Passo 0 — Obter o plano e o aceite. **Antes** de ler o cliente.

Duas coisas, e as duas são bloqueantes:

| | O que é |
|---|---|
| **O plano** | O relatório da auditoria, colado no comando, em `relatorios/`, ou na conversa acima |
| **O aceite** | Quais itens aplicar. "Todos" é resposta válida; silêncio não é |

Não tendo o plano, **pare e peça**. Não tendo o aceite, liste os itens numerados e pergunte quais entram
(no Claude Code, a ferramenta `AskUserQuestion`).

**Se não houver como perguntar** — execução automatizada, runtime sem mecanismo de pergunta — a regra é a
mesma, nunca mais frouxa: pare, diga o que faria e não escreva. *A ausência da ferramenta de perguntar não
é permissão para decidir no lugar do usuário.*

Exiba a lista do que vai aplicar antes de tocar em arquivo. Um item por linha, com o arquivo que muda.

---

## Passo 1 — Ler tudo antes de escrever qualquer coisa

`config/agente.md` · `config/variaveis.md` · `config/clienteinfo.json` · todos os
`ferramentas/manuais/*.md` · todos os `ferramentas/dados/*.json` **quando existirem**.

**Correção aplicada sem ler o conjunto quebra outra coisa.** Metade das regras destes agentes vive em dois
arquivos que precisam concordar: trocar a fila no prompt e não trocar no dicionário produz um defeito pior
do que o original, porque agora os dois lados se contradizem em silêncio.

Em particular, antes de editar, saiba **onde mais** aparece o que você vai mudar:

```bash
grep -rn "<o valor que muda>" config/ ferramentas/
```

---

## Passo 2 — Aplicar, item por item

Um item por vez. Para cada um:

1. **Releia o trecho** que o plano cita, no arquivo. Se o que está lá não bate com o que o plano descreve,
   **pare nesse item** e reporte: o arquivo mudou desde a auditoria, e aplicar às cegas sobrescreve o que
   mudou.
2. **Aplique a correção do plano**, não uma variação sua dela.
3. **Propague.** Se o valor aparece em outro arquivo (Passo 1), corrija lá também — isso não é
   acrescentar achado, é completar o item.
4. **Marque o item como aplicado**, para o relatório.

### O que exige parar e perguntar, em vez de decidir

| Situação | Por quê |
|---|---|
| O plano diz "definir com o cliente" | Não invente o valor. É dado de cliente, e ficha em branco é melhor do que palpite |
| Duas correções do plano se contradizem | Aplicar as duas na ordem produz um resultado que ninguém aprovou |
| A correção exige nome de fila, convênio, unidade ou URL que não está no plano | Nunca inventar identificador. Grafia divergente é transbordo perdido, e não dá erro visível |
| O item pede remover uma regra de segurança ou de limite de atuação | Confirmar explicitamente. Domínio regulado exige essas regras mesmo que o cliente não peça |

---

## Passo 3 — Reestruturar arquivo exige round-trip. **Antes** de salvar.

Vale quando o item **move ou reorganiza** conteúdo, em vez de trocar um valor: fundir funções, renomear
seções de manual, migrar estrutura de pastas, reescrever o dicionário de variáveis.

**A pasta do cliente não está sob controle de versão.** Não existe `git checkout` para desfazer.

O round-trip:

1. Antes de escrever, liste **todos** os campos, chaves e regras do arquivo original.
2. Escreva o arquivo novo.
3. Reconstrua a lista a partir do resultado.
4. Compare as duas listas, campo a campo.

Faltando qualquer coisa na segunda lista, **restaure e recomece**. Um campo perdido numa reestruturação já
se perdeu para sempre neste tipo de pasta.

Guarde uma cópia do original antes de reestruturar, e só a descarte depois da comparação.

---

## Passo 4 — Verificação mecânica

Rodar **todas**, depois de aplicar tudo. São as mesmas que governam a criação:

```bash
# o prompt tem exatamente 4 seções
grep -c '^## ' config/agente.md

# todo manual tem exatamente 2 seções
for f in ferramentas/manuais/*.md; do echo "$(grep -c '^## ' "$f") $f"; done

# negrito duplo no que vira prompt
grep -n '\*\*' config/agente.md

# caminho de arquivo ou número de seção citado no prompt
grep -nE 'config/|ferramentas/|§[0-9]' config/agente.md

# despedida ou aviso de transferência: quem envia é a plataforma
grep -niE 'vou (te )?transferir|estou (te )?encaminhando|vou encerrar' config/agente.md

# variável declarada e ausente do card
comm -23 <(grep -oE '^\| `_{0,2}[A-Z][A-Z0-9_]+_{0,2}`' config/variaveis.md | grep -oE '[A-Z][A-Z0-9_]+' | sed 's/_*$//' | sort -u) \
         <(grep -oE '[A-Z][A-Z0-9_]{2,}' config/clienteinfo.json | sed 's/_*$//' | sort -u)

# JSONs válidos
python -c "import json;json.load(open('config/clienteinfo.json',encoding='utf-8'))"
[ -d ferramentas/dados ] && for f in ferramentas/dados/*.json; do python -c "import json,sys;json.load(open(sys.argv[1],encoding='utf-8'))" "$f" || echo "INVALIDO: $f"; done

# valor ambíguo nos dados
[ -d ferramentas/dados ] && grep -n '\[\]\|null' ferramentas/dados/*.json

# grafia de fila consistente entre os arquivos do cliente
grep -rhoE '\b[A-Z][a-z]+_[A-Za-z_]+\b' config/ ferramentas/ | sort | uniq -c | sort -rn | head
```

**Verificação que falha é correção incompleta**, não ruído a ignorar. Conserte antes de reportar pronto.

Rodar as verificações **não** é rodar o agente: nenhuma delas é execução no modelo. Não chame o resultado
de aprovação.

---

## Passo 5 — Relatório

1. **Itens aplicados**, um por linha, com o arquivo e o que mudou em uma frase.
2. **Itens não aplicados**, com o motivo: fora do aceite, bloqueado por dado de cliente que falta, ou o
   arquivo não bate mais com o plano.
3. **O que você viu e não corrigiu** — os achados fora do plano, como observação, para o usuário decidir.
   Nunca aplicados nesta passada.
4. **Resultado das verificações mecânicas**, incluindo as que falharam e o que você fez.
5. **O que precisa ser refeito na plataforma**: variável a recadastrar, função a reregistrar, fila a criar
   com a grafia exata. Correção em arquivo não se propaga sozinha para a plataforma.

Havendo matriz de homologação em `relatorios/homologacao.md`, diga **quais casos dela** as correções
afetam, para serem retestados. Não marque caso nenhum como aprovado: esta skill não executa o agente.

---

## Common Mistakes

| Erro | Correção |
|---|---|
| Reauditar em vez de aplicar | Sem plano aprovado, pare e peça. Esta skill não diagnostica |
| Corrigir achado novo encontrado no caminho | Reporte como observação no Passo 5. Quem decide é o usuário |
| Aproveitar para padronizar o resto | Diff maior do que o aprovado é diff que ninguém revisa |
| Editar um lado de uma regra que vive em dois arquivos | Passo 1 existe para achar o outro lado |
| Reestruturar sem round-trip | A pasta não está no git. Campo perdido não volta |
| Inventar fila, convênio ou URL que o plano não trouxe | Grafia divergente é transbordo perdido, sem erro visível |
| Chamar verificação mecânica de aprovação | Nenhuma delas roda o agente no modelo |

## Changelog

- **1.0.0** — Versão inicial. Fecha o ciclo auditar → corrigir, que antes era pedido em conversa a cada
  vez. O desenho preserva a separação entre diagnosticar e escrever: recebe plano aprovado e aplica item a
  item, sem reauditar e sem acrescentar achado. O Passo 3 (round-trip antes de reestruturar) existe porque
  a pasta do cliente não está sob controle de versão, e uma reestruturação sem ele já perdeu um campo para
  sempre.
