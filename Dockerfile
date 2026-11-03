# Imagem do site de relatórios (Cloud Run): FastAPI + Uvicorn, 1 worker por instância, porta $PORT, sem --reload.
# O site NÃO sobe com AUTH=off quando K_SERVICE (Cloud Run) está definido — ver app/config.py e app/main.py.
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=America/Sao_Paulo \
    DEV=false

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
# D65 (31/10/2026): a base congelada do corte (app/base_congelada/) já vem no COPY acima; a Previsão lê o retrato gravado
# pelo job de ML local (o job não roda no Cloud Run). Mesmo caminho do config.PREVISAO_ARQ (/app/ml/saida/previsao.json);
# sem o arquivo, o build falha (de propósito: a página não pode ir sem números)
COPY ml/saida/previsao.json ./ml/saida/previsao.json
# F01 (auditoria de 31/10/2026): com o corte ligado (CORTE_DADOS, padrão do código), o build PARA se a base congelada
# estiver ausente, incompleta ou incoerente com o manifesto, se a Previsão não for do mesmo corte e da mesma carga, ou se
# a LIA não for até o corte. Sem rede e sem BigQuery. O arranque em produção confere a base de novo (congelamento.exigir)
# D67 (Caio, 03/11/2026): base congelada da carga de 03/11 (dados até 02/11; folga de 2 dias no config.py). O build
# volta a conferir a base, a Previsão e a LIA. Descongelar: off (docs/congelar_outubro.md)
ARG CORTE_DADOS=2026-10-31
RUN python -m app.conferir_base

# roda sem privilégios de root
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --proxy-headers --forwarded-allow-ips='*'"]
