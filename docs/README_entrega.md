# Entrega do portal "ViU Agenciamento" (V2) — índice para a auditoria

Escrito em 31/10/2026. Projeto: `PPD-AGENCIAMENTO-SLA-V2` (porta local 8400). Reunião de diretoria em **04/11/2026**,
apresentada pelo gerente do Caio, com os dados congelados em **31/10/2026**. Nada publicado.

## 1. Comece por aqui

| Documento | Para quê |
|---|---|
| [PRD_V2.md](PRD_V2.md) | **PRD principal da entrega**: visão geral, arquitetura, uma seção por página (fonte, regras, memória de cálculo, números da carga de 30/10/2026, SQL, interações, testes, decisões), regras transversais, dados e congelamento, segurança, desempenho, testes, pendências |
| [PRD_V2.md, seção 10](PRD_V2.md#10-pontos-para-a-auditoria) | **Pontos para a auditoria** (A1–A45): suspeitas de bug, ficha × código, números fixos, regras duplicadas, tratamento de erro e desempenho, com arquivo e linha. Nada foi corrigido |
| [../CLAUDE.md](../CLAUDE.md) | Guia de retomada do projeto (estado e regras de trabalho) |
| [PRD.md](PRD.md) | Histórico e decisões D1–D65; decisões abertas DC1–DC16 na seção 9.7; achados nos dados na seção 10 |

## 2. Fichas por página

[paginas/](paginas/) — uma ficha por página, com a memória de cálculo datada, o SQL para reproduzir no BigQuery, as
validações e o histórico. O índice antigo está em [paginas/README.md](paginas/README.md) (não lista as fichas da V2;
ponto A22).

| Página | Ficha |
|---|---|
| Capa | [paginas/capa.md](paginas/capa.md) |
| Roadmap (hub) | [paginas/roadmap.md](paginas/roadmap.md) |
| Demanda | [paginas/inicio.md](paginas/inicio.md) |
| Talentos | [paginas/talentos.md](paginas/talentos.md) |
| SLA e estudo "Como medimos" | [paginas/sla.md](paginas/sla.md) (bloco "V2" no topo vale sobre o resto) |
| LIA | [paginas/lia.md](paginas/lia.md) |
| Vídeo "A LIA na prática" | [paginas/lia-na-pratica.md](paginas/lia-na-pratica.md) |
| Iniciativas | [paginas/iniciativas.md](paginas/iniciativas.md) |
| Previsão | [paginas/previsao.md](paginas/previsao.md) |
| Encerramento | [paginas/encerramento.md](paginas/encerramento.md) |
| Ocultas: Atendimento, Resultado, Qualidade, O que falta | [paginas/atendimento.md](paginas/atendimento.md), [paginas/demais.md](paginas/demais.md), [paginas/o_que_falta.md](paginas/o_que_falta.md) |

## 3. Roteiros

| Roteiro | Conteúdo |
|---|---|
| [deploy_iniciativas.md](deploy_iniciativas.md) | Deploy temporário no Cloud Run com IAP (`AUTH=iap`, exceção à D10 **a aprovar pelo Caio**), Firestore e bucket das Iniciativas, papéis, verificação e como tirar do ar. Nada executado |
| [congelar_outubro.md](congelar_outubro.md) | Corte e congelamento em 31/10/2026 (D65): caminhos A/B do fim de semana, passos 0–6, conferência sem BigQuery, deploy e como descongelar |

## 4. Projetos antigos (legado, só leitura)

[legado/](legado/) — **não fazem parte da entrega atual**.

| Documento | Projeto |
|---|---|
| [legado/PRD_portal_original_8100.md](legado/PRD_portal_original_8100.md) | `../PPD-AGENCIAMENTO-SLA`, o portal apresentado em 28/10 (congelado; cópias em `_congelado/`) e o que a V2 mudou |
| [legado/PRD_cola_8200.md](legado/PRD_cola_8200.md) | `../PPD-AGENCIAMENTO-COLA`, a cola do apresentador (`/sinc`, `/cola/{ficha}`); **não funciona com a V2 publicada** |
| [legado/PRD_interveniencia_8300.md](legado/PRD_interveniencia_8300.md) | `../PPD-FECHAMENTO-INTERVENIENCIA`, o deck de fechamentos de interveniência (bronze do SharePoint) |

## 5. Como conferir

```powershell
cd "G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-SLA-V2"
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m pytest tests -q -p no:cacheprovider   # 564 testes, sem BigQuery
```

Conferências contra o BigQuery (só leitura, credenciais do gcloud-viu): `tools/checar_reuniao.py`,
`tools/conferir_estudo.py`, `tools/congelar_base.py --conferir` (sem BigQuery, sobre a base congelada). Layout:
`node tools/conferir_layout.mjs` com o servidor no ar. Registros de validação em [validacao/](validacao/); revisões e
auditorias anteriores em [historico/](historico/).
