"""Quadro das Iniciativas com dados no servidor (Caio e gerente, 30/10/2026).

Duas camadas:
- **Backend** (onde os dados moram), com a mesma interface pequena em dois sabores:
  - `SqliteBackend` (padrão no computador): um arquivo SQLite FORA do Google Drive (SQLite em pasta sincronizada pode
    corromper) e uma pasta de anexos ao lado. Caminhos em `config.INICIATIVAS_DB` e `config.INICIATIVAS_ANEXOS`.
  - `FirestoreBackend` (padrão no Cloud Run): coleções do Firestore (`iniciativas`, `anexos`, `iniciativas_meta`) e os
    arquivos num bucket privado do Cloud Storage, servidos pelo próprio app (proxy de leitura). Credenciais = ADC
    (conta de serviço do Cloud Run); nenhuma chave em arquivo.
- **`Quadro`** (regras): semente a partir do `catalogo.py` na 1ª execução, validação, ordem dentro da fase, exclusão
  lógica, anexos (tipo por extensão e assinatura, 10 MB, nome salvo = uuid) e a importação única do que um navegador
  guardou no localStorage (chave `ini-quadro:v1`, versão anterior da página).

Escala: dezenas de iniciativas e poucas pessoas editando. Uma trava por processo serializa as escritas; no Cloud Run
(máx. 2 instâncias) duas edições simultâneas na mesma coluna podem, no pior caso, deixar a ordem com um empate, que a
próxima mudança renumera. Aceitável aqui; ver a ficha (docs/paginas/iniciativas.md).
"""

from __future__ import annotations

import re
import sqlite3
import threading
import unicodedata
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app import config
from app.apresentacoes.gestao_orcamentos.iniciativas import catalogo

# limites dos textos (os mesmos do pop-up de edição, maxlength no template)
MAX = {"sigla": 40, "nome": 120, "descricao": 400, "responsavel": 80, "status": 120, "proximo": 120}
CAMPOS = tuple(MAX)
MAX_ANEXO = 10 * 1024 * 1024  # 10 MB por arquivo
MAX_ANEXOS_POR_INICIATIVA = 30
MAX_NOME_ANEXO = 120

# tipos aceitos: extensão → (tipo MIME, assinatura). SVG e HTML ficam de fora (podem levar script: risco de XSS)
TIPOS = {
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp",
    "pdf": "application/pdf",
}
EXT_DO_TIPO = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp", "application/pdf": "pdf"}


class ErroQuadro(Exception):
    """Erro de regra (vira 400/404/413 na API), com mensagem que pode ir à tela."""

    def __init__(self, mensagem: str, status: int = 400):
        super().__init__(mensagem)
        self.status = status


class QuadroIndisponivel(Exception):
    """O armazenamento não respondeu (arquivo, Firestore ou bucket). A página cai para o catálogo, só leitura."""


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fases() -> tuple[str, ...]:
    return tuple(g["chave"] for g in catalogo.GRUPOS)


def slug(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-") or "item"


def tipo_pela_assinatura(cabeca: bytes) -> str | None:
    if cabeca.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if cabeca.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if cabeca[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if cabeca[:4] == b"RIFF" and cabeca[8:12] == b"WEBP":
        return "image/webp"
    if cabeca.startswith(b"%PDF-"):
        return "application/pdf"
    return None


def validar_arquivo(nome: str, conteudo: bytes) -> tuple[str, str]:
    """(nome de exibição limpo, tipo MIME). Recusa extensão fora da lista, assinatura diferente da extensão, vazio e
    acima de 10 MB. O nome do usuário nunca vira caminho: só aparece na legenda."""
    nome = unicodedata.normalize("NFC", (nome or "").replace("\\", "/").split("/")[-1]).strip()
    nome = re.sub(r"[\x00-\x1f\x7f]", "", nome)[:MAX_NOME_ANEXO] or "arquivo"
    ext = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if ext not in TIPOS:
        raise ErroQuadro("Tipo de arquivo não aceito. Use PNG, JPEG, WebP, GIF ou PDF.", 415)
    if not conteudo:
        raise ErroQuadro("Arquivo vazio.")
    if len(conteudo) > MAX_ANEXO:
        raise ErroQuadro("Arquivo acima de 10 MB.", 413)
    tipo = tipo_pela_assinatura(conteudo[:16])
    if tipo != TIPOS[ext]:
        raise ErroQuadro("O conteúdo do arquivo não confere com a extensão (.%s)." % ext, 415)
    return nome, tipo


def _limpo(dados: dict, parcial: bool = False) -> dict:
    """Textos aparados e cortados no limite; fase dentro das válidas. Usado pela API (depois do Pydantic) e pela
    importação do navegador."""
    out = {}
    for k in CAMPOS:
        if k in dados or not parcial:
            v = dados.get(k) or ""
            if not isinstance(v, str):
                raise ErroQuadro(f"Campo {k} inválido.")
            v = v.strip()
            if len(v) > MAX[k]:
                raise ErroQuadro(f"{k} passa de {MAX[k]} caracteres.")
            out[k] = v
    if "fase" in dados or not parcial:
        if dados.get("fase") not in fases():
            raise ErroQuadro("Fase inválida.")
        out["fase"] = dados["fase"]
    return out


# ---------------------------------------------------------------- backends
class SqliteBackend:
    """Arquivo SQLite local (fora do Drive) + pasta de anexos. Uma conexão por operação (simples e seguro com threads)."""

    nome = "sqlite"

    def __init__(self, arquivo: Path, pasta_anexos: Path):
        self.arquivo, self.pasta = Path(arquivo), Path(pasta_anexos)
        try:
            self.arquivo.parent.mkdir(parents=True, exist_ok=True)
            self.pasta.mkdir(parents=True, exist_ok=True)
            with self._con() as c:
                c.executescript("""
                    CREATE TABLE IF NOT EXISTS iniciativas (
                        id TEXT PRIMARY KEY, sigla TEXT NOT NULL DEFAULT '', nome TEXT NOT NULL DEFAULT '',
                        fase TEXT NOT NULL, ordem INTEGER NOT NULL DEFAULT 0, responsavel TEXT NOT NULL DEFAULT '',
                        descricao TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT '',
                        proximo TEXT NOT NULL DEFAULT '', link_rotulo TEXT NOT NULL DEFAULT '',
                        link_href TEXT NOT NULL DEFAULT '', semente INTEGER NOT NULL DEFAULT 0,
                        criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL, atualizado_por TEXT NOT NULL DEFAULT '',
                        excluido INTEGER NOT NULL DEFAULT 0);
                    CREATE TABLE IF NOT EXISTS anexos (
                        id TEXT PRIMARY KEY, iniciativa_id TEXT NOT NULL REFERENCES iniciativas(id),
                        nome_original TEXT NOT NULL, arquivo TEXT NOT NULL, tipo TEXT NOT NULL,
                        tamanho INTEGER NOT NULL, ordem INTEGER NOT NULL DEFAULT 0, criado_em TEXT NOT NULL);
                    CREATE INDEX IF NOT EXISTS anexos_iniciativa ON anexos(iniciativa_id);
                    CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT NOT NULL);
                """)
        except (OSError, sqlite3.Error) as e:
            raise QuadroIndisponivel(f"SQLite indisponível: {e}") from e

    @contextmanager
    def _con(self):
        con = sqlite3.connect(self.arquivo, timeout=10)
        con.row_factory = sqlite3.Row
        try:
            with con:  # transação: commit no fim, rollback se der erro
                yield con
        finally:
            con.close()

    def _rodar(self, fn):
        try:
            with self._con() as c:
                return fn(c)
        except sqlite3.Error as e:
            raise QuadroIndisponivel(f"SQLite: {e}") from e

    def iniciativas(self) -> list[dict]:
        return self._rodar(lambda c: [dict(r) for r in c.execute("SELECT * FROM iniciativas")])

    def gravar(self, itens: list[dict]) -> None:
        if not itens:
            return
        colunas = list(itens[0])

        def fn(c):
            c.executemany(
                f"INSERT OR REPLACE INTO iniciativas ({', '.join(colunas)}) VALUES ({', '.join('?' * len(colunas))})",
                [tuple(i[k] for k in colunas) for i in itens])
        self._rodar(fn)

    def meta(self, chave: str) -> str | None:
        r = self._rodar(lambda c: c.execute("SELECT valor FROM meta WHERE chave = ?", (chave,)).fetchone())
        return r["valor"] if r else None

    def meta_gravar(self, chave: str, valor: str) -> None:
        self._rodar(lambda c: c.execute("INSERT OR REPLACE INTO meta (chave, valor) VALUES (?, ?)", (chave, valor)))

    def meta_criar(self, chave: str, valor: str) -> bool:
        """Cria só se não existe (a semente roda uma vez só, mesmo com dois processos)."""
        return self._rodar(lambda c: c.execute(
            "INSERT OR IGNORE INTO meta (chave, valor) VALUES (?, ?)", (chave, valor)).rowcount == 1)

    def semear(self, itens: list[dict], momento: str) -> bool:
        """F04 (auditoria de 31/10/2026): semente numa transação só (itens + marcas), com a trava de escrita do SQLite
        desde o início (BEGIN IMMEDIATE: dois processos não semeiam ao mesmo tempo). Semeia se não houver marca, ou se
        houver marca e nenhuma linha (semente interrompida pela versão anterior, que gravava a marca antes dos itens).
        Uma falha no meio desfaz tudo: a próxima tentativa recomeça do zero."""
        def fn(c):
            c.execute("BEGIN IMMEDIATE")
            marca = c.execute("SELECT 1 FROM meta WHERE chave = 'semeado_em'").fetchone()
            tem = c.execute("SELECT 1 FROM iniciativas LIMIT 1").fetchone()
            if marca and tem:
                return False
            if not tem and itens:
                colunas = list(itens[0])
                c.executemany(
                    f"INSERT INTO iniciativas ({', '.join(colunas)}) VALUES ({', '.join('?' * len(colunas))})",
                    [tuple(i[k] for k in colunas) for i in itens])
                c.execute("INSERT OR REPLACE INTO meta (chave, valor) VALUES ('alterado', '0')")
            c.execute("INSERT OR REPLACE INTO meta (chave, valor) VALUES ('semeado_em', ?)", (momento,))
            return True
        return self._rodar(fn)

    def anexos(self) -> list[dict]:
        return self._rodar(lambda c: [dict(r) for r in c.execute("SELECT * FROM anexos ORDER BY ordem, criado_em, id")])

    def gravar_anexo(self, meta: dict, conteudo: bytes) -> None:
        destino = self.pasta / meta["arquivo"]
        try:
            destino.write_bytes(conteudo)
        except OSError as e:
            raise QuadroIndisponivel(f"pasta de anexos: {e}") from e
        colunas = list(meta)
        self._rodar(lambda c: c.execute(
            f"INSERT INTO anexos ({', '.join(colunas)}) VALUES ({', '.join('?' * len(colunas))})",
            tuple(meta[k] for k in colunas)))

    def ler_anexo(self, meta: dict) -> bytes:
        try:
            return (self.pasta / meta["arquivo"]).read_bytes()
        except OSError as e:
            raise QuadroIndisponivel(f"pasta de anexos: {e}") from e

    def apagar_anexo(self, meta: dict) -> None:
        self._rodar(lambda c: c.execute("DELETE FROM anexos WHERE id = ?", (meta["id"],)))
        try:
            (self.pasta / meta["arquivo"]).unlink(missing_ok=True)
        except OSError:
            pass  # a linha já saiu; o arquivo órfão não aparece em lugar nenhum


class FirestoreBackend:
    """Firestore (dados) + Cloud Storage (arquivos). Os clientes são criados na 1ª chamada, com ADC; nos testes,
    entram clientes falsos (tests/test_iniciativas_repositorio.py). Nenhum recurso é criado por aqui: banco, bucket e
    permissões são do roteiro de deploy (docs/deploy_iniciativas.md), rodado pelo Caio."""

    nome = "firestore"

    def __init__(self, projeto: str, banco: str, bucket: str, prefixo: str = "", cliente=None, bucket_obj=None):
        if not bucket and bucket_obj is None:
            raise QuadroIndisponivel("INICIATIVAS_BUCKET não definido (bucket dos anexos).")
        self._projeto, self._banco, self._nome_bucket, self._prefixo = projeto, banco, bucket, prefixo
        self._cli, self._bucket = cliente, bucket_obj

    def _db(self):
        if self._cli is None:
            from google.cloud import firestore  # só em produção (requirements.txt)

            self._cli = firestore.Client(project=self._projeto, database=self._banco)
        return self._cli

    def _b(self):
        if self._bucket is None:
            from google.cloud import storage

            self._bucket = storage.Client(project=self._projeto).bucket(self._nome_bucket)
        return self._bucket

    def _col(self, nome: str):
        return self._db().collection(self._prefixo + nome)

    @staticmethod
    def _falha(e: Exception) -> QuadroIndisponivel:
        return QuadroIndisponivel(f"Firestore/Storage: {type(e).__name__}: {e}")

    def iniciativas(self) -> list[dict]:
        try:
            return [{**d.to_dict(), "id": d.id} for d in self._col("iniciativas").stream()]
        except Exception as e:  # noqa: BLE001 (erros da biblioteca: rede, permissão, cota)
            raise self._falha(e) from e

    def gravar(self, itens: list[dict]) -> None:
        if not itens:
            return
        try:
            lote = self._db().batch()
            for i in itens:
                lote.set(self._col("iniciativas").document(i["id"]), {k: v for k, v in i.items() if k != "id"})
            lote.commit()
        except Exception as e:  # noqa: BLE001
            raise self._falha(e) from e

    def meta(self, chave: str) -> str | None:
        try:
            d = self._col("iniciativas_meta").document(chave).get()
        except Exception as e:  # noqa: BLE001
            raise self._falha(e) from e
        return (d.to_dict() or {}).get("valor") if d.exists else None

    def meta_gravar(self, chave: str, valor: str) -> None:
        try:
            self._col("iniciativas_meta").document(chave).set({"valor": valor})
        except Exception as e:  # noqa: BLE001
            raise self._falha(e) from e

    def meta_criar(self, chave: str, valor: str) -> bool:
        try:
            self._col("iniciativas_meta").document(chave).create({"valor": valor})
            return True
        except Exception as e:  # noqa: BLE001
            if type(e).__name__ in ("AlreadyExists", "Conflict"):
                return False
            raise self._falha(e) from e

    def semear(self, itens: list[dict], momento: str) -> bool:
        """F04 (auditoria de 31/10/2026): itens e marcas num batch só (atômico no Firestore: tudo ou nada). A marca
        `semeado_em` entra no mesmo batch, depois dos itens; sem marca, ela vai como `create` (se outra réplica semeou
        antes, o batch inteiro é recusado e nada muda). Com marca e nenhum documento (semente interrompida pela versão
        anterior), semeia de novo."""
        try:
            marca = self._col("iniciativas_meta").document("semeado_em").get().exists
            tem = any(True for _ in self._col("iniciativas").stream())
            if marca and tem:
                return False
            lote = self._db().batch()
            if not tem:
                for i in itens:
                    lote.set(self._col("iniciativas").document(i["id"]), {k: v for k, v in i.items() if k != "id"})
                lote.set(self._col("iniciativas_meta").document("alterado"), {"valor": "0"})
            doc_marca = self._col("iniciativas_meta").document("semeado_em")
            if marca:
                lote.set(doc_marca, {"valor": momento})
            else:
                lote.create(doc_marca, {"valor": momento})
            lote.commit()
            return True
        except Exception as e:  # noqa: BLE001
            if type(e).__name__ in ("AlreadyExists", "Conflict"):
                return False
            raise self._falha(e) from e

    def anexos(self) -> list[dict]:
        try:
            lista = [{**d.to_dict(), "id": d.id} for d in self._col("anexos").stream()]
        except Exception as e:  # noqa: BLE001
            raise self._falha(e) from e
        return sorted(lista, key=lambda a: (a.get("ordem", 0), a["criado_em"], a["id"]))

    def _objeto(self, meta: dict) -> str:
        return f"anexos/{meta['iniciativa_id']}/{meta['arquivo']}"

    def gravar_anexo(self, meta: dict, conteudo: bytes) -> None:
        try:
            self._b().blob(self._objeto(meta)).upload_from_string(conteudo, content_type=meta["tipo"])
            self._col("anexos").document(meta["id"]).set({k: v for k, v in meta.items() if k != "id"})
        except Exception as e:  # noqa: BLE001
            raise self._falha(e) from e

    def ler_anexo(self, meta: dict) -> bytes:
        try:
            return self._b().blob(self._objeto(meta)).download_as_bytes()
        except Exception as e:  # noqa: BLE001
            raise self._falha(e) from e

    def apagar_anexo(self, meta: dict) -> None:
        try:
            self._col("anexos").document(meta["id"]).delete()
        except Exception as e:  # noqa: BLE001
            raise self._falha(e) from e
        try:
            self._b().blob(self._objeto(meta)).delete()
        except Exception:  # noqa: BLE001 (o registro já saiu; objeto órfão não aparece)
            pass


# ---------------------------------------------------------------- regras do quadro
class Quadro:
    def __init__(self, backend):
        self.b = backend
        self._trava = threading.RLock()
        self._semeado = False

    # ---------- semente ----------
    @staticmethod
    def itens_da_semente() -> list[dict]:
        momento, usados, out = agora(), set(), []
        for g in catalogo.GRUPOS:
            for k, i in enumerate(g["itens"]):
                titulo = i["sigla"] or i["nome"]
                base, n = slug(titulo), 2
                ident = base
                while ident in usados:
                    ident, n = f"{base}-{n}", n + 1
                usados.add(ident)
                link = i.get("link") or {}
                out.append({"id": ident, "sigla": i["sigla"], "nome": i["nome"], "fase": g["chave"], "ordem": k,
                            "responsavel": i.get("responsavel", "").strip(), "descricao": i["desc"] or i["curta"],
                            "status": i.get("status", "").strip(), "proximo": i.get("proximo", "").strip(),
                            "link_rotulo": link.get("rotulo", ""), "link_href": link.get("href", ""), "semente": 1,
                            "criado_em": momento, "atualizado_em": momento, "atualizado_por": "", "excluido": 0})
        return out

    def _semear(self) -> None:
        if self._semeado:
            return
        with self._trava:
            # F04: transacional/idempotente no backend (itens antes da marca, tudo ou nada); falha = exceção, e a
            # próxima leitura tenta de novo (_semeado só vira True depois de dar certo)
            self.b.semear(self.itens_da_semente(), agora())
            self._semeado = True

    def na_semente(self) -> bool:
        """True enquanto ninguém mexeu no quadro pelo servidor (condição para importar o que um navegador guardou)."""
        self._semear()
        return self.b.meta("alterado") in (None, "0")

    def _alterou(self) -> None:
        self.b.meta_gravar("alterado", "1")

    # ---------- leitura ----------
    def _todas(self) -> list[dict]:
        self._semear()
        return self.b.iniciativas()

    def listar(self) -> list[dict]:
        ordem = {f: k for k, f in enumerate(fases())}
        vivas = [i for i in self._todas() if not i.get("excluido") and i.get("fase") in ordem]
        return sorted(vivas, key=lambda i: (ordem[i["fase"]], i.get("ordem", 0), i.get("criado_em", ""), i["id"]))

    def obter(self, ident: str) -> dict:
        for i in self._todas():
            if i["id"] == ident and not i.get("excluido"):
                return i
        raise ErroQuadro("Iniciativa não encontrada.", 404)

    def anexos(self, iniciativa_id: str | None = None) -> list[dict]:
        self._semear()
        todos = self.b.anexos()
        return [a for a in todos if iniciativa_id is None or a["iniciativa_id"] == iniciativa_id]

    def anexo(self, anexo_id: str) -> dict:
        for a in self.anexos():
            if a["id"] == anexo_id:
                return a
        raise ErroQuadro("Anexo não encontrado.", 404)

    # ---------- escrita ----------
    def _coluna(self, fase: str, sem: str | None = None) -> list[dict]:
        return [i for i in self.listar() if i["fase"] == fase and i["id"] != sem]

    @staticmethod
    def _renumerar(coluna: list[dict], momento: str, mudados: dict) -> None:
        for k, i in enumerate(coluna):
            if i.get("ordem") != k:
                i["ordem"] = k
                mudados.setdefault(i["id"], i)

    def criar(self, dados: dict, por: str = "") -> dict:
        d = _limpo(dados)
        if not d["sigla"] and not d["nome"]:
            raise ErroQuadro("Preencha a sigla ou o nome.")
        with self._trava:
            existentes = {i["id"] for i in self._todas()}
            ident = "ini-" + uuid.uuid4().hex[:10]
            while ident in existentes:
                ident = "ini-" + uuid.uuid4().hex[:10]
            momento = agora()
            novo = {"id": ident, **d, "ordem": len(self._coluna(d["fase"])), "link_rotulo": "", "link_href": "",
                    "semente": 0, "criado_em": momento, "atualizado_em": momento, "atualizado_por": por, "excluido": 0}
            self.b.gravar([novo])
            self._alterou()
            return novo

    def editar(self, ident: str, dados: dict, por: str = "") -> dict:
        with self._trava:
            item = dict(self.obter(ident))
            d = _limpo(dados, parcial=True)
            final = {**item, **d}
            if not final["sigla"] and not final["nome"]:
                raise ErroQuadro("Preencha a sigla ou o nome.")
            momento, mudados = agora(), {}
            if final["fase"] != item["fase"]:  # mudou de fase pelo seletor: vai para o fim da nova coluna
                final["ordem"] = len(self._coluna(final["fase"]))
                self._renumerar(self._coluna(item["fase"], sem=ident), momento, mudados)
            final.update(atualizado_em=momento, atualizado_por=por)
            mudados[ident] = final
            self.b.gravar(list(mudados.values()))
            self._alterou()
            return final

    def mover(self, ident: str, fase: str, posicao: int, por: str = "") -> dict:
        if fase not in fases():
            raise ErroQuadro("Fase inválida.")
        with self._trava:
            item = dict(self.obter(ident))
            origem, momento, mudados = item["fase"], agora(), {}
            destino = self._coluna(fase, sem=ident)
            posicao = max(0, min(int(posicao), len(destino)))
            item.update(fase=fase, atualizado_em=momento, atualizado_por=por)
            destino.insert(posicao, item)
            self._renumerar(destino, momento, mudados)
            mudados[ident] = item
            if origem != fase:
                self._renumerar(self._coluna(origem, sem=ident), momento, mudados)
            self.b.gravar(list(mudados.values()))
            self._alterou()
            return item

    def excluir(self, ident: str, por: str = "") -> None:
        """Exclusão lógica: a linha fica (excluido = 1), com os anexos; some da tela."""
        with self._trava:
            item = dict(self.obter(ident))
            momento, mudados = agora(), {}
            item.update(excluido=1, atualizado_em=momento, atualizado_por=por)
            mudados[ident] = item
            self._renumerar(self._coluna(item["fase"], sem=ident), momento, mudados)
            self.b.gravar(list(mudados.values()))
            self._alterou()

    def restaurar_semente(self) -> None:
        """Volta o quadro ao catálogo: itens da semente com os textos e a ordem do catálogo; os incluídos ficam
        excluídos (logicamente). Anexos ficam. Só pela ferramenta tools/iniciativas_admin.py (sem botão na tela)."""
        with self._trava:
            self._semear()
            atuais = {i["id"]: i for i in self.b.iniciativas()}
            momento, saida = agora(), []
            semente = self.itens_da_semente()
            ids = {s["id"] for s in semente}
            for s in semente:
                if s["id"] in atuais:
                    s["criado_em"] = atuais[s["id"]].get("criado_em", momento)
                saida.append(s)
            for ident, i in atuais.items():
                if ident not in ids and not i.get("excluido"):
                    saida.append({**i, "excluido": 1, "atualizado_em": momento})
            self.b.gravar(saida)
            self.b.meta_gravar("alterado", "0")

    # ---------- anexos ----------
    def anexar(self, iniciativa_id: str, nome: str, conteudo: bytes) -> dict:
        nome, tipo = validar_arquivo(nome, conteudo)
        with self._trava:
            self.obter(iniciativa_id)
            atuais = self.anexos(iniciativa_id)
            if len(atuais) >= MAX_ANEXOS_POR_INICIATIVA:
                raise ErroQuadro(f"Limite de {MAX_ANEXOS_POR_INICIATIVA} anexos por iniciativa.")
            aid = uuid.uuid4().hex
            meta = {"id": aid, "iniciativa_id": iniciativa_id, "nome_original": nome,
                    "arquivo": f"{aid}.{EXT_DO_TIPO[tipo]}", "tipo": tipo, "tamanho": len(conteudo),
                    "ordem": max((a.get("ordem", 0) for a in atuais), default=-1) + 1, "criado_em": agora()}
            self.b.gravar_anexo(meta, conteudo)
            self._alterou()
            return meta

    def ler_anexo(self, anexo_id: str) -> tuple[dict, bytes]:
        meta = self.anexo(anexo_id)
        return meta, self.b.ler_anexo(meta)

    def remover_anexo(self, anexo_id: str) -> None:
        with self._trava:
            self.b.apagar_anexo(self.anexo(anexo_id))
            self._alterou()

    # ---------- importação única do navegador (localStorage "ini-quadro:v1") ----------
    def importar(self, estado: dict, por: str = "") -> dict:
        """Aplica o que a versão anterior da página guardou no navegador: {fases: {fase: [ids]}, dados: {id: campos},
        novos: {id: campos}, excluidos: [ids]} (campos com os nomes antigos: desc, resp, prox). Só com o quadro na
        semente (senão, 409: alguém já editou no servidor e a importação poderia desfazer)."""
        antigos = {"sigla": "sigla", "nome": "nome", "desc": "descricao", "resp": "responsavel", "status": "status",
                   "prox": "proximo"}

        def campos(d):
            if not isinstance(d, dict):
                return None
            return {novo: str(d.get(velho) or "")[:MAX[novo]] for velho, novo in antigos.items()}

        with self._trava:
            if not self.na_semente():
                raise ErroQuadro("O quadro já foi alterado no servidor; a importação foi recusada.", 409)
            fases_estado = estado.get("fases") if isinstance(estado.get("fases"), dict) else {}
            vivos = {i["id"]: i for i in self.listar()}
            mapa, feitos = {}, {"incluidas": 0, "editadas": 0, "excluidas": 0}
            onde = {ident: f for f, ids in fases_estado.items() if f in fases() and isinstance(ids, list)
                    for ident in ids if isinstance(ident, str)}
            for ident, d in list((estado.get("novos") or {}).items())[:100]:
                c = campos(d)
                if not c or not (c["sigla"] or c["nome"]):
                    continue
                novo = self.criar({**c, "fase": onde.get(ident, fases()[-1])}, por)
                mapa[ident] = novo["id"]
                feitos["incluidas"] += 1
            for ident, d in (estado.get("dados") or {}).items():
                c = campos(d)
                if ident in vivos and c and (c["sigla"] or c["nome"]):
                    self.editar(ident, c, por)
                    feitos["editadas"] += 1
            for ident in estado.get("excluidos") or []:
                if isinstance(ident, str) and ident in vivos:
                    self.excluir(ident, por)
                    feitos["excluidas"] += 1
            for f, ids in fases_estado.items():
                if f not in fases() or not isinstance(ids, list):
                    continue
                k = 0
                for ident in ids:
                    real = mapa.get(ident, ident)
                    if real in vivos or real in mapa.values():
                        try:
                            self.mover(real, f, k, por)
                            k += 1
                        except ErroQuadro:
                            pass  # excluída acima
            return feitos


# ---------------------------------------------------------------- instância do processo
_quadro: Quadro | None = None
_trava_global = threading.Lock()


def criar_backend():
    if config.INICIATIVAS_BACKEND == "firestore":
        return FirestoreBackend(config.PROJETO, config.INICIATIVAS_FIRESTORE_DB, config.INICIATIVAS_BUCKET,
                                config.INICIATIVAS_PREFIXO)
    if config.INICIATIVAS_BACKEND != "sqlite":
        raise QuadroIndisponivel(f"INICIATIVAS_BACKEND desconhecido: {config.INICIATIVAS_BACKEND!r}")
    return SqliteBackend(config.INICIATIVAS_DB, config.INICIATIVAS_ANEXOS)


def quadro() -> Quadro:
    global _quadro
    with _trava_global:
        if _quadro is None:
            _quadro = Quadro(criar_backend())
        return _quadro


def redefinir(novo: Quadro | None = None) -> None:
    """Troca a instância (testes; ou depois de mudar a configuração)."""
    global _quadro
    with _trava_global:
        _quadro = novo
