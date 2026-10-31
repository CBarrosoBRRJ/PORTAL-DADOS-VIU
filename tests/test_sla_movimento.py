"""D46 (25/10/2026): movimento do estudo "Como medimos" — regras verificáveis no CSS, no JS e no HTML.

O que se confere aqui: o movimento só existe sob prefers-reduced-motion: no-preference e html.js (sem JS e com
movimento reduzido, a tela é o HTML do servidor); nada passa de ~1,2 s; sem mola e sem loop; a cascata antiga de 2,6 s
do slide 1 saiu; os agrupamentos do template (histograma, média) e o pathLength das linhas desenhadas; nenhum style=""
no estudo (CSP); e os ganchos do JS (entrada só na 1ª visita, troca de slide com View Transition, grupo sem repetir).
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSS = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
JS = (RAIZ / "app" / "static" / "apresentacao.js").read_text(encoding="utf-8")
INICIO = CSS.index('/* ---------- D46 (25/10/2026): movimento do estudo "Como medimos"')
BLOCO = CSS[INICIO:]


def _media_no_preference(bloco: str) -> str:
    """Conteúdo do 1º @media (prefers-reduced-motion: no-preference) do bloco, contando chaves."""
    i = bloco.index("@media (prefers-reduced-motion: no-preference) {")
    j = bloco.index("{", i) + 1
    nivel = 1
    while nivel:
        nivel += {"{": 1, "}": -1}.get(bloco[j], 0)
        j += 1
    return bloco[i:j]


def test_movimento_so_com_movimento_permitido_e_js():
    media = _media_no_preference(BLOCO)
    resto = re.sub(r"/\*.*?\*/", "", BLOCO.replace(media, ""), flags=re.S)
    # fora do @media só ficam @keyframes e o bloco de impressão (nada que esconda ou mova por si)
    for regra in re.findall(r"^([^@\s}][^{]*)\{", resto, flags=re.M):
        assert regra.strip().startswith(("from", "to", ".slide-estudo, .slide-estudo *")), regra
    # todo estado de partida (escondido/encolhido) exige html.js e :not(.entrou)
    for linha in media.splitlines():
        if re.search(r"opacity: 0;|scale[XY]?\(0|clip-path: inset\(0 (0 100%|100%)|stroke-dashoffset: 1;", linha) and "{" in linha:
            assert "html.js" in linha and ":not(.entrou)" in linha, linha
    # animações de entrada só na 1ª visita
    for linha in media.splitlines():
        if "animation:" in linha and ".entrou" in linha:
            assert ".entrou:not(.revisto)" in linha, linha


def test_impressao_sem_movimento():
    assert re.search(r"@media print \{\s*\.slide-estudo, \.slide-estudo \*, .*animation: none !important; transition: none !important;", BLOCO)


def test_tempos_curtos_sem_mola_sem_loop():
    media = _media_no_preference(BLOCO)
    for linha in media.splitlines():
        if "animation" not in linha:
            continue
        # duração + atraso fixo de cada animação ≤ 1,2 s (atrasos por --t/--k/--cz-t conferidos abaixo)
        for nome, dur, atraso in re.findall(r"animation:\s*([\w-]+) ([\d.]+)s [^,;]*?(?:([\d.]+)s )?backwards", linha):
            assert float(dur) + float(atraso or 0) <= 1.2, linha
    for v in re.findall(r"--t: ([\d.]+)s", media) + re.findall(r"--cz-t: ([\d.]+)s", media):
        assert float(v) <= 0.9
    assert "infinite" not in BLOCO and "alternate" not in BLOCO
    assert "cubic-bezier(0.3, 1.6" not in CSS  # a mola dos marcos do slide 1 saiu


def test_cascata_antiga_do_slide_1_saiu():
    assert ".slide-estudo .estudo-gancho { --t: 2.6s; }" not in CSS
    assert "html.js .slide-cem .cem-waffle .cq { opacity: 0" not in CSS  # os 100 quadrados não animam um a um
    # números, regras e gancho do slide 1 não têm mais estado escondido
    assert not re.search(r"(exemplo-numeros|regra-caixa|estudo-gancho)[^{]*\{[^}]*opacity: 0", BLOCO)


def test_slide_5_nao_mexe_em_cada_ponto():
    media = _media_no_preference(BLOCO)
    for linha in media.splitlines():
        if re.search(r"\.mx-(ate2|de2a5|mais5|p)\b", linha):
            assert "transform" not in linha and "clip-path" not in linha and "filter" not in linha, linha


def test_fim_do_estudo_anel_uma_vez():
    """V2 (30/10/2026, Caio): o ✕ do último slide abre um anel uma vez ao chegar (sem loop, só com movimento e JS)."""
    media = _media_no_preference(BLOCO)
    assert "html.js .slide-estudo.entrou:not(.revisto) .fechar-fim { animation: fim-anel 0.9s ease-out 0.3s backwards; }" in media
    assert "@keyframes fim-anel" in BLOCO and "fechar-fim" not in BLOCO.replace(media, "")


def test_template_agrupa_e_desenha_sem_style():
    tpl = (RAIZ / "app" / "templates" / "como_medimos.html").read_text(encoding="utf-8")
    assert '<g class="ex-barras">' in tpl and '<g class="ex-ns">' in tpl and '<g class="ex-camada ex-alfinetes">' in tpl
    assert "data-passo" not in tpl and "data-explora" not in tpl  # V2 (30/10/2026): slide 2 num passo só
    assert '<div class="ct-waffle" role="img"' in tpl  # V2: o waffle é uma máscara única (a curva acumulada saiu)
    assert '<polyline class="mx-tipico" points="{{ gm.linha }}" pathLength="1"/>' in tpl
    assert 'style="' not in tpl and "<style" not in tpl and "<script" not in tpl  # CSP: style-src-attr 'none'


def test_js_entrada_unica_troca_de_slide_e_de_grupo():
    assert 'classList.add("entrou", "revisto")' in JS and "s.dataset.visto" in JS
    assert "document.startViewTransition" in JS and "skipTransition()" in JS
    assert "!semMovimento && document.startViewTransition" in JS  # movimento reduzido: troca direta
    assert '"estudo-sem-entrada"' in JS and 'estudo-grupos a[aria-current]' in JS
    assert "data-explora-ir" not in JS and "passo-volta" not in CSS  # V2: sem os quadros do slide 2
