# Changelog — agv-fix

- **1.0.1** — **A checagem de grafia de fila passou a verificar fila real.** A anterior procurava o formato
  `Palavra_Palavra`; filas como `Chat` ou `Atendimentos Chat` não casavam, e a verificação passava sem ter
  verificado nada. Agora compara, fila a fila do ENUM, a contagem exata com a contagem sem distinção de
  caixa. Corrigida também a frase que apresentava estas verificações como "as mesmas que governam a
  criação" — são o subconjunto mecânico. O changelog saiu do `SKILL.md` para este arquivo.

- **1.0.0** — Versão inicial. Fecha o ciclo auditar → corrigir, que antes era pedido em conversa a cada
  vez. O desenho preserva a separação entre diagnosticar e escrever: recebe plano aprovado e aplica item a
  item, sem reauditar e sem acrescentar achado. O Passo 3 (round-trip antes de reestruturar) existe porque
  a pasta do cliente não está sob controle de versão, e uma reestruturação sem ele já perdeu um campo para
  sempre.
