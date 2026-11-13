# agent-builder

<p>
  <img alt="plugin" src="https://img.shields.io/badge/plugin-v2.1.1-1f6feb">
  <img alt="skills" src="https://img.shields.io/badge/skills-8%20ativas-2da44e">
  <img alt="custo" src="https://img.shields.io/badge/sempre--ativo-~512%20tok-8250df">
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
é a `fix`, depois de você aprovar.
▸ **A auditoria já rodou e você aprovou o plano.** `fix`. Aplica item por item o que você marcou, e
reporta separado o que viu e não corrigiu.
▸ **O agente já existe e está certo.** `relatorio-homolog` para mandar para teste,
`relatorio-prod` para registrar o que foi entregue.
▸ **Não sei nem em qual cliente isso está.** `indice`.

### Custo

Só as descrições ficam sempre-ativas; o corpo da skill é lido no momento em que ela dispara.

| | Sempre-ativo | Ao disparar |
|---|---|---|
| Conjunto das 8 | **~512 tok** por sessão | n/a |
| `agv-novo-dinamico` | ~60 | ~13,6k |
| `agv-novo-estatico` | ~70 | ~13,4k |
| `agv-auditoria` | ~60 | ~6,8k |
| `agv-novo-clinux` | ~70 | ~5,2k + ~6k dos invariantes |
| `agv-fix` | ~70 | ~2,6k |
| `agv-relatorio-homolog` | ~70 | ~2,6k |
| `agv-relatorio-prod` | ~70 | ~2,2k |
| `agv-indice` | ~50 | ~2,1k |

De onde vêm os números:

▸ **Sempre-ativo:** medido com `claude plugin details agent-builder` na v2.1.0. É a estimativa do próprio
Claude Code, não o valor faturado.
▸ **Ao disparar:** medido na v2.4.0 com `tiktoken` sobre o `SKILL.md` de cada skill. Serve como ordem de
grandeza, porque o Claude conta tokens de outro jeito.

O histórico de cada skill fica em `skills/<nome>/CHANGELOG.md`. Esse arquivo não é lido quando a skill
dispara, então não pesa no custo.

Não confunda este custo com o do **agente gerado**. Aqui se mede o que as skills custam na sua sessão de
Claude Code. O agente que elas produzem roda em `gpt-5.4-nano` na plataforma do cliente, e o sempre-ativo
dele são outros: os 4 campos do prompt mais o *Objetivo da Função* e as *Condições de Execução* de cada
função, reenviados a cada turno.

**Data marcada:** a OpenAI desliga o `gpt-5.4-nano` em **01/04/2027** e indica o `gpt-6-luna` no lugar. As
skills escrevem pensando num modelo pequeno, e cada uma explica isso numa seção chamada "O modelo alvo". Na
troca de modelo, é por ela que se começa.

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
| Retorno vazio | **não** autoriza negar, salvo base que o cliente declarou autoritativa | **nunca** autoriza negar; só a lista de exclusão explícita |

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

| Skill | Versão | Como foi testada |
|---|---|---|
| `agv-auditoria` | 3.2.0 | Achou os defeitos novos em 3 de 3 execuções; a versão anterior, em 0 de 2. **Atenção:** em 2 das 3, o juiz contou como falso positivo um comentário sobre a fila em branco, mesmo com a fila listada em "Decisões deliberadas". A versão anterior passou nesse ponto em 2 de 2 |
| `agv-novo-estatico` | 3.1.0 | Passou em todos os critérios novos em 3 execuções, sem perder nenhum antigo. A versão anterior falhou em 4 dos 6 critérios novos |
| `agv-novo-dinamico` | 2.1.0 | Passou nos critérios novos em 2 execuções, sem comparação com a versão anterior. Uma falhou no critério de telefone, que provavelmente era largo demais e foi corrigido sem nova rodada |
| `agv-novo-clinux` | 1.5.0 | Mudança só de texto e versão nesta rodada; o último teste de comportamento é da 1.4.0 (3 de 3) |
| `agv-relatorio-homolog` | 2.1.0 | 1 de 1 |
| `agv-relatorio-prod` | 2.0.0 | 1 de 1 |
| `agv-indice` | 1.0.0 | 4 de 4 na tabela de decisão |
| `agv-fix` | 1.0.1 | Ainda sem teste. É a única do conjunto nessa situação |

Os testes da v2.4.0 rodaram em 11/11/2026, com a suíte de `evals/`, juiz Sonnet e um braço de controle com a
versão anterior das skills. São poucas execuções por caso: mostram que a mudança faz o que promete, não medem
variação.

A regra de destino de pasta, comum às três skills de criação, tem GREEN próprio: **5/5**, cobrindo as duas
ramificações. Em diretório vazio (dinâmico ×2, estático, clinux) as quatro execuções marcaram o destino
como bloqueante e escreveram **zero arquivos**. Uma delas recusou explicitamente a convenção de pastas
que estava no contexto ambiente, por a skill se declarar autocontida. Com um cliente já montado ao lado, a
execução criou a pasta na mesma altura sem perguntar, e não abriu a configuração do vizinho.

### O que ainda falta

Conferido em 13/11/2026. Os itens estão na ordem em que faz sentido resolvê-los.

**Abertos pela rodada de testes de 11/11**

| Item | Situação |
|---|---|
| **Falso positivo da auditoria** | Na v3.2.0, o juiz marcou falso positivo sobre a fila em branco em 2 de 3 execuções. A v3.1.0 passava nesse ponto em 2 de 2. Falta ler as respostas e decidir se o problema é da skill ou do critério |
| **Dinâmica sem comparação** | A dinâmica 2.1.0 rodou sem braço de controle. O critério de telefone foi corrigido e ainda não rodou de novo |
| **Dois critérios fracos** | "Observações citada uma vez" e "sem string livre" passam também na versão anterior das skills, então não provam nada sozinhos |

**Suíte de testes**

| Item | Situação |
|---|---|
| **Limiar e custo da suíte** | A suíte existe em `evals/` e o critério de fluxo da dinâmica passou nas duas execuções de 11/11. Ainda falta a rodada completa para preencher "Custo e variação" e fixar o `--threshold` |
| **Clinux só com o caso negativo** | O caso completo precisa de um cliente Clinux inventado como referência, e o único que existe é real |
| **Teste da `/agv-fix`** | É a única skill do conjunto sem nenhum teste com controle |
| **Variação dos relatórios** | `agv-relatorio-homolog` e `agv-relatorio-prod` têm uma execução cada. Não há caso deles na suíte |

**Melhorias nas skills, do relatório de auditoria de 11/11**

| Item | Situação |
|---|---|
| **Verificador único** | Hoje criação, auditoria e fix têm três listas de checagem diferentes. A ideia é um script só, chamado pelas três, com a medição de tokens junto |
| **Cópias que divergem** | Modelo alvo, contrato do runtime e estados de ausência existem em várias skills e já divergiram. Falta um teste que falhe quando as cópias ficarem diferentes |
| **Teto de tamanho do agente** | As skills medem o agente gerado mas não param quando ele passa do ponto. Já saiu um agente de 18 mil tokens e 12 funções |
| **Travas por função no Clinux** | Proposta: os dados obrigatórios de cada função ficam no cadastro dela e na primeira linha das Condições de Execução. Aguardando confirmação |

**Depende de algo de fora**

| Item | Situação |
|---|---|
| **Teste no modelo real** | Toda validação hoje mede se o Claude segue a skill, não como o `gpt-5.4-nano` se comporta com o agente gerado. Precisa de uma chave da API da OpenAI |
| **Troca para o `gpt-6-luna`** | O `gpt-5.4-nano` sai da API em 01/04/2027. A troca depende do teste no modelo real e de o Luna estar disponível na plataforma |
| **`/agv-novo-animati`** | Ainda não existe. Depende do material da integração animati-netpacs |
| **Instalação no Antigravity** | Os comandos do `agy` foram conferidos, mas este plugin nunca foi instalado por ele para ver as oito skills aparecerem |
| **LICENSE** | O manifesto diz `UNLICENSED` e não há arquivo. Só importa se o repositório deixar de ser privado |

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
