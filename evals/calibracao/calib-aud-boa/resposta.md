# Auditoria — Clínica Aurora (agente "Nina")

**Categoria: Base de conhecimento.** Há 2 JSONs em `ferramentas/dados/` e as variáveis usam o prefixo `IA_`.

**O que li:** os 3 arquivos de `config/`, os 3 manuais e os 2 JSONs de dados. Não existem as pastas `origem/` e `relatorios/`. Para saber se algo foi decidido de propósito, só pude consultar `variaveis.md`.

**Verificações mecânicas:** este ambiente não tem shell, então rodei as checagens com Grep e conferi o resto lendo os arquivos. Os scripts `comm` e `python json.load` da skill não foram executados. Resultado:
- Seções do prompt: 4, o que está correto.
- Manuais: 3 seções cada, com rótulos antigos e cabeçalho `FUNÇÃO:`.
- Negrito duplo `**`: aparece em `agente.md`.
- `IA_OBSERVACOES`: 0 ocorrências.
- XML, caminhos de arquivo e negativas do tipo "não realiza": nenhuma ocorrência.
- Card (`clienteinfo.json`): as 8 variáveis estão presentes e as listas estão pareadas (4/4 e 3/3).

Nenhum arquivo foi alterado.

---

## Crítico

### 1. Os casos de exceção que o prompt manda preencher não cabem no que os campos aceitam
- **Onde:**
  - Motivo não reconhecido: `agente.md:34` manda transferir quando o motivo é vazio ou fora da lista, mas `variaveis.md:17` exige um motivo da lista fechada `Exame, Duvida, Resultado`, sem valor de reserva.
  - CPF e telefone: `agente.md:53` e `:57` mandam gravar "Não coletado"/"Não Informado", mas `variaveis.md:13-14` exige 11 dígitos e 10–11 dígitos.
  - **Procedência:** a contradição foi observada. O efeito é inferido, porque o schema real não está na pasta.
- **Efeito em produção:** se o schema aplicar essas restrições, a chamada de transbordo é descartada sem aviso e o paciente fica sem destino.
- **Correção:**
  - Acrescentar um valor `Outro` à lista de `motivo` e usá-lo no fallback.
  - Acrescentar as três marcações de ausência à validação de CPF e telefone, como alternativa ao formato de dígitos.
  - **Não** trocar esses campos por texto livre.

## Alto

### 2. O aviso "Vou transferir você para a nossa equipe agora" está no prompt e vale para todo transbordo
- **Onde:** `agente.md:22`, repetido em `set_transbordo.md:28` e `get_convenios.md:27` (observado).
- **Efeito em produção:**
  - Na trilha B, onde a dúvida já foi resolvida, o paciente ouve que será transferido, e ninguém atende.
  - A mensagem duplica a que a plataforma já envia depois da chamada.
- **Correção:** remover a linha 22 e os exemplos. A mensagem de encerramento fica com a plataforma.

### 3. A trilha B responde "dúvida de horário" pela base, mas nenhuma função devolve horário
- **Onde:** `agente.md:31` e `:42`. Os dados só têm convênios e resultados (observado).
- **Efeito em produção:** o modelo pequeno inventa um horário e marca a conversa como resolvida ("Sim"). Fica registrada como resolvida uma resposta falsa.
- **Correção:** criar `get_horarios` com os dados do cliente. Enquanto ela não existir, enviar essa demanda para atendimento humano com resolvido "Nao" e uma fila definida.

### 4. A trilha C coleta o protocolo, mas nada aproveita esse dado, e a função `get_resultados` nunca é chamada
- **Onde:**
  - `agente.md:46` só manda coletar o protocolo e transferir.
  - `variaveis.md:16` liga o protocolo a `get_resultados -> identificador`, mas essa função devolve o mesmo texto para todos (`get_resultados.json`) e não é chamada na trilha.
  - `get_resultados.md:27` pede o protocolo para uma pergunta geral ("como pego meu resultado?").
  - **Procedência:** observado.
- **Efeito em produção:**
  - O protocolo tende a chegar vazio no card, porque a função a que ele está ligado nunca roda (inferido).
  - Uma pergunta que a base responde ("portal ou recepção, 1 a 5 dias úteis") vai para a fila `resultados`.
  - A função parece uma consulta autenticada, mas não é.
- **Correção:** separar dois casos:
  - **Orientação geral:** chamar `get_resultados` sem pedir identificador, marcar resolvido "Sim" e deixar a fila em branco.
  - **Consulta individual:** coletar o protocolo e ligá-lo a `set_transbordo -> protocolo`.

### 5. A trilha A valida cobertura sem perguntar qual exame e não separa convênio de particular
- **Onde:** `agente.md:36-39`, `get_convenios.md:4` e a ausência de uma variável de exame em `variaveis.md` e no card (observado).
- **Efeito em produção:**
  - Não há exame para comparar com a cobertura.
  - Quem não tem convênio esgota as tentativas e é gravado como "Não Informado", que significa recusa.
  - O atendente de agendamento não sabe qual exame marcar.
- **Correção:**
  - Perguntar primeiro "convênio ou particular?".
  - Criar a variável `IA_EXAME` e incluí-la no card.
  - Gravar "Não se aplica" no convênio de quem é particular.
  - Definir o que fazer quando o exame não tem cobertura.

### 6. As três marcações de ausência se contradizem
- **Onde:**
  - `agente.md:53`: dado não obtido em 2 tentativas → "Não coletado".
  - `agente.md:57`: o mesmo caso → "Não Informado".
  - `variaveis.md:7`: "Não coletado" significa que o dado *nunca foi perguntado*.
  - "Não se aplica" não aparece em nenhuma instrução do prompt.
  - **Procedência:** observado.
- **Efeito em produção:** o atendente lê como "não perguntado" o que na verdade foi recusa. Nas trilhas B e C, os campos que essas trilhas não pedem ficam com valor indeterminado.
- **Correção:** apagar a linha 53 e escrever, para cada trilha, qual marcação vai em cada campo que ela não coleta.

### 7. Não há consentimento antes de pedir nome, CPF e telefone (condicional)
- **Onde:** `agente.md:37` é o primeiro pedido de dado pessoal, e não há frase de consentimento antes dele (observado).
- **Efeito em produção:** coleta de dado pessoal sem consentimento, se a plataforma não fizer isso antes.
- **Correção:** se a plataforma não trata o consentimento, incluir uma frase curta antes da primeira coleta e aguardar a resposta. Recusa encerra a conversa sem transbordo.

## Médio

### 8. Nenhum resumo é confirmado antes de chamar `set_transbordo`
- **Onde:** `agente.md:36-46` (observado).
- **Efeito em produção:** CPF ou telefone digitado errado chega ao atendente sem chance de correção.
- **Correção:** confirmar os dados uma vez e executar no mesmo turno em que a confirmação chega.

### 9. O telefone de quem está na conversa é pedido
- **Onde:** `agente.md:37`, `variaveis.md:14` e o card (observado).
- **Efeito em produção:** mais uma pergunta e mais um dado pessoal, sendo que a plataforma já entrega esse número em `__CONTATO__`.
- **Correção:** remover a coleta e mostrar `__CONTATO__` no card. Isso não vale se a regra for pedir o telefone de outra pessoa (ver "O que não foi possível julgar").

### 10. A regra "Uma pergunta por mensagem" contradiz a própria trilha A e encarece a conversa
- **Onde:** `agente.md:64` contra `agente.md:37`, que pede três dados de uma vez (observado).
- **Efeito em produção:** o modelo precisa escolher qual das duas regras seguir. Se seguir a da linha 64, são três mensagens cobradas no WhatsApp em vez de uma.
- **Correção:** "Agrupar as perguntas do mesmo bloco; uma escolha por vez só em menu numerado."

### 11. Nenhum passo diz para não perguntar de novo o que o paciente já informou
- **Onde:** `agente.md:36-46` (inferido).
- **Efeito em produção:** o agente pode perguntar de novo um dado que o paciente deu na primeira mensagem.
- **Correção:** cada passo de coleta ganha a cláusula "se já informado, preencher sem perguntar".

### 12. A troca de assunto não leva a uma nova classificação
- **Onde:** `agente.md:42` pergunta "mais alguma coisa?" sem dizer o que fazer com a resposta (inferido).
- **Efeito em produção:** uma nova demanda herda o motivo e a fila da anterior, e o atendente recebe um caso que não corresponde à conversa.
- **Correção:** escrever que uma nova demanda volta à tabela de classificação.

### 13. Não existe o campo de observações `IA_OBSERVACOES`
- **Onde:** 0 ocorrências em `agente.md`, `variaveis.md` e no card (observado).
- **Efeito em produção:** o atendente não recebe nenhum contexto livre da conversa.
- **Correção:** criar a variável em um único ponto do prompt, com limite de tamanho e restrita ao que o paciente disse ou ao que a função retornou.

### 14. Obrigatoriedade e ligação de parâmetros divergem entre os arquivos
- **Onde:**
  - `set_transbordo.md:15` diz que só `resolvido` é obrigatório; `variaveis.md:17` diz que o motivo também é.
  - `variaveis.md:15-16` liga convênio e protocolo às funções `get_*`, enquanto `set_transbordo.md:14` os lista como parâmetros do transbordo.
  - `variaveis.md:12` exige o nome na trilha C, que não coleta nome (`agente.md:46`).
  - **Procedência:** observado.
- **Efeito em produção:** campos vazios no card da trilha C e comportamento diferente dependendo de qual arquivo a próxima correção alterar.
- **Correção:** ligar todos os dados que vão para o card a `set_transbordo` e alinhar a obrigatoriedade entre os arquivos.

### 15. Os três manuais estão no formato antigo
- **Onde:** todos os manuais têm 3 seções com os rótulos "Descrição da Função", "Diretrizes de Prompt" e "Exemplos Práticos", além da linha `FUNÇÃO:` e de blocos de código markdown (`get_convenios.md:1,8,11,21` e equivalentes nos outros dois) (observado).
- **Efeito em produção:** a seção 3 não tem campo na plataforma onde ser colada. Os exemplos dela ensinam comportamento errado, como transferir logo depois de dizer "cobre sim", sem coletar nada. O cabeçalho `FUNÇÃO:` é pago em todo turno.
- **Correção:** migrar para `## 1. Objetivo da Função` e `## 2. Condições de Execução`, apagar a seção 3, a linha `FUNÇÃO:` e as cercas de código.

### 16. A tabela de filas e a regra "ao final de toda trilha" estão duplicadas
- **Onde:** `set_transbordo.md:12` e `:17` repetem `agente.md:28-34` (observado).
- **Efeito em produção:** o texto é pago duas vezes em todo turno, e a próxima mudança de fila tende a ser feita em só um dos lados.
- **Correção:** manter a tabela só no prompt.

### 17. Os casos de exceção das funções não fecham
- **Onde:** `agente.md:51-52` (inferido).
- **Efeito em produção:**
  - "Não localizou, pergunte de novo" não faz sentido para funções sem parâmetro.
  - "Não localizou" aplicado a um convênio soa como recusa de cobertura.
  - Não há instrução para depois da segunda falha técnica.
- **Correção:** retorno vazio → não afirmar nem negar e transferir. Segunda falha → transferir com resolvido "Nao".

### 18. O prompt manda usar negrito com `**`
- **Onde:** `agente.md:67` (observado).
- **Efeito em produção:** o WhatsApp mostra os asteriscos literalmente para o paciente.
- **Correção:** trocar para `*texto*`.

## Baixo

### 19. Não há meta de número de interações
- **Onde:** em nenhum arquivo (observado).
- **Efeito em produção:** não há como medir se o fluxo está longo demais.
- **Correção:** declarar a meta e contar o caminho mais longo, que hoje é a trilha A.

### 20. "Em conflito, vence Segurança" aparece duas vezes
- **Onde:** `agente.md:54` e `:86` (observado).
- **Efeito em produção:** só custo de tokens.
- **Correção:** manter apenas a linha 86.

### 21. Os nomes de variável são escritos de dois jeitos
- **Onde:** `IA_PACIENTE_NOME` em `variaveis.md` contra `__IA_PACIENTE_NOME__` no card (observado).
- **Efeito em produção:** só confusão na manutenção.
- **Correção:** padronizar para `__IA_X__` em `variaveis.md`.

---

## Decisões deliberadas mantidas
- **Fila em branco quando a dúvida é resolvida (trilha B):** está registrado em `variaveis.md:18` ("Em branco quando Sim"). Não é defeito.
- **A fila não aceita marcação de ausência e usa `atendimento_geral` como reserva:** está registrado em `variaveis.md:18`.
- **`**` no título do card (`clienteinfo.json:3`):** o card aparece no painel do atendente, onde esse negrito funciona. Não é a mesma situação do item 18.

## O que não foi possível julgar
- **Schema real da plataforma:** preciso saber se CPF e telefone têm validação de formato (`pattern`), se `motivo` é de fato uma lista fechada no cadastro da função e quais parâmetros são obrigatórios. É isso que confirma ou não a gravidade crítica do item 1.
- **Consentimento:** a plataforma já pede consentimento antes da conversa? Se sim, o item 7 sai do plano.
- **Telefone:** o telefone pedido pode ser de outra pessoa, como um responsável? Se essa for uma regra de negócio, o item 9 sai do plano.
- **Variações de nome de exame** ("ultrassom" × "Ultrassonografia"): `get_convenios.md:15` só limita a variação de grafia ao nome do convênio. Falta definir a regra para os nomes de exame.
- **Intenção do cliente:** como não existe `origem/`, não consegui procurar registro de intenção no material original. Alguma assimetria acima pode ser regra de negócio não documentada.

Diga quais itens aprova e eu passo às correções.