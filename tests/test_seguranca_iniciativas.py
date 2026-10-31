"""Correções da auditoria do Codex (31/10/2026), bloco "Segurança e Iniciativas": F06 (chaves do IAP), A29 (/saude com
IAP), F04 (semente das Iniciativas), F11 (upload), F12/A32 (/sinc), F17/A33 (pacote) e F19 (botões do Roadmap).
Registro em docs/auditoria/correcoes_2026-10-31.md. Tudo local: sem rede, sem GCP (chaves do IAP geradas aqui)."""

import asyncio
import base64
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import test_iniciativas_servidor as tis
from app import config, iap
from app.apresentacoes.gestao_orcamentos.iniciativas import api, repositorio

RAIZ = Path(__file__).resolve().parents[1]
PUBLICO = "/projects/123/locations/us-central1/services/relatorios-agenciamento"


# ---------------------------------------------------------------- F06: chaves do IAP
@pytest.fixture
def iap_limpo(monkeypatch):
    monkeypatch.setattr(config, "IAP_AUDIENCE", PUBLICO)
    monkeypatch.setattr(iap, "_estado", {"renovando": False, "falhou_em": None, "kid_renovado_em": None})
    monkeypatch.setattr(iap, "ESPERA_S", (0, 0))
    chamadas = []

    def falha():
        chamadas.append(threading.current_thread().name)
        raise OSError("rede fora")

    monkeypatch.setattr(iap, "_buscar_chaves", falha)
    monkeypatch.setattr(iap, "_log", lambda *a, **k: None)
    return chamadas


def _esperar_renovacao():
    for _ in range(200):
        if not iap._estado["renovando"]:
            return
        time.sleep(0.01)
    raise AssertionError("renovação em segundo plano não terminou")


def test_f06_renovacao_que_falha_mantem_as_chaves_anteriores(monkeypatch, iap_limpo):
    token, chaves = tis._token_iap(PUBLICO)
    duas_horas = time.monotonic() - 2 * 3600  # passou da renovação (1 h), dentro das 24 h
    monkeypatch.setattr(iap, "_cache", {"chaves": chaves, "em": duas_horas})
    # a requisição não espera a rede: segue com as chaves atuais e a renovação vai para uma thread
    assert iap.autenticar(token) == (200, "gerente@viu.com.br")
    _esperar_renovacao()
    assert iap_limpo and all(nome == "iap-chaves" for nome in iap_limpo)  # buscou só em segundo plano, 3 tentativas
    assert len(iap_limpo) == iap.TENTATIVAS
    assert iap._cache["chaves"] == chaves and iap._cache["em"] == duas_horas  # falhou: manteve as anteriores
    assert iap.autenticar(token).status == 200  # e continua aceitando o token verificado
    assert len(iap_limpo) == iap.TENTATIVAS  # depois de uma falha, sem nova busca antes de 60 s


def test_f06_token_adulterado_continua_401(monkeypatch, iap_limpo):
    token, chaves = tis._token_iap(PUBLICO)
    monkeypatch.setattr(iap, "_cache", {"chaves": chaves, "em": time.monotonic() - 2 * 3600})
    cabeca, corpo, assinatura = token.split(".")
    dados = json.loads(base64.urlsafe_b64decode(corpo + "=" * (-len(corpo) % 4)))
    dados["email"] = "accounts.google.com:intruso@exemplo.com"
    falso = base64.urlsafe_b64encode(json.dumps(dados).encode()).decode().rstrip("=")
    assert iap.autenticar(f"{cabeca}.{falso}.{assinatura}") == (401, None)
    assert iap.autenticar(f"{cabeca}.{corpo}.") == (401, None)  # sem assinatura
    _esperar_renovacao()


def test_f06_chaves_vencidas_ha_mais_de_24h_viram_503_e_nao_401(monkeypatch, iap_limpo, quadro_limpo):
    from app.main import app

    token, chaves = tis._token_iap(PUBLICO)
    monkeypatch.setattr(iap, "_cache", {"chaves": chaves, "em": time.monotonic() - 25 * 3600})
    assert iap.autenticar(token) == (503, None)  # nunca aceita sem verificar; e não confunde com token inválido
    assert iap.autenticar(None) == (401, None)
    monkeypatch.setattr(config, "AUTH", "iap")
    with TestClient(app) as c:
        r = c.get("/especulacao.json", headers={iap.CABECALHO: token})
        assert r.status_code == 503 and r.headers["retry-after"] == "30"
        assert c.get("/especulacao.json").status_code == 401  # sem cabeçalho continua 401
    # a rede voltou: a próxima busca (passados os 60 s) renova e aceita
    monkeypatch.setattr(iap, "_buscar_chaves", lambda: chaves)
    monkeypatch.setattr(iap, "_estado", {"renovando": False, "falhou_em": None, "kid_renovado_em": None})
    assert iap.autenticar(token).status == 200 and time.monotonic() - iap._cache["em"] < 5


def test_f06_chave_nova_do_iap_renova_na_hora(monkeypatch, iap_limpo):
    token, chaves = tis._token_iap(PUBLICO)
    monkeypatch.setattr(iap, "_cache", {"chaves": {"outra": "x"}, "em": time.monotonic()})
    monkeypatch.setattr(iap, "_buscar_chaves", lambda: chaves)
    assert iap.autenticar(token) == (200, "gerente@viu.com.br")


def test_f06_middleware_confere_fora_do_event_loop(monkeypatch, quadro_limpo):
    from app.main import app

    visto = {}

    def autenticar(token):
        try:
            asyncio.get_running_loop()
            visto["no_loop"] = True
        except RuntimeError:
            visto["no_loop"] = False
        return iap.Resultado(200, "gerente@viu.com.br")

    monkeypatch.setattr(config, "AUTH", "iap")
    monkeypatch.setattr(iap, "autenticar", autenticar)
    with TestClient(app) as c:
        assert c.get("/especulacao.json", headers={iap.CABECALHO: "x"}).status_code == 200
    assert visto == {"no_loop": False}
    texto = (RAIZ / "app" / "main.py").read_text(encoding="utf-8")
    assert "await run_in_threadpool(iap.autenticar" in texto and "iap.verificar(" not in texto


# ---------------------------------------------------------------- A29: /saude com IAP
def test_a29_saude_nao_fica_isenta_e_o_deploy_nao_usa_sonda_http(monkeypatch, quadro_limpo):
    """Decisão: /saude não fica isenta do JWT (mostra a situação das tabelas); nenhuma sonda HTTP a usa. O Cloud Run
    fica com a sonda de partida padrão (TCP na porta), que não passa pelo middleware."""
    from app.main import app

    monkeypatch.setattr(config, "AUTH", "iap")
    monkeypatch.setattr(config, "IAP_AUDIENCE", PUBLICO)
    with TestClient(app) as c:
        assert c.get("/saude").status_code == 401
    assert "HEALTHCHECK" not in (RAIZ / "Dockerfile").read_text(encoding="utf-8")
    roteiro = (RAIZ / "docs" / "deploy_iniciativas.md").read_text(encoding="utf-8")
    deploy = roteiro[roteiro.index("gcloud beta run deploy relatorios-agenciamento"):]
    deploy = deploy[:deploy.index("```")]
    assert "probe" not in deploy and "/saude" not in deploy
    assert "A29" in roteiro and "sonda" in roteiro


# ---------------------------------------------------------------- F04: semente transacional e idempotente
def test_f04_sqlite_falha_no_meio_da_semente_nao_deixa_marca_e_recupera(monkeypatch, tmp_path):
    original = repositorio.Quadro.itens_da_semente

    def quebrada():
        itens = original()
        itens[5]["fase"] = None  # NOT NULL: falha no meio do INSERT
        return itens

    b = repositorio.SqliteBackend(tmp_path / "q.db", tmp_path / "anexos")
    q = repositorio.Quadro(b)
    monkeypatch.setattr(repositorio.Quadro, "itens_da_semente", staticmethod(quebrada))
    with pytest.raises(repositorio.QuadroIndisponivel):
        q.listar()
    assert b.meta("semeado_em") is None and b.iniciativas() == []  # tudo ou nada
    monkeypatch.setattr(repositorio.Quadro, "itens_da_semente", staticmethod(original))
    assert len(q.listar()) == 11 and b.meta("semeado_em") and q.na_semente()  # a mesma instância tenta de novo


def test_f04_sqlite_marca_parcial_da_versao_anterior_semeia_de_novo(tmp_path):
    b = repositorio.SqliteBackend(tmp_path / "q.db", tmp_path / "anexos")
    assert b.meta_criar("semeado_em", "2026-10-31T00:00:00+00:00")  # o estado que a versão anterior deixava
    assert len(repositorio.Quadro(b).listar()) == 11
    # com itens, não semeia de novo (nem sobre um quadro todo excluído)
    q = repositorio.Quadro(b)
    for i in q.listar():
        q.excluir(i["id"])
    assert repositorio.Quadro(b).listar() == [] and len(b.iniciativas()) == 11


class _LoteAtomico(tis._Lote):
    def __init__(self, fs):
        super().__init__()
        self.fs, self.criar = fs, []

    def create(self, doc, d):
        self.criar.append((doc, d))

    def commit(self):
        if self.fs.quebrar:
            raise RuntimeError("DeadlineExceeded")
        for doc, _ in self.criar:  # tudo ou nada, como o batch do Firestore
            if doc.id in doc.col.dados:
                raise tis._Existe("já existe")
        super().commit()
        for doc, d in self.criar:
            doc.create(d)


class _FirestoreAtomico(tis._Firestore):
    quebrar = False

    def batch(self):
        return _LoteAtomico(self)


def test_f04_firestore_batch_com_falha_nao_grava_nada_e_recupera():
    fs = _FirestoreAtomico()
    fs.quebrar = True
    q = repositorio.Quadro(repositorio.FirestoreBackend("p", "(default)", "", "", cliente=fs, bucket_obj=tis._Bucket()))
    with pytest.raises(repositorio.QuadroIndisponivel):
        q.listar()
    assert not fs.collection("iniciativas").dados and "semeado_em" not in fs.collection("iniciativas_meta").dados
    fs.quebrar = False
    assert len(q.listar()) == 11 and fs.cols["iniciativas_meta"].dados["alterado"] == {"valor": "0"}
    assert "semeado_em" in fs.cols["iniciativas_meta"].dados
    # marca parcial (versão anterior) + coleção vazia: semeia de novo; com itens, outra réplica não semeia
    fs2 = _FirestoreAtomico()
    fs2.collection("iniciativas_meta").dados["semeado_em"] = {"valor": "antes"}
    assert len(repositorio.Quadro(repositorio.FirestoreBackend("p", "(default)", "", "", cliente=fs2,
                                                               bucket_obj=tis._Bucket())).listar()) == 11
    q.editar("gps", {"nome": "Pastas"})
    q2 = repositorio.Quadro(repositorio.FirestoreBackend("p", "(default)", "", "", cliente=fs, bucket_obj=tis._Bucket()))
    assert q2.obter("gps")["nome"] == "Pastas"


# ---------------------------------------------------------------- F11: upload limitado na recepção
def _multipart(nome, partes):
    yield (b'--limite\r\nContent-Disposition: form-data; name="arquivo"; filename="' + nome.encode()
           + b'"\r\nContent-Type: application/octet-stream\r\n\r\n')
    yield from partes
    yield b"\r\n--limite--\r\n"


def test_f11_envio_sem_content_length_acima_do_limite_e_413(quadro_limpo):
    from app.main import app

    cab = {**tis.CSRF, "Content-Type": "multipart/form-data; boundary=limite"}
    mega = b"\x00" * (1024 * 1024)
    with TestClient(app) as c:
        r = c.post(f"{tis.API}/iniciativas/lia/anexos", headers=cab,
                   content=_multipart("grande.png", [tis.PNG] + [mega] * 11))
        assert r.status_code == 413 and "10 MB" in r.json()["detail"]
        assert c.get(f"{tis.API}/iniciativas/lia/anexos").json() == []
        ok = c.post(f"{tis.API}/iniciativas/lia/anexos", headers=cab, content=_multipart("tela.png", [tis.PNG]))
        assert ok.status_code == 201 and ok.json()["nome"] == "tela.png"  # o mesmo caminho, dentro do limite


def test_f11_gravacao_do_anexo_fora_do_event_loop(monkeypatch, quadro_limpo):
    from app.main import app

    visto, original = {}, repositorio.Quadro.anexar

    def anexar(self, *a, **k):
        try:
            asyncio.get_running_loop()
            visto["no_loop"] = True
        except RuntimeError:
            visto["no_loop"] = False
        return original(self, *a, **k)

    monkeypatch.setattr(repositorio.Quadro, "anexar", anexar)
    with TestClient(app) as c:
        assert tis._enviar(c, "lia", "tela.png", tis.PNG).status_code == 201
    assert visto == {"no_loop": False}
    assert api.LIMITE_CORPO == repositorio.MAX_ANEXO + 64 * 1024


# ---------------------------------------------------------------- F12/A32: /sinc
def test_f12_sinc_post_valida_a_origem(monkeypatch):
    from app import main

    monkeypatch.setattr(config, "SINC", True)
    monkeypatch.setattr(main, "_SINC", {"url": None, "versao": 0, "origem": None, "sessao": "t"})

    def post(**cab):
        return c.post("/sinc", content=json.dumps({"url": "/viu-agenciamento/sla", "origem": "portal"}),
                      headers={"Content-Type": "text/plain", **cab})

    with TestClient(main.app) as c:
        assert post(Origin="https://exemplo.com").status_code == 403
        assert post(**{"Sec-Fetch-Site": "cross-site"}).status_code == 403
        assert main._SINC["versao"] == 0  # nada mudou
        assert post(Origin="http://testserver").status_code == 200  # mesma origem (o portal)
        assert post(Origin=config.SINC_ORIGENS[0]).status_code == 200  # a cola
        assert post(**{"Sec-Fetch-Site": "same-origin"}).status_code == 200


def test_a32_sinc_desligado_por_padrao_na_v2():
    env = {k: v for k, v in os.environ.items() if k not in ("SINC", "K_SERVICE")}
    saida = subprocess.run([sys.executable, "-c", "from app import config; print(config.SINC)"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, timeout=60)
    assert saida.stdout.strip() == "False", saida.stderr
    env["SINC"] = "on"
    saida = subprocess.run([sys.executable, "-c", "from app import config; print(config.SINC)"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, timeout=60)
    assert saida.stdout.strip() == "True", saida.stderr


# ---------------------------------------------------------------- F17/A33: pacote
@pytest.mark.parametrize("arquivo", [".dockerignore", ".gcloudignore"])
def test_f17_pacote_exclui_prototipos_e_pastas_de_trabalho(arquivo):
    linhas = {l.strip() for l in (RAIZ / arquivo).read_text(encoding="utf-8").splitlines()}
    for item in ("app/static/roadmap_proto/", "_congelado/", "_descartados/", ".playwright-mcp/", ".taste-skill/",
                 "docs/", "tests/", "tools/", "ml/*", "!ml/saida/", "ml/saida/*", "!ml/saida/previsao.json"):
        assert item in linhas, item
    assert (RAIZ / "app" / "static" / "roadmap_proto").is_dir()  # fora da imagem, mas no disco
    texto = (RAIZ / "app").as_posix()
    for p in (RAIZ / "app").rglob("*"):  # nada do portal aponta para os protótipos
        if p.suffix in (".py", ".html", ".js", ".css") and "roadmap_proto" not in p.as_posix():
            assert "roadmap_proto" not in p.read_text(encoding="utf-8", errors="ignore"), p.as_posix()[len(texto):]


# ---------------------------------------------------------------- F19: botões do Roadmap mais lentos, sem parar
def test_f19_botoes_do_roadmap_desaceleram_sem_parar():
    css = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    ini = css.index("/* Roadmap da área (V2")
    rm = css[ini:css.index("/* ---------- LIA (D-LIA-3", ini)]
    m = rm.index("@media (prefers-reduced-motion: no-preference)")
    movimento = rm[m:rm.index("\n}\n", m)]
    assert "html.js .rm-botoes > li { animation: rm-deriva-botao 7s ease-in-out infinite; }" in movimento
    assert "html.js .rm-botoes .rm-destino { animation: rm-deriva-lenta 21s ease-in-out infinite; }" in movimento
    assert "html.js .rm-categorias:hover, html.js .rm-categorias:focus-within { --rm-amp: 0px; --rm-amp-lenta: 1px; }" in movimento
    assert "--rm-amp: 2px;" in movimento and "transition: --rm-amp 900ms" in movimento
    assert "animation-play-state" not in movimento and "animation: none" not in movimento  # não para
    assert '@property --rm-amp { syntax: "<length>"' in rm and '@property --rm-amp-lenta { syntax: "<length>"' in rm
    # os chips decorativos seguem com a deriva de antes
    assert "html.js .rm-solto, html.js .rm-mini-pilha, html.js .rm-pendente > .rm-mini { animation: rm-deriva 7s" in movimento
    assert "@keyframes rm-deriva { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-0.2em); } }" in rm


# ---------------------------------------------------------------- D66: link aberto (AUTH=publico), só leitura
def test_d66_publico_sobe_em_producao_sem_edicao():
    env = {k: v for k, v in os.environ.items() if k not in ("SINC",)}
    env.update(K_SERVICE="viu-agenciamento", AUTH="publico", INICIATIVAS_EDICAO="on", CORTE_DADOS="off")
    cod = "from app import config, main; print(config.EM_PRODUCAO, config.INICIATIVAS_EDICAO, config.DEV)"
    saida = subprocess.run([sys.executable, "-c", cod], cwd=RAIZ, env=env, capture_output=True, text=True, timeout=120)
    assert saida.stdout.strip().splitlines()[-1] == "True False False", saida.stderr
    env["AUTH"] = "off"  # sem o modo explícito, a trava da D10 continua
    saida = subprocess.run([sys.executable, "-c", "import app.main"], cwd=RAIZ, env=env, capture_output=True, text=True,
                           timeout=120)
    assert saida.returncode != 0 and "AUTH=off" in saida.stderr


# ---------------------------------------------------------------- D66b: VPS temporária (chave no link e espelho)
def test_d66b_chave_no_link(monkeypatch, quadro_limpo):
    from app.main import app

    monkeypatch.setattr(config, "CHAVE_ACESSO", "chave-de-teste")
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/static/estilo.css").status_code == 403  # sem a chave nada passa, nem os estáticos
        assert c.get("/static/estilo.css?k=errada").status_code == 403
        r = c.get("/static/estilo.css?k=chave-de-teste&v=1")
        assert r.status_code == 303 and r.headers["location"] == "/static/estilo.css?v=1"  # a chave sai do endereço
        assert "httponly" in r.headers["set-cookie"].lower()
        r = c.get("/static/estilo.css?v=1")  # o cookie gravado basta daqui em diante
        assert r.status_code == 200 and r.headers["x-robots-tag"] == "noindex, nofollow"


def test_d66b_espelho_le_arquivos_sem_bigquery(monkeypatch, tmp_path):
    import pandas as pd
    from app import congelamento, dados

    t = dados.Tabela("Teste", "projeto.gold.tab_teste", chave=("a",))
    pd.DataFrame({"a": [1, 2]}).to_parquet(tmp_path / f"{congelamento.nome(t)}.parquet", index=False)
    (tmp_path / "espelho.json").write_text(json.dumps({"tabelas": {congelamento.nome(t): {
        "linhas": 2, "modificada_em": "2026-10-30T12:02:00+00:00"}}}), encoding="utf-8")
    monkeypatch.setattr(config, "ESPELHO_DIR", str(tmp_path))
    monkeypatch.setattr(dados, "cliente", lambda: (_ for _ in ()).throw(AssertionError("BigQuery consultado")))
    assert list(t.df()["a"]) == [1, 2] and t.congelada  # lida uma vez, não recarrega
