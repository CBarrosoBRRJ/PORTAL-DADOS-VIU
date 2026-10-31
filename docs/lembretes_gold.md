# Lembretes para validar no projeto da gold

Situações encontradas ao montar o site que precisam ser conferidas em `../PPD-GOLDEN-AGENCIAMENTO-MONDAY`
(tabela `gold_monday.gld_agenciamento_2026_sla_movimentos`). Ao resolver, registrar a decisão na ficha da tabela e
riscar aqui.

**27/10/2026 (D57): o site passou a ler só a gold.** Resolvidos do lado do site: o expediente sem almoço está na gold
(`sla_sem_almoco_horas`, R24, e a view `gld_agenciamento_2026_sla_entregas`); a divisão e o ranking de talentos
(`gld_agenciamento_2026_talentos_ano` e `..._talentos_ranking`) e o status das saídas sem entrega
(`gld_agenciamento_2026_saidas_status`) são tabelas da gold, calculadas a partir da silver no job. Seguem abertos os
pontos de dado da origem abaixo (vigência da exclusividade, Squad, Inbound não exclusivo, voltas para Entrada).

## L-G1 — Projeto volta para Entrada depois de Aguardando Feedback (21/10/2026)

Exemplo: [Globoplay] Gil do Vigor —
<https://globocorp.monday.com/boards/18429499488/pulses/12965546394>

| Passo | Status | Fase | Entrada | Horas úteis |
|---|---|---|---|---|
| 1 | Entrada | equipe | 01/09 09:59 | 0,25 |
| 2 | Em elaboração - Orçamentos | equipe | 01/09 10:14 | 0,09 |
| 3 | Em revisão - Validação Talento | equipe | 01/09 10:20 | 0,69 |
| 4 | Aguardando Feedback | cliente | 01/09 11:01 | 5,58 |
| 5 | Entrada | equipe | 01/09 16:36 | 0,02 |

No site (slide 1, regras C1–C3): tempo com a equipe até pronto = 0,25 + 0,09 + 0,69 = 1,03 h úteis ("até 1 dia");
calendário até pronto = 11:01 − 09:59 = 1,03 h corridas; mês = setembro. Os horários acima estão em minutos; a gold
calcula em segundos (entradas 09:59:21, 10:14:54, 10:20:05, 11:01:29), por isso as horas não fecham ao segundo a partir
da tabela.

O que validar:

1. **Volta para Entrada (passo 5):** é um pedido novo no mesmo card, um ajuste do cliente (retrabalho) ou um clique
   errado? A gold marca como retrabalho (R19); se for pedido novo, deveria abrir um ciclo novo de SLA.
2. **Entrada antes do expediente (09:59):** o tempo útil começa às 10h (0,25 h até 10:14). Conferir se é o esperado.
3. **Passos curtos seguidos** (Entrada 15 min → Orçamentos 5 min → Validação 41 min): o card é atualizado depois do
   trabalho feito (limitação L5 da ficha)? Se for, o tempo medido subestima o trabalho real.
4. Quantos projetos têm esse padrão (cliente → Entrada) — levantar a contagem antes de decidir.


## 23/10/2026 — achados da conferência gold × silver (site)

1. **Entradas de 2025 sem data de criação:** no board de 2025, 725 cards não têm `criado_em`; 576 têm `data_de_saida` e
   recebem data estimada (R2: saída − 5 dias úteis); 149 ficam fora de todas as contas. Até 22/10/2025 as estimadas são
   445 de 2.890 entradas (15%; Mercado 197, Inbound 117, Internos 75, Proativo 56). Há como recuperar a criação real
   (log do board de 2025, `item_id` no nome, export antigo)? Pendência Q11 no site.
2. **Entregas 2026, gold × silver:** gold (1ª entrega pelo log) 4.391 × silver (`data_de_saida`) 4.425 até 22/10.
   Listar os 34 cards da diferença para fechar a ponte (reenvio regravando a data? saída sem log?).
3. **Entregas 2025:** gold 2.294 × silver 2.297 (+ 11 cards do board de 2024 com saída em 2025). Confirmar se os do
   board de 2024 entram e por que a diferença é de 3.
4. **SLA:** a base de entregues jan–set passou de 2.428 (21/10) para 2.425 (23/10). Quais 3 projetos saíram e por quê?
5. **"Saíram sem entrega" por status:** o site mostra declinados, standby e encerrados juntos porque o
   `fluxo_mensal` só traz `evento = nao_seguiu`. Abrir o status (Declinado, Standby, Encerrado) numa coluna permitiria
   mostrar a divisão na dica do extrato.

## 23/10/2026 — validação em três camadas (agentes)

6. **Duplicados entre boards (F7):** "[Pacote Pipoca 2026]" Doce, Gourmet e Sal à Gosto estão no board 2025 (12965495388,
   12965495374, 12965495372) e no 2026 (12965343143, 12965343144, 12965343145); a R21 conta os do 2026 em 15/10/2025.
   Deduplicar por nome + data de saída entre boards.
7. **`criado_em` de cards sem `create_pulse` (F8):** a silver usa o 1º evento do log (lote MIA - Marca em 05 e 07/10).
   Usar `data_de_entrada` nesses casos. 10 cards ainda caem em outubro: 12965451578, 12965451308, 12965425482,
   12965450002, 12965366807, 12965366993, 12965424812, 12965450813, 12965402377, 12965480384.
8. **R2 com `data_de_entrada`:** 5 cards de 2026 com `criado_em` nulo têm `data_de_entrada` real e mesmo assim recebem
   estimativa (12965424763, 12965366908, 12965367218, 12965451258, 12965451261).
9. **Entregas sem ida ao cliente (F9):** 185 em 2026 vêm só da `data_de_saida` (R13). Definir com a equipe se
   Encerrado/Declinado com data de saída é entrega.
10. **Duplicados no mesmo board:** 2025 "[Bradesco] Tadeu | Conec" (4 em 11/07/2025), "[Pacote Efemérides] Giovanna Pitel"
   (2 em 04/08/2025); 2026: 15 pares, a maioria de 07/10/2026 (Seara, União, Yamaha, Mov). Conferir no monday.

## 23/10/2026 — validação final da página Início (4 validadores, D28 no site)

Tabelas `gld_agenciamento_entrada_diaria` e `gld_agenciamento_fluxo_mensal`. Os números do site batem com a gold e com a
silver (0 divergências); os itens abaixo são regras da gold que mudam ou podem mudar o que a tela mostra.

11. **R21 sem `data_de_saida` (complementa o item 7, efeito medido):** os 10 cards do lote de 05–07/10 (2 Encerrado,
    2 Declinado pelo Mercado, 6 Declinado Internamente) não têm `data_de_saida`, então a R21 não recua a entrada: caem
    em **outubro** pela `criado_em` e viram "não seguiu" sem data. **Efeito hoje: out/26 novos 508 → deveriam ser 498;
    saíram sem entrega 102 → 92 (74 → 64 na linha dos novos de outubro)**; jan–jul ganhariam esses 10. Proposta
    (R21b): com `data_de_saida` nula, `data_de_entrada < DATE(criado_em)` e status final, usar `data_de_entrada` como
    entrada; mês do "não seguiu" = mês da entrada. A checagem diária do site acompanha o total
    (`nao_seguiu_sem_data_ano` = 10 em 22/10).
12. **Status de "não seguiu" sem corte em `fim`:** `gld_agenciamento_fluxo_mensal.sql` (l. 170) e a diária usam o status
    **atual** e `status_desde` sem `<= fim`. Card declinado no dia da carga entra como "saiu sem entrega" com mês = mês
    da carga; no dia 1º, a situação do mês anterior o conta como "saiu sem entrega" e o extrato desse mês o conta em
    "seguem". Efeito pequeno e sem medida hoje; risco em todo dia 1º. Correção: `WHEN (STARTS_WITH(c.status,'Declinado')
    OR c.status IN ('Standby','Encerrado')) AND COALESCE(c.status_desde, pr.fim) <= pr.fim THEN 'nao_seguiu'` nas duas
    tabelas, como o corte que já existe para a entrega (`saida <= fim`).
13. **Lista fixa de boards:** a gold faz UNION das silvers 2024, 2025 e 2026. Se houver "Backlog 2027", os pedidos novos
    não entram e o site fica parado em 2026 **sem erro**. Há indício de recriação de cards abertos no board novo (2025
    tem 0 "em andamento"). Incluir a silver 2027 antes de jan/2027, checar duplicados entre boards (liga com o item 6) e
    pôr na pauta de dezembro.
14. **43 cards de setembro contados em outubro (a confirmar):** criados em 05–15/10 com `data_de_entrada` em 22–29/09 e
    saída depois da criação; a R21 só recua quando a saída é anterior à criação (ex.: 35 cards 13210… de 05/10,
    13210596339, 13210593647, 13212294488, 13238103426, 13300478913). Mais 11 com saída < criação, mas sem
    `data_de_entrada` válida (13278478050, 13359113888). Efeito possível: set/26 até 43 a menos e out/26 até 43 a mais
    (~8%). Medido por um validador só (S1); **confirmar a contagem** antes de decidir uma regra (ex.: usar
    `data_de_entrada` quando anterior à criação em até N dias, mesmo sem saída). Parente do item 7, outra causa.
15. **Meses passados mudam a cada carga:** a gold recalcula tudo com `state='active'` e o estado de hoje. Card arquivado
    some; card reaberto e declinado muda de mês (usa a última entrada no status); "não seguiu" depois entregue vira
    entregue; cadastro retroativo reescreve meses (90 cards do lote 12965… recuados para jan–set). O extrato de maio
    visto hoje ≠ o visto em junho. O site documenta "foto do dia". Se o Caio quiser histórico: snapshot mensal
    `..._fila_fechamento` (`mes_ref`) e coluna `fim` explícita nas duas tabelas (o site passaria a comparar `fim` em vez
    de `_processado_em`).
16. **`state` em 2024/2025:** a gold não filtra `state` nos boards 2024 e 2025 (hoje 100% `active`, sem efeito).
    Adicionar `state='active'` por consistência com 2026. Prioridade baixa.

## Complemento da revisão de 24/10/2026

- **PD19 — Data das saídas e identificação da carga:** obter eventos da Silver para Golden de entrada/fluxo; publicar `load_id` e `data_referencia` comuns, mês efetivo, status/motivo e sinalizador de data ausente/atribuída. Há dez saídas sem data em 2026, atribuídas ao mês de entrada no relatório. Reconciliar por mês e tipo as quatro situações, além do total; não substituir ausência por uma data observada fictícia.
- **PD20 — Continuidade multianual de Talentos:** Golden com identidade estável do pedido, board de origem, transferências e exclusividade na data do pedido. Mesma população e corte de entradas; dispensar troca manual de tabela em janeiro. Fonte atual continua configurada no board 2026.
- **PD21 — Tempo da equipe pronto na gold (SLA, D-SLA-5, 25/10/2026):** (1) fase própria para "Em elaboração - Retorno Marca/Executivo" (hoje o site tira pelo nome do status; é espera da marca, não trabalho da equipe); (2) manter na tabela de movimentos quem já teve a 1ª entrega e voltou à equipe (R1: hoje o projeto some do mês fechado até voltar ao cliente); (3) coluna de pacote/lote (hoje só o prefixo "[Pacote" no nome; 27 dos 28 "fora da curva" de jan–set são pacotes); (4) relógio para cards criados direto em Em Elaboração/Em revisão (sem Entrada, R11/R12); (5) tabela de pedidos em andamento, sem 1ª entrega, com as horas até a carga (para Kaplan-Meier: o mês parcial só fecha quando todos são entregues); (6) conferir 28 `encerrado_sem_entrega` e 19 `entrega_sem_aguardando` da validação de 25/10; (7) v2 sem almoço (10h–13h + 14h–19h) em `sla_util_horas`, para o site deixar de recalcular (C2).
- **PD13 permanece:** a curva atual é reconstruída, não fotografia fechada. Manter snapshots de referência sem reescrever o passado silenciosamente.

São requisitos locais preparados para análise no projeto da Golden; nenhuma alteração de BigQuery foi executada. Ver `docs/historico/REVISAO_2026-10-24.md` para evidências e critérios de aceite. No Atendimento, 170 × 160 foi resolvido por convenção explícita de mês atribuído; a ausência das datas na fonte continua pendente.

## 25/10/2026 — cadastro de exclusividade (Talentos; decisão 12 do Caio)

Levar à gold e à equipe de Talentos como **correção de cadastro** (PD01, PD02b, PD03). Conferido no BigQuery (só SELECT)
na silver `slv_agenciamento_2026_itens`, processada em 23/10/2026 11:05 UTC, pedidos de 01/01 a 22/10/2026 pela regra de
data da T1; SQL na ficha `docs/paginas/talentos.md`, seção 6.4.

- **L-T1 — Talentos com os dois vínculos no mesmo ano:** 7 talentos, **356 pedidos**, aparecem como exclusivos em parte
  dos pedidos e não exclusivos em outra (exclusividade na data do pedido, T2): Viviane Araújo 81/6, Jonas Fernando
  Sulzbach 3/65 (exclusivo intercalado com não exclusivo), Angélica 43/12, Sofia Miranda 41/3, Ana Paula Xongani 37/2,
  Mariana Spinelli 23/9, Luana Maluf 26/5. Validar se houve mudança real de contrato em cada data ou erro de cadastro;
  a gold precisa guardar a vigência do vínculo (PD01) para a divisão não depender da silver.
- **L-T2 — `talentos_exclusivos` preenchido com `exclusivo = FALSE`:** 25 cards em 2026, dos quais **6 do "Squad de
  Talentos"**. Um Squad formado só por talentos exclusivos conta hoje como não exclusivo (regra 60 da silver). Decidir na
  gold se o Squad herda o vínculo dos integrantes ou vira categoria própria (PD02b/PD03).

## 26/10/2026 — Inbound marcado como talento não exclusivo (D55 no site, PD24)

- Regra do Caio: **não existe Inbound de talento não exclusivo**; o que aparece assim na silver 2026 é erro de
  preenchimento (do talento ou do tipo de input). Contagem (mesmo critério de `app/sql/talentos_ano.sql`, hoje na gold
  `gld_agenciamento_2026_previsao_exclusividade_diaria`; carga de
  26/10/2026 09:01, dados até 25/10): jan 7 · fev 11 · mar 5 · abr 6 · mai 19 · jun 12 · jul 14 · ago 3 · set 1 ·
  out 19 (parcial) — **78 de 1.194 de jan–set (6,5%)**. Proposta: alarme na gold (Inbound com exclusivo = FALSE) e
  correção no cadastro; até lá, a Previsão conta esses pedidos como exclusivos.

## 26/10/2026 — status da saída sem entrega (D53 no site)

- O Atendimento separa as saídas sem entrega por **status do board** (Declinado Internamente, Standby, Declinado pelo
  Mercado, Declinado pelo talento, Encerrado) para a taxa de capacidade (A27: só Mercado, talento e Encerrado saem da
  base). ~~A `gld_agenciamento_fluxo_mensal` não guarda o status; o site refaz na silver 2026 (`app/sql/saidas_status.sql`,
  exceção como a D30-b).~~ **Resolvido em 27/10/2026 (D57):** tabela gold `gld_agenciamento_2026_saidas_status` (mês ×
  status). Segue como sugestão: coluna `status_saida` (ou motivo) no grão do fluxo para eventos `nao_seguiu`.
  Conferência de 26/10: silver = gold nos 10 meses de 2026 (974 no ano; 10 cards de outubro sem data de mudança no log).

