"""API JSON do quadro das Iniciativas (/viu-agenciamento/iniciativas/api/...). Contrato na ficha
(docs/paginas/iniciativas.md, seção "API").

Leitura sempre aberta (a mesma da página). Escrita (criar, editar, mover, excluir, anexar, remover anexo, importar):
- só com `config.INICIATIVAS_EDICAO` (ligada no computador; em produção desligada por padrão: 403);
- proteção mínima contra CSRF: cabeçalho `X-Requested-With: iniciativas` (um formulário de outro site não consegue
  mandá-lo sem preflight, que este app não autoriza) e, quando o navegador informa, Origin/Sec-Fetch-Site do próprio site.
Arquivos dos anexos: servidos pelo app (no Cloud Run, lidos do bucket privado), com o tipo certo, `nosniff`,
`Content-Disposition: inline` e uma CSP própria e fechada.
"""

from __future__ import annotations

from pathlib import Path as PathLib
from urllib.parse import quote, urlsplit

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.concurrency import run_in_threadpool

from app import config, dados
from app.apresentacoes.gestao_orcamentos import SLUG, endereco_atual
from app.apresentacoes.gestao_orcamentos.iniciativas import catalogo
from app.apresentacoes.gestao_orcamentos.iniciativas import repositorio as repo

PREFIXO = f"/{SLUG}/iniciativas/api"
CABECALHO_CSRF = "iniciativas"
ID = r"^[a-z0-9][a-z0-9-]{0,59}$"
ID_ANEXO = r"^[0-9a-f]{32}$"
# CSP do arquivo servido: nada roda, nada carrega de fora; só o próprio site pode emoldurar (visor de PDF)
CSP_ANEXO = "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; object-src 'self'; frame-ancestors 'self'"
LIMITE_CORPO = repo.MAX_ANEXO + 64 * 1024  # corpo multipart inteiro: o arquivo de até 10 MB + cabeçalhos das partes

router = APIRouter(prefix=PREFIXO)


# ---------------------------------------------------------------- contrato
class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def _fase_valida(v):
    if v is not None and v not in repo.fases():
        raise ValueError("fase inválida")
    return v


class Criar(_Base):
    sigla: str = Field("", max_length=repo.MAX["sigla"])
    nome: str = Field("", max_length=repo.MAX["nome"])
    fase: str
    responsavel: str = Field("", max_length=repo.MAX["responsavel"])
    descricao: str = Field("", max_length=repo.MAX["descricao"])
    status: str = Field("", max_length=repo.MAX["status"])
    proximo: str = Field("", max_length=repo.MAX["proximo"])
    valida_fase = field_validator("fase")(classmethod(lambda cls, v: _fase_valida(v)))


class Editar(_Base):
    sigla: str | None = Field(None, max_length=repo.MAX["sigla"])
    nome: str | None = Field(None, max_length=repo.MAX["nome"])
    fase: str | None = None
    responsavel: str | None = Field(None, max_length=repo.MAX["responsavel"])
    descricao: str | None = Field(None, max_length=repo.MAX["descricao"])
    status: str | None = Field(None, max_length=repo.MAX["status"])
    proximo: str | None = Field(None, max_length=repo.MAX["proximo"])
    valida_fase = field_validator("fase")(classmethod(lambda cls, v: _fase_valida(v)))


class Mover(_Base):
    fase: str
    posicao: int = Field(ge=0, le=500)
    valida_fase = field_validator("fase")(classmethod(lambda cls, v: _fase_valida(v)))


class Importar(_Base):
    model_config = ConfigDict(extra="ignore")
    fases: dict[str, list[str]] = Field(default_factory=dict)
    dados: dict[str, dict] = Field(default_factory=dict)
    novos: dict[str, dict] = Field(default_factory=dict)
    excluidos: list[str] = Field(default_factory=list, max_length=200)


def publico(i: dict) -> dict:
    link = {"rotulo": i["link_rotulo"], "href": endereco_atual(i["link_href"])} if i.get("link_href") else None
    return {k: i.get(k, "") for k in ("id", "sigla", "nome", "fase", "ordem", "responsavel", "descricao", "status",
                                      "proximo", "atualizado_em")} | {"link": link}


def fotos_fixas(ident: str) -> list[dict]:
    """Caio, 03/11/2026: fotos fixas do catálogo (catalogo.FOTOS), no mesmo formato dos anexos, com fixo=True e a
    versão do arquivo no endereço (o navegador não fica com a cópia antiga)."""
    estaticos = PathLib(__file__).resolve().parents[3] / "static"
    saida = []
    for k, f in enumerate(catalogo.FOTOS.get(ident, ()), 1):
        pasta = f.get("pasta", "iniciativas")
        arq = estaticos / pasta / f["arquivo"]
        if not arq.is_file():
            continue
        info = arq.stat()
        saida.append({"id": f"foto-{ident}-{k}", "iniciativa_id": ident, "nome": f["nome"], "tipo": "image/webp",
                      "tamanho": info.st_size, "imagem": True, "fixo": True,
                      "url": f"/static/{pasta}/{f['arquivo']}?v={info.st_size:x}{info.st_mtime_ns // 1_000_000_000:x}"})
    return saida


def anexo_publico(a: dict) -> dict:
    return {"id": a["id"], "iniciativa_id": a["iniciativa_id"], "nome": a["nome_original"], "tipo": a["tipo"],
            "tamanho": a["tamanho"], "imagem": a["tipo"].startswith("image/"),
            "url": f"{PREFIXO}/anexos/{a['id']}/arquivo"}


# ---------------------------------------------------------------- guarda das escritas
def _usuario(request: Request) -> str:
    return getattr(request.state, "usuario", "") or ""


def escrita(request: Request) -> str:
    if not config.INICIATIVAS_EDICAO:
        raise HTTPException(403, "Edição desligada neste ambiente.")
    if request.headers.get("x-requested-with") != CABECALHO_CSRF:
        raise HTTPException(403, "Requisição recusada (cabeçalho ausente).")
    site = request.headers.get("sec-fetch-site")
    if site and site not in ("same-origin", "none"):
        raise HTTPException(403, "Requisição recusada (outra origem).")
    origem = request.headers.get("origin")
    if origem and urlsplit(origem).netloc != request.headers.get("host", ""):
        raise HTTPException(403, "Requisição recusada (outra origem).")
    return _usuario(request)


def _q() -> repo.Quadro:
    try:
        return repo.quadro()
    except repo.QuadroIndisponivel as e:
        dados.log("ERROR", "quadro das iniciativas indisponível", erro=str(e))
        raise HTTPException(503, "Armazenamento indisponível. Tente de novo em instantes.")


def _rodar(fn):
    try:
        return fn()
    except repo.ErroQuadro as e:
        raise HTTPException(e.status, str(e))
    except repo.QuadroIndisponivel as e:
        dados.log("ERROR", "quadro das iniciativas indisponível", erro=str(e))
        raise HTTPException(503, "Armazenamento indisponível. Tente de novo em instantes.")


def _log(acao: str, por: str, **campos) -> None:
    dados.log("INFO", "iniciativas: " + acao, usuario=por or "local", **campos)


# ---------------------------------------------------------------- leitura
@router.get("/iniciativas")
def listar():
    q = _q()

    def fn():
        anexos: dict[str, list] = {}
        itens = q.listar()
        for i in itens:  # fotos fixas do catálogo primeiro (Caio, 03/11/2026)
            if catalogo.FOTOS.get(i["id"]):
                anexos[i["id"]] = fotos_fixas(i["id"])
        for a in q.anexos():
            anexos.setdefault(a["iniciativa_id"], []).append(anexo_publico(a))
        return {"iniciativas": [publico(i) for i in itens], "anexos": anexos,
                "na_semente": q.na_semente(), "edicao": config.INICIATIVAS_EDICAO}
    return _rodar(fn)


@router.get("/iniciativas/{ident}/anexos")
def listar_anexos(ident: str = Path(pattern=ID)):
    q = _q()
    return _rodar(lambda: (q.obter(ident), fotos_fixas(ident) + [anexo_publico(a) for a in q.anexos(ident)])[1])


@router.get("/anexos/{aid}/arquivo")
def arquivo(aid: str = Path(pattern=ID_ANEXO)):
    q = _q()
    meta, conteudo = _rodar(lambda: q.ler_anexo(aid))
    nome = meta["nome_original"]
    ascii_ = "".join(c if c.isascii() and c.isprintable() and c not in '"\\;' else "_" for c in nome)
    return Response(conteudo, media_type=meta["tipo"], headers={
        "Content-Disposition": f"inline; filename=\"{ascii_}\"; filename*=UTF-8''{quote(nome)}",
        "Content-Security-Policy": CSP_ANEXO, "X-Content-Type-Options": "nosniff",
        "Cross-Origin-Resource-Policy": "same-origin"})


# ---------------------------------------------------------------- escrita
@router.post("/iniciativas", status_code=201)
def criar(corpo: Criar, por: str = Depends(escrita)):
    q = _q()
    item = _rodar(lambda: q.criar(corpo.model_dump(), por))
    _log("criada", por, id=item["id"])
    return publico(item)


@router.put("/iniciativas/{ident}")
def editar(corpo: Editar, ident: str = Path(pattern=ID), por: str = Depends(escrita)):
    q = _q()
    item = _rodar(lambda: q.editar(ident, corpo.model_dump(exclude_none=True), por))
    _log("editada", por, id=ident)
    return publico(item)


@router.post("/iniciativas/{ident}/mover")
def mover(corpo: Mover, ident: str = Path(pattern=ID), por: str = Depends(escrita)):
    q = _q()
    item = _rodar(lambda: q.mover(ident, corpo.fase, corpo.posicao, por))
    _log("movida", por, id=ident, fase=corpo.fase, posicao=corpo.posicao)
    return publico(item)


@router.delete("/iniciativas/{ident}", status_code=204)
def excluir(ident: str = Path(pattern=ID), por: str = Depends(escrita)):
    q = _q()
    _rodar(lambda: q.excluir(ident, por))
    _log("excluída", por, id=ident)
    return Response(status_code=204)


@router.post("/iniciativas/{ident}/anexos", status_code=201)
async def anexar(request: Request, ident: str = Path(pattern=ID), por: str = Depends(escrita)):
    tamanho = request.headers.get("content-length")
    if tamanho and tamanho.isdigit() and int(tamanho) > LIMITE_CORPO:
        raise HTTPException(413, "Arquivo acima de 10 MB.")
    if not request.headers.get("content-type", "").startswith("multipart/form-data"):
        raise HTTPException(400, "Envie o arquivo como multipart/form-data (campo \"arquivo\").")
    # F11 (auditoria de 31/10/2026): o limite vale durante a recepção, contando os bytes do corpo (sem depender do
    # Content-Length, que pode faltar no envio em partes); passou do limite, 413 na hora, sem ler o resto
    recebido = bytearray()
    async for parte in request.stream():
        recebido += parte
        if len(recebido) > LIMITE_CORPO:
            raise HTTPException(413, "Arquivo acima de 10 MB.")
    request._body = bytes(recebido)  # o parser do formulário (Starlette) relê o corpo já recebido
    try:
        form = await request.form(max_files=1, max_fields=1)
    except Exception:  # noqa: BLE001 (corpo multipart malformado ou acima dos limites)
        raise HTTPException(400, "Envio inválido.")
    try:
        f = form.get("arquivo")
        if f is None or not hasattr(f, "read"):
            raise HTTPException(400, "Campo \"arquivo\" ausente.")
        conteudo = await f.read(repo.MAX_ANEXO + 1)
        nome = f.filename or ""
    finally:
        await form.close()
    # F11: abrir o quadro e gravar o anexo (SQLite + pasta, ou Firestore + bucket) é I/O bloqueante: fora do event loop
    meta = await run_in_threadpool(lambda: _rodar(lambda: _q().anexar(ident, nome, conteudo)))
    _log("anexo enviado", por, id=ident, anexo=meta["id"], tipo=meta["tipo"], tamanho=meta["tamanho"])
    return anexo_publico(meta)


@router.delete("/anexos/{aid}", status_code=204)
def remover_anexo(aid: str = Path(pattern=ID_ANEXO), por: str = Depends(escrita)):
    q = _q()
    _rodar(lambda: q.remover_anexo(aid))
    _log("anexo removido", por, anexo=aid)
    return Response(status_code=204)


@router.post("/importar")
def importar(corpo: Importar, por: str = Depends(escrita)):
    q = _q()
    feito = _rodar(lambda: q.importar(corpo.model_dump(), por))
    _log("importação do navegador", por, **feito)
    return JSONResponse(feito)
