# Revisão dos efeitos de movimento

Escopo: ajustes de movimento em todos os relatórios habilitados. Layout, conteúdo, cálculo e formato dos gráficos preservados. A reorganização visual da Previsão permanece como [proposta separada](PROPOSTA_PREVISAO_EXECUTIVA.md).

## Alterações aplicadas

| Área | Resultado |
|---|---|
| Preferência de acessibilidade | Todas as animações e transições CSS não essenciais ficam desligadas em `prefers-reduced-motion: reduce`, incluindo hover e diálogos; rolagem programática respeita a preferência existente |
| Animações JavaScript | Concluídas no estado final quando a preferência muda ou antes da impressão; o controle da corrida restaura os valores e remove a cópia decorativa |
| Talentos | Corrida interrompida ao pedir movimento reduzido; controle acompanha mudanças da preferência nos dois sentidos sem recarregar. Não inicia automaticamente ao reativar movimento. Limpeza também ao sair da página (`pagehide`) |
| Estudo de SLA | Trocas rápidas encerram a transição anterior, tratam o cancelamento esperado e só exibem o último slide solicitado; estado de direção é limpo ao terminar |
| Previsão | Entrada curta do histórico (320 ms); linha prevista se revela em 500 ms com atraso de 120 ms; faixa/pontos surgem suavemente. Eixos, valores e desenho final preservados; sem repetição em visita marcada como revista |

Defeito reproduzido antes da correção: durante a corrida de Talentos, mudar para movimento reduzido deixava `.corrida-palco` ativa e o botão habilitado com rótulo “Parar”. Após a correção: cópia removida, valores finais preservados e controle desabilitado. Ao reativar o movimento, ele volta a aceitar o play por ação da pessoa.

## Avaliação por relatório

- **Início:** preservados a entrada das colunas e o extrato; política global cobre também as transições de estados no modo reduzido. Sem novo contador numérico ou repetição contínua.
- **Talentos:** preservada a abertura e a corrida solicitadas na D51. Melhorado o ciclo de interrupção/restauração; não foram alterados os tempos, o ranking, os valores ou as posições finais.
- **Atendimento:** mantidos o fade do conjunto e a entrada breve dos pontos, que já respeitam a hierarquia atual. Sem animação adicional em cada célula do quadro.
- **SLA:** mantidos os trilhos e seus valores finais. Nenhuma alteração de mediana, metas ou escalas.
- **Como medimos:** oito slides conferidos, incluindo navegação rápida; preservada a entrada só na primeira visita e a volta com leitura pronta.
- **Previsão:** movimento agora apresenta o histórico antes da projeção, sem deslocar o gráfico ou recontar pedidos. Mudança de distribuição/gráficos só no documento de proposta.
- **Qualidade e O que falta:** mantidos os estados e movimentos existentes; não foram acrescentados efeitos para simular dados ou maturidade das telas pendentes.
- **Resultado:** desabilitado no modo de reunião; não foi ativado nem preenchido para esta revisão.

## Verificação

[Evidência do navegador](../validacao/movimento_2026-10-26.json): sete páginas em desktop 1440×900 e celular 390×844, nos modos normal e reduzido (**28 combinações**). Todas responderam 200, sem erro JavaScript, sem rolagem horizontal global, sem animações infinitas e sem animações de entrada ainda rodando após a espera de 1,35 s.

Percorridos também os oito slides de Como medimos no desktop: um slide visível por vez, nenhum movimento em execução após a espera e navegação rápida terminando no slide 8 solicitado, sem rejeição JavaScript não tratada.

Talentos: iniciado com movimento reduzido, reativado e iniciado pelo play, interrompido ao reduzir novamente; teste de impressão durante a corrida; corrida completa até o término. Em todos os encerramentos testados, o texto da tabela original permaneceu idêntico e a cópia decorativa foi removida. Esta é verificação de comportamento, não nova conferência do banco.

**Suíte completa: 475 testes passaram**, com um aviso de descontinuação Starlette/httpx. Registro em [JUnit](../validacao/testes_movimento_2026-10-26.xml). Antes da conferência completa, os 53 testes selecionados de movimento/interface passaram. Os testes D51 foram ajustados ao controle dinâmico da preferência, mantendo a exigência de não iniciar a abertura no modo reduzido.

Backup anterior a esta rodada: `C:/Users/CCMB/AppData/Local/Codex/Backups/PPD-AGENCIAMENTO-SLA-movimento-20261026`. Arquivos de execução alterados nesta rodada: apenas `app/static/apresentacao.js` e `app/static/estilo.css`. Não houve alteração nos templates, bibliotecas, fontes, dados ou configurações do GCP.

Limites: os testes de navegador usam o Chrome do ambiente local; não equivalem a certificação de todos os navegadores, dispositivos ou leitores de tela. Os efeitos respeitam a identidade atual e não incluem novas bibliotecas de animação.
