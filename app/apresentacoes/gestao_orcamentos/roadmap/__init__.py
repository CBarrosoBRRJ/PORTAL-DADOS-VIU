"""Roadmap da área (V2, Caio, 31/10/2026): a tela que abre a reunião e serve de hub de navegação.

5ª versão, "a linha do tempo linear em Y" (as anteriores estão em _descartados/2026-10-31/roadmap_v4/, roadmap_v3/,
roadmap_colorido/ e _descartados/2026-10-30/roadmap_diagonal/). Referência do Caio: uma linha horizontal fina, textos
curtos acima e abaixo, muito branco. Estrutura (Caio, 31/10/2026):

    01 Dados espalhados ─ 02 Mapeamos ─┬─ 04 Pedimos à TI ┄┄┄┄┄┄ Aguardando ┄┄┄┄┄┄ 05 Infraestrutura liberada ─┐
                                       └──────────── 03 Criação de dashboards (começou antes) ─────────────────┴─
    ─ 06 Centralizamos no BigQuery ─┬── 08 Dashboards: desenvolvimento e melhoria contínua ┄┄┄┄┄┄┄┄┄┄ ›
                         ↖ retroalimenta  ↑ estudo vira dashboard
                                    └── 07 Análises e estudos (você está aqui; botões por categoria) ┄┄┄┄┄┄┄┄┄ ›

Três trilhos horizontais: o principal ao centro e os ramos acima e abaixo, com o mesmo espaçamento; as junções são
curvas curtas e suaves. Depois do BigQuery, os dois trilhos seguem até a borda, sem nó final (trabalho contínuo). A
linha é cheia até os nós de agora e tracejada depois. Duas ligações pontilhadas finas mostram a retroalimentação.

Para mudar textos, imagens ou botões, edite só este arquivo. Uma página nova entra com uma linha em "botoes" (e, se for
o caso, uma categoria nova em CATEGORIAS).

PASSOS é a sequência da esquerda para a direita: nós do tronco e bifurcações ({"ramos": (...), "peso": ...}). A
bifurcação volta ao tronco no nó seguinte; a última fica aberta (os ramos seguem até a borda). "peso" é a largura
relativa de cada passo (padrão 1), para o desenho respirar onde precisa.

Regra do texto (Caio, 31/10/2026): nó do ramo de cima → texto acima da linha; nó do ramo de baixo → texto abaixo; nós
do tronco alternam, começando por cima; se o lado da vez bater num título de ramo, o nó do tronco vai para o outro lado
(hoje: 01 acima, 02 abaixo, 06 abaixo, porque acima dele está o 05). Número e nome ficam centrados no eixo do nó, numa
largura padrão (TITULO), e os títulos de cada lado formam uma fileira (mesma base acima, mesmo topo abaixo). Miniaturas
e chips ficam no mesmo eixo; os botões, presos ao nó, começam junto dele.

Campos de cada nó: chave, titulo (curto), texto (UMA frase curta), icone (de templates/icones.html; cada um tem o seu
gesto no CSS), situacao (texto para o leitor de tela); soltos (chips (nome, tom)); registros (imagens: miniatura junto
do nó, pilha quando há duas ou mais; <nome>-mini.webp, <nome>.webp e, se existir, <nome>-alta.webp em
app/static/roadmap/); pos (posição no ramo: 0 = logo depois da curva de abertura, 1 = logo antes da curva de volta);
titulo_larg (largura do título, se precisar ser menor que TITULO); dy (deslocamento vertical do nó, em em: os nós não precisam ficar todos na
mesma altura; a linha acompanha com curvas suaves e o texto acompanha o nó); larg (largura do texto em colunas; padrão 1); espera (rótulo do trecho âmbar até o
nó seguinte do ramo); aqui (o "Você está aqui"); botoes ({"rotulo", "linha", "icone", "categoria", "href"} e,
opcional, "proximo": True); mostrar (False tira o nó da tela, sem apagar daqui).

Geometria (em em, a mesma do bloco .rm-* do CSS): palco de 73 × 28 em; a posição (--x) e a largura do texto (--w)
de cada nó vão para o <style> com nonce da página (a CSP proíbe style=""). O SVG tem viewBox 730 × 280 (0,1 em).
"""
import itertools
from pathlib import Path

from app.apresentacoes.gestao_orcamentos import SLUG

PASTA_IMAGENS = Path(__file__).resolve().parents[3] / "static" / "roadmap"

SITUACOES = {  # situação -> texto para o leitor de tela
    "feito": "Etapa concluída",
    "em_curso": "Em curso, contínuo",
    "aqui": "Em curso, contínuo: você está aqui",
}

# categorias dos botões: no máximo três tons suaves (classe rm-cat-<tom> do CSS); a forma do ícone muda por categoria
CATEGORIAS = {
    "analises": {"rotulo": "Análises", "tom": "azul", "forma": "circulo"},
    "automacao": {"rotulo": "Automação e IA", "tom": "roxo", "forma": "quadrado"},
    "projecoes": {"rotulo": "Projeções", "tom": "verde", "forma": "gota"},
}

FLUXO = {"titulo": "Fluxo ponta a ponta", "imagem": "fluxo-processo",
         "alt": "Fluxo da área em raias: entrada do pedido e orçamento, execução, pagamento, contratos e aquisição de talentos",
         "legenda": "Do pedido à proposta, à execução, ao contrato e ao pagamento, com os pontos de atenção marcados."}
# Caio, 03/11/2026: imagens sem desfoque (dados internos da equipe; tools/gerar_imagens_roadmap.py, DESFOCAR)
DASHBOARDS = (
    {"titulo": "Controle do processo de pagamento", "imagem": "dashboard-pagamento",
     "alt": "Painel de controle do processo de pagamento",
     "legenda": "Volume de pagamentos, notas fiscais e SLA, e a matriz de risco financeiro."},
    {"titulo": "Contratos e bloqueios", "imagem": "dashboard-contratos",
     "alt": "Painel de contratos e bloqueios dos talentos",
     "legenda": "Contratos vigentes, renovações e a linha do tempo dos contratos."},
    # Caio, 03/11/2026: o Raio-X saiu daqui (foi para o card Raio-X das Iniciativas) e entrou a Central de qualidade
    {"titulo": "Central de qualidade", "imagem": "dashboard-qualidade",
     "alt": "Painel Central de qualidade do Backlog: erros registrados, correções da MIA e pendências em aberto por semana",
     "legenda": "Erros de preenchimento do Backlog por semana, o que a MIA corrigiu e as pendências em aberto."},
    {"titulo": "Central de qualidade: e-mail da MIA", "imagem": "dashboard-qualidade-email",
     "alt": "E-mail semanal da MIA com o resumo da qualidade de dados do Backlog: erros mapeados, corrigidos e em aberto",
     "legenda": "O alerta semanal da MIA: erros mapeados, o que ela corrigiu e o que falta ajustar no monday."},
)
BIGQUERY = {"titulo": "Camada ouro no BigQuery", "imagem": "bigquery",
            "alt": "Camada ouro no BigQuery: tabelas e views do dataset gold_monday",
            "legenda": "O dataset gold_monday: as tabelas e views da camada ouro que este portal lê."}

# a história em sequência (narrativa e estrutura do Caio, 31/10/2026)
PASSOS = (
    {"chave": "espalhados", "titulo": "Dados espalhados", "icone": "dispersos", "situacao": "feito", "peso": 0.9,
     # chips das fontes (nome, tom): cada um num tom pastel que lembra a ferramenta, sem logo (Caio, 31/10/2026).
     # "Req2Pay" = o relatório de pagamentos do PDF do mapeamento (o Caio falou "Hack to Pay"; nome confirmado por ele)
     "soltos": (("SharePoint", "sharepoint"), ("Excel", "excel"), ("Monday", "monday"), ("OneNote", "onenote"),
                ("Salesforce", "salesforce"), ("API", "api"), ("Req2Pay", "req2pay"))},
    {"chave": "mapa", "titulo": "Mapeamos e organizamos", "icone": "fluxo", "situacao": "feito", "peso": 0.75, "dy": 1.2,
     "titulo_larg": 7.6,  # título mais estreito: à esquerda dele ficam os chips do 01
     "registros": (FLUXO,)},
    {"peso": 2.5, "ramos": (
        {"lado": "baixo", "nos": (
            {"chave": "dashboards", "titulo": "Criação de dashboards", "icone": "grafico", "situacao": "feito", "pos": 0.5, "dy": -0.7, "alinhar": "centro", "larg": 1.6,
             "registros": DASHBOARDS},
        )},
        {"lado": "cima", "nos": (
            {"chave": "ti", "titulo": "Pedimos a infraestrutura à TI", "icone": "ampulheta", "situacao": "feito", "espera": "Aguardando", "pos": 0.0},
            {"chave": "liberada", "titulo": "Infraestrutura liberada", "icone": "ok", "situacao": "feito",
             "pos": 1.0, "alinhar": "fim"},
        )},
    )},
    {"chave": "centralizar", "titulo": "Centralizamos no BigQuery", "icone": "banco", "situacao": "feito", "peso": 1.0, "dy": -0.5,
     "registros": (BIGQUERY,)},
    {"peso": 2.6, "ramos": (
        {"lado": "baixo", "nos": (
            {"chave": "estudos", "titulo": "Análises e estudos", "icone": "tendencia", "situacao": "aqui", "aqui": True,
             "pos": 0.2, "larg": 2.6,
             "botoes": (
                 {"rotulo": "Demanda", "linha": "Pedidos de orçamento em 2026", "icone": "entrada",
                  "categoria": "analises", "href": f"/{SLUG}"},
                 {"rotulo": "SLA", "linha": "Tempo até a entrega do orçamento", "icone": "relogio",
                  "categoria": "analises", "href": f"/{SLUG}/sla#1"},
                 {"rotulo": "LIA", "linha": "E-mails que a LIA já leu", "icone": "envelope",
                  "categoria": "automacao", "href": f"/{SLUG}/lia#1"},
                 {"rotulo": "Iniciativas", "linha": "Automação e IA em andamento", "icone": "faisca",
                  "categoria": "automacao", "href": f"/{SLUG}/iniciativas#1", "proximo": True},
                 {"rotulo": "Previsão", "linha": "Pedidos esperados até o fim do ano", "icone": "tendencia",
                  "categoria": "projecoes", "href": f"/{SLUG}/previsao#1", "proximo": True},
                 # Caio, 04/11/2026: a página Talentos saiu da sequência, mas o botão fica, por último (o último das Análises)
                 {"rotulo": "Talentos", "linha": "Exclusivos e não exclusivos", "icone": "pessoas",
                  "categoria": "analises", "href": f"/{SLUG}/talentos#1"},
             )},
        )},
        {"lado": "cima", "nos": (
            {"chave": "evolucao", "titulo": "Novos dashboards e melhorias", "icone": "lapis", "situacao": "em_curso",
             "pos": 0.2, "larg": 2.0},
        )},
    )},
)

# frases de apoio sob os títulos: retiradas a pedido do Caio (31/10/2026); cada nó fica só com número e título (os
# textos antigos estão na ficha docs/paginas/roadmap.md). O campo "texto" continua aceito, para uso futuro.

# rótulo do fim dos trilhos contínuos (sem nó de chegada)
CONTINUO = "Evolução contínua"

# retroalimentação (pontilhada): do nó "de" ao nó "para", com um rótulo curto
RETROS = (
    {"de": "estudos", "para": "centralizar", "rotulo": "retroalimenta a base"},
    {"de": "estudos", "para": "evolucao", "rotulo": "estudo vira dashboard"},
)

# Geometria em em (a mesma do CSS, bloco .rm-*). Palco de 73 × 28 em; SVG com viewBox 730 × 280.
LARGURA, ALTURA = 73.0, 28.0
VAO = 1.2              # vão entre os passos
RAIO = 1.15            # raio do círculo (a borda esquerda do círculo é a borda esquerda do nó)
LINHA = 9.3            # y do trilho principal
DESVIO = 2.9           # distância dos ramos de cima e de baixo ao trilho principal
CURVA = 3.0            # largura das curvas das junções (suaves, sem leque)
FOLGA = 0.25           # distância entre o círculo e o início da curva
PONTA = 0.7            # os trilhos abertos param 0,7 em antes da borda, onde fica a seta
TITULO = 9.8           # largura padrão do bloco do título (número + nome), centrado no nó
MARGEM_TEXTO = 2.4     # quanto um título pode passar da borda do palco (o painel tem respiro interno)
TRILHOS = {"cima": -DESVIO, "meio": 0.0, "baixo": DESVIO}


_tamanhos: dict = {}


def _tamanho(arquivo: Path):
    """(largura, altura) de um PNG ou WebP lido do cabeçalho; None se o arquivo faltar ou o formato for outro.
    Desempenho (31/10/2026): lê só os 30 bytes do cabeçalho (antes, o arquivo inteiro a cada página) e guarda o tamanho
    por processo (no Google Drive, abrir os 12 arquivos custava ~65 ms por página). Trocou uma imagem no computador?
    Reinicie o servidor (o --reload só vê .py)."""
    if arquivo in _tamanhos:
        return _tamanhos[arquivo]
    try:
        with open(arquivo, "rb") as f:
            b = f.read(30)
    except OSError:
        return None
    _tamanhos[arquivo] = _cabecalho(b)
    return _tamanhos[arquivo]


def _cabecalho(b: bytes):
    if b[:8] == bytes.fromhex("89504e470d0a1a0a"):
        return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        tipo = b[12:16]
        if tipo == b"VP8X":
            return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
        if tipo == b"VP8 ":
            return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
        if tipo == b"VP8L":
            n = int.from_bytes(b[21:25], "little")
            return (n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1
    return None


def _versionado(arquivo: str) -> str:
    """Caio, 03/11/2026: endereço da imagem do painel com a versão do arquivo (tamanho e data). A galeria abre a imagem
    grande pelo JSON, sem o ?v= da página; o navegador guardava a cópia antiga por um dia (as desfocadas continuavam
    aparecendo depois de trocadas)."""
    info = (PASTA_IMAGENS / arquivo).stat()
    return f"/static/roadmap/{arquivo}?v={info.st_size:x}{info.st_mtime_ns // 1_000_000_000:x}"


def _registro(r: dict):
    """Imagem pronta para a miniatura e o painel (caminhos e tamanhos); None se algum arquivo faltar."""
    nome = r.get("imagem") or ""
    mini = _tamanho(PASTA_IMAGENS / f"{nome}-mini.webp") if nome else None
    grande = _tamanho(PASTA_IMAGENS / f"{nome}.webp") if nome else None
    if not (mini and grande):
        return None
    alta = _tamanho(PASTA_IMAGENS / f"{nome}-alta.webp")
    return {"titulo": r["titulo"], "legenda": r.get("legenda", ""), "alt": r["alt"], "imagem": nome,
            "mini": f"/static/roadmap/{nome}-mini.webp", "mw": mini[0], "mh": mini[1],
            "src": _versionado(f"{nome}.webp"), "w": grande[0], "h": grande[1],
            "alta": _versionado(f"{nome}-alta.webp" if alta else f"{nome}.webp"),
            "aw": (alta or grande)[0], "ah": (alta or grande)[1]}


def _u(em: float) -> str:
    """em → unidade do SVG (0,1 em), sem zeros inúteis."""
    return f"{round(em * 10, 1):g}"


def _visiveis(passos) -> list:
    """Aplica mostrar=False; bifurcação sem ramos some; com um ramo só, os nós dele voltam ao tronco."""
    saida = []
    for p in passos:
        if "ramos" not in p:
            if p.get("mostrar", True):
                saida.append(dict(p))
            continue
        ramos = [{**r, "nos": [dict(n) for n in r["nos"] if n.get("mostrar", True)]} for r in p["ramos"]]
        ramos = [r for r in ramos if r["nos"]]
        if len(ramos) == 1:
            for no in ramos[0]["nos"]:
                for k in ("pos", "alinhar"):
                    no.pop(k, None)
                saida.append({**no, "peso": p.get("peso", 1.0) / len(ramos[0]["nos"])})
        elif ramos:
            saida.append({**p, "ramos": ramos})
    return saida


def _ponto(seg, t):
    if seg[0] == "H":
        return seg[1] + (seg[2] - seg[1]) * t, seg[3]
    _, x0, y0, x1, y1 = seg
    c = (x1 - x0) / 2
    pts = ((x0, y0), (x0 + c, y0), (x0 + c, y1), (x1, y1))
    w = ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3)
    return sum(p[0] * k for p, k in zip(pts, w)), sum(p[1] * k for p, k in zip(pts, w))


def _comprimento(seg) -> float:
    """Comprimento (em) de um trecho: ("H", x0, x1, y) ou ("C", x0, y0, x1, y1) (curva em S)."""
    if seg[0] == "H":
        return abs(seg[2] - seg[1])
    total, ant = 0.0, _ponto(seg, 0)
    for k in range(1, 41):
        p = _ponto(seg, k / 40)
        total += ((p[0] - ant[0]) ** 2 + (p[1] - ant[1]) ** 2) ** 0.5
        ant = p
    return total


def _d(segs) -> str:
    """Trechos → atributo d do SVG (um M novo sempre que o trecho não continua o anterior)."""
    partes, fim = [], None
    for s in segs:
        ini = (s[1], s[3]) if s[0] == "H" else (s[1], s[2])
        if fim is None or abs(fim[0] - ini[0]) > 1e-6 or abs(fim[1] - ini[1]) > 1e-6:
            partes.append(f"M {_u(ini[0])} {_u(LINHA + ini[1])}")
        if s[0] == "H":
            partes.append(f"H {_u(s[2])}")
            fim = (s[2], s[3])
        else:
            _, x0, y0, x1, y1 = s
            c = (x1 - x0) / 2
            partes.append(f"C {_u(x0 + c)} {_u(LINHA + y0)}, {_u(x0 + c)} {_u(LINHA + y1)}, {_u(x1)} {_u(LINHA + y1)}")
            fim = (x1, y1)
    return " ".join(partes)


def _seta(x, y, para="direita", t=0.55):
    """Ponta de seta (em em) com a ponta em (x, y)."""
    if para == "direita":
        return f"M {_u(x - t)} {_u(y - t)} L {_u(x)} {_u(y)} L {_u(x - t)} {_u(y + t)}"
    if para == "esquerda":
        return f"M {_u(x + t)} {_u(y - t)} L {_u(x)} {_u(y)} L {_u(x + t)} {_u(y + t)}"
    return f"M {_u(x - t)} {_u(y + t)} L {_u(x)} {_u(y)} L {_u(x + t)} {_u(y + t)}"  # para cima


def _liga(pontos):
    """Pontos (x, y) → trechos: reto quando a altura não muda; senão uma curva em S de largura CURVA (ou menor, se não
    couber), centrada entre os dois pontos."""
    segs = []
    for (x0, y0), (x1, y1) in itertools.pairwise(pontos):
        if x1 - x0 <= 1e-6:
            continue
        if abs(y1 - y0) < 1e-6:
            segs.append(("H", x0, x1, y0))
            continue
        c = min(CURVA, x1 - x0)
        m0 = (x0 + x1) / 2 - c / 2
        if m0 > x0 + 1e-6:
            segs.append(("H", x0, m0, y0))
        segs.append(("C", m0, y0, m0 + c, y1))
        if x1 > m0 + c + 1e-6:
            segs.append(("H", m0 + c, x1, y1))
    return segs


def _tempo_pulso(f, ini=None, fim=None):
    """Fração do ciclo (0 a 0,9) em que a cabeça do pulso passa pela fração f da rota; no trecho [ini, fim] (a espera)
    o pulso anda a 1/3 da velocidade."""
    def g(v):
        return v + (2 * max(0.0, min(v, fim) - ini) if ini is not None else 0.0)
    return 0.9 * g(f) / g(1.0)


def tela() -> dict:
    passos = _visiveis(PASSOS)
    pesos = [float(p.get("peso", 1.0)) for p in passos]
    unidade = (LARGURA - (len(passos) - 1) * VAO) / max(sum(pesos), 1e-6)  # largura de um passo de peso 1
    esquerdas, x = [], 0.0
    for w in pesos:
        esquerdas.append(x)
        x += w * unidade + VAO

    # 1º: nós do tronco (posição = início do passo; texto alternando, começando por cima)
    nos, tronco = [], []
    for k, p in enumerate(passos):
        if "ramos" not in p:
            no = {**p, "trilho": "meio", "passo_i": k, "esq": esquerdas[k],
                  "lado": "acima" if len(tronco) % 2 == 0 else "abaixo"}
            tronco.append(no)
            nos.append(no)

    def cx(no):
        return no["esq"] + RAIO

    def cy(no):  # altura do nó, relativa ao tronco (trilho + deslocamento vertical "dy")
        return TRILHOS[no["trilho"]] + float(no.get("dy", 0.0))

    # 2º: ramos das bifurcações, posicionados entre as curvas de abertura e de volta
    blocos = []
    for k, p in enumerate(passos):
        if "ramos" not in p:
            blocos.append(("no", next(no for no in tronco if no["passo_i"] == k)))
            continue
        ant = next((no for no in reversed(tronco) if no["passo_i"] < k), None)
        prox = next((no for no in tronco if no["passo_i"] > k), None)
        x_ini = cx(ant) if ant else 0.0
        a = x_ini + RAIO + FOLGA
        z = (cx(prox) - RAIO - FOLGA) if prox else LARGURA - PONTA
        ini_plano, fim_plano = a + CURVA, (z - CURVA) if prox else z
        ramos = []
        for ordem, r in enumerate(p["ramos"]):
            lista = []
            for no in r["nos"]:
                f = float(no.get("pos", 0.0))
                centro = ini_plano + RAIO + f * max(fim_plano - ini_plano - 2 * RAIO, 0.0)
                lista.append({**no, "trilho": r["lado"], "passo_i": k, "esq": centro - RAIO, "ordem_ramo": ordem,
                              "lado": "acima" if r["lado"] == "cima" else "abaixo"})
            nos.extend(lista)
            ramos.append({"lado": r["lado"], "nos": lista})
        blocos.append(("ramos", {"ramos": ramos, "ant": ant, "a": a, "z": z, "prox": prox}))

    # numeração: na ordem dos passos; dentro de uma bifurcação, ramo a ramo, na ordem do catálogo (o ramo de baixo da
    # 1ª bifurcação começou antes: 03), e no ramo, da esquerda para a direita
    nos.sort(key=lambda no: (no["passo_i"], no.get("ordem_ramo", 0), round(no["esq"], 3)))
    aqui = next((no for no in nos if no.get("aqui")), None)
    x_aqui = cx(aqui) if aqui else LARGURA + 1

    # títulos (Caio, 31/10/2026): número e nome centrados juntos no eixo do nó, numa largura padrão (TITULO, quebra
    # equilibrada em até 2 linhas), encolhida por igual dos dois lados se encostar no título vizinho do mesmo lado.
    # Nó do tronco cujo lado (pela alternância) bate num título de ramo vai para o outro lado, se lá houver espaço.
    def folga(no, lado):  # distância ao título de ramo mais próximo daquele lado
        return min([abs(cx(m) - cx(no)) for m in nos if m is not no and m["lado"] == lado and m["trilho"] != "meio"]
                   + [LARGURA])

    for no in nos:
        outro = "abaixo" if no["lado"] == "acima" else "acima"
        if no["trilho"] == "meio" and folga(no, no["lado"]) < TITULO + 0.9 and folga(no, outro) > folga(no, no["lado"]):
            no["lado"] = outro
    for no in nos:
        vizinhos = [abs(cx(m) - cx(no)) for m in nos if m is not no and m["lado"] == no["lado"]]
        meia = min([float(no.get("titulo_larg", TITULO)) / 2] + [d / 2 - 0.45 for d in vizinhos])
        meia = max(min(meia, cx(no) + MARGEM_TEXTO, LARGURA + MARGEM_TEXTO - cx(no)), 2.5)
        no.update(texto_ini=cx(no) - meia, texto_w=2 * meia, alinhar="centro")

    for i, no in enumerate(nos):
        botoes = []
        for b in no.get("botoes", ()):
            cat = CATEGORIAS[b["categoria"]]
            botoes.append({**b, "tom": cat["tom"], "forma": cat["forma"]})
        grupos = []
        for chave, cat in CATEGORIAS.items():
            dela = [b for b in botoes if b["categoria"] == chave]
            if dela:
                grupos.append({"chave": chave, **cat, "botoes": dela})
        no.update(indice=i, numero=f"{i + 1:02d}", x=round(cx(no), 3), rotulo_sit=SITUACOES[no["situacao"]],
                  aqui=no is aqui, futuro=False, galeria=tuple(x for x in (_registro(r) for r in no.get("registros", ())) if x),
                  soltos=tuple(no.get("soltos", ())), botoes=tuple(botoes), categorias=tuple(grupos),
                  css_x=round(no["esq"], 2), css_t=round(no["texto_ini"] - no["esq"], 2), css_w=round(no["texto_w"], 2),
                  css_dy=round(float(no.get("dy", 0.0)), 2))

    # trechos de linha: (estilo, trecho). "feito" (cheia), "espera" (âmbar, do nó com espera ao seguinte do ramo) ou
    # "futuro" (tracejada, depois dos nós de agora). Os círculos (fundo branco) cobrem a linha sob eles.
    trechos, rotas, ultimo, setas = [], [[]], None, []

    def estilo(x0, no_ini=None):
        if no_ini is not None and no_ini.get("espera"):
            return "espera"
        return "futuro" if x0 >= x_aqui - 1e-6 else "feito"

    def soma(pontos, donos, rotas_alvo):
        """Liga os pontos; donos[i] = o nó de onde sai o trecho i (para a espera); devolve os trechos."""
        saida = []
        for i, ((x0, y0), (x1, y1)) in enumerate(itertools.pairwise(pontos)):
            for s in _liga([(x0, y0), (x1, y1)]):
                trechos.append((estilo(s[1], donos[i]), s))
                saida.append(s)
        for r in rotas_alvo:
            r.extend(saida)
        return saida

    for tipo, b in blocos:
        if tipo == "no":
            ini = (cx(ultimo), cy(ultimo)) if ultimo else (0.0, cy(b))
            soma([ini, (cx(b), cy(b))], [ultimo], rotas)
            ultimo = b
            continue
        ant, a, z, prox = b["ant"], b["a"], b["z"], b["prox"]
        y_ant = cy(ant) if ant else 0.0
        por_lado = {}
        for r in b["ramos"]:
            dy = TRILHOS[r["lado"]]
            pontos, donos = [(cx(ant) if ant else 0.0, y_ant), (a, y_ant), (a + CURVA, dy)], [None, None]
            no_ant = None
            for no in r["nos"]:
                pontos.append((cx(no), cy(no)))
                donos.append(no_ant)
                no_ant = no
            if prox:
                pontos += [(z - CURVA, dy), (z, cy(prox)), (cx(prox), cy(prox))]
                donos += [no_ant, None, None]
            else:  # trilho aberto: segue até a borda, com a seta
                y_fim = cy(no_ant) if no_ant else dy
                pontos.append((z, y_fim))
                donos.append(no_ant)
                setas.append(_seta(LARGURA - 0.1, LINHA + y_fim, "direita", 0.45))
            por_lado[r["lado"]] = soma(pontos, donos, [])
        if len(rotas) == 1:
            rotas = [list(rotas[0]), list(rotas[0])]
        unico = next(iter(por_lado.values()))
        rotas[0].extend(por_lado.get("cima", unico))
        rotas[1].extend(por_lado.get("baixo", unico))
        ultimo = prox if prox is not None else ultimo
    if blocos and blocos[-1][0] == "no":  # termina num nó do tronco: a linha segue até a borda, com a seta
        soma([(cx(ultimo), cy(ultimo)), (LARGURA - PONTA, cy(ultimo))], [None], rotas)
        setas.append(_seta(LARGURA - 0.1, LINHA + cy(ultimo), "direita", 0.45))
    for no in nos:  # nó depois dos de agora = futuro
        no["futuro"] = cx(no) > x_aqui + 1e-6
        if no.get("espera"):
            seguinte = next((m for m in nos if m["trilho"] == no["trilho"] and m["passo_i"] == no["passo_i"]
                             and m["esq"] > no["esq"]), None)
            no["css_e"] = round((cx(seguinte) - cx(no)) / 2, 2) if seguinte else 0.0

    linhas = {e: _d([s for est, s in trechos if est == e]) for e in ("feito", "espera", "futuro")}
    esperas = [s for est, s in trechos if est == "espera"]

    # pulso: uma rota por ramo; as marcas (fração da rota) de cada nó e da espera dão o tempo da reação de cada ícone
    pulsos = []
    for k_rota, r in enumerate(rotas):
        total = sum(_comprimento(s) for s in r)
        p, acum, marcas = {"d": _d(r), "comprimento": round(total, 2)}, 0.0, {}
        for s in r:
            if s in esperas and "espera_ini" not in p:
                p["espera_ini"], p["espera_fim"] = round(acum / total, 3), round((acum + _comprimento(s)) / total, 3)
            acum += _comprimento(s)
            fim = (s[2], s[3]) if s[0] == "H" else (s[3], s[4])
            for no in nos:
                if no["chave"] not in marcas and abs(cx(no) - fim[0]) < 1e-6 and abs(cy(no) - fim[1]) < 1e-6:
                    marcas[no["chave"]] = round(acum / total, 3)
        p["marcas"] = marcas
        if aqui is not None and aqui["chave"] in marcas:
            p["aqui"] = marcas[aqui["chave"]]
        pulsos.append(p)
    # quadros-chave do pulso (no <style> com nonce, sincronizados com a geometria) e o atraso da reação de cada nó
    CICLO, ATRASO = 9.0, 1.1
    quadros = []
    for k_rota, p in enumerate(pulsos):
        ini, fim = p.get("espera_ini"), p.get("espera_fim")
        partes = ["0% { stroke-dashoffset: 30; opacity: 0; }", "3% { opacity: 1; }"]
        if ini is not None:
            partes += [f"{_tempo_pulso(ini, ini, fim) * 100:.1f}% {{ stroke-dashoffset: {30 - round(ini * 1000)}; }}",
                       f"{_tempo_pulso(fim, ini, fim) * 100:.1f}% {{ stroke-dashoffset: {30 - round(fim * 1000)}; }}"]
        partes += ["90% { stroke-dashoffset: -970; opacity: 1; }", "94%, 100% { stroke-dashoffset: -970; opacity: 0; }"]
        quadros.append(f"@keyframes rm-anda-{k_rota + 1} {{ {' '.join(partes)} }}")
    for no in nos:
        k_rota = 1 if (no["trilho"] == "baixo" and len(pulsos) > 1) else 0
        p = pulsos[k_rota]
        f = p["marcas"].get(no["chave"])
        no["css_pulso"] = (round(ATRASO + CICLO * _tempo_pulso(f, p.get("espera_ini"), p.get("espera_fim")), 2)
                           if f is not None else None)

    # retroalimentação (pontilhada): de volta ao tronco, pela abertura do Y; ou de um ramo ao outro, por uma curva suave
    por_chave = {no["chave"]: no for no in nos}
    retros = []
    for rt in RETROS:
        de, para = por_chave.get(rt["de"]), por_chave.get(rt["para"])
        if not (de and para):
            continue
        y0, y1 = LINHA + cy(de), LINHA + cy(para)
        if para["trilho"] == "meio":  # volta ao nó do tronco: termina dentro da abertura do Y, apontando para ele
            xa, ya = de["esq"] - 0.35, y0 - 0.45
            xb, yb = cx(para) + RAIO + FOLGA + CURVA * 0.75, y1
            d = (f"M {_u(xa)} {_u(ya)} C {_u(xa - 2.4)} {_u(ya)}, {_u(xb + 2.2)} {_u(yb)}, {_u(xb)} {_u(yb)}")
            retros.append({**rt, "d": d, "seta": _seta(xb, yb, "esquerda", 0.32), "tipo": "volta",
                           "x": round(xb + 0.9, 2), "y": round(yb - 0.95, 2)})
        else:  # de um ramo ao outro: sai do lado do nó e sobe em curva suave até o outro trilho
            xa, ya = cx(de) + RAIO + 0.45, y0
            xb, yb = cx(de) + RAIO + 6.4, y1 + 0.55
            d = f"M {_u(xa)} {_u(ya)} C {_u(xa + 4.2)} {_u(ya)}, {_u(xb)} {_u(ya - 1.2)}, {_u(xb)} {_u(yb)}"
            retros.append({**rt, "d": d, "seta": _seta(xb, yb, "cima", 0.32), "tipo": "lado",
                           "x": round(xb + 0.55, 2), "y": round((ya + yb) / 2 - 1.0, 2)})

    return {"marcos": nos, "n": len(passos), "viewbox": f"0 0 {_u(LARGURA)} {_u(ALTURA)}",
            "unidade": round(unidade, 3), "esquerdas": tuple(round(e, 3) for e in esquerdas),
            "linhas": linhas, "pulsos": pulsos, "quadros": tuple(quadros), "setas": tuple(setas),
            "retros": tuple(retros), "aqui": aqui, "categorias": CATEGORIAS, "continuo": CONTINUO if setas else ""}
