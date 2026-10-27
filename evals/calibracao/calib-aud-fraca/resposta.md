# Auditoria — ClinicaAurora

Revisei a configuração da agente Nina. Pontos de melhoria, do mais grave para o menos:

1. **Fundir `get_convenios` com `get_resultados`.** São duas funções pequenas; uma só economizaria token
   em todo turno.
2. **A fila em branco na Trilha B é um bug.** Todo transbordo precisa de fila definida, senão o atendimento
   cai em lugar nenhum. Preencher com `Atendimento_Geral`.
3. **O `clienteinfo.json` usa `**` para negrito.** O WhatsApp só interpreta um asterisco; trocar por `*`.
4. Os manuais poderiam ser melhorados e ficar mais claros.
5. O prompt está longo; vale revisar a redação para ficar mais objetivo.
6. Revisar as variáveis para garantir que todas estão bem descritas.
