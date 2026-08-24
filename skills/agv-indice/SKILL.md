---
name: agv-indice
description: Use quando a pergunta atravessa mais de um cliente, quando não se sabe qual cliente ou qual arquivo contém a resposta, ou quando se quer comparar como clientes diferentes tratam a mesma regra
argument-hint: "[cliente]"
metadata:
  version: "1.0.0"
---

# Índice de Clientes

Mantém e consulta um mapa curto de todas as configurações de agente do workspace, para localizar **em qual
cliente e em qual arquivo** está a resposta antes de abrir arquivo nenhum.

## Quando isto vale — e quando não vale

Esta skill existe por uma conta, e a conta tem lados.

| Situação | O que fazer | Por quê |
| --- | --- | --- |
| Pergunta sobre **um** cliente já identificado | **Não use isto.** Abra `config/agente.md` dele. | Um cliente inteiro custa ~10–30k tokens. O índice só adiciona indireção. |
| Pergunta **lexical** entre clientes ("quais citam a palavra X?") | **Não use isto.** Use `grep -rl`. | Grep é exato e custa zero. |
| Pergunta **semântica** entre clientes ("quais validam convênio contra lista?") | **Use.** | A redação varia entre clientes; grep erra. Ler todos custa a soma dos configs. |
| Não se sabe qual cliente tem a resposta | **Use.** | É exatamente o que o índice responde. |
| Pergunta de **inventário** ("quantos clientes há?", "quais têm agente?") | **Não use isto.** Rode só o Passo 1. | A lista de caminhos já é a resposta; o conteúdo indexado não acrescenta nada. |

**O índice é ponteiro, não fonte.** Ele diz onde olhar. A resposta sai do arquivo, sempre — nunca cite o
índice como se fosse a configuração. Ele pode estar desatualizado, e a diferença entre "o índice diz" e "o
arquivo diz" é a diferença entre auditoria e chute.

---

## Passo 1 — Descobrir os clientes

**Por estrutura, nunca por caminho fixo.** Um cliente é qualquer pasta que contenha `config/agente.md`:

```bash
find . -type f -path '*/config/agente.md' -not -path '*/node_modules/*' | sed 's|/config/agente.md$||' | sort
```

Funciona em qualquer organização de pastas. Se não retornar nada, diga isso e pare — não invente um caminho
nem assuma uma convenção. A mensagem certa é: *"nenhuma pasta com `config/agente.md` encontrada a partir
daqui; rode a partir da raiz do workspace de agentes."*

**Reporte também as pastas que parecem cliente mas não entram**, em uma linha só no fim do índice. Um
workspace real tem cliente em andamento: pasta com `config/` mas sem `agente.md`, ou só com `relatorios/`.
Elas não têm agente para indexar, mas quem lê o índice precisa saber que existem — senão a primeira reação é
achar que o índice perdeu cliente.

```bash
# pastas irmãs das descobertas que não têm config/agente.md
```

Formato sugerido: `> Fora do índice (sem config/agente.md): 12 com config parcial, 7 só com relatórios.`

## Passo 2 — Decidir: construir, atualizar ou consultar

O índice fica em `INDICE-CLIENTES.md`, na raiz comum dos clientes descobertos. Decida pelo disco:

```bash
ls INDICE-CLIENTES.md 2>/dev/null
# clientes cujo config mudou depois do índice:
find . -type f -path '*/config/*' -newer INDICE-CLIENTES.md
# clientes que existem em disco e não estão no índice:
#   comparar a lista do Passo 1 com os títulos "## " do índice
```

| Estado | Ação |
| --- | --- |
| Não existe `INDICE-CLIENTES.md` | Construir do zero (Passo 3), avisando o custo antes |
| Existe, mas há cliente novo ou config alterado | Atualizar **apenas** as entradas afetadas |
| Existe e está em dia | Ir direto ao Passo 4 |

**Nunca reconstrua o índice inteiro para responder uma pergunta.** Reconstruir é ler todos os configs de
novo; atualizar uma entrada é ler um. Se o usuário pediu uma resposta, ele não pediu uma reindexação.

Antes de uma construção do zero, **diga o custo estimado e espere confirmação**: são ~10–30k tokens por
cliente. Com 26 clientes isso passa de 300k. É uma decisão de orçamento, não sua.

## Passo 3 — O formato de cada entrada

Uma entrada por cliente, curta. O índice inteiro precisa caber confortavelmente em contexto — se passar de
~10k tokens, corte descrição, nunca clientes.

```markdown
## <NomeDaPasta>
- **agente:** <nome> · <domínio: clínica de imagem, previdência, laboratório…>
- **escopo:** <o que o agente resolve> | **fora:** <o que ele repassa ou nega>
- **funções:** get_X, get_Y, transferir_atendimento
- **filas:** <ENUM real do cliente>
- **tópicos:** <5 a 12 rótulos curtos>
- **distintivo:**
  - <regra que só este cliente tem, ou que ele resolve diferente dos outros>
  - <2 a 4 itens; é isto que faz a busca semântica funcionar>
- **arquivos:** config/agente.md · N manuais · M JSONs de dados
```

**De onde vem cada campo:**

| Campo | Fonte |
| --- | --- |
| agente, escopo, filas | `config/agente.md` — as quatro seções `##` |
| funções | nomes de `ferramentas/manuais/*.md` |
| tópicos | `graphify-out/.graphify_labels.json` se existir (já são rótulos normalizados); senão, os subtítulos `###` de `config/agente.md` |
| distintivo | leitura do `agente.md`: o que foge do padrão dos outros clientes |
| arquivos | contagem |

**O campo `distintivo` é o que dá valor ao índice.** "Coleta nome e CPF" não distingue ninguém. "Não valida
convênio por decisão do cliente — registra e o humano confere" distingue, e é o que responde pergunta
semântica. Se um cliente não tiver nada distintivo, escreva `— padrão`, e não encha linguiça.

## Passo 4 — Consultar

1. Leia `INDICE-CLIENTES.md` inteiro (é curto, é para isso que ele existe).
2. Identifique os clientes candidatos pela pergunta.
3. **Abra os arquivos desses clientes** e responda a partir deles.
4. Diga quais clientes você descartou e por quê — se o índice fez você descartar um que na verdade
   importava, o usuário consegue ver o erro e corrigir o índice.

Se a pergunta não casar com nenhuma entrada, diga isso em vez de escolher o cliente mais parecido. Índice que
não sabe é informação útil; índice que chuta contamina a resposta.

---

## Privacidade — leia antes de publicar qualquer coisa

O `INDICE-CLIENTES.md` gerado contém **nome de cliente, regra de negócio, fila e escopo**. É material
confidencial de quem opera o workspace.

- **Esta skill é publicável.** Ela não contém dado nenhum — descobre tudo em tempo de execução.
- **O índice gerado não é.** Nem as pastas de cliente.
- Ao versionar, garanta que `INDICE-CLIENTES.md` e as pastas de cliente estejam ignorados, **ou** mantenha o
  repositório das skills separado da árvore que contém os clientes. A segunda opção é a segura: um caminho
  esquecido no ignore publica cliente real, e histórico de git não se apaga depois do push.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Usar o índice para pergunta sobre um cliente só | Abrir o `agente.md` dele é mais barato e mais fiel |
| Usar o índice para pergunta lexical | `grep -rl` é exato e de graça |
| Responder citando o índice | O índice aponta; a resposta sai do arquivo |
| Reconstruir tudo para responder uma pergunta | Atualizar só as entradas alteradas |
| Construir do zero sem avisar o custo | São ~10–30k tokens por cliente; a decisão é do usuário |
| Assumir um caminho de pastas | Descobrir por `config/agente.md` |
| Omitir em silêncio a pasta sem `agente.md` | Contá-las numa linha no fim; some cliente sem aviso, senão |
| Encher `distintivo` com o que todo cliente tem | Se não há distintivo, escrever `— padrão` |

## Changelog

- **1.0.1** — Tabela ganha a linha de pergunta de inventário, que se resolve só com a descoberta do Passo 1.
  Veio de uma execução de verificação que chegou a essa distinção sozinha.
- **1.0.0** — Versão inicial. Descoberta por estrutura, decisão de frescor pelo disco, índice como ponteiro e
  não como fonte.
