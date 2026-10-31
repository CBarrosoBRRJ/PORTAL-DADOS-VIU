"""Monta o PDF e o PowerPoint do portal a partir das capturas de tools/exportar_paginas.mjs (D66, 31/10/2026).

    python tools/montar_pdf_ppt.py <pasta_capturas> <pasta_destino> [nome_base]

Uma página/lâmina por captura, na ordem dos nomes (01_capa, 02_roadmap, ...), em 16:9. Precisa de Pillow e
python-pptx (fora do requirements do site: instalar só onde for rodar, p.ex. `pip install --target <pasta> python-pptx`).
"""

import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Emu, Inches

NOMES = {
    "capa": "Capa", "roadmap": "Roadmap", "demanda": "Demanda", "talentos": "Talentos", "sla": "SLA de entrega",
    "estudo": "Como medimos (estudo do SLA)", "lia": "LIA", "iniciativas": "Iniciativas", "previsao": "Previsão de demanda",
    "encerramento": "Encerramento",
}


def titulo(arq: Path) -> str:
    partes = arq.stem.split("_")
    nome = NOMES.get(partes[1], partes[1])
    return f"{nome}, slide {partes[2]}" if len(partes) > 2 else nome


def main() -> int:
    origem, destino = Path(sys.argv[1]), Path(sys.argv[2])
    base = sys.argv[3] if len(sys.argv) > 3 else "ViU Agenciamento"
    imagens = sorted(origem.glob("*.png"))
    if not imagens:
        print("Nenhuma captura em", origem)
        return 1

    # PDF: uma página por captura, 16:9, em 150 dpi (2400 px = 16 polegadas)
    paginas = [Image.open(p).convert("RGB") for p in imagens]
    pdf = destino / f"{base}.pdf"
    paginas[0].save(pdf, save_all=True, append_images=paginas[1:], resolution=150.0,
                    title=base, author="Caio Barroso", subject="Relatório da área de Agenciamento")

    # PowerPoint: lâmina 16:9 com a captura inteira; o nome da página no título oculto (leitor de tela) e nas notas
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    vazio = prs.slide_layouts[6]
    for p in imagens:
        s = prs.slides.add_slide(vazio)
        with Image.open(p) as im:
            w, h = im.size
        alt_l = prs.slide_height * w / h
        if alt_l <= prs.slide_width:  # página mais alta que 16:9: centra na largura
            larg, alt = Emu(int(alt_l)), prs.slide_height
        else:
            larg, alt = prs.slide_width, Emu(int(prs.slide_width * h / w))
        foto = s.shapes.add_picture(str(p), (prs.slide_width - larg) // 2, (prs.slide_height - alt) // 2, larg, alt)
        foto.name = titulo(p)
        foto._element.nvPicPr.cNvPr.set("descr", f"ViU Agenciamento: {titulo(p)}")
        s.notes_slide.notes_text_frame.text = titulo(p)
    pptx = destino / f"{base}.pptx"
    prs.core_properties.title, prs.core_properties.author = base, "Caio Barroso"
    prs.save(pptx)
    print(f"{len(imagens)} páginas\n{pdf}\n{pptx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
