# agent-builder

Plugin de skills para **criar, auditar e documentar agentes virtuais de atendimento por WhatsApp**
baseados em OpenAI Function Calling.

As skills são autocontidas: carregam por dentro as regras, os formatos de arquivo e os critérios de
verificação. Não dependem de nenhum documento de convenções externo nem de uma estrutura de pastas
específica — a pasta do cliente é descoberta pelo conteúdo e, quando não existe nenhuma, a skill pergunta
onde criar.

---

## Instalação

As skills seguem o padrão aberto [Agent Skills](https://agentskills.io), então rodam nos três runtimes.

**Claude Code** — como plugin:

```bash
claude plugin marketplace add https://github.com/arthuld/agent-builder
```

```bash
claude plugin install agent-builder@agent-builder
```

Instalado, valem em **qualquer projeto** — não é preciso clonar o repositório nem montar pasta. Custo
sempre-ativo do conjunto: **~425 tokens** por sessão, medido com `claude plugin details agent-builder`.

**Gemini CLI** — tem instalador próprio:

```bash
gemini skills install https://github.com/arthuld/agent-builder.git --path skills
```

**opencode** — não tem comando de instalação; descobre por diretório. Clone o repositório e copie as pastas
`agv-*` para `~/.agents/skills/`, caminho interoperável lido tanto pelo opencode quanto pelo Gemini CLI
(`~/.config/opencode/skills/` também serve, mas só o opencode):

```powershell
git clone https://github.com/arthuld/agent-builder.git; New-Item -ItemType Directory -Force ~/.agents/skills; Copy-Item -Recurse -Force agent-builder/skills/agv-* ~/.agents/skills/
```

Copie apenas as pastas `agv-*`. O opencode varre subdiretórios em profundidade, então uma pasta de skills
fora de circulação colocada ali seria carregada como skill ativa.

Como é cópia e não instalação, **precisa ser refeita a cada atualização** — não há update automático. Num
projeto que já tenha `.agents/skills/`, o opencode lê dali direto, sem instalação nenhuma.

> Repositório privado: a instalação exige que o git da máquina tenha acesso. Colaborador adicionado no
> GitHub consegue; terceiro sem acesso, não.

---

## As skills

| Skill | O que faz |
|---|---|
| `/agv-novo-dinamico` | Cria agente de **interação livre** — o usuário descreve a demanda, o agente classifica e conduz |
| `/agv-novo-estatico` | Cria agente **estático** — árvore de menus numerados, ainda respondendo pergunta fora do menu |
| `/agv-novo-clinux` | Cria agente de **autoagendamento com integração clinux-genesis** |
| `/agv-auditoria` | Audita em cinco dimensões — fluxo, lógica, segurança, conduta, eficiência. Propõe, não aplica |
| `/agv-indice` | Mapa curto dos clientes, para achar em qual cliente e qual arquivo está a resposta |
| `/agv-relatorio-homolog` | Relatório resumido de entrega para teste |
| `/agv-relatorio-prod` | Relatório completo de arquitetura da versão final |

Futura: `/agv-novo-animati` — integração animati-netpacs.


---

## Uso

### Criar um agente

```
/agv-novo-dinamico MeuCliente
```

**A skill para e pergunta antes de escrever.** Ela monta uma ficha de parâmetros com cada linha preenchida
ou marcada `[PERGUNTAR]`, e qualquer `[PERGUNTAR]` bloqueia. São bloqueantes: onde criar a pasta, grafia
comercial do cliente, nome e gênero do agente, saudação literal, filas reais e cada regra de negócio.

**O material do cliente chega de duas formas, e as duas funcionam:** arquivos numa pasta `origem/`, ou
colados direto no comando ao invocar a skill. Nenhuma é obrigatória e nenhuma tem precedência — o que existir
vira fonte primária, e o que vier colado é salvo em `origem/` para ficar registrado.

### A estrutura que a skill gera

```
MeuCliente/
├── config/
│   ├── agente.md          system prompt: perfil, diretrizes, conduta, segurança
│   ├── variaveis.md       dicionário das variáveis de contexto
│   └── clienteinfo.json   card do atendente
├── ferramentas/
│   ├── dados/             get_*.json — bases de conhecimento
│   └── manuais/           get_*.md + a função de transbordo
├── origem/                material bruto recebido do cliente
└── relatorios/
```

Onde essa pasta nasce depende do seu workspace: a skill procura clientes já montados e coloca o novo ao
lado; não achando nenhum, pergunta.

### Auditar e documentar

```
/agv-auditoria MeuCliente          → plano de correção, aprovável
/agv-relatorio-homolog MeuCliente  → relatório de entrega para teste
/agv-relatorio-prod MeuCliente     → documentação final de arquitetura
```

A auditoria **propõe e não aplica**. A separação entre diagnosticar e escrever é o que impede uma
auditoria de "consertar" configuração correta para satisfazer um falso positivo.

### Achar coisas entre clientes

```
/agv-indice qual cliente valida convênio contra lista?
```

Para pergunta que **atravessa** clientes. Para pergunta sobre um cliente só, abrir o `config/agente.md`
dele é mais barato — e a skill diz isso em vez de fazer trabalho desnecessário.

---

## Como as skills são construídas

Cada uma passa por **RED / GREEN / REFACTOR** com subagentes: mede-se o comportamento sem a skill,
escreve-se contra as falhas observadas e valida-se contra um braço de controle. Sem controle não há como
saber se a skill agrega ou se o modelo acertaria sozinho.

O método pega o que revisão de código não pega:

- Uma skill de criação **perdeu para o próprio controle** — 8/8 sem skill contra 7/8, 8/8 e 7/8 com ela.
  Foi arquivada e reescrita.
- Uma auditoria sem skill escreveu o encerramento como mensagem (*"estou te encaminhando"*) em vez de
  execução da função, e inventou uma exceção à entrega única.
- Duas correções vieram de execuções de teste que **rejeitaram a regra recém-escrita e estavam certas**.

Cada regra dentro de uma skill vem com o motivo. Regra sem motivo é regra que a próxima revisão
"simplifica", reintroduzindo o defeito que ela existia para evitar.

---

## Estado atual

| Skill | Versão | Validação |
|---|---|---|
| `agv-novo-dinamico` | 1.0.0 | GREEN 3/3 · controle empatou; o ganho é portabilidade |
| `agv-novo-estatico` | 2.0.0 | GREEN 3/3 + 2 execuções extras · controle falhou no encerramento |
| `agv-novo-clinux` | 1.0.0 | GREEN 3/3 |
| `agv-auditoria` | 2.0.0 | GREEN 2/2 · casos sem critério de julgamento: 5 → 0 e 1 |
| `agv-indice` | 1.0.0 | 4/4 na tabela de decisão |
| `agv-relatorio-homolog` | 2.0.0 | GREEN 1/1 |
| `agv-relatorio-prod` | 2.0.0 | GREEN 1/1 |

A regra de destino de pasta, comum às três skills de criação, tem GREEN próprio: **5/5**, cobrindo as duas
ramificações. Em diretório vazio (dinâmico ×2, estático, clinux) as quatro execuções marcaram o destino como
bloqueante e escreveram **zero arquivos** — uma delas recusou explicitamente a convenção de pastas que estava
no contexto ambiente, por a skill se declarar autocontida. Com um cliente já montado ao lado, a execução criou
a pasta na mesma altura sem perguntar, e não abriu a configuração do vizinho.

### O que ainda falta

| Item | Situação |
|---|---|
| **Suíte de evals** | `claude plugin eval` existe e o repositório não tem `evals/`. Hoje toda validação é subagente ad-hoc, refeita à mão a cada mudança. Uma suíte transformaria os GREEN já obtidos em regressão automática — o maior ganho de manutenção disponível |
| **`/agv-fix`** | Não existe. A auditoria propõe e a correção é pedida em conversa. Fecharia o ciclo auditar → corrigir com validação própria |
| **`/agv-novo-animati`** | Não existe. Integração animati-netpacs |
| **Variância dos GREEN de relatório** | `agv-relatorio-homolog` e `agv-relatorio-prod` têm uma execução cada. As mudanças são estruturais — aparecem ou não —, mas a variância nunca foi medida |
| **LICENSE** | O manifesto declara `UNLICENSED` e não há arquivo. Irrelevante enquanto o repositório for privado |
| **Gemini CLI não foi verificado** | A descoberta no opencode foi conferida de verdade (`opencode debug skill`: 7 de 7). O Gemini não está instalado nesta máquina, então o comando de instalação vem da documentação, não de execução |

---

## Configuração de cliente nunca entra aqui

Este repositório é o plugin: manifesto, skills e este README. Os clientes e suas configurações ficam no
workspace de quem opera, e o `.gitignore` protege contra o engano — mas ele é a última linha, não a
primeira. Antes de qualquer commit:

```bash
git status --short
```

Histórico de git não se apaga depois do push.
