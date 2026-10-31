# Prompt: revisão completa do projeto pelo Codex

> **Histórico (prompt de 22/10/2026).** O `tools/conferir_entrega.py` citado abaixo foi aposentado e movido para `_descartados/2026-10-26/tools/` em 26/10/2026 (regra antiga, com almoço); hoje a conferência é `tools/checar_reuniao.py` e `tools/conferir_estudo.py`.

Uso: colar no Codex com a pasta `G:/Meu Drive/Workspace/globo/scripts/PPD-AGENCIAMENTO-SLA` aberta. Atualizar a data
e a lista de pendências antes de usar de novo.

---

Você é um revisor sênior (dados, backend Python, front-end e acessibilidade). Revise o projeto
`PPD-AGENCIAMENTO-SLA` inteiro e me entregue um relatório em português do Brasil. Não altere nada ainda: primeiro
o relatório; mudanças só depois que eu aprovar.

## Contexto

Site interno de relatórios (FastAPI + Jinja2, HTML/CSS/JS sem framework) que lê a tabela gold
`gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos` (BigQuery; variável `TAB_SLA` no `.env`)
e mostra apresentações de uma página por slide. Hoje existe a área "Gestão de orçamentos" com a seção SLA (slide
"Quanto tempo levamos para entregar um orçamento?") e páginas em branco (início da área e regras).

Leia primeiro, nesta ordem: `CLAUDE.md`, `docs/PRD.md` (arquitetura, regras de acesso A1–A10, regras de cálculo
C1–C11 na seção 9.1, decisões D1–D18, achados F1–F3, custos, histórico), `README.md`, `docs/lembretes_gold.md`.
A tabela de origem está documentada no projeto irmão:
`../PPD-GOLDEN-AGENCIAMENTO-MONDAY/docs/tabelas/gld_agenciamento_2026_sla_movimentos.md` (regras R1–R22, em especial
R13 horas úteis, R14 calendário de feriados, R15 fases) e `../PPD-GOLDEN-AGENCIAMENTO-MONDAY/docs/melhorias_processo.md`
(L10 e L11 foram anotados por este projeto).

## Limites (obrigatórios)

- GCP corporativo: **só consultas**. Nunca criar, alterar ou apagar nada no BigQuery, Cloud Run ou IAM. Consultas
  de leitura são permitidas com as credenciais locais (`CLOUDSDK_CONFIG=C:\Users\CCMB\AppData\Roaming\gcloud-viu`,
  `GOOGLE_APPLICATION_CREDENTIALS=...\gcloud-viu\application_default_credentials.json`); informe o volume lido.
- Nenhuma API paga de LLM, embeddings ou avaliadores (regra do projeto, D2). Não proponha isso como melhoria.
- Regras de negócio (C1–C11) não mudam por conta própria: se discordar de uma, explique e deixe a decisão para mim.
- Venv: `C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe`. Testes: `python -m pytest tests -q`.
  Pode rodar `tools/conferir_entrega.py` e `tools/conferir_expediente.py` (leitura) e subir o site localmente com
  `AUTH=off` (ver README). Nunca sugira publicar com `AUTH=off` (D10).

## O que revisar

1. **Cálculos** (`app/apresentacoes/gestao_orcamentos/sla/calculos.py`, `app/expediente.py`, `app/sla.py`,
   `app/formato.py`):
   - cada regra C1–C11 do PRD está implementada como descrita? Aponte divergências com arquivo e linha;
   - o calendário de `expediente.py` reproduz a R14 da gold (feriados fixos, móveis pela Páscoa, 2020 até o ano
     seguinte)? `tools/conferir_expediente.py` deve dar diferença zero contra `sla_util_horas`;
   - reproduza os números da tela de forma independente (SQL no BigQuery ou pandas): 2.428 entregues jan–set,
     mediana 15,2 h com a equipe, 2,87 dias corridos, 53% em até 16 h, faixas por mês, exclusivos 13 h × não
     exclusivos 21 h. Confirme ou aponte diferenças;
   - casos de borda: projeto cuja 1ª ida ao cliente é o passo 1, passos sem `saida`, `exclusivo` nulo, mês sem
     entregas, virada de ano (jan/2027), `_processado_em` em janeiro (C7 e `periodo`), arredondamento C8 quando
     `ate1 == ate2`;
   - há algo na análise F3 (quinta/sexta dobram a espera) ou nos lembretes `docs/lembretes_gold.md` que invalide
     um número mostrado?
2. **Backend** (`app/main.py`, `app/dados.py`, `app/config.py`): cache e recarga pelo metadado (thread-safety sob
   vários workers do Uvicorn, o que acontece se o BigQuery falhar no `lifespan`), tratamento de erros, cabeçalhos
   de segurança (CSP com `style-src-attr 'unsafe-inline'` — há alternativa?), versionamento dos estáticos,
   `auto_reload` do Jinja, logs, pontos de falha em produção no Cloud Run (mín. 0 instâncias, 2 máx.).
3. **Front-end** (`app/templates/*.html`, `app/apresentacoes/**/template.html`, `app/static/*.css|js`): CSS com
   regras mortas ou redundantes (o arquivo teve muitas emendas — liste o que pode sair, ex.: `--trilha`,
   `.chave-meta`, `.legenda-dica`, `.slide-rodape`), seletores que se cancelam, container queries, comportamento
   sem JS, animação com `prefers-reduced-motion`, o deslizar da pílula entre páginas (sessionStorage), o menu
   recolhível (localStorage), a barra inferior no celular.
4. **Acessibilidade** (WCAG 2.2 AA): nomes acessíveis, ordem de foco, foco visível, gaveta do menu (foco e Esc),
   contraste (medir cores reais do CSS), leitor de tela no gráfico (texto por mês), `aria-current`, `aria-live`,
   título da página, tamanho de alvo de toque na barra inferior.
5. **Testes** (`tests/`): o que falta cobrir (ex.: recarga pelo metadado, `versao_estaticos`, grupo inválido,
   página inicial, 404, C7 na virada do ano). Os dados sintéticos de `tests/conftest.py` estão corretos em relação
   às regras? Proponha casos novos com valores calculados à mão.
6. **Documentação**: PRD, CLAUDE.md, README e `docs/lembretes_gold.md` estão coerentes entre si e com o código?
   Liste afirmações desatualizadas (nomes de arquivos, endereços, números, regras revertidas como "sem Entrada").
   A estimativa de custo (PRD seção 7) continua válida com o desenho atual?
7. **Pronto para a próxima fase**: o que falta para a fase 2 (controle de acesso por link no e-mail, A1–A10) e
   para a fase 3 (deploy): não há `Dockerfile`, `.gcloudignore` nem `requirements` fixados para produção; avalie o
   que criar e os riscos (segredos, `AUTH`, porta, `--reload` fora do computador).

## Formato do relatório

1. Resumo em 5 linhas: estado geral e os 3 problemas mais graves.
2. Achados em tabela, ordenados por gravidade (bloqueia / grave / médio / baixo): `arquivo:linha`, o que está
   errado, como reproduzir ou medir, correção proposta (trecho de código quando couber).
3. Divergências de cálculo com os números que você obteve de forma independente (consulta ou script usado).
4. Melhorias sugeridas (não defeitos), com esforço estimado (P/M/G) e benefício.
5. Lista do que você rodou (comandos, bytes lidos no BigQuery) e do que não conseguiu verificar.

Seja específico e verificável; evite elogios e generalidades. Se precisar de uma decisão minha para seguir,
pergunte no fim do relatório, numerado.
