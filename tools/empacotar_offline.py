"""Empacota o portal em HTML estático, para abrir sem servidor (Caio, 30/10/2026: enviar a quem não tem o VS Code).

Só leitura: percorre o portal LOCAL já no ar (porta 8100, base congelada), grava cada página (e cada estado de filtro:
?talentos=, ?mes=, ?passo=) como um arquivo .html, copia os estáticos e reescreve os links para os arquivos. Tira o
que depende de servidor: sincronização com a cola (sinc.js), checagem de nova carga (metas relatorio-*) e a troca da
caixa do extrato por fetch (os meses passam a recarregar a página, como sem JS). O que fica: layout, filtros, dicas,
setas, slides do estudo, tela cheia. Uso: python tools/empacotar_offline.py [http://127.0.0.1:8100] <pasta_saida>
"""

import re
import shutil
import sys
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

import requests

BASE = (sys.argv[1] if len(sys.argv) > 2 else "http://127.0.0.1:8100").rstrip("/")
SAIDA = Path(sys.argv[-1])
AREA = "/viu-agenciamento"
ESTATICOS = Path(__file__).resolve().parent.parent / "app" / "static"
PARAMS = ("talentos", "mes", "passo")  # parâmetros que viram arquivos diferentes


def nome_arquivo(url: str) -> tuple[str, str]:
    """URL do portal -> (arquivo.html, #hash)."""
    u = urlsplit(url)
    caminho = u.path.rstrip("/")
    if caminho in ("", AREA):
        base = "demanda"
    elif caminho == f"{AREA}/sla/como-medimos":
        base = "estudo"
    else:
        base = caminho.removeprefix(AREA + "/").replace("/", "-")
    q = parse_qs(u.query)
    sufixo = ""
    for p in PARAMS:
        v = q.get(p, [None])[0]
        if v and not (p == "talentos" and v == "todos"):
            sufixo += f"--{p}-{v}" if p != "talentos" else f"--{v}"
    return f"{base}{sufixo}.html", (f"#{u.fragment}" if u.fragment else "")


def interno(href: str) -> bool:
    return href.startswith(("/", "?", AREA)) and not href.startswith("//") and not href.startswith("/static/")


def reescrever(html: str, url_pagina: str, fila: list[str], vistos: set[str]) -> str:
    talentos_pagina = parse_qs(urlsplit(url_pagina).query).get("talentos", [None])[0]

    def troca(m):
        atrib, href = m.group(1), m.group(2)
        tag = m.group(0)
        if href.startswith("/static/"):
            return f'{atrib}="{href.removeprefix("/").split("?")[0]}"'
        if not interno(href):
            return tag
        absoluto = urljoin(url_pagina, href)
        # links que levam o filtro de talentos (data-filtro-talentos) recebem o filtro da página atual
        if talentos_pagina and talentos_pagina != "todos" and "talentos=" not in absoluto and m.group(3):
            u = urlsplit(absoluto)
            sep = "&" if u.query else ""
            absoluto = u._replace(query=f"{u.query}{sep}talentos={talentos_pagina}").geturl()
        sem_hash = absoluto.split("#")[0]
        if sem_hash not in vistos:
            vistos.add(sem_hash)
            fila.append(sem_hash)
        arq, hash_ = nome_arquivo(absoluto)
        return f'{atrib}="{arq}{hash_}"'

    # atributo href/src/action + (opcionalmente) a marca data-filtro-talentos na mesma tag, capturada antes do atributo
    padrao = re.compile(r'(?:(data-filtro-talentos)\s+)?\b(href|src|action)="([^"]*)"')

    def troca2(m):
        marca, atrib, href = m.group(1), m.group(2), m.group(3)
        # reaproveita a lógica acima com o grupo da marca
        class M:  # pequeno adaptador para troca()
            def group(self, i):
                return {0: m.group(0), 1: atrib, 2: href, 3: marca}[i]
        return troca(M())

    # 1ª passada: tags com a marca antes do href; 2ª: tags com a marca depois do href
    html = padrao.sub(troca2, html)
    html = re.sub(r'\b(href)="([^"]*)"(\s+[^>]*?)?\s+data-filtro-talentos',
                  lambda m: troca(type("M", (), {"group": lambda s, i: {0: m.group(0), 1: m.group(1), 2: m.group(2), 3: "x"}[i]})())
                  + (m.group(3) or ""), html)
    html = html.replace(" data-filtro-talentos", "")
    # fora do servidor: sem sincronização com a cola, sem checagem de nova carga, extrato por recarga da página
    html = re.sub(r'<script src="static/sinc\.js[^"]*"></script>\s*', "", html)
    html = re.sub(r'<meta name="relatorio-(versao|intervalo)" content="[^"]*">\s*', "", html)
    html = html.replace(" data-caixa-troca", "")
    return html


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    if (SAIDA / "static").exists():
        shutil.rmtree(SAIDA / "static")
    shutil.copytree(ESTATICOS, SAIDA / "static", ignore=shutil.ignore_patterns("sinc.js", "__pycache__"))
    css = (SAIDA / "static" / "estilo.css").read_text(encoding="utf-8")
    (SAIDA / "static" / "estilo.css").write_text(css.replace('url("/static/', 'url("'), encoding="utf-8", newline="")
    inicio = f"{BASE}{AREA}/capa"
    fila, vistos, gravados = [inicio], {inicio}, {}
    while fila:
        url = fila.pop(0)
        r = requests.get(url, allow_redirects=True, timeout=120)
        if r.status_code != 200:
            print("  pulado", url, r.status_code)
            continue
        final = r.url if urlsplit(r.url).path != urlsplit(url).path else url
        html = reescrever(r.text, url, fila, vistos)
        arq, _ = nome_arquivo(url)
        (SAIDA / arq).write_text(html, encoding="utf-8", newline="")
        gravados[arq] = url
        print(f"  {arq:40s} <- {url.removeprefix(BASE)}")
    shutil.copy(SAIDA / "capa.html", SAIDA / "index.html")
    # conferência: todo link interno aponta para um arquivo que existe
    faltam = set()
    for arq in SAIDA.glob("*.html"):
        for h in re.findall(r'href="([a-z0-9-]+\.html)', arq.read_text(encoding="utf-8")):
            if not (SAIDA / h).exists():
                faltam.add(h)
    print(f"\n{len(gravados)} páginas em {SAIDA}")
    print("links sem arquivo:", sorted(faltam) or "nenhum")


if __name__ == "__main__":
    main()
