# Changelog — agv-novo-clinux

- **1.5.0** — Relação de endpoints virou dado bloqueante do Passo 0 e fonte dos nomes de variável, que
  mudaram entre duas instalações do mesmo Clinux; um JSON por endpoint em `ferramentas/endpoints/`, com só os
  `__VARIAVEL__` como parâmetros. Retorno envelopado em `RESPONSE_*` (invariante 17). Trilha de consulta
  derivável de referência que a tenha, com médico opcional; mesmo endpoint vira uma função só; particular com
  plano fixo; gênero neutro; endpoint de disponibilidade sem data ou sem hora inicial. Origem: segundo
  cliente Clinux, 29/10/2026. Na mesma versão: a ficha ganhou a linha `destino.pasta`, que o texto citava e o
  bloco não trazia; o relatório final deixou de pedir medição "antes × depois", que cliente novo não tem; e
  o changelog saiu do `SKILL.md` para este arquivo.

- **1.4.0** — Retorno da gravação (invariante 15): decidir pelo campo de resultado, nunca pelo `valor`;
  `FALHA - HORARIO OCUPADO` pergunta outro horário ou atendente; gravação fora do retry silencioso;
  sucesso não transborda salvo anexo falho. Contrato de retorno virou dado bloqueante do Passo 0.
  `ARQUIVO_PEDIDO` guarda a URL do arquivo, nunca marcador de texto (invariante 16). Origem: UltramedRJ,
  21/10/2026.

- **1.3.0** — Alinhamento com a correção do contrato do runtime nas skills de Pré Agendamento. O invariante
  de custo dizia que ali a §2 do manual não chegava ao modelo; não é verdade — são os mesmos dois campos
  por função, e o Auto Agendamento era quem estava certo. Removida a regra de mascaramento de documento,
  descontinuada pelo cliente.

- **1.2.0** — **Formato declarado: markdown para estruturar, nunca XML.** A documentação oficial não
  prescreve formato de prompt para o `gpt-5.4-nano` — o que ela exige é *ter* estrutura. Markdown
  entrega isso mais barato (~+5% do campo para converter em XML, sem ganho), e aqui o custo seria pago
  em dobro, pelos dois campos por função.
- **1.1.0** — Modelo alvo declarado em `invariantes-clinux.md`, com o peso extra que ele tem nesta
  categoria: sempre-ativo dobrado por função, e retorno vazio como canal único de erro. Convenções do
  projeto antes citadas por número passam a vir enunciadas por extenso — o arquivo viaja no plugin, para
  workspaces onde o documento de convenções não existe, e exceção a regra invisível convida a
  reintroduzir o defeito que ela evitava.
- **1.0.0** — Versão inicial.
