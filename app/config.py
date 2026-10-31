"""Configuração do site, lida do ambiente (no computador, também do .env da raiz)."""

import os
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

FUSO = ZoneInfo("America/Sao_Paulo")
PROJETO = os.environ.get("GCP_PROJECT_ID", "gglobo-viu-dados-hdg-prd")
# D57 (27/10/2026): o site só lê a gold (dataset gold_monday, job gold-agenciamento do PPD-GOLDEN-AGENCIAMENTO-MONDAY).
# Cada visual lê a sua tabela ou view; nenhuma regra de negócio é refeita aqui. Mapa página × gráfico × tabela na ficha
# de cada página (docs/paginas/) e no PRD (seção 8).
GOLD = os.environ.get("GOLD_DATASET", "gglobo-viu-dados-hdg-prd.gold_monday").strip()


def _tabela(variavel: str, nome: str) -> str:
    return os.environ.get(variavel, f"{GOLD}.{nome}").strip()


# tabelas (job seg–sex 09:00)
TAB_SLA = _tabela("TAB_SLA", "gld_agenciamento_2026_sla_movimentos")  # um passo por linha; R24 = horas sem almoço
TAB_ENTRADA = _tabela("TAB_ENTRADA", "gld_agenciamento_entrada_diaria")  # Início, Atendimento, Talentos (total)
TAB_FLUXO = _tabela("TAB_FLUXO", "gld_agenciamento_fluxo_mensal")  # o que aconteceu com cada safra, e em que mês
TAB_TALENTOS_ANO = _tabela("TAB_TALENTOS_ANO", "gld_agenciamento_2026_talentos_ano")  # divisão do ano (T1–T5)
TAB_TALENTOS_RANKING = _tabela("TAB_TALENTOS_RANKING", "gld_agenciamento_2026_talentos_ranking")  # top 10 (T6–T10)
TAB_SAIDAS_STATUS = _tabela("TAB_SAIDAS_STATUS", "gld_agenciamento_2026_saidas_status")  # A26: status das saídas
TAB_LOTES = _tabela("TAB_LOTES", "gld_agenciamento_2026_previsao_lotes")  # diagnóstico do mês da previsão (S6)
# views (sem carga própria: refletem a tabela de base na hora; a recarga segue o `modified` da base)
TAB_SLA_ENTREGAS = _tabela("TAB_SLA_ENTREGAS", "gld_agenciamento_2026_sla_entregas")  # C1–C4, C9, C14: um por entrega
TAB_SLA_ENTREGAS_STATUS = _tabela("TAB_SLA_ENTREGAS_STATUS", "gld_agenciamento_2026_sla_entregas_status")  # K1
TAB_FILA = _tabela("TAB_FILA", "gld_agenciamento_fila_mensal")  # extrato do mês do Início (E7)
TAB_ATENDIMENTO = _tabela("TAB_ATENDIMENTO", "gld_agenciamento_atendimento_mensal")  # A13/A27: fila mês a mês
TAB_PREVISAO_MENSAL = _tabela("TAB_PREVISAO_MENSAL", "gld_agenciamento_previsao_mensal")  # S1, S2 da previsão
TAB_EXCLUSIVIDADE_MENSAL = _tabela("TAB_EXCLUSIVIDADE_MENSAL", "gld_agenciamento_2026_previsao_exclusividade_mensal")
# única leitura fora da gold: a sensibilidade de 2025 do ML (ml/sensibilidade, fonte fraca, não vai à tela). A silver 2025
# não tem gold; a série não entra em nenhum gráfico
TAB_SILVER_2025 = os.environ.get(
    "TAB_SILVER_2025", "gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2025_itens").strip()

# minutos entre duas checagens do metadado das tabelas (recarga só se a tabela mudou; também o intervalo de
# nova tentativa depois de uma falha)
RECARGA_MIN = int(os.environ.get("RECARGA_MIN", "5"))

# agenda da gold (job gold-agenciamento, seg–sex 09:00 de Brasília): passada a tolerância num dia útil, uma tabela
# que não é daquele dia é considerada desatualizada e a tela avisa
GOLD_HORA = int(os.environ.get("GOLD_HORA", "9"))
GOLD_TOLERANCIA_MIN = int(os.environ.get("GOLD_TOLERANCIA_MIN", "45"))

# controle de acesso: "off" só no computador (D10). Enquanto a fase 2 não existe, o site não sobe sem "off".
AUTH = os.environ.get("AUTH", "on").strip().lower()
# ambiente de desenvolvimento: templates relidos a cada página e versão dos estáticos refeita a cada 5 s
DEV = os.environ.get("DEV", "true" if AUTH == "off" else "false").strip().lower() == "true"
# modo apresentação (reunião no computador do Caio, D30): só as seções na_reuniao aparecem (ou as de SECOES_VISIVEIS,
# separadas por vírgula) e nada de tela com dados fictícios, mesmo com DEV ligado
MODO_APRESENTACAO = os.environ.get("MODO", "").strip().lower() == "apresentacao"
# D59 (Caio, 27/10/2026): menu lateral fora por ora, para o portal ter cara de apresentação (navegação pelas abas do
# topo); MENU_LATERAL=on traz de volta. No celular a gaveta "Áreas" continua
MENU_LATERAL = os.environ.get("MENU_LATERAL", "off").strip().lower() in ("on", "true", "1")
SECOES_VISIVEIS = frozenset(s.strip() for s in os.environ.get("SECOES_VISIVEIS", "").split(",") if s.strip())
# Cloud Run define K_SERVICE: lá, AUTH=off nunca é aceito (trava independente da fase 2)
EM_PRODUCAO = bool(os.environ.get("K_SERVICE"))
# D62 (Caio, 27/10/2026): sincronia com a cola do apresentador (../PPD-AGENCIAMENTO-COLA, porta 8200): o portal guarda em
# /sinc a página em que está, e portal e cola seguem um ao outro. Só no computador (nunca em produção); SINC=off desliga
# F12/A32 (auditoria de 31/10/2026): na V2 o padrão é DESLIGADO (a V2 não usa a cola); SINC=on liga, só no computador
SINC = not EM_PRODUCAO and os.environ.get("SINC", "off").strip().lower() in ("on", "true", "1")
SINC_ORIGENS = ("http://127.0.0.1:8200", "http://localhost:8200")
# base congelada (batalha de agentes, 25/10/2026, B-N8): na reunião, a base lida na subida do servidor não se recarrega
# (nenhuma carga nova troca uma leitura do estudo na frente da diretoria). D63 (Caio, 28/10/2026): ligada por padrão no
# computador — os números ficam os da carga lida na subida do servidor, sem recarga por hora e sem o aviso de "a base não
# atualizou" (o rodapé datado continua). CONGELAR=false volta a recarregar. Nunca em produção.
CONGELAR = not EM_PRODUCAO and os.environ.get("CONGELAR", "true").strip().lower() == "true"
# D65 (Caio, 31/10/2026): corte e congelamento dos dados para a reunião de 04/11/2026 (outubro completo). Vale no
# computador e em produção. Com o corte ligado, o portal aceita cargas novas enquanto o fim delas (regra E3, app/corte.py)
# for anterior ao corte; a 1ª carga com fim >= corte (até CORTE_FOLGA_DIAS depois: 31/10 é sábado e a carga agendada
# seguinte, de 02/11, cobre até 01/11) é a última aceita: congela e fica gravada em BASE_CONGELADA_DIR (parquet + ficha
# JSON por tabela). Daí em diante, nenhuma carga troca a base. Com os arquivos presentes (no computador ou na imagem do
# Cloud Run), o portal lê só deles, sem consultar o BigQuery. Descongelar: CORTE_DADOS=off (docs/congelar_outubro.md).
# Enquanto o corte estiver ligado, ele substitui o CONGELAR acima na recarga (o CONGELAR continua parando o job, J5).
_CORTE_TXT = os.environ.get("CORTE_DADOS", "2026-10-31").strip().lower()
CORTE_DADOS = None if _CORTE_TXT in ("", "off", "false", "0", "nao", "não") else date.fromisoformat(_CORTE_TXT)
CORTE_FOLGA_DIAS = int(os.environ.get("CORTE_FOLGA_DIAS", "1"))
BASE_CONGELADA_DIR = Path(os.environ.get("BASE_CONGELADA_DIR", str(RAIZ / "app" / "base_congelada")))
# previsão de demanda (D47): a página só lê o JSON que o job de ML grava (ml/saida/previsao.json); o site não depende
# das bibliotecas de ML. No computador, a carga nova da gold de entradas dispara o job em segundo plano
# (PREVISAO_JOB=off desliga; PREVISAO_PYTHON = o Python que tem as bibliotecas). Em produção o job é separado.
PREVISAO_ARQ = Path(os.environ.get("PREVISAO_ARQ", str(RAIZ / "ml" / "saida" / "previsao.json")))
PREVISAO_JOB = not EM_PRODUCAO and os.environ.get("PREVISAO_JOB", "on").strip().lower() not in ("off", "false", "0")
PREVISAO_PYTHON = os.environ.get("PREVISAO_PYTHON", "").strip()
LABELS = {"projeto": "ppd-agenciamento-sla", "app": "relatorios-agenciamento"}

# Iniciativas com dados no servidor (Caio e gerente, 30/10/2026; ficha docs/paginas/iniciativas.md). Backend "sqlite" no
# computador (arquivo e anexos FORA do Google Drive: SQLite em pasta sincronizada pode corromper) e "firestore" no Cloud
# Run (Firestore + bucket privado do Cloud Storage, credenciais ADC da conta de serviço). Roteiro: docs/deploy_iniciativas.md
_INI_LOCAL = Path.home() / ".ppd-agenciamento-v2"
INICIATIVAS_BACKEND = os.environ.get("INICIATIVAS_BACKEND", "firestore" if EM_PRODUCAO else "sqlite").strip().lower()
INICIATIVAS_DB = Path(os.environ.get("INICIATIVAS_DB", str(_INI_LOCAL / "iniciativas.db")))
INICIATIVAS_ANEXOS = Path(os.environ.get("INICIATIVAS_ANEXOS", str(_INI_LOCAL / "anexos")))
INICIATIVAS_FIRESTORE_DB = os.environ.get("INICIATIVAS_FIRESTORE_DB", "(default)").strip()
INICIATIVAS_BUCKET = os.environ.get("INICIATIVAS_BUCKET", "").strip()
INICIATIVAS_PREFIXO = os.environ.get("INICIATIVAS_PREFIXO", "").strip()  # prefixo das coleções do Firestore
# escrita (criar, editar, mover, excluir, anexar): ligada no computador; em produção DESLIGADA por padrão (D10: sem
# controle de acesso, ninguém de fora escreve). INICIATIVAS_EDICAO=on em produção só com o serviço atrás do IAP (AUTH=iap)
INICIATIVAS_EDICAO = os.environ.get("INICIATIVAS_EDICAO", "off" if EM_PRODUCAO else "on").strip().lower() in ("on", "true", "1")
# D66 (Caio, 31/10/2026): AUTH=publico = link aberto, sem login, de propósito e só nesta fase (compartilhamento controlado
# pelo Caio; depois volta o IAP para os 4 e-mails). Ninguém identificado = ninguém escreve: a edição fica desligada,
# mesmo com INICIATIVAS_EDICAO=on
if AUTH == "publico":
    INICIATIVAS_EDICAO = False
# AUTH=iap (exceção temporária à D10: publicação para a reunião do gerente): o serviço fica atrás do Identity-Aware Proxy
# e o app confere, em toda requisição, o cabeçalho assinado pelo IAP (x-goog-iap-jwt-assertion) com este público
# (audience). Sem IAP_AUDIENCE, o app não sobe com AUTH=iap. Ver app/iap.py e docs/deploy_iniciativas.md
IAP_AUDIENCE = os.environ.get("IAP_AUDIENCE", "").strip()
# D66b (Caio, 31/10/2026): espelho TEMPORÁRIO numa VPS própria enquanto o acesso no GCP não é liberado. Sem credencial
# nenhuma do GCP fora dele: o portal lê as tabelas de arquivos (ESPELHO_DIR, gerados no computador por
# tools/gerar_espelho.py) e nunca consulta o BigQuery. Vazio = desligado (o normal)
ESPELHO_DIR = os.environ.get("ESPELHO_DIR", "").strip()
# D66b: com CHAVE_ACESSO definida, só entra quem abriu o link com ?k=<chave> (vira um cookie de 30 dias); o resto, 403.
# É o "qualquer pessoa com o link" literal: o endereço sem a chave não abre nada
CHAVE_ACESSO = os.environ.get("CHAVE_ACESSO", "").strip()
