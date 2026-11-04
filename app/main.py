"""Site de relatórios do Agenciamento (FastAPI). Rodar no computador: ver README."""

import hashlib
import json
import mimetypes
import secrets
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, select_autoescape
from starlette.concurrency import run_in_threadpool

from app import config, congelamento, dados, formato, iap
from app.apresentacoes import descobrir
from app.apresentacoes.gestao_orcamentos import SLUG, SLUG_ANTIGO
from app.dados import DadosIndisponiveis

if config.AUTH == "off" and config.EM_PRODUCAO:
    # A10/D10: no Cloud Run o site nunca sobe sem controle de acesso, por engano ou de propósito
    raise RuntimeError("AUTH=off não é aceito em produção (K_SERVICE definido).")
if config.AUTH == "iap":
    # exceção temporária à D10 (30/10/2026, publicação para a reunião do gerente): o serviço fica atrás do IAP e o app
    # confere o cabeçalho assinado pelo IAP em toda requisição (app/iap.py). Sem o público esperado, não sobe
    if not config.IAP_AUDIENCE:
        raise RuntimeError("AUTH=iap exige IAP_AUDIENCE (público do IAP; ver docs/deploy_iniciativas.md).")
    iap.iniciar_renovacao()  # F06: as chaves públicas do IAP já vêm sendo buscadas, em segundo plano, antes da 1ª página
elif config.AUTH == "publico":
    # D66 (Caio, 31/10/2026): exceção temporária e explícita à D10 — link aberto (sem login), só leitura (a edição das
    # Iniciativas é desligada em config). Volta para AUTH=iap quando o acesso for restrito aos e-mails
    pass
elif config.AUTH != "off":
    # D10: enquanto o controle de acesso (fase 2) não existe, o site só roda no computador, com AUTH=off
    raise RuntimeError("Controle de acesso ainda não implementado: rode com AUTH=off, só no computador.")

PASTA = Path(__file__).resolve().parent
APRESENTACOES = descobrir()
POR_SLUG = {a.slug: a for a in APRESENTACOES}

class _CarregadorConferido(FileSystemLoader):
    """No computador (DEV, auto_reload) o Jinja confere a data de cada template a cada página; no Google Drive cada
    consulta custa ~8 ms (≈ 40 ms por página). Desempenho, 31/10/2026: a data é conferida no máximo a cada 2 s."""

    def get_source(self, environment, template):
        fonte, nome, em_dia = super().get_source(environment, template)
        visto = {"em": time.monotonic(), "ok": True}

        def conferir() -> bool:
            if visto["ok"] and time.monotonic() - visto["em"] < 2:
                return True
            visto.update(em=time.monotonic(), ok=em_dia())
            return visto["ok"]

        return fonte, nome, conferir


ambiente = Environment(
    loader=ChoiceLoader([_CarregadorConferido(PASTA / "templates"), _CarregadorConferido(PASTA / "apresentacoes")]),
    autoescape=select_autoescape(["html"]),
    auto_reload=config.DEV,  # fora do computador os templates não mudam: não reler o disco a cada página
)
ambiente.filters.update(formato.FILTROS_JINJA)


def _hash_estaticos() -> str:
    """Resumo de todos os arquivos estáticos pelo caminho, tamanho e data de modificação: muda quando qualquer arquivo
    muda, sem ler o conteúdo (F20, 31/10/2026: antes lia ~1 MB a cada conferência)."""
    h = hashlib.sha1()
    for p in sorted((PASTA / "static").rglob("*")):
        if p.is_file():
            info = p.stat()
            h.update(f"{p.relative_to(PASTA).as_posix()}|{info.st_size}|{info.st_mtime_ns}\n".encode())
    return h.hexdigest()[:12]


_versao = {"valor": _hash_estaticos(), "lido_em": time.monotonic(), "refazendo": False}


def _refazer_versao() -> None:
    try:
        _versao["valor"] = _hash_estaticos()
    finally:
        _versao.update(lido_em=time.monotonic(), refazendo=False)


def versao_estaticos() -> str:
    """Versão dos estáticos nos links (?v=): o navegador guarda CSS/JS por um ano e só baixa de novo quando o
    conteúdo muda. Em produção é calculada uma vez; no computador, refeita no máximo a cada 5 s, em segundo plano
    (desempenho, 31/10/2026: reler os estáticos no Google Drive custava 0,5–0,9 s a cada 5 s, dentro da troca de
    página); a página responde com a versão atual e a seguinte já leva a nova."""
    if config.DEV and not _versao["refazendo"] and time.monotonic() - _versao["lido_em"] > 5:
        _versao["refazendo"] = True
        threading.Thread(target=_refazer_versao, name="versao-estaticos", daemon=True).start()
    return _versao["valor"]


ambiente.globals["v"] = versao_estaticos
templates = Jinja2Templates(env=ambiente)


@asynccontextmanager
async def ao_iniciar(_app):
    # tenta carregar as tabelas e os cálculos ao subir; se o BigQuery falhar, o processo sobe mesmo assim
    # (a primeira requisição tenta de novo) — processo vivo e dados prontos são coisas diferentes (/saude)
    if config.EM_PRODUCAO:
        # F01 (auditoria de 31/10/2026): com o corte ligado, a instância só sobe com a base congelada completa e coerente
        # (manifesto); sem ela, BaseInvalida derruba o arranque e o Cloud Run mantém a revisão anterior
        congelamento.exigir()
    for a in APRESENTACOES:
        if a.inicio:
            try:
                a.inicio({})
            except DadosIndisponiveis as e:
                dados.log("ERROR", "dados indisponíveis ao iniciar", secao=a.slug, erro=str(e))
            except Exception as e:  # noqa: BLE001 — F05: uma seção com falha não derruba o portal
                dados.log("ERROR", "falha ao aquecer a seção ao iniciar", secao=a.slug, erro=f"{type(e).__name__}: {e}"[:300])
        for s in _visiveis(a):  # F20: só as seções da navegação (as ocultas calculam se alguém abrir o endereço)
            try:
                s.montar({})
            except DadosIndisponiveis as e:
                dados.log("ERROR", "dados indisponíveis ao iniciar", secao=f"{a.slug}/{s.slug}", erro=str(e))
            except Exception as e:  # noqa: BLE001 — F05: idem; a página tenta de novo quando alguém a abrir
                dados.log("ERROR", "falha ao aquecer a seção ao iniciar", secao=f"{a.slug}/{s.slug}",
                          erro=f"{type(e).__name__}: {e}"[:300])
    _aquecer_paginas()
    yield


def _visiveis(a) -> tuple:
    return a.visiveis()  # seções da navegação (D59): sem as ocultas e, no modo apresentação, só as da reunião


def _aquecer_paginas() -> None:
    """Desempenho (31/10/2026): a 1ª visita de cada página não paga a compilação dos templates (até ~0,9 s) nem o
    estudo "Como medimos" (sorteio do exemplo e cobertura, ~1 s). Só otimização: falhas ficam no log."""
    nomes = ["capa.html", "encerramento.html", "como_medimos.html", "indisponivel.html", "o_que_falta.html"]
    for a in APRESENTACOES:
        nomes.append(f"{a.pasta}/inicio.html")
        for s in _visiveis(a):
            nomes.append(a.template(s))
            if s.montar_estudo is not None:
                try:
                    s.montar_estudo({})
                except Exception as e:  # noqa: BLE001 — a página calcula na hora se precisar
                    dados.log("WARNING", "estudo não aquecido ao iniciar", secao=f"{a.slug}/{s.slug}", erro=str(e)[:200])
    for nome in nomes:
        try:
            ambiente.get_template(nome)
        except Exception as e:  # noqa: BLE001
            dados.log("WARNING", "template não aquecido ao iniciar", template=nome, erro=str(e)[:200])


app = FastAPI(title="Relatórios Agenciamento", docs_url=None, redoc_url=None, openapi_url=None, lifespan=ao_iniciar)
app.add_middleware(GZipMiddleware, minimum_size=1000)
# Caio, 03/11/2026 (bug do gerente): o Python do Windows e da imagem slim não conhece .webp/.woff2, e o StaticFiles servia
# esses arquivos como application/octet-stream (com nosniff): o "Abrir em nova aba" das imagens baixava o arquivo
for _tipo, _ext in (("image/webp", ".webp"), ("font/woff2", ".woff2"), ("text/vtt", ".vtt"), ("video/mp4", ".mp4")):
    mimetypes.add_type(_tipo, _ext)
app.mount("/static", StaticFiles(directory=PASTA / "static"), name="static")
# Iniciativas com dados no servidor (30/10/2026): API JSON em /viu-agenciamento/iniciativas/api/... (antes das rotas
# genéricas /{slug}/{secao})
from app.apresentacoes.gestao_orcamentos.iniciativas.api import (
    router as iniciativas_api,
)

app.include_router(iniciativas_api)

# Scripts só do próprio site. Estilos: arquivo do site + blocos <style> com o nonce da página (alturas do gráfico);
# atributos style="" proibidos. Mudanças de estilo feitas pelo script (element.style) não são afetadas pela CSP.
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'nonce-{nonce}'; style-src-attr 'none'; "
       "img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; "
       "form-action 'self'; object-src 'none'")


COOKIE_CHAVE = "viu_acesso"


def _chave_ok(request: Request):
    """D66b: True se não há CHAVE_ACESSO ou se a requisição traz o cookie dela; ?k=<chave> certo responde com um
    redirecionamento para o mesmo endereço sem o k, gravando o cookie; senão, 403."""
    if not config.CHAVE_ACESSO:
        return True
    marca = hashlib.sha256(config.CHAVE_ACESSO.encode()).hexdigest()
    # em bytes: compare_digest com str recusa caractere fora do ASCII (TypeError = 500); assim, chave errada = 403
    if secrets.compare_digest(request.cookies.get(COOKIE_CHAVE, "").encode(), marca.encode()):
        return True
    if secrets.compare_digest(request.query_params.get("k", "").encode(), config.CHAVE_ACESSO.encode()):
        resto = [(c, v) for c, v in request.query_params.multi_items() if c != "k"]
        destino = request.url.path + (("?" + urlencode(resto)) if resto else "")
        r = RedirectResponse(destino, status_code=303)
        r.set_cookie(COOKIE_CHAVE, marca, max_age=30 * 24 * 3600, httponly=True, secure=request.url.scheme == "https"
                     or request.headers.get("x-forwarded-proto") == "https", samesite="lax")
        return r
    return Response("Acesso só pelo link completo que você recebeu.", status_code=403, media_type="text/plain")


@app.middleware("http")
async def cabecalhos(request: Request, call_next):
    request.state.nonce = secrets.token_urlsafe(16)  # novo a cada resposta
    request.state.usuario = ""
    chave_ok = _chave_ok(request)
    if chave_ok is not True:  # D66b: sem a chave do link (ou o cookie dela), nada passa; com ?k= certo, grava o cookie
        resposta = chave_ok
    elif config.AUTH == "iap":
        # AUTH=iap: sem o cabeçalho assinado pelo IAP (ou com um inválido), nada passa, nem os estáticos nem /saude
        # (A29: nenhuma sonda HTTP usa /saude no deploy). F06: a conferência pode buscar as chaves do IAP (rede), então
        # roda fora do event loop; chaves indisponíveis = 503 (com log em app/iap.py), token inválido = 401
        r = await run_in_threadpool(iap.autenticar, request.headers.get(iap.CABECALHO))
        if r.status == 503:
            resposta = Response("Verificação de acesso indisponível no momento. Tente de novo em instantes.",
                                status_code=503, media_type="text/plain", headers={"Retry-After": "30"})
        elif r.status != 200:
            resposta = Response("Acesso só pelo endereço protegido (IAP).", status_code=401, media_type="text/plain")
        else:
            request.state.usuario = r.email
            resposta = await call_next(request)
    else:
        resposta = await call_next(request)
    # os anexos das Iniciativas levam uma CSP própria, mais fechada (api.CSP_ANEXO); o resto, a do site
    if "content-security-policy" not in resposta.headers:
        resposta.headers["Content-Security-Policy"] = CSP.format(nonce=request.state.nonce)
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    if config.AUTH == "publico" or config.CHAVE_ACESSO:  # D66: link aberto não entra em buscador
        resposta.headers["X-Robots-Tag"] = "noindex, nofollow"
    resposta.headers["Referrer-Policy"] = "same-origin"
    # D59: só o próprio site pode se emoldurar (quadro da tela cheia); sites de fora continuam bloqueados
    resposta.headers["X-Frame-Options"] = "SAMEORIGIN"
    if request.url.path.startswith("/static/"):
        # com ?v= o endereço muda quando o conteúdo muda: pode guardar por 1 ano; fontes e logo, por 1 dia. Só respostas
        # boas vão para o cache: um 403 (sem a chave) ou um 404 guardado como immutable ficaria preso no navegador
        if resposta.status_code in (200, 206, 304):  # 304: a cópia guardada continua válida
            versionado = "v" in request.query_params
            resposta.headers["Cache-Control"] = "public, max-age=31536000, immutable" if versionado else "public, max-age=86400"
        else:
            resposta.headers["Cache-Control"] = "no-store"
    else:
        resposta.headers["Cache-Control"] = "private, no-store"  # páginas com dados internos nunca ficam guardadas
        if resposta.headers.get("content-type", "").startswith("text/html"):
            # troca de página instantânea (Chrome/Edge): ao parar o mouse numa aba, a página seguinte é preparada em
            # segundo plano; regras num arquivo do próprio site (a CSP não aceita regras embutidas)
            resposta.headers["Speculation-Rules"] = '"/especulacao.json"'
    return resposta


def _contexto(a, secao, **extra) -> dict:
    # situação dos dados para o cartão de status e a data no slide: as tabelas da seção; na página inicial, nas páginas
    # gerais e nas seções sem tabela própria (máscaras, G2-5/G4-N1), as do Início — toda página tem o rodapé datado
    chaves = (secao.tabelas if secao else ()) or a.tabelas_inicio or tuple(dados.TABELAS)
    fontes = [s for s in (dados.TABELAS[t].situacao() for t in chaves) if s["versao"] > 0]
    anterior, proxima = a.vizinhas(extra.pop("posicao", secao))  # ordem da reunião (D30)
    assinatura = hashlib.sha256(json.dumps(
        [extra, [{k: f.get(k) for k in ('tabela', 'versao', 'modificada_em', 'estado', 'erro')} for f in fontes]],
        sort_keys=True, default=str).encode()).hexdigest()[:16]
    congelada = dados.base_congelada(fontes)
    # F15 (31/10/2026): com a base congelada (D65) ou em produção, a página não pede o HTML de novo a cada intervalo
    # para saber se há carga nova (nada muda); sem o intervalo, apresentacao.js não consulta
    sondar = not (config.EM_PRODUCAO or congelada)
    return {"apresentacao": a, "secao_atual": secao, "apresentacoes": APRESENTACOES, "fontes": fontes,
            "assinatura_dados": assinatura, "intervalo_dados": max(60, config.RECARGA_MIN * 60) if sondar else None,
            "base_congelada": congelada,  # D65: com o corte, só depois da carga do corte
            "modo_apresentacao": config.MODO_APRESENTACAO,
            "menu_lateral": config.MENU_LATERAL,  # D59
            "sinc": config.SINC,  # D62: sincronia com a cola do apresentador
            "anterior": anterior, "proxima": proxima, **extra}


@app.get("/")
def inicio():
    a = APRESENTACOES[0]
    return RedirectResponse(f"/{a.slug}/capa" if a.capa else f"/{a.slug}")  # D59: a reunião começa na capa


_PAGINAS = [{"href_matches": "/*"}, {"not": {"href_matches": "/static/*"}}, {"not": {"href_matches": "/*/api/*"}}]
# desempenho (31/10/2026; F15 da auditoria): o apresentador anda pela seta → (sem passar o mouse), então só a próxima
# página provável (o link rel="next" da sequência) fica montada assim que a página abre (immediate): uma renderização a
# mais no servidor por página. Os demais destinos (Roadmap, Estudo, ← e ✕) só por intenção: mouse parado ~200 ms sobre
# o link, ou toque (moderate)
PROXIMA = "[rel~=next]"
ESPECULACAO = {
    "prerender": [
        {"where": {"and": [*_PAGINAS, {"selector_matches": PROXIMA}]}, "eagerness": "immediate"},
        {"where": {"and": [*_PAGINAS, {"not": {"href_matches": r"/*\?*"}}]},  # sem parâmetros (filtros, ?exemplo=1)
         "eagerness": "moderate"},
    ],
}


@app.get("/especulacao.json")
def especulacao():
    # regras de pré-carga das páginas (Speculation Rules); tipo exigido pelo navegador
    return Response(json.dumps(ESPECULACAO), media_type="application/speculationrules+json")


# D62 (Caio, 27/10/2026): sincronia portal ↔ cola do apresentador (porta 8200). Guarda só a página atual (memória do
# processo, nada de dado): {url, versao, origem}. A versão sobe quando a página (normalizada) muda. Corpo em texto puro
# (JSON dentro) para o navegador da cola não precisar de preflight. Só no computador (config.SINC)
# "sessao" muda a cada subida do servidor: a versão recomeça do zero, e portal e cola zeram o que já tinham visto
_SINC = {"url": None, "versao": 0, "origem": None, "sessao": secrets.token_hex(4)}


def _sinc_normal(url: str) -> str:
    """A mesma regra da cola: sem a query; sem o #, exceto no estudo (o # é o slide). No slide 2 do estudo o quadro
    (?passo=, Formato/Sino/Faixas) também é posição: "…/como-medimos#2:N" (N = 1 sem passo)."""
    base, _, hash_ = url.partition("#")
    caminho, _, consulta = base.partition("?")
    caminho = caminho.rstrip("/") or "/"
    if not (caminho.endswith("/como-medimos") and hash_):
        return caminho
    if hash_ == "2":
        passo = next((v for k, _, v in (p.partition("=") for p in consulta.split("&")) if k == "passo" and v), "1")
        return f"{caminho}#2:{passo}"
    return f"{caminho}#{hash_}"


def _sinc_resposta(request: Request) -> JSONResponse:
    r = JSONResponse(_SINC)
    origem = request.headers.get("origin")
    if origem in config.SINC_ORIGENS:
        r.headers["Access-Control-Allow-Origin"] = origem
        r.headers["Vary"] = "Origin"
    return r


def _sinc_origem_ok(request: Request) -> bool:
    # Origin presente: a do próprio portal (mesmo host) ou a da cola. Sem Origin (fora de navegador, como curl
    # local), vale o Sec-Fetch-Site quando houver: só same-origin ou none
    origem = request.headers.get("origin")
    if origem:
        return origem in config.SINC_ORIGENS or urlsplit(origem).netloc == request.headers.get("host", "")
    return request.headers.get("sec-fetch-site") in (None, "same-origin", "none")


@app.get("/sinc")
def sinc_ler(request: Request):
    if not config.SINC:
        raise HTTPException(404, "Página não encontrada")
    return _sinc_resposta(request)


@app.post("/sinc")
async def sinc_gravar(request: Request):
    if not config.SINC:
        raise HTTPException(404, "Página não encontrada")
    # F12 (auditoria de 31/10/2026): só o próprio portal (mesma origem) ou a cola (SINC_ORIGENS) mudam a página
    if not _sinc_origem_ok(request):
        raise HTTPException(403, "Origem não permitida")
    try:
        corpo = json.loads((await request.body()).decode("utf-8") or "{}")
        url, origem = str(corpo.get("url", "")), str(corpo.get("origem", ""))
    except (ValueError, AttributeError):
        raise HTTPException(400, "Corpo inválido")
    # só endereços do próprio portal (caminho relativo), de quem sabemos quem é
    if not url.startswith("/") or url.startswith("//") or origem not in ("portal", "cola") or len(url) > 300:
        raise HTTPException(400, "Endereço inválido")
    if _SINC["url"] is None or _sinc_normal(url) != _sinc_normal(_SINC["url"]):
        _SINC.update(url=url, versao=_SINC["versao"] + 1, origem=origem)
    return _sinc_resposta(request)


@app.get("/saude")
def saude():
    """Processo vivo e situação dos dados (versão, data da tabela, atraso). Não derruba a instância por atraso."""
    tabelas = {chave: {k: v for k, v in t.situacao().items() if k in (
        "versao", "modificada_em", "processado_em", "carregada_em", "verificada_em", "linhas", "estado", "erro")}
        for chave, t in dados.TABELAS.items()}
    # F02: "base_congelada" separa congelada em memória (congeladas_em_memoria) de persistida e validada (persistida),
    # com o erro da última gravação e as tentativas
    return {"ok": True, "dados_prontos": all(t.versao > 0 for t in dados.TABELAS.values()), "tabelas": tabelas,
            "base_congelada": congelamento.situacao()}


@app.get("/cola/{ficha}")
def texto_cola(request: Request, ficha: str):
    """Somente no ambiente local da cola; texto agregado, sem exportar dados individuais."""
    from app.apresentacoes.gestao_orcamentos.cola import IDS, compor
    if not config.SINC or config.EM_PRODUCAO:
        raise HTTPException(404, "Página não encontrada")
    origem = request.headers.get("origin")
    if origem and origem not in config.SINC_ORIGENS:
        raise HTTPException(403, "Origem não permitida")
    headers = {"Cache-Control": "no-store"}
    if origem:
        headers.update({"Access-Control-Allow-Origin": origem, "Vary": "Origin"})
    if ficha not in IDS:
        return JSONResponse({"erro": "Ficha não encontrada"}, status_code=404, headers=headers)
    try:
        for _ in range(2):
            antes = {k: t.versao for k, t in dados.TABELAS.items()}
            texto = compor(ficha)
            fontes = [dados.TABELAS[k].situacao() for k in texto.pop('fontes')]
            if antes == {k: t.versao for k, t in dados.TABELAS.items()}:
                break
        else:
            raise DadosIndisponiveis('Carga em atualização')
        if any(f.get('erro') for f in fontes):
            raise DadosIndisponiveis('Não foi possível verificar a carga')
        datas = [f.get('processado_em') for f in fontes if f.get('processado_em')]
        # Datas já são serializadas pela camada de dados; não confundir com a hora desta requisição.
        return JSONResponse({"ficha": ficha, "texto": texto, "congelada": config.CONGELAR,
                             "cargas": [str(d) for d in datas], "recorte": "Todos"}, headers=headers)
    except DadosIndisponiveis:
        return JSONResponse({"erro": "Dados indisponíveis ou em atualização. Confira o portal."},
                            status_code=503, headers=headers)


@app.get("/p/{antigo}")
def endereco_antigo(antigo: str):
    # endereços da fase 1 (/p/visao_geral) levam à apresentação nova
    return RedirectResponse("/", status_code=301)


@app.get("/sla")
def sla_antigo(request: Request):
    # o SLA virou a seção SLA da Gestão de orçamentos (D17); mantém filtros como ?talentos=
    consulta = f"?{request.url.query}" if request.url.query else ""
    return RedirectResponse(f"/{SLUG}/sla{consulta}", status_code=301)


@app.api_route(f"/{SLUG_ANTIGO}{{resto:path}}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
               include_in_schema=False)
def endereco_antigo_area(request: Request, resto: str):
    # Caio, 31/10/2026: /gestao-orcamentos[/...] virou /viu-agenciamento[/...]. Um só redirecionamento para tudo, com a
    # query; o # o navegador mantém. GET/HEAD: 301; os demais métodos (API das Iniciativas): 308, que mantém o método
    # e o corpo. Declarada antes das rotas genéricas /{slug}; /gestao-orcamentosX (sem barra) não é endereço antigo
    if resto and not resto.startswith("/"):
        raise HTTPException(404, "Página não encontrada")
    bruto = request.scope.get("raw_path", b"").decode("latin-1")  # caminho como veio (sem decodificar %xx)
    prefixo = f"/{SLUG_ANTIGO}"
    resto = bruto[len(prefixo):] if bruto.startswith(prefixo) else resto
    resto = "" if resto == "/" else resto
    consulta = f"?{request.url.query}" if request.url.query else ""
    codigo = 301 if request.method in ("GET", "HEAD") else 308
    return RedirectResponse(f"/{SLUG}{resto}{consulta}", status_code=codigo)


@app.get("/{slug}")
def apresentacao(request: Request, slug: str):
    # página inicial da área (<pasta>/inicio.html), com os dados de Apresentacao.inicio quando houver
    a = POR_SLUG.get(slug)
    if a is None:
        raise HTTPException(404, "Apresentação não encontrada")
    try:
        extra = a.inicio(dict(request.query_params)) if a.inicio else {}
    except DadosIndisponiveis as e:
        dados.log("ERROR", "página sem dados", secao=a.slug, erro=str(e))
        return templates.TemplateResponse(request, "indisponivel.html", _contexto(a, None, sem_controles=True),
                                          status_code=503, headers={"Retry-After": str(config.RECARGA_MIN * 60)})
    return templates.TemplateResponse(request, f"{a.pasta}/inicio.html", _contexto(a, None, sem_controles=True, **extra))


@app.get("/{slug}/o-que-falta")
def o_que_falta(request: Request, slug: str):
    # fecho da área (D30): estado de cada seção e o que falta para completá-la (pendencias.py). Declarada antes de
    # /{slug}/{secao} para não ser lida como uma seção
    a = POR_SLUG.get(slug)
    if a is None:
        raise HTTPException(404, "Apresentação não encontrada")
    return templates.TemplateResponse(request, "o_que_falta.html", _contexto(
        a, None, posicao="o-que-falta", titulo_pagina="O que falta"))


@app.get("/{slug}/capa")
def capa(request: Request, slug: str):
    # D59 (Caio, 27/10/2026): capa da reunião, antes da 1ª análise; o roteiro lista a sequência de perguntas. Declarada
    # antes de /{slug}/{secao} para não ser lida como uma seção
    a = POR_SLUG.get(slug)
    if a is None or not a.capa:
        raise HTTPException(404, "Página não encontrada")
    # F20 (31/10/2026): a capa da V2 não mostra o relógio da jornada (D61); a medida do SLA não é mais calculada aqui
    # Caio, 03/11/2026: capa nova aplicada (sem subtítulo, sem textos no desenho e sem o rodapé datado: sem_rodape)
    return templates.TemplateResponse(request, "capa.html", _contexto(
        a, None, posicao="capa", pagina_especial="capa", sem_controles=True, sem_rodape=True))


@app.get("/{slug}/capa-nova")
def capa_nova(request: Request, slug: str):
    # Caio, 03/11/2026: proposta de capa nova, fora da navegação, para comparar com a validada (/capa). Aprovada, substitui
    # capa.html e esta rota sai; a validada está em _descartados/2026-11-03/capa_validada/
    # aprovada e aplicada em 03/11/2026: o endereço da proposta leva à capa
    return RedirectResponse(f"/{slug}/capa", status_code=301)


@app.get("/{slug}/encerramento")
def encerramento(request: Request, slug: str):
    # D59: tela de encerramento depois da última seção (agradecimento e os pedidos de decisão, pendencias.PEDIDOS)
    a = POR_SLUG.get(slug)
    if a is None or not a.encerramento:
        raise HTTPException(404, "Página não encontrada")
    return templates.TemplateResponse(request, "encerramento.html", _contexto(
        a, None, posicao="encerramento", pagina_especial="encerramento", sem_controles=True))


@app.get("/{slug}/{secao}/como-medimos")
def como_medimos(request: Request, slug: str, secao: str):
    # subpágina "Como medimos" do SLA: a análise por trás da métrica, tela por tela (24/10/2026, em construção com o Caio)
    a = POR_SLUG.get(slug)
    s = a.secao(secao) if a else None
    if s is None or s.montar_estudo is None:
        raise HTTPException(404, "Página não encontrada")
    consulta = f"?{request.url.query}" if request.url.query else ""  # volta com o mesmo filtro (ex.: talentos)
    try:
        estudo = s.montar_estudo(dict(request.query_params))
    except DadosIndisponiveis as e:
        dados.log("ERROR", "página sem dados", secao=f"{a.slug}/{s.slug}/como-medimos", erro=str(e))
        return templates.TemplateResponse(request, "indisponivel.html", _contexto(a, s, sem_controles=True),
                                          status_code=503)
    # estudo em slides (página 1, 2, 3…): Anterior/Próximo sempre à mostra. D62: na sequência da reunião (SLA → estudo →
    # Previsão) — as setas saem do último slide para a Previsão; o gancho fica só para o leitor de tela (o estudo tem os seus)
    return templates.TemplateResponse(request, "como_medimos.html", _contexto(
        a, s, consulta=consulta, titulo_pagina="Como medimos", controles_sempre=True, gancho_oculto=True,
        posicao=f"{s.slug}/como-medimos", **estudo))


@app.get("/{slug}/{secao}/regras")
def regras(request: Request, slug: str, secao: str):
    # batalha 2 (G3-7/G4-N1): a página de regras saiu (texto fixo que contradizia as regras vigentes). Endereço antigo
    # leva ao estudo "Como medimos" da seção (SLA) ou à própria seção, com o mesmo filtro; as regras ficam nas fichas
    a = POR_SLUG.get(slug)
    s = a.secao(secao) if a else None
    if s is None:
        raise HTTPException(404, "Página não encontrada")
    consulta = f"?{request.url.query}" if request.url.query else ""
    destino = f"/{a.slug}/{s.slug}/como-medimos{consulta}#1" if s.montar_estudo else f"/{a.slug}/{s.slug}{consulta}"
    return RedirectResponse(destino, status_code=301)


@app.get("/{slug}/{secao}")
def secao(request: Request, slug: str, secao: str):
    a = POR_SLUG.get(slug)
    s = a.secao(secao) if a else None
    if s is None:
        raise HTTPException(404, "Página não encontrada")
    try:
        contexto = s.montar(dict(request.query_params))  # carrega as tabelas antes de ler a situação delas
    except DadosIndisponiveis as e:
        dados.log("ERROR", "página sem dados", secao=f"{a.slug}/{s.slug}", erro=str(e))
        return templates.TemplateResponse(request, "indisponivel.html", _contexto(a, s, sem_controles=True),
                                          status_code=503, headers={"Retry-After": str(config.RECARGA_MIN * 60)})
    return templates.TemplateResponse(request, a.template(s), _contexto(a, s, **contexto))
