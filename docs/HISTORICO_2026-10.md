# Histórico da etapa — outubro de 2026 (21 a 27/10)

28/10: cola passa a carregar falas numéricas do contexto das páginas via `/cola/{ficha}`; sem fotografia fixa no JavaScript, com identificação do recorte e aviso de indisponibilidade.

28/10: gancho e sequência principal corrigidos para SLA → Previsão; estudo mantido como aprofundamento pelo botão. Sem alteração de cálculos ou layout.

Linha do tempo resumida do portal "Gestão de orçamentos" até a véspera da reunião de diretoria de 28/10/2026. Cada
entrada aponta a decisão do [PRD](PRD.md) (seção 8, tabela de decisões) e a ficha da página em [paginas/](paginas/README.md).
O detalhe dia a dia está no PRD, seção 11 (histórico) e seção 12 (blocos de retomada como foram escritos).
Estado atual: PRD, "Estado atual"; decisões em aberto: PRD 9.7.

## Visão em uma tela

| Data | Marco | Decisões | Testes |
|---|---|---|---|
| 21/10 | Arquitetura, acesso e esqueleto local; 1º slide do SLA | D1–D17 | — |
| 22/10 | Navegação, segurança, dados recentes; Previsão e Qualidade preparadas; Início com a entrada mensal | D18–D23 | 17 → 45 |
| 23/10 | **Início entregue** (validação em três camadas, 0 divergências); área vira portal com máscaras e "O que falta" | D24–D30, D30-b | 89 |
| 24/10 | **Talentos entregue**; **Atendimento entregue**; SLA redesenhado e estudo "Como medimos" (slides 1–2) | D31–D35 | 116 |
| 25/10 | Correções nas três páginas; **regras novas do SLA** (D37) e **meta de 2 dias** (D38); estudo completo (slides 3–8); batalha do estudo e movimento | D36–D46 | 271 |
| 26/10 | **Previsão de demanda** com números (D47) e no protocolo do Caio (D48); **batalha do portal** em três levas (D49) | D47–D49 | 392 |
| 27/10 | **O site só lê a gold**: 8 tabelas e 8 views no `gold_monday`; leitor trocado, silver e `app/sql/` fora, 0 diferenças na mesma carga | D57 | 475 |
| 27/10 | **Atendimento**: "Declinados (Não teve seguimento)", "Entregues no Mês"; % dos recebidos na faixa | D58 | 475 |
| 27/10 | **Atendimento**: % = Entregues no Mês ÷ Para atender (set 661 ÷ 834 = 79%); selo do topo removido | D58b | 475 |
| 27/10 | **Portal com cara de apresentação**: Resultado e Qualidade fora da navegação; sem menu lateral; gancho para a próxima página visível (termina na Previsão); tela cheia mantida ao navegar | D59 | 474 |
| 27/10 | **Capa e encerramento**: capa com o roteiro da reunião; encerramento com agradecimento e pedidos; aba "Demanda"; setas trocam de página | D60 | 475 |
| 27/10 | **Capa no desenho de referência**: jornada animada de um pedido (relógio para no típico do SLA), encerramento marinho, capas de seção pelas setas; cola do apresentador em projeto separado (porta 8200) | D61 | 476 |
| 27/10 | **Ajustes da capa** (Caio): etapas na altura toda do plano marinho; frase da etapa em roleta ao lado das horas; capas de seção desligadas (`CAPAS_SECAO` guardado); capa e encerramento sem aba | D61 | 476 |
| 27/10 | **Sincronia portal ↔ cola** (`/sinc`, `static/sinc.js`): trocar a página num troca no outro, inclusive o slide do estudo e em tela cheia; cola refeita (clara, sucinta, com a fala de cada página) | D62 | 479 |
| 28/10 | **Base congelada por padrão** no computador (sem recarga por hora e sem aviso do banco) e **falas narrativas da cola** com números ao vivo | D63 | 497 |

## 1. Fundação (21–22/10)

- **21/10 — arquitetura e acesso (D1–D12).** Site próprio em Cloud Run + FastAPI, sem LLM por API (D2), login por link
  no e-mail (D3), dados em memória com recarga pelo metadado da tabela (D6, D7), nada publicado sem controle de acesso
  (D10). Fase 1: esqueleto local, números conferidos contra o BigQuery.
- **21/10 — apresentação em slides (D13–D17).** Lâmina 16:9 que escala, identidade VIU, área "Gestão de orçamentos"
  com seções; 1º slide do SLA com as regras C1–C11 (entrega = 1ª ida a Aguardando Feedback; Entrada conta; sem almoço,
  dia de 8 h).
- **22/10 — navegação e robustez (D18–D22).** Menu recolhível e barra do celular; CSP sem estilo inline; última carga
  válida continua no ar quando o BigQuery falha; Previsão (D20) e Qualidade (D21) preparadas; nomes curtos das abas.
- **22/10 — Início (D23).** Entrada mensal por tipo de input a partir da gold `gld_agenciamento_entrada_diaria`.

## 2. Páginas entregues (23–24/10)

- **23/10 — Início ENTREGUE (D24–D29).** Leitura por tipo de input e extrato do mês como fila (D25); sempre o ano
  corrente com comparação ao mesmo período do ano anterior (D26); proporção ao lado da quantidade (D27); validação em
  três camadas, 624 itens, 0 divergências, correções B1–B8 (D28); decisões do Caio sobre janeiro e o extrato (D29).
  Ficha [inicio.md](paginas/inicio.md).
- **23/10 — portal (D30, D30-b).** Ordem da reunião, pergunta por seção, máscaras "Aguardando dados" geradas de
  `pendencias.py`, página "O que falta", modo apresentação. Exceção D30-b: Talentos lê a silver até a PD01.
- **24/10 — Talentos ENTREGUE (D31)** e regra da data de entrega pelo log (D32). Ficha [talentos.md](paginas/talentos.md).
- **24/10 — Atendimento ENTREGUE (D33).** Faixa dos números do ano, quadro do extrato em 7 linhas e dispersão sobre o
  que havia para atender (A25: objetivo 100%, alerta 90%). Ficha [atendimento.md](paginas/atendimento.md).

## 3. SLA e meta (24–25/10)

- **24/10 — SLA redesenhado (D34).** Página única com a resposta tipográfica (horas de trabalho da equipe e dias para o
  cliente), seletor de talentos e trilhos por mês; lupa para o estudo "Como medimos".
- **25/10 — regras novas do SLA (D37: D-SLA-1 a D-SLA-6).** Depois de validar o cálculo no BigQuery: mês = mês da 1ª
  entrega; "Retorno Marca/Executivo" fora das horas da equipe; só meses completos de entrega; mês vigente vazado;
  meta sugerida de 75% em 3 dias (revista no mesmo dia). Pendência PD21 para a gold.
- **25/10 (noite) — meta de 2 dias (D38, D-SLA-7).** Meta sugerida = **metade dos orçamentos prontos em até 2 dias de
  trabalho (16 h)**, a que vale hoje; a de 75% era inatingível (melhor mês 58%). Ainda não oficial: é o pedido nº 1 do
  "O que falta".
- **26/10 — vocabulário (D49, 1ª leva).** "Típico" no lugar de "mediana"; prazo do cliente em dias úteis no calendário
  (C3b, conferido no BigQuery); selo do mês com 1 casa perto de 16 h. Ficha [sla.md](paginas/sla.md), "Estado vigente".

## 4. Estudo "Como medimos" (24–25/10)

| Slide | Pergunta | Decisão | Regras |
|---|---|---|---|
| 1 | Como chegamos ao tempo da equipe? (um orçamento real do dia) | D34, D37 | E1–E3 |
| 2 | A maioria é rápida. Poucos demoram muito. (formato, sino, faixas) | D35, D37, D38 | X1–X7 |
| 3 | De cada 100 pedidos, em quanto tempo entregamos? | D39 | W1–W7 |
| 4 | Para onde vai o tempo? | D40 | V1–V8 |
| 5 | Foi um mês ruim, ou é sempre assim? | D41 | U1–U9 |
| 6 | Onde o tempo trava? (tempo inteiro de quem travou, revisão do Caio) | D42 | K1–K8 |
| 7 | Em que tipo de pedido o tempo trava? | D43 | J1–J9 |
| 8 | O que os dados nos mostraram | D44 | Z1–Z8 |

- **25/10 (noite) — batalha do estudo (D45).** Base congelada para a reunião (`CONGELAR`), exemplo fixo (`?exemplo=`),
  conferência automática no BigQuery (`tools/conferir_estudo.py`) e de layout (`tools/conferir_layout.mjs`), recorte
  visível em cada slide. Nenhuma regra mudou.
- **25/10 (noite) — movimento (D46).** Um gesto de dado por slide, até ~1,15 s, sem mola nem loop, respeitando
  "menos movimento".

## 5. Previsão de demanda (26/10)

- **D47 — com números.** Laboratório `ml/` com 58 modelos em 6 famílias, régua única de origem móvel; o site só lê
  `ml/saida/previsao.json`. Escolha revista pela D48 (saída antiga guardada em `ml/saida/d47/`).
- **D48 — protocolo do Caio.** Janela móvel de 12 meses, teste jun–set/2026 a 1 mês à frente, vence o menor erro
  (WAPE), execução mensal (retrato quando o mês fecha; acompanhamento diário só do realizado), gráficos só de 2026.
  Inbound = média de 6 meses (14%); Mercado = rede neural de 1 neurônio (13%, mas 27% em jan–mai contra 25% da
  ingênua). Ficha [previsao.md](paginas/previsao.md). Decisões abertas: vencedor do Mercado e nov/dez como cenário (PRD 9.7).

## 6. Batalha do portal (26/10, D49)

Grupos de especialistas revisaram todas as páginas pensando na diretora que vê o portal pela primeira vez; um painel
aprovou só o que não muda regra de negócio.

1. **1ª leva — dados, cálculos e textos.** Vocabulário único do SLA, C3b com SQL, slide 2 em linguagem simples,
   glossário, "O que falta" sem marcador provisório, corte E3 único em `app/corte.py`, job da Previsão parado com a base
   congelada, contrato do snapshot, PD22 e PD23. 361 testes.
2. **2ª leva — interface e movimento.** Números prontos desde o 1º quadro, um gesto por página, navegação só com o voo
   da pílula, aviso de dados novos no modo apresentação, base congelada sem aviso de atraso, rodapé datado em toda rota,
   `/regras` retirada, Previsão com as duas medidas de erro, `tools/checar_reuniao.py`. 390 testes.
3. **3ª leva — documentação e limpeza.** PRD com o estado atual no topo e os blocos antigos em arquivo; decisões do Caio
   numa tabela (PRD 9.7); retrato da carga da reunião em cada ficha; "Estado vigente" na ficha do SLA; este histórico;
   registro da checagem em `docs/validacao/reuniao_2026-10-26.json`; sobras em `_descartados/2026-10-26/`. 392 testes.

## 6b. O site só lê a gold (27/10, D57)

As 8 tabelas e 8 views do plano de golds por visual foram criadas no PPD-GOLDEN-AGENCIAMENTO-MONDAY e subidas pelo Caio;
o job `gold-agenciamento` passou a atualizar as tabelas. No site, o leitor (`app/dados.py`, `ml/dados.py`) trocou a silver,
a classe `Consulta`, `app/sql/` e o expediente recalculado pelas golds: cada gráfico lê a sua tabela ou view (mapa no
PRD, "Retrato do código"). Sem mudar layout, texto nem regra: o código antigo e o novo montaram as 21 visões sobre a mesma
carga real (27/10, 11:11) com 0 diferenças; na previsão, 1 pedido do Mercado exclusivos passa de abril para março
(calendário completo da gold). Limpeza: código e ferramentas que dependiam da silver em `_descartados/2026-10-27/`;
revisões e auditorias externas em `docs/historico/`. 475 testes (a regra antiga, só como simulação da gold, em
`tests/gold_simulada.py`).

## 6c. Endereço novo (31/10)

`/gestao-orcamentos/...` → `/viu-agenciamento/...` (slug em
`app/apresentacoes/gestao_orcamentos/__init__.py`; pasta mantida). O endereço antigo redireciona (301; 308 nos métodos
que não são GET/HEAD, para a API das Iniciativas). `<title>` de todas as páginas: "ViU Agenciamento". Testes e
documentação vigente atualizados; históricos, auditorias e evidências de validação ficaram com o endereço da época.

## 6d. Varredura de responsividade (31/10, antes do deploy)

`node tools/conferir_responsivo.mjs [URL] [--capturas PASTA] [--so 1920x1080,...] [--paginas ...] [--fim]` (novo, só
leitura; Chrome headless por CDP como o `conferir_layout.mjs`): 14 telas (1366 a 3840, ultrawide 3440x1440, tablets,
celulares 390/360, zoom de 125%/150% como viewport + DPR) x 16 vistas (inclui os 5 slides do estudo e os pop-ups do
Roadmap e da LIA). Nenhuma rolagem lateral, nada fora da tela nem erro no console em nenhuma combinação. Corrigido só em
CSS (`estilo.css`, bloco "telas grandes" antes do D46; sem mudar texto, número nem regra): acima de 1920x1080 o pé
(recorte datado, gancho da próxima pergunta, barra Anterior/Próximo do estudo) e os pop-ups (Roadmap, LIA, Iniciativas)
crescem na proporção da tela, pelo lado menor (antes ficavam em px fixos, minúsculos no 4K, e o pop-up da LIA espremia o
vídeo); até 1920x1080 nada muda. Pop-up da LIA com piso de 14 px (1024x768); gancho do estudo com área de toque maior
(padding vertical em elemento inline, sem mover a linha). Limites aceitos: em 1366x768 e 1024x768 (lâmina 16:9 inteira
na tela) os rótulos discretos ficam entre 8 e 11 px; no celular, os rótulos do histograma do estudo (slide 2) só com zoom
de pinça.

## 7. Próximos passos (depois da reunião)

- Decisões do Caio da seção 9.7 do PRD (DC1–DC16), uma por vez.
- Retrato por mês fechado com alarme quando um mês já fechado muda entre cargas (candidato à tela de Qualidade).
- Renumerar as seções "0000…" da ficha do SLA; `@pytest.mark.lento` nos testes de `ml/`.
- Fases 2 (controle de acesso) e 3 (GCP, com o Caio rodando os comandos); job da Previsão em produção (PD23).
