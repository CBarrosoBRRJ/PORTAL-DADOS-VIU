"""Movimento do portal (batalha 2, 2ª leva, 26/10/2026): a D46 vale para todas as páginas, não só para o estudo.

Regras verificáveis no CSS, no JS e nos templates: números prontos desde o 1º quadro (nenhum data-contar, nenhuma
contagem no JS); nenhuma curva com ressalto (cubic-bezier com y fora de [0, 1]) nem loop; cada animação/transição de
entrada (.entrou) das páginas termina em até 1,2 s (contando a onda até o 12º mês); navegação sem brilho, pílula
"líquida" ou aba que sobe; impressão parada; a página revisitada pelo seletor de talentos aparece pronta (.revisto).
O estudo "Como medimos" tem os testes próprios em test_sla_movimento.py.

Exceção explícita D51 (26/10/2026, Caio): só na página Talentos, a barra do ano conta de 0 ao valor e o mapa roda a
"corrida do ano" (bloco "D51" de apresentacao.js e de estilo.css; testes em test_talentos_d51.py). Fora desse bloco,
a regra dos números prontos continua valendo e é conferida aqui.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSS = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
JS = (RAIZ / "app" / "static" / "apresentacao.js").read_text(encoding="utf-8")
# tudo antes do bloco D46 do estudo (que tem testes próprios)
PORTAL = re.sub(r"/\*.*?\*/", "", CSS[:CSS.index('/* ---------- D46 (25/10/2026): movimento do estudo "Como medimos"')], flags=re.S)
TEMPOS = {"--dur-xs": 120, "--dur-s": 180, "--dur-m": 320, "--dur-l": 520, "--dur-xl": 800, "--passo": 35,
          "--atraso-dados": 160}
ONDA = {"--i": 11, "--k": 14}  # 12 meses (0..11); linhas do extrato até 14


def _ms(expr: str, onda: dict | None = None) -> float:
    """Tempo em ms de um valor CSS (número com ms/s, var(--dur-*), calc com var(--i) no pior caso)."""
    onda = onda or ONDA
    e = re.sub(r"var\((--[\w-]+)(?:,[^)]*)?\)",
               lambda m: f"{TEMPOS[m.group(1)]}ms" if m.group(1) in TEMPOS else str(onda[m.group(1)]), expr)
    e = re.sub(r"(\d*\.?\d+)ms", r"(\1)", e)
    e = re.sub(r"(\d*\.?\d+)s\b", r"(\1*1000)", e).replace("calc", "")
    assert re.fullmatch(r"[\d.()*+\-/ ]+", e), expr
    return float(eval(e))  # noqa: S307 — expressão já restrita a números e operadores


def _partes(valor: str) -> list[str]:
    """Separa por vírgulas de nível 0 (fora de calc()/cubic-bezier())."""
    partes, nivel, atual = [], 0, ""
    for ch in valor:
        nivel += {"(": 1, ")": -1}.get(ch, 0)
        if ch == "," and nivel == 0:
            partes.append(atual)
            atual = ""
        else:
            atual += ch
    return partes + [atual]


def _tokens(parte: str) -> list[str]:
    toks, nivel, atual = [], 0, ""
    for ch in parte.strip():
        nivel += {"(": 1, ")": -1}.get(ch, 0)
        if ch == " " and nivel == 0:
            toks.append(atual)
            atual = ""
        else:
            atual += ch
    return [t for t in toks + [atual] if t]


def _e_tempo(tok: str) -> bool:
    return bool(re.fullmatch(r"\d*\.?\d+m?s", tok) or re.fullmatch(r"var\(--(dur-\w+|passo|atraso-dados)\)", tok)
                or tok.startswith("calc("))


def _regras():
    for sel, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", PORTAL):
        yield sel.strip(), corpo


def test_templates_sem_contagem_e_js_sem_contar():
    for p in list((RAIZ / "app").rglob("*.html")):
        assert "data-contar" not in p.read_text(encoding="utf-8"), p
    assert "function contar" not in JS and "[data-contar]" not in JS
    # D51: a única contagem do portal fica no bloco da página Talentos e só age dentro de .talentos-corpo
    inicio, fim = JS.index("// ---------- D51"), JS.index("// ---------- fim D51")
    fora = JS[:inicio] + JS[fim:]
    assert "nodeValue = br(" not in fora and "corrida" not in fora.lower()
    bloco = JS[inicio:fim]
    assert 'document.querySelector(".talentos-corpo")' in bloco and "semMovimento" in bloco


def test_sem_mola_sem_loop_no_css_todo():
    for a, y1, b, y2 in re.findall(r"cubic-bezier\(\s*([\d.]+),\s*(-?[\d.]+),\s*([\d.]+),\s*(-?[\d.]+)\)", CSS):
        assert 0 <= float(y1) <= 1 and 0 <= float(y2) <= 1, f"curva com ressalto: {a}, {y1}, {b}, {y2}"
    assert "--ease-mola" not in CSS and "--mola" not in CSS
    # exceção (Caio, 30/10/2026): o fluxo contínuo da capa roda em loop, mas por SMIL no SVG de capa.html, contínuo por
    # decisão do Caio (capa_fluxo.js para com a aba oculta e com movimento reduzido); o CSS segue sem loop (tests/test_v2_paginas.py::test_capa_sem_menu_com_comecar_para_o_roadmap)
    # exceção 2 (Caio, 30/10/2026): o Roadmap tem movimento contínuo (pulso nos dois ramos, ondas no "Você está aqui",
    # ícones e tracejados), só no bloco .rm-* e só dentro de @media (prefers-reduced-motion: no-preference)
    # exceção 3 (Caio, 31/10/2026): o mascote do encerramento acena, pisca, flutua e o coração pulsa em loop contínuo,
    # também só por SMIL no SVG de encerramento.html (fim.js começa os loops depois da entrada e para tudo com a aba
    # oculta e com movimento reduzido); o bloco .fim-* do CSS segue sem loop (conferido aqui, junto com o resto)
    # (as linhas animadas de fundo das Iniciativas saíram a pedido do Caio, 30/10/2026: a página fica sem loop)
    ini = CSS.index("/* Roadmap da área (V2")
    fim = CSS.index("/* ---------- LIA (D-LIA-3", ini)
    rm, fora = CSS[ini:fim], CSS[:ini] + CSS[fim:]
    assert "infinite" not in fora and "alternate" not in fora and "alternate" not in rm
    m = rm.index("@media (prefers-reduced-motion: no-preference)")
    movimento = rm[m:rm.index("\n}\n", m)]
    assert rm.count("infinite") == movimento.count("infinite") > 0
    for nome in ("pilula-brilho", "pilula-liquida", "aba-sobe", "aba-acende", "faixa-sobe", "celula-entra", "celula-acende",
                 "total-surge"):
        assert nome not in CSS, nome


def test_entrada_das_paginas_ate_1200ms():
    vistos = 0
    for sel, corpo in _regras():
        if ".entrou" not in sel:
            continue
        decls = dict((k.strip(), v.strip()) for k, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", corpo))
        if "animation" in decls and decls["animation"] != "none":
            partes = [[t for t in _tokens(p) if _e_tempo(t)] for p in _partes(decls["animation"])]
            onda = {**ONDA, "--i": 2} if "divisao-parte" in sel else ONDA  # Talentos: 3 partes na barra
            atrasos = [_ms(x, onda) for x in _partes(decls["animation-delay"])] if "animation-delay" in decls else None
            for k, ts in enumerate(partes):
                dur = _ms(ts[0]) if ts else 0
                atraso = atrasos[min(k, len(atrasos) - 1)] if atrasos else (_ms(ts[1]) if len(ts) > 1 else 0)
                assert dur + atraso <= 1200, (sel, dur, atraso)
                vistos += 1
        if "transition" in decls and decls["transition"] != "none":
            for p in _partes(decls["transition"]):
                ts = [t for t in _tokens(p) if _e_tempo(t)]
                assert sum(_ms(t) for t in ts[:2]) <= 1200, (sel, p)
                vistos += 1
        if "transition-delay" in decls:  # a duração vem da regra base (.entra: --dur-s; pior caso --dur-l)
            assert _ms(decls["transition-delay"]) + TEMPOS["--dur-l"] <= 1200, sel
    assert vistos >= 5  # a análise de fato encontrou as entradas das páginas


def test_numeros_meta_e_frase_sem_estado_escondido():
    # linha da meta, totais do mês, faixa e régua do Atendimento, frase do SLA: visíveis desde o 1º quadro
    for sel, corpo in _regras():
        if ":not(.entrou)" in sel and re.search(r"opacity:\s*0|scale", corpo):
            assert not re.search(r"linha-meta|pilha-total|traco-entradas|kpi-parte|\.frase|resposta-numero|hero-numero|kpi-num",
                                 sel), sel


def test_impressao_e_revisita_parados():
    assert re.search(r"@media print \{\s*\*, \*::before, \*::after \{ animation: none !important; transition: none !important; \}", CSS)
    assert "html.js .slide.revisto:not(.slide-estudo) :not(.navegador-pilula, .navegador-reflexo)" in CSS
    # o seletor de talentos de qualquer página (SLA, Previsão) e a recarga por carga nova abrem a página pronta
    assert '[data-chave^="talentos"] a' in JS and "p: location.pathname" in JS
    assert "semEntrada.p !== location.pathname" in JS


def test_navegacao_so_com_o_voo_da_pilula():
    assert "::view-transition-group(aba-ativa) { animation-duration: 320ms;" in CSS
    assert "::view-transition-image-pair(aba-ativa)" not in CSS
    assert ".navegador > .navegador-pilula::after" not in CSS


def test_modo_reuniao_sem_recarga_automatica():
    assert "dadosNovos()" in JS and '"Atualizar"' in JS and 'meta[name="relatorio-modo"][content="apresentacao"]' in JS
    # a única recarga automática restante fica fora do modo reunião
    trecho = JS[JS.index("function dadosNovos"):JS.index("if (avisoNovo) return;")]
    assert "if (!modoReuniao)" in trecho and "location.reload()" in trecho


def test_encerramento_loop_so_por_smil_e_parado_sem_movimento():
    """Exceção 3 (Caio, 31/10/2026): o mascote do encerramento acena, pisca, flutua e o coração pulsa em loops contínuos,
    só por SMIL; os loops só começam pelo fim.js (sem JS: parado) e param com movimento reduzido e com a aba oculta."""
    tpl = (RAIZ / "app" / "templates" / "encerramento.html").read_text(encoding="utf-8")
    fimjs = (RAIZ / "app" / "static" / "fim.js").read_text(encoding="utf-8")
    ini, fim = CSS.index("/* Encerramento (V2, Caio, 31/10/2026)"), CSS.index("/* fim do bloco do encerramento (V2) */")
    bloco = CSS[ini:fim]
    assert "infinite" not in bloco and ".fim-boneco" in bloco
    loops = re.findall(r"<animateTransform [^>]*>", tpl)
    assert len(loops) == 5 and all('begin="indefinite" repeatCount="indefinite"' in a for a in loops)
    aceno = [a for a in loops if 'type="rotate"' in a and 'dur="1.4s"' in a]
    assert len(aceno) == 2  # antebraço e mão, ciclo de 1,4 s sem pausa
    assert any('type="scale"' in a and 'dur="3.4s"' in a for a in loops)  # piscar
    assert "prefers-reduced-motion: reduce" in fimjs and "document.hidden" in fimjs and "pauseAnimations" in fimjs
    assert "beginElement" in fimjs
