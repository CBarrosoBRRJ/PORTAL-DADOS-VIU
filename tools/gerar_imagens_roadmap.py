"""Gera as imagens do Roadmap (V2, 30/10/2026): o mapeamento "Viu Agenciamento - Fluxo 1" (PDF) e o print do BigQuery.

Uso (PyMuPDF e Pillow; o venv do projeto não tem PyMuPDF, o Python 3.12 do computador tem):
    python -I tools/gerar_imagens_roadmap.py <PDF do fluxo> app/static/roadmap [<PNG do BigQuery>]
    python -I tools/gerar_imagens_roadmap.py --dashboards app/static/roadmap <PNG pagamento> <PNG contratos>

Dashboards (prints do Caio, 30/10/2026): <nome>-mini.webp e <nome>.webp (o painel usa a própria ampliada a 100%: o print
já está na resolução da tela). Desfocados os nomes de talentos, marcas e projetos, os valores e datas por linha, a
saudação com nome e a data e hora; ficam o título, os filtros (vazios), os totais agregados dos indicadores e a estrutura.
O painel "Pontos de atenção" saiu da página (30/10/2026); os arquivos foram para _descartados/2026-10-30/.

Para cada painel do PDF grava três versões: <nome>-mini.webp (miniatura na lâmina), <nome>.webp (ampliada, visão
inteira no painel) e <nome>-alta.webp (alta resolução, carregada só quando se amplia a 100% no painel, para ler as
caixas). O print do BigQuery vira bigquery-mini.webp e bigquery.webp (recorte sem a barra do Google Cloud, sem a conta e
sem os menus laterais).

Privacidade: na alta resolução o texto das caixas fica legível, então são desfocados (em todas as versões) os trechos com
nomes de pessoas, o exemplo de contrato de talento, o e-mail da caixa de pedidos e todas as capturas de tela coladas no
quadro (podem ter nomes, rostos ou valores); ficam só os ícones pequenos.
"""
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageFilter

MINI_LARG = 440  # px; a miniatura aparece com ~140 px de largura na lâmina (nítida em tela de densidade 2x)
IMAGEM_MIN_PT = 8  # capturas coladas no quadro maiores que isto (em pontos do PDF) são desfocadas
NOMES = (  # trechos (x0, y0, x1, y1 em pontos do PDF) com nomes de pessoas, contrato de talento ou e-mail
    (643, 121, 661, 128),   # fluxo: controles de bloqueio/exclusividade com nome de pessoa
    (622, 150, 642, 166),   # fluxo: caminhos do contrato (nome de pessoa) e exemplo de contrato de talento
    (426, 163, 438, 174),   # fluxo: contatos da gestão de elenco (nomes)
    (814, 147, 830, 155),   # fluxo: aprovações com nome de diretor
    (802, 92, 840, 99),     # fluxo: aprovações da RC com nome de diretor
    (328, 98, 347, 102),    # fluxo: e-mail da caixa de pedidos
    (465, 14, 510, 80),     # fluxo: exemplo de proposta (nomes de talentos, marca e escopo)
    (369, 264, 389, 274),   # pontos de atenção: controles de bloqueio/exclusividade com nome de pessoa
    (393, 270, 414, 287),   # pontos de atenção: caminhos do contrato e exemplo de contrato de talento
    (392, 345, 418, 367),   # pontos de atenção: caminhos do contrato (repetição no plano de ação)
    (229, 253, 249, 258),   # pontos de atenção: e-mail da caixa de pedidos
)
PAINEIS = {
    # nome: (recorte x0, y0, x1, y1 em pontos, escala da ampliada, escala da alta, fração da largura na miniatura).
    # A miniatura do fluxo mostra só o começo (entrada e orçamento): o painel inteiro é largo demais (5:1)
    "fluxo-processo": ((208, 0, 1262, 211), 2.6, 9.0, 0.42),
}
BQ_RECORTE = (326, 80, 1845, 893)  # px do print: do caminho "projeto / Datasets / gold_monday" à paginação


def _desfocar(img: Image.Image, r: pymupdf.Rect, escala: float, caixas) -> None:
    for x0, y0, x1, y1 in caixas:
        caixa = pymupdf.Rect(x0, y0, x1, y1) & r
        if caixa.is_empty:
            continue
        box = tuple(int(round(v)) for v in ((caixa.x0 - r.x0) * escala, (caixa.y0 - r.y0) * escala,
                                            (caixa.x1 - r.x0) * escala, (caixa.y1 - r.y0) * escala))
        img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(max(6, 3.5 * escala))), box[:2])


def _mini(img: Image.Image, fracao: float, destino: Path) -> Image.Image:
    corte = img.crop((0, 0, round(img.width * fracao), img.height))
    mini = corte.resize((MINI_LARG, round(corte.height * MINI_LARG / corte.width)), Image.LANCZOS)
    mini.save(destino, "WEBP", quality=82, method=6)
    return mini


def gerar(pdf: Path, destino: Path) -> None:
    pagina = pymupdf.open(pdf)[0]
    destino.mkdir(parents=True, exist_ok=True)
    capturas = [tuple(i["bbox"]) for i in pagina.get_image_info()
                if min(i["bbox"][2] - i["bbox"][0], i["bbox"][3] - i["bbox"][1]) >= IMAGEM_MIN_PT]
    for nome, (caixa, escala, escala_alta, fracao) in PAINEIS.items():
        r = pymupdf.Rect(*caixa)
        for sufixo, e in (("", escala), ("-alta", escala_alta)):
            pix = pagina.get_pixmap(matrix=pymupdf.Matrix(e, e), clip=r)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            _desfocar(img, r, e, NOMES + tuple(capturas))
            img.save(destino / f"{nome}{sufixo}.webp", "WEBP", quality=74 if sufixo else 78, method=6)
            print(nome + sufixo, img.size, (destino / f"{nome}{sufixo}.webp").stat().st_size // 1024, "KB")
            if not sufixo:
                _mini(img, fracao, destino / f"{nome}-mini.webp")


def gerar_bigquery(png: Path, destino: Path) -> None:
    img = Image.open(png).convert("RGB").crop(BQ_RECORTE)
    img.save(destino / "bigquery.webp", "WEBP", quality=86, method=6)
    _mini(img, 0.62, destino / "bigquery-mini.webp")  # miniatura: o título e o começo da lista
    print("bigquery", img.size, (destino / "bigquery.webp").stat().st_size // 1024, "KB")


DASHBOARDS = {
    # nome: (trechos a desfocar em px do print, fração da largura na miniatura)
    "dashboard-pagamento": (((0, 548, 1198, 828),), 1.0),      # tabela por talento, marca e projeto (nomes, valores, datas)
    "dashboard-contratos": ((
        (78, 42, 300, 86),       # saudação com o nome e a data
        (950, 38, 1100, 62),     # data e hora da atualização
        (20, 466, 300, 817),     # nomes dos talentos e contagem por talento
        (950, 466, 1100, 817),   # datas e prazos por contrato
    ), 1.0),
}


def gerar_dashboards(destino: Path, *pngs: Path) -> None:
    for (nome, (caixas, fracao)), png in zip(DASHBOARDS.items(), pngs):
        img = Image.open(png).convert("RGB")
        for box in caixas:
            img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(9)), box[:2])
        img.save(destino / f"{nome}.webp", "WEBP", quality=86, method=6)
        _mini(img, fracao, destino / f"{nome}-mini.webp")
        print(nome, img.size, (destino / f"{nome}.webp").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    if sys.argv[1] == "--dashboards":
        gerar_dashboards(Path(sys.argv[2]), *map(Path, sys.argv[3:]))
        sys.exit()
    gerar(Path(sys.argv[1]), Path(sys.argv[2]))
    if len(sys.argv) > 3:
        gerar_bigquery(Path(sys.argv[3]), Path(sys.argv[2]))
