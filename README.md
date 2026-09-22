# agent-builder

<p>
  <img alt="plugin" src="https://img.shields.io/badge/plugin-v2.0.0-1f6feb">
  <img alt="skills" src="https://img.shields.io/badge/skills-8%20ativas-2da44e">
  <img alt="custo" src="https://img.shields.io/badge/sempre--ativo-~441%20tok-8250df">
  <img alt="padrão" src="https://img.shields.io/badge/padr%C3%A3o-Agent%20Skills-555555">
  <img alt="validação" src="https://img.shields.io/badge/valida%C3%A7%C3%A3o-RED%20%2F%20GREEN-bf8700">
</p>

Skills para **criar, auditar e documentar agentes virtuais de atendimento por WhatsApp** baseados em
OpenAI Function Calling.

---

## Por que isto existe

Configurar um agente de atendimento é escrever um contrato: o que ele pode afirmar, o que precisa
perguntar antes de agir, e para quem passa a bola quando não sabe. O trabalho não é difícil. É fácil de
fazer *quase* certo, e o quase não aparece em teste.

Os defeitos que chegam em produção se repetem: regra obrigatória num arquivo que o modelo nunca recebe,
convênio deduzido de outro parecido, pergunta repetida depois de já respondida, transbordo apontando para
uma fila fora do enum e descartado em silêncio. Nada disso é erro de digitação. É erro de arquitetura de
prompt, e só aparece comparando arquivos entre si.

Este plugin transforma esse acúmulo em processo. **Cada regra vem com o motivo ao lado**, porque regra sem
motivo é regra que a próxima revisão "simplifica", trazendo de volta o defeito que ela evitava.

▸ **Para quem opera** configuração de agentes de pré-atendimento e precisa que a próxima pessoa consiga
revisar o que foi feito.
▸ **Autocontidas.** Cada skill traz por dentro as regras, os formatos e os critérios de verificação. Não
dependem de documento externo nem de pasta fixa: a pasta do cliente é descoberta pelo conteúdo, e quando
não existe nenhuma a skill pergunta onde criar.

---

## Instalação

As skills seguem o padrão aberto [Agent Skills](https://agentskills.io), então rodam nos três runtimes.
Instaladas, valem em **qualquer projeto**: não é preciso clonar o repositório nem montar pasta.

### Claude Code

```bash
claude plugin marketplace add https://github.com/arthuld/agent-builder
```

```bash
claude plugin install agent-builder@agent-builder
```

### Antigravity CLI (`agy`)

Gerenciador de plugin próprio, no mesmo padrão do Claude Code:

```bash
agy plugin install agent-builder@agent-builder
```

O alvo aceita `plugin@marketplace`; `agy plugin list` mostra o que está importado. Quem vinha do Gemini CLI
tem ainda `agy plugin import gemini`, que traz as extensões já instaladas lá.

### opencode

Não tem comando de instalação: descobre por diretório. Clone e copie as pastas `agv-*` para
`~/.agents/skills/`, caminho interoperável lido tanto pelo opencode quanto pelo Antigravity
(`~/.config/opencode/skills/` também serve, mas só o opencode):

```powershell
git clone https://github.com/arthuld/agent-builder.git; New-Item -ItemType Directory -Force ~/.agents/skills; Copy-Item -Recurse -Force agent-builder/skills/agv-* ~/.agents/skills/
```

Copie **apenas** as pastas `agv-*`: o opencode varre subdiretórios em profundidade, então uma pasta de
skills fora de circulação colocada ali seria carregada como skill ativa. Como é cópia e não instalação,
**precisa ser refeita a cada atualização**, porque não há update automático. Num projeto que já tenha
`.agents/skills/`, o opencode lê dali direto, sem instalação nenhuma.

> **Repositório privado.** A instalação exige que o git da máquina tenha acesso. Colaborador adicionado no
> GitHub consegue; terceiro sem acesso, não.

---

## As oito skills

| Skill | O que você recebe no fim | Alcance |
|---|---|---|
| `/agv-novo-dinamico` | A configuração de um agente de **interação livre**: o usuário escreve o que quer, o agente classifica a demanda e conduz. Pasta completa, pronta para colar nos campos da plataforma | um cliente |
| `/agv-novo-estatico` | A configuração de um agente **de menus numerados**, que ainda responde pergunta feita fora do menu em vez de repetir as opções | um cliente |
| `/agv-novo-clinux` | A configuração de um agente de **autoagendamento integrado** ao clinux-genesis: as funções são endpoints reais e o caminho feliz termina em gravação, não em transbordo | um cliente |
| `/agv-auditoria` | Um **plano de correção aprovável**, item por item, com arquivo, linha e o efeito em produção de cada defeito. Cinco dimensões: fluxo, lógica, segurança, conduta, eficiência. **Propõe e não aplica** | um cliente |
| `/agv-fix` | A configuração **corrigida**, aplicando só os itens do plano de auditoria que você aprovou. Não reaudita, não acrescenta achado, não aproveita para melhorar o resto | um cliente |
| `/agv-relatorio-homolog` | O **documento curto de entrega para teste**: como acionar, o menu, as variáveis, e a lista de pendências de plataforma que impedem a validação de fechar | um cliente |
| `/agv-relatorio-prod` | A **documentação de arquitetura da versão final**: fluxos, filas, variáveis, funções, lógica de transbordo, decisões deliberadas e limitações conhecidas | um cliente |
| `/agv-indice` | Um **mapa curto de todos os clientes**, para achar em qual deles e em qual arquivo está a resposta | atravessa clientes |

Futura: `/agv-novo-animati`, integração animati-netpacs.

### Qual usar

▸ **Vou criar de zero.** O usuário final vai digitar livremente o que precisa? `dinamico`. Vai escolher
opções numeradas? `estatico`. O agendamento grava direto no sistema da clínica? `clinux`.
▸ **O agente já existe e algo está errado.** `auditoria`. Ela diagnostica e devolve o plano; a correção
você pede em conversa depois de aprovar.
▸ **A auditoria já rodou e você aprovou o plano.** `fix`. Aplica item por item o que você marcou, e
reporta separado o que viu e não corrigiu.
▸ **O agente já existe e está certo.** `relatorio-homolog` para mandar para teste,
`relatorio-prod` para registrar o que foi entregue.
▸ **Não sei nem em qual cliente isso está.** `indice`.

### Custo

Só as descrições ficam sempre-ativas; o corpo da skill é lido no momento em que ela dispara. Números da
v2.0.0, antes da entrada da `agv-fix`.

| | Sempre-ativo | Ao disparar |
|---|---|---|
| Conjunto das 8 | **~441 tok** por sessão | n/a |
| `agv-novo-dinamico` | ~60 | ~13,1k |
| `agv-novo-estatico` | ~70 | ~12,8k |
| `agv-auditoria` | ~60 | ~6,2k |
| `agv-novo-clinux` | ~70 | ~4,4k |
| `agv-relatorio-homolog` | ~70 | ~2,5k |
| `agv-relatorio-prod` | ~70 | ~2k |
| `agv-indice` | ~50 | ~1,9k |

Medido com `claude plugin details agent-builder` na v2.0.0. São estimativas do runtime, não faturamento.

Não confunda este custo com o do **agente gerado**. Aqui se mede o que as skills custam na sua sessão de
Claude Code. O agente que elas produzem roda em `gpt-5.4-nano` na plataforma do cliente, e o sempre-ativo
dele são outros: os 4 campos do prompt mais o *Objetivo da Função* e as *Condições de Execução* de cada
função, reenviados a cada turno.

---

## Os dois tipos de agente

Metade dos critérios de auditoria vale para um tipo só, e aplicar os critérios errados produz ruído de
alta gravidade. As skills detectam o tipo antes de julgar qualquer coisa: pelos sinais abaixo, não pelo
nome da pasta.

| Sinal | Base de conhecimento | Integrado |
|---|---|---|
| Dados | `ferramentas/dados/*.json` estáticos | endpoints do sistema do cliente |
| Nome de variável | `__IA_CAMPO__` | nome do parâmetro do endpoint |
| Fim do caminho feliz | transbordo para humano | gravação no sistema |
| Sentinela de ausência | três estados, declarados no `enum` | proibida em campo obrigatório: retém a chamada e pergunta |
| Retorno vazio | pode indicar ausência na base | **nunca** autoriza negar; só a lista de exclusão explícita |

---

## Como usar

### Criar um agente

```
/agv-novo-dinamico MeuCliente
```

**A skill para e pergunta antes de escrever.** Ela monta uma ficha de parâmetros com cada linha preenchida
ou marcada `[PERGUNTAR]`, e qualquer `[PERGUNTAR]` bloqueia. São bloqueantes: onde criar a pasta, grafia
comercial do cliente, nome e gênero do agente, saudação literal, filas reais e cada regra de negócio.

**O material do cliente chega de duas formas, e as duas funcionam:** arquivos numa pasta `origem/`, ou
colados direto no comando ao invocar a skill. Nenhuma é obrigatória e nenhuma tem precedência: o que
existir vira fonte primária, e o que vier colado é salvo em `origem/` para ficar registrado.

### A estrutura que a skill gera

```
MeuCliente/
├── config/
│   ├── agente.md          system prompt: perfil, diretrizes, conduta, segurança
│   ├── variaveis.md       dicionário das variáveis de contexto
│   └── clienteinfo.json   card do atendente
├── ferramentas/
│   ├── dados/             get_*.json, bases de conhecimento
│   └── manuais/           get_*.md + a função de transbordo
├── origem/                material bruto recebido do cliente
└── relatorios/
```

As quatro seções `##` de `config/agente.md` correspondem exatamente aos quatro campos da tela da
plataforma: Perfil, Diretrizes, Conduta e Segurança. Uma quinta seção não teria onde ser colada.

O mesmo vale para os manuais: as duas seções são `Objetivo da Função` e `Condições de Execução`, os dois
campos que a plataforma abre por função. **As duas são sempre-ativas**, reenviadas em todo turno junto com
o schema. Não existe seção de exemplos, porque não há um terceiro campo para colá-la.

Onde essa pasta nasce depende do seu workspace: a skill procura clientes já montados e coloca o novo ao
lado; não achando nenhum, pergunta.

### Auditar e documentar

```
/agv-auditoria MeuCliente          → plano de correção, aprovável
/agv-fix MeuCliente                → aplica o plano aprovado, item por item
/agv-relatorio-homolog MeuCliente  → relatório de entrega para teste
/agv-relatorio-prod MeuCliente     → documentação final de arquitetura
```

A auditoria **propõe e não aplica**, e a `agv-fix` aplica e não propõe. A separação entre diagnosticar e
escrever é o que impede uma auditoria de "consertar" configuração correta para satisfazer um falso
positivo, e é por isso que a `fix` exige um plano aprovado em vez de reauditar por conta própria. Ela também separa
**achado de observação**: sem critério para julgar, o item é reportado como observação. Auditoria que
classifica dúvida como defeito faz o cliente corrigir o que estava certo.

### Achar coisas entre clientes

```
/agv-indice qual cliente valida convênio contra lista?
```

Para pergunta que **atravessa** clientes. Para pergunta sobre um cliente só, abrir o `config/agente.md`
dele é mais barato, e a skill diz isso em vez de fazer trabalho desnecessário.

---

## Como as skills são construídas

Cada uma passa por **RED / GREEN / REFACTOR** com subagentes: mede-se o comportamento sem a skill,
escreve-se contra as falhas observadas e valida-se contra um braço de controle. Sem controle não há como
saber se a skill agrega ou se o modelo acertaria sozinho.

O método pega o que revisão de código não pega:

▸ Uma skill de criação **perdeu para o próprio controle**: 8/8 sem skill contra 7/8, 8/8 e 7/8 com ela.
Foi arquivada e reescrita.
▸ Uma auditoria sem skill escreveu o encerramento como mensagem (*"estou te encaminhando"*) em vez de
execução da função, e inventou uma exceção à entrega única.
▸ Duas correções vieram de execuções de teste que **rejeitaram a regra recém-escrita e estavam certas**.
▸ O critério de formato de prompt entrou com baseline de **0/3** apontando o defeito e **3/3** achando o
defeito-controle plantado no mesmo arquivo, prova de que a lacuna era de critério, não de atenção.

O controle é o que torna um GREEN interpretável. Um braço de tratamento que acerta sozinho não provou
nada; um braço de controle que erra o alvo mas acerta um defeito vizinho provou exatamente onde estava o
buraco.

---

## Estado atual

| Skill | Versão | Validação |
|---|---|---|
| `agv-auditoria` | 2.2.0 | GREEN 3/3 no formato de prompt, baseline 0/3 · GREEN 2/2 anterior · casos sem critério de julgamento: 5 → 0 e 1 |
| `agv-novo-estatico` | 2.2.0 | GREEN 3/3 + 2 execuções extras · controle falhou no encerramento |
| `agv-novo-dinamico` | 1.2.0 | GREEN 3/3 · controle empatou; o ganho é portabilidade |
| `agv-novo-clinux` | 1.2.0 | GREEN 3/3 |
| `agv-relatorio-homolog` | 2.0.0 | GREEN 1/1 |
| `agv-relatorio-prod` | 2.0.0 | GREEN 1/1 |
| `agv-indice` | 1.0.0 | 4/4 na tabela de decisão |

A regra de destino de pasta, comum às três skills de criação, tem GREEN próprio: **5/5**, cobrindo as duas
ramificações. Em diretório vazio (dinâmico ×2, estático, clinux) as quatro execuções marcaram o destino
como bloqueante e escreveram **zero arquivos**. Uma delas recusou explicitamente a convenção de pastas
que estava no contexto ambiente, por a skill se declarar autocontida. Com um cliente já montado ao lado, a
execução criou a pasta na mesma altura sem perguntar, e não abriu a configuração do vizinho.

### O que ainda falta

| Item | Situação |
|---|---|
| **Suíte de evals** | `claude plugin eval` existe e o repositório não tem `evals/`. Hoje toda validação é subagente ad-hoc, refeita à mão a cada mudança. Uma suíte transformaria os GREEN já obtidos em regressão automática, o maior ganho de manutenção disponível |
| **`/agv-fix`** | Não existe. A auditoria propõe e a correção é pedida em conversa. Fecharia o ciclo auditar → corrigir com validação própria |
| **`/agv-novo-animati`** | Não existe. Integração animati-netpacs |
| **Variância dos GREEN de relatório** | `agv-relatorio-homolog` e `agv-relatorio-prod` têm uma execução cada. As mudanças são estruturais, aparecem ou não, mas a variância nunca foi medida |
| **LICENSE** | O manifesto declara `UNLICENSED` e não há arquivo. Irrelevante enquanto o repositório for privado |
| **Instalação no Antigravity ponta a ponta** | O `agy` está instalado e os subcomandos foram conferidos no binário. O que não foi feito é instalar **este** repositório por ali e abrir uma sessão para confirmar que as sete skills aparecem, como foi feito no opencode (`opencode debug skill`: 7 de 7) |

---

## Editar uma skill e republicar

Editar skill é editar `skills/<nome>/SKILL.md` **neste repositório**. Uma cópia local em
`.claude/skills/` não tem efeito nenhum no que roda.

Commit e push sozinhos **não** bastam: o marketplace é um clone git em cache, e sem atualizá-lo o
install continua servindo o commit antigo:

```bash
git push origin main
```

```bash
claude plugin marketplace update agent-builder
```

```bash
claude plugin update agent-builder
```

Depois, **reiniciar**. A CLI avisa *"Restart to apply changes"*, e a sessão em curso segue com a versão
velha até lá.

**Sintoma de que faltou republicar:** a skill que roda divergiu da fonte. Para conferir:

```bash
diff -rq --strip-trailing-cr skills ~/.claude/plugins/cache/agent-builder/agent-builder/<versão>/skills
```

O `--strip-trailing-cr` não é opcional: sem ele **todo** arquivo aparece como diferente, por causa de
CRLF, e o diagnóstico real se perde no ruído.

> `.agents/skills/` é espelho local para os runtimes que descobrem por diretório, e é gitignored. `git add`
> nele falha, e dentro de um `&&` isso aborta o commit inteiro.

---

## Configuração de cliente nunca entra aqui

Este repositório é o plugin: manifesto, skills e este README. Os clientes e suas configurações ficam no
workspace de quem opera, e o `.gitignore` protege contra o engano, mas ele é a última linha, não a
primeira. Caminho novo que ninguém previu não está coberto. Antes de qualquer commit:

```bash
git status --short
```

Histórico de git não se apaga depois do push. Um relatório com nome de cliente, regra de negócio e fila
publicado num repositório de plugin não volta atrás.
