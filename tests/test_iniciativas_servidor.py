"""Iniciativas com dados no servidor (Caio e gerente, 30/10/2026): quadro salvo, API, anexos, segurança e produção.

Tudo com banco temporário (fixture quadro_limpo, em tests/conftest.py: SQLite em tmp_path); o backend de produção
(Firestore + Cloud Storage) é testado com clientes falsos, sem rede e sem GCP. AUTH=iap é testado com um JWT ES256
gerado aqui (chave de teste), no lugar das chaves públicas do IAP.
"""

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import config, iap
from app.apresentacoes.gestao_orcamentos import iniciativas
from app.apresentacoes.gestao_orcamentos.iniciativas import api, catalogo, repositorio

API = "/viu-agenciamento/iniciativas/api"
CSRF = {"X-Requested-With": "iniciativas"}
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
PDF = b"%PDF-1.4\n" + b"0" * 64
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 32
GIF = b"GIF89a" + b"\x00" * 32


@pytest.fixture
def cliente(quadro_limpo):
    from app.main import app

    with TestClient(app) as c:
        yield c


def _enviar(c, ident, nome, conteudo, cabecalhos=CSRF):
    return c.post(f"{API}/iniciativas/{ident}/anexos", files={"arquivo": (nome, conteudo, "application/octet-stream")},
                  headers=cabecalhos)


# ---------------------------------------------------------------- semente e regras do quadro
def test_semente_vem_do_catalogo_uma_vez(quadro_limpo):
    q = quadro_limpo
    itens = q.listar()
    assert [i["id"] for i in itens][:2] == ["lia", "gps"] and len(itens) == 13
    assert itens[0]["link_href"] == "/viu-agenciamento/lia#1" and itens[0]["fase"] == "producao"
    assert [i["ordem"] for i in itens if i["fase"] == "esteira"] == [0, 1, 2, 3, 4]
    assert q.na_semente()
    # uma 2ª instância sobre o mesmo arquivo não semeia de novo (e enxerga o que foi gravado)
    q.editar("gps", {"nome": "Pastas"})
    outro = repositorio.Quadro(repositorio.SqliteBackend(config.INICIATIVAS_DB, config.INICIATIVAS_ANEXOS))
    assert len(outro.listar()) == 13 and outro.obter("gps")["nome"] == "Pastas" and not outro.na_semente()


def test_crud_mover_e_exclusao_logica(quadro_limpo):
    q = quadro_limpo
    novo = q.criar({"sigla": "RAIO-X", "nome": "Fila Inteligente", "fase": "testes", "descricao": "Prioriza a fila."})
    assert novo["id"].startswith("ini-") and novo["ordem"] == 2  # fim da coluna
    q.editar(novo["id"], {"responsavel": "Time de Dados", "status": "Piloto"})
    assert q.obter(novo["id"])["responsavel"] == "Time de Dados"
    # mover para o topo de Em produção: renumera destino e origem
    q.mover(novo["id"], "producao", 0)
    prod = [i["id"] for i in q.listar() if i["fase"] == "producao"]
    testes = [(i["id"], i["ordem"]) for i in q.listar() if i["fase"] == "testes"]
    assert prod == [novo["id"], "lia", "gps", "mia"] and testes == [("orca-ai", 0), ("cop-ia", 1)]
    # mudar a fase pela edição leva para o fim da nova coluna
    q.editar("lia", {"fase": "esteira"})
    assert [i["id"] for i in q.listar() if i["fase"] == "esteira"][-1] == "lia"
    # exclusão lógica: some da lista, a linha fica no banco
    q.excluir("gps")
    assert "gps" not in [i["id"] for i in q.listar()]
    assert any(i["id"] == "gps" and i["excluido"] for i in q.b.iniciativas())
    with pytest.raises(repositorio.ErroQuadro):
        q.obter("gps")
    # posição fora do intervalo é ajustada; fase inválida é recusada
    q.mover("cachE".lower(), "testes", 99)
    assert [i["id"] for i in q.listar() if i["fase"] == "testes"][-1] == "cache"
    with pytest.raises(repositorio.ErroQuadro):
        q.mover("cache", "lua", 0)
    with pytest.raises(repositorio.ErroQuadro):
        q.criar({"sigla": "", "nome": " ", "fase": "testes"})


def test_restaurar_semente(quadro_limpo):
    q = quadro_limpo
    n = q.criar({"nome": "Extra", "fase": "esteira"})
    q.editar("lia", {"nome": "Outro nome", "fase": "testes"})
    q.excluir("gps")
    q.restaurar_semente()
    ids = [i["id"] for i in q.listar()]
    assert ids[:2] == ["lia", "gps"] and n["id"] not in ids and q.obter("lia")["nome"] == "Leitura Inteligente Automatizada"
    assert q.na_semente()


def test_importacao_do_navegador(quadro_limpo):
    q = quadro_limpo
    estado = {"fases": {"producao": ["gps", "lia"], "testes": ["orca-ai", "nova-abc"], "desenvolvimento": ["fila", "cache"],
                        "esteira": ["salesforce", "match", "auto", "guia"]},
              "dados": {"fila": {"sigla": "RAIO-X", "nome": "Fila", "desc": "d", "resp": "Dados", "status": "", "prox": ""}},
              "novos": {"nova-abc": {"sigla": "XYZ", "nome": "Novo", "desc": "", "resp": "", "status": "", "prox": ""}},
              "excluidos": ["cop-ia", "g1-ia"]}
    feito = q.importar(estado)
    assert feito == {"incluidas": 1, "editadas": 1, "excluidas": 2}
    por_fase = {}
    for i in q.listar():
        por_fase.setdefault(i["fase"], []).append(i["sigla"])
    assert por_fase["producao"] == ["GPS", "LIA", "MIA"] and por_fase["testes"] == ["Orça+AI", "XYZ"]
    assert por_fase["desenvolvimento"] == ["RAIO-X", "CACHÊ"] and q.obter("fila")["responsavel"] == "Dados"
    with pytest.raises(repositorio.ErroQuadro) as e:  # o quadro já não está na semente: 409
        q.importar(estado)
    assert e.value.status == 409


# ---------------------------------------------------------------- API
def test_api_crud_e_pagina_renderizada_do_banco(cliente):
    r = cliente.get(f"{API}/iniciativas")
    assert r.status_code == 200 and len(r.json()["iniciativas"]) == 13 and r.json()["edicao"] is True
    r = cliente.post(f"{API}/iniciativas", json={"sigla": "TESTE", "nome": "Iniciativa de teste", "fase": "esteira",
                                                 "descricao": "Criada pelo teste."}, headers=CSRF)
    assert r.status_code == 201
    ident = r.json()["id"]
    r = cliente.put(f"{API}/iniciativas/{ident}", json={"responsavel": "Caio", "proximo": "Piloto"}, headers=CSRF)
    assert r.status_code == 200 and r.json()["responsavel"] == "Caio" and r.json()["sigla"] == "TESTE"
    r = cliente.post(f"{API}/iniciativas/{ident}/mover", json={"fase": "producao", "posicao": 0}, headers=CSRF)
    assert r.status_code == 200 and r.json()["fase"] == "producao" and r.json()["ordem"] == 0
    html = cliente.get("/viu-agenciamento/iniciativas").text  # a página lê o quadro salvo
    assert f'data-ini-id="{ident}" data-ini-sigla="TESTE"' in html and "<dt>Responsável</dt><dd>Caio</dd>" in html
    assert html.index(f'data-ini-id="{ident}"') < html.index('data-ini-id="lia"')
    assert "14</span> iniciativas" in html and 'data-ini-semente="0"' in html and 'style="' not in html
    assert cliente.delete(f"{API}/iniciativas/{ident}", headers=CSRF).status_code == 204
    assert cliente.delete(f"{API}/iniciativas/{ident}", headers=CSRF).status_code == 404
    assert f'data-ini-id="{ident}"' not in cliente.get("/viu-agenciamento/iniciativas").text


def test_api_validacao(cliente):
    r = cliente.post(f"{API}/iniciativas", json={"sigla": "A", "fase": "marte"}, headers=CSRF)
    assert r.status_code == 422
    r = cliente.post(f"{API}/iniciativas", json={"sigla": "A" * 41, "fase": "testes"}, headers=CSRF)
    assert r.status_code == 422
    r = cliente.post(f"{API}/iniciativas", json={"sigla": "A", "fase": "testes", "extra": 1}, headers=CSRF)
    assert r.status_code == 422
    r = cliente.post(f"{API}/iniciativas", json={"sigla": "", "nome": "", "fase": "testes"}, headers=CSRF)
    assert r.status_code == 400 and "sigla ou o nome" in r.json()["detail"]
    assert cliente.put(f"{API}/iniciativas/nao-existe", json={"nome": "x"}, headers=CSRF).status_code == 404
    assert cliente.put(f"{API}/iniciativas/..%2Fx", json={"nome": "x"}, headers=CSRF).status_code in (404, 422)
    r = cliente.post(f"{API}/iniciativas/lia/mover", json={"fase": "testes", "posicao": -1}, headers=CSRF)
    assert r.status_code == 422


def test_csrf_sem_cabecalho_ou_outra_origem(cliente):
    corpo = {"sigla": "X", "fase": "testes"}
    assert cliente.post(f"{API}/iniciativas", json=corpo).status_code == 403
    assert cliente.post(f"{API}/iniciativas", json=corpo, headers={"X-Requested-With": "XMLHttpRequest"}).status_code == 403
    assert cliente.post(f"{API}/iniciativas", json=corpo,
                        headers={**CSRF, "Origin": "https://malicioso.example"}).status_code == 403
    assert cliente.post(f"{API}/iniciativas", json=corpo, headers={**CSRF, "Sec-Fetch-Site": "cross-site"}).status_code == 403
    assert cliente.delete(f"{API}/iniciativas/lia").status_code == 403
    assert _enviar(cliente, "lia", "a.png", PNG, cabecalhos={}).status_code == 403
    # mesma origem passa
    r = cliente.post(f"{API}/iniciativas", json=corpo, headers={**CSRF, "Origin": "http://testserver",
                                                                 "Sec-Fetch-Site": "same-origin"})
    assert r.status_code == 201


def test_producao_simulada_escrita_bloqueada_leitura_aberta(cliente, monkeypatch):
    monkeypatch.setattr(config, "INICIATIVAS_EDICAO", False)  # padrão no Cloud Run (K_SERVICE) sem INICIATIVAS_EDICAO=on
    assert cliente.get(f"{API}/iniciativas").status_code == 200
    assert cliente.post(f"{API}/iniciativas", json={"sigla": "X", "fase": "testes"}, headers=CSRF).status_code == 403
    assert cliente.put(f"{API}/iniciativas/lia", json={"nome": "x"}, headers=CSRF).status_code == 403
    assert cliente.post(f"{API}/iniciativas/lia/mover", json={"fase": "testes", "posicao": 0}, headers=CSRF).status_code == 403
    assert cliente.delete(f"{API}/iniciativas/lia", headers=CSRF).status_code == 403
    assert _enviar(cliente, "lia", "a.png", PNG).status_code == 403
    assert cliente.post(f"{API}/importar", json={}, headers=CSRF).status_code == 403
    html = cliente.get("/viu-agenciamento/iniciativas").text
    assert 'data-ini-edicao="off"' in html and html.count('<details class="ini-quadro">') == 13


def _config_novo():
    """Uma cópia nova de app/config.py, lida com o ambiente atual (sem recarregar o módulo usado pelos outros testes)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("config_copia", Path(config.__file__))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_padroes_de_configuracao_em_producao(monkeypatch):
    """Com K_SERVICE (Cloud Run): backend firestore e edição desligada por padrão; INICIATIVAS_EDICAO=on liga."""
    for k in ("INICIATIVAS_BACKEND", "INICIATIVAS_EDICAO", "INICIATIVAS_DB", "INICIATIVAS_ANEXOS"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("K_SERVICE", "relatorios-agenciamento")
    c = _config_novo()
    assert c.EM_PRODUCAO and c.INICIATIVAS_BACKEND == "firestore" and c.INICIATIVAS_EDICAO is False
    assert c.INICIATIVAS_DB == Path.home() / ".ppd-agenciamento-v2" / "iniciativas.db"
    monkeypatch.setenv("INICIATIVAS_EDICAO", "on")
    assert _config_novo().INICIATIVAS_EDICAO is True
    monkeypatch.delenv("K_SERVICE")
    monkeypatch.delenv("INICIATIVAS_EDICAO")
    c = _config_novo()
    assert c.INICIATIVAS_BACKEND == "sqlite" and c.INICIATIVAS_EDICAO is True


# ---------------------------------------------------------------- anexos
def test_upload_valido_listar_servir_e_remover(cliente):
    r = _enviar(cliente, "fila", "raio-x tela 1.png", PNG)
    assert r.status_code == 201
    a = r.json()
    assert a["tipo"] == "image/png" and a["imagem"] and a["nome"] == "raio-x tela 1.png"
    assert _enviar(cliente, "fila", "relatório.pdf", PDF).json()["tipo"] == "application/pdf"
    for nome, conteudo in (("b.jpg", JPEG), ("c.jpeg", JPEG), ("d.webp", WEBP), ("e.gif", GIF)):
        assert _enviar(cliente, "fila", nome, conteudo).status_code == 201, nome
    lst = cliente.get(f"{API}/iniciativas/fila/anexos").json()
    assert len(lst) == 6 and lst[0]["id"] == a["id"]
    # nome salvo = uuid; nunca o nome do usuário no caminho
    arquivos = sorted(p.name for p in Path(config.INICIATIVAS_ANEXOS).iterdir())
    assert len(arquivos) == 6 and all(len(n.split(".")[0]) == 32 for n in arquivos) and "raio" not in "".join(arquivos)
    f = cliente.get(a["url"])
    assert f.status_code == 200 and f.content == PNG and f.headers["content-type"] == "image/png"
    assert f.headers["x-content-type-options"] == "nosniff"
    assert f.headers["content-disposition"].startswith("inline;")
    assert f.headers["content-security-policy"] == api.CSP_ANEXO  # CSP própria do arquivo
    pdf = cliente.get(lst[1]["url"])
    assert pdf.headers["content-type"] == "application/pdf" and "frame-ancestors 'self'" in pdf.headers["content-security-policy"]
    # a página mostra as miniaturas (links para o arquivo, sem JS)
    html = cliente.get("/viu-agenciamento/iniciativas").text
    assert f'href="{a["url"]}" data-ini-anexo="{a["id"]}"' in html and 'aria-label="Imagem 1 de 6: raio-x tela 1.png"' in html
    assert 'style="' not in html
    assert cliente.delete(f"{API}/anexos/{a['id']}", headers=CSRF).status_code == 204
    assert cliente.get(a["url"]).status_code == 404
    assert len(list(Path(config.INICIATIVAS_ANEXOS).iterdir())) == 5


@pytest.mark.parametrize("nome, conteudo, status", [
    ("x.svg", b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>", 415),
    ("x.html", b"<html><script>alert(1)</script></html>", 415),
    ("x.png", b"<svg onload=alert(1)>", 415),          # extensão boa, conteúdo SVG
    ("x.png", JPEG, 415),                             # assinatura de outro tipo
    ("x.pdf", PNG, 415),
    ("x", PNG, 415),                                   # sem extensão
    ("x.exe", b"MZ" + b"\x00" * 20, 415),
    ("x.png", b"", 400),                               # vazio
])
def test_upload_invalido(cliente, nome, conteudo, status):
    r = _enviar(cliente, "lia", nome, conteudo)
    assert r.status_code == status, r.text
    assert cliente.get(f"{API}/iniciativas/lia/anexos").json() == []


def test_upload_acima_de_10_mb(cliente):
    grande = PNG + b"\x00" * (repositorio.MAX_ANEXO + 1)
    assert _enviar(cliente, "lia", "grande.png", grande).status_code == 413
    with pytest.raises(repositorio.ErroQuadro) as e:
        repositorio.validar_arquivo("a.png", PNG + b"\x00" * repositorio.MAX_ANEXO)
    assert e.value.status == 413
    assert repositorio.validar_arquivo("C:\\fotos\\..\\a.PNG", PNG) == ("a.PNG", "image/png")  # só o nome, sem caminho


def test_upload_em_iniciativa_inexistente_ou_excluida(cliente):
    assert _enviar(cliente, "nao-existe", "a.png", PNG).status_code == 404
    cliente.delete(f"{API}/iniciativas/gps", headers=CSRF)
    assert _enviar(cliente, "gps", "a.png", PNG).status_code == 404
    assert cliente.get(f"{API}/anexos/{'0' * 32}/arquivo").status_code == 404
    assert cliente.get(f"{API}/anexos/nao-hex/arquivo").status_code == 422


def test_pagina_cai_para_o_catalogo_se_o_armazenamento_falhar(monkeypatch, quadro_limpo):
    def falha():
        raise repositorio.QuadroIndisponivel("teste")

    monkeypatch.setattr(repositorio, "quadro", falha)
    t = iniciativas.tela()
    assert t["total"] == 13 and t["edicao"] is False and "só para leitura" in t["aviso"]
    from app.main import app

    with TestClient(app) as c:
        html = c.get("/viu-agenciamento/iniciativas").text
        assert 'class="ini-painel-aviso" role="status"' in html and 'data-ini-edicao="off"' in html
        assert c.get(f"{API}/iniciativas").status_code == 503


# ---------------------------------------------------------------- backend de produção (Firestore + Storage), falsos
class _Existe(Exception):
    pass


_Existe.__name__ = "AlreadyExists"


class _Snap:
    def __init__(self, ident, dado):
        self.id, self._d = ident, dado
        self.exists = dado is not None

    def to_dict(self):
        return dict(self._d) if self._d is not None else None


class _Doc:
    def __init__(self, col, ident):
        self.col, self.id = col, ident

    def set(self, d):
        self.col.dados[self.id] = dict(d)

    def create(self, d):
        if self.id in self.col.dados:
            raise _Existe("já existe")
        self.col.dados[self.id] = dict(d)

    def get(self):
        return _Snap(self.id, self.col.dados.get(self.id))

    def delete(self):
        self.col.dados.pop(self.id, None)


class _Col:
    def __init__(self):
        self.dados = {}

    def document(self, ident):
        return _Doc(self, ident)

    def stream(self):
        return [_Snap(k, v) for k, v in list(self.dados.items())]


class _Lote:
    def __init__(self):
        self.ops = []

    def set(self, doc, d):
        self.ops.append((doc.set, d))

    def create(self, doc, d):  # F04: a marca da semente entra no batch como create
        self.ops.append((doc.create, d))

    def commit(self):
        for op, d in self.ops:
            op(d)


class _Firestore:
    def __init__(self):
        self.cols = {}

    def collection(self, nome):
        return self.cols.setdefault(nome, _Col())

    def batch(self):
        return _Lote()


class _Blob:
    def __init__(self, b, nome):
        self.b, self.nome = b, nome

    def upload_from_string(self, dados, content_type=None):
        self.b.objetos[self.nome] = (dados, content_type)

    def download_as_bytes(self):
        return self.b.objetos[self.nome][0]

    def delete(self):
        del self.b.objetos[self.nome]


class _Bucket:
    def __init__(self):
        self.objetos = {}

    def blob(self, nome):
        return _Blob(self, nome)


def test_backend_firestore_com_falsos(monkeypatch):
    fs, bucket = _Firestore(), _Bucket()
    q = repositorio.Quadro(repositorio.FirestoreBackend("proj", "(default)", "", "", cliente=fs, bucket_obj=bucket))
    assert len(q.listar()) == 13 and q.na_semente()
    assert set(fs.cols) >= {"iniciativas", "iniciativas_meta"} and fs.cols["iniciativas_meta"].dados["alterado"] == {"valor": "0"}
    n = q.criar({"sigla": "FS", "nome": "Firestore", "fase": "testes"})
    q.mover(n["id"], "producao", 1)
    assert [i["id"] for i in q.listar() if i["fase"] == "producao"] == ["lia", n["id"], "gps", "mia"]
    q.excluir("gps")
    assert fs.cols["iniciativas"].dados["gps"]["excluido"] == 1 and not q.na_semente()
    a = q.anexar(n["id"], "tela.png", PNG)
    objeto = f"anexos/{n['id']}/{a['arquivo']}"
    assert bucket.objetos[objeto] == (PNG, "image/png")  # bucket privado: o app lê e serve (proxy)
    assert q.ler_anexo(a["id"])[1] == PNG and fs.cols["anexos"].dados[a["id"]]["nome_original"] == "tela.png"
    q.remover_anexo(a["id"])
    assert objeto not in bucket.objetos and a["id"] not in fs.cols["anexos"].dados
    # 2ª instância (outra réplica do Cloud Run) não semeia de novo
    q2 = repositorio.Quadro(repositorio.FirestoreBackend("proj", "(default)", "", "", cliente=fs, bucket_obj=bucket))
    assert n["id"] in [i["id"] for i in q2.listar()] and "gps" not in [i["id"] for i in q2.listar()]
    # prefixo das coleções
    fs2 = _Firestore()
    repositorio.Quadro(repositorio.FirestoreBackend("p", "(default)", "", "teste_", cliente=fs2, bucket_obj=_Bucket())).listar()
    assert "teste_iniciativas" in fs2.cols


def test_backend_firestore_falhas_viram_indisponivel(monkeypatch):
    class Quebrado(_Firestore):
        def collection(self, nome):
            raise RuntimeError("PermissionDenied")

    q = repositorio.Quadro(repositorio.FirestoreBackend("p", "(default)", "", "", cliente=Quebrado(), bucket_obj=_Bucket()))
    with pytest.raises(repositorio.QuadroIndisponivel):
        q.listar()
    with pytest.raises(repositorio.QuadroIndisponivel):  # sem bucket configurado
        repositorio.FirestoreBackend("p", "(default)", "", "")


def test_fabrica_escolhe_o_backend_pela_configuracao(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "INICIATIVAS_BACKEND", "firestore")
    monkeypatch.setattr(config, "INICIATIVAS_BUCKET", "bucket-teste")
    b = repositorio.criar_backend()
    assert isinstance(b, repositorio.FirestoreBackend) and b._nome_bucket == "bucket-teste" and b._cli is None  # preguiçoso
    monkeypatch.setattr(config, "INICIATIVAS_BACKEND", "sqlite")
    monkeypatch.setattr(config, "INICIATIVAS_DB", tmp_path / "x.db")
    monkeypatch.setattr(config, "INICIATIVAS_ANEXOS", tmp_path / "a")
    assert isinstance(repositorio.criar_backend(), repositorio.SqliteBackend)
    monkeypatch.setattr(config, "INICIATIVAS_BACKEND", "mongo")
    with pytest.raises(repositorio.QuadroIndisponivel):
        repositorio.criar_backend()


# ---------------------------------------------------------------- AUTH=iap (exceção temporária à D10)
def _token_iap(publico, emissor=iap.EMISSOR, email="gerente@viu.com.br", validade=600):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from google.auth import crypt, jwt

    chave = ec.generate_private_key(ec.SECP256R1())
    pem_priv = chave.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                   serialization.NoEncryption())
    pem_pub = chave.public_key().public_bytes(serialization.Encoding.PEM,
                                              serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    assinante = crypt.ES256Signer.from_string(pem_priv, key_id="chave-teste")
    agora = int(time.time())
    token = jwt.encode(assinante, {"iss": emissor, "aud": publico, "email": f"accounts.google.com:{email}",
                                   "iat": agora, "exp": agora + validade})
    return token.decode(), {"chave-teste": pem_pub}


def test_iap_verifica_assinatura_publico_e_emissor(monkeypatch):
    publico = "/projects/123/locations/us-central1/services/relatorios-agenciamento"
    monkeypatch.setattr(config, "IAP_AUDIENCE", publico)
    token, chaves = _token_iap(publico)
    monkeypatch.setattr(iap, "_cache", {"chaves": chaves, "em": time.monotonic()})
    assert iap.verificar(token) == "gerente@viu.com.br"
    assert iap.verificar(None) is None and iap.verificar("lixo") is None
    outro, ch2 = _token_iap("/projects/999/outro")
    monkeypatch.setattr(iap, "_cache", {"chaves": {**chaves, **ch2}, "em": time.monotonic()})
    assert iap.verificar(outro) is None  # público errado
    falso, ch3 = _token_iap(publico, emissor="https://atacante.example")
    monkeypatch.setattr(iap, "_cache", {"chaves": ch3, "em": time.monotonic()})
    assert iap.verificar(falso) is None  # emissor errado
    monkeypatch.setattr(iap, "_cache", {"chaves": ch2, "em": time.monotonic()})
    assert iap.verificar(token) is None  # assinado por outra chave


def test_auth_iap_fecha_tudo_sem_o_cabecalho(monkeypatch, quadro_limpo):
    from app.main import app

    publico = "/projects/123/locations/us-central1/services/relatorios-agenciamento"
    token, chaves = _token_iap(publico)
    monkeypatch.setattr(config, "AUTH", "iap")
    monkeypatch.setattr(config, "IAP_AUDIENCE", publico)
    monkeypatch.setattr(iap, "_cache", {"chaves": chaves, "em": time.monotonic()})
    with TestClient(app) as c:
        for caminho in ("/viu-agenciamento/iniciativas", f"{API}/iniciativas", "/static/estilo.css", "/especulacao.json"):
            r = c.get(caminho)
            assert r.status_code == 401 and "IAP" in r.text, caminho
        assert c.get("/especulacao.json", headers={iap.CABECALHO: "invalido"}).status_code == 401
        ok = c.get("/especulacao.json", headers={iap.CABECALHO: token})
        assert ok.status_code == 200 and "content-security-policy" in ok.headers
        r = c.post(f"{API}/iniciativas", json={"sigla": "IAP", "fase": "testes"}, headers={**CSRF, iap.CABECALHO: token})
        assert r.status_code == 201
    assert quadro_limpo.obter(r.json()["id"])["atualizado_por"] == "gerente@viu.com.br"  # quem editou fica registrado


def test_main_recusa_auth_iap_sem_publico(monkeypatch):
    """O guarda do app/main.py: AUTH=off continua recusado em produção; AUTH=iap exige IAP_AUDIENCE."""
    texto = (Path(__file__).resolve().parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    assert 'if config.AUTH == "off" and config.EM_PRODUCAO:' in texto
    assert 'if not config.IAP_AUDIENCE:' in texto and 'AUTH=iap exige IAP_AUDIENCE' in texto


def test_catalogo_segue_como_semente():
    # o catálogo continua no código, como semente e histórico: 4 fases e 13 itens (MIA em produção e Raio-X na esteira, 03/11/2026)
    assert len(catalogo.GRUPOS) == 4 and sum(len(g["itens"]) for g in catalogo.GRUPOS) == 13
    assert [s["id"] for s in repositorio.Quadro.itens_da_semente()][:4] == ["lia", "gps", "mia", "orca-ai"]


# ---------------------------------------------------------------- persistência de ponta a ponta (pedido do Caio)
def test_persistencia_de_ponta_a_ponta_sobrevive_a_reinicio(quadro_limpo):
    """Cria, edita, move, exclui e anexa pela API; depois um processo "novo" (outra instância do quadro sobre o mesmo
    arquivo, como depois de reiniciar o servidor ou abrir em outro navegador) lê tudo igual, pela API e pela página."""
    from app.main import app

    with TestClient(app) as c:
        nova = c.post(f"{API}/iniciativas", json={"sigla": "PERSIST", "nome": "Teste de persistência", "fase": "esteira",
                                                  "descricao": "Criada no teste."}, headers=CSRF).json()
        assert c.put(f"{API}/iniciativas/{nova['id']}", json={"responsavel": "Gerente", "status": "Em teste",
                                                               "proximo": "Apresentar"}, headers=CSRF).status_code == 200
        assert c.post(f"{API}/iniciativas/{nova['id']}/mover", json={"fase": "producao", "posicao": 1},
                      headers=CSRF).status_code == 200
        assert c.put(f"{API}/iniciativas/fila", json={"nome": "Fila Inteligente (RAIO-X)"}, headers=CSRF).status_code == 200
        assert c.delete(f"{API}/iniciativas/auto", headers=CSRF).status_code == 204
        anexo = _enviar(c, nova["id"], "raio-x.png", PNG).json()
        assert _enviar(c, nova["id"], "proposta.pdf", PDF).status_code == 201

    repositorio.redefinir()  # "reinício": nenhuma memória do processo anterior; só o que está no arquivo
    with TestClient(app) as c2:
        dados = c2.get(f"{API}/iniciativas").json()
        por_id = {i["id"]: i for i in dados["iniciativas"]}
        n = por_id[nova["id"]]
        assert (n["fase"], n["ordem"], n["responsavel"], n["status"], n["proximo"]) == (
            "producao", 1, "Gerente", "Em teste", "Apresentar")
        assert [i["id"] for i in dados["iniciativas"] if i["fase"] == "producao"] == ["lia", nova["id"], "gps", "mia"]
        assert por_id["fila"]["nome"] == "Fila Inteligente (RAIO-X)" and "auto" not in por_id
        assert [a["nome"] for a in dados["anexos"][nova["id"]]] == ["raio-x.png", "proposta.pdf"]
        assert c2.get(anexo["url"]).content == PNG and dados["na_semente"] is False
        html = c2.get("/viu-agenciamento/iniciativas").text
        assert f'data-ini-id="{nova["id"]}" data-ini-sigla="PERSIST"' in html and "Fila Inteligente (RAIO-X)" in html
        assert 'data-ini-id="auto"' not in html and "<dt>Responsável</dt><dd>Gerente</dd>" in html
        assert html.index('data-ini-id="lia"') < html.index(f'data-ini-id="{nova["id"]}"') < html.index('data-ini-id="gps"')
        assert 'aria-label="Imagem 1 de 2: raio-x.png"' in html and 'aria-label="Documento 2 de 2: proposta.pdf"' in html
        assert "13</span> iniciativas" in html  # 13 + 1 nova - 1 excluída


def test_falha_na_gravacao_nao_finge_que_salvou(cliente, monkeypatch, quadro_limpo):
    """Se o armazenamento falhar na escrita, a API responde 503 com mensagem (o JS mostra no aviso aria-live e, no
    pop-up, em role=alert) e nada muda; o JS só pinta "Salvo" depois da resposta OK do servidor."""
    def quebra(*a, **k):
        raise repositorio.QuadroIndisponivel("disco cheio")

    monkeypatch.setattr(quadro_limpo.b, "gravar", quebra)
    monkeypatch.setattr(quadro_limpo.b, "gravar_anexo", quebra)
    r = cliente.post(f"{API}/iniciativas", json={"sigla": "X", "fase": "testes"}, headers=CSRF)
    assert r.status_code == 503 and "indisponível" in r.json()["detail"]
    assert cliente.post(f"{API}/iniciativas/lia/mover", json={"fase": "testes", "posicao": 0}, headers=CSRF).status_code == 503
    assert _enviar(cliente, "lia", "a.png", PNG).status_code == 503
    monkeypatch.undo()
    assert [i["id"] for i in quadro_limpo.listar()][:2] == ["lia", "gps"] and len(quadro_limpo.listar()) == 13
    js = (Path(__file__).resolve().parents[1] / "app" / "static" / "iniciativas.js").read_text(encoding="utf-8")
    assert 'estado(err.message, "erro")' in js and "falha.hidden = false" in js  # erro visível no aviso e no pop-up
    assert 'O quadro voltou ao que está salvo.' in js  # mover/excluir que falham voltam ao estado do servidor
    assert js.index('pedido.then(function (i) {') < js.index('estado("Salvo", "ok");\n      op.focoFinal')  # "Salvo" só após OK
