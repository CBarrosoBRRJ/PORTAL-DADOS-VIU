"""Iniciativas de automação e IA (PRD Iniciativas, @cris, 30/10/2026).

Redesenho de 30/10/2026: colunas por fase (da mais madura à próxima) com a contagem e um medidor de maturidade; o
detalhe abre num painel fixo à direita. `nivel` = degraus acesos do medidor (a 1ª fase do catálogo acende todos).

Dados no servidor (Caio e gerente, 30/10/2026, noite): as iniciativas vêm do quadro salvo (`repositorio.py`: SQLite
fora do Drive no computador, Firestore + Cloud Storage no Cloud Run). Na 1ª execução o quadro nasce do `catalogo.py`
(semente); depois o quadro é a fonte da página, e o catálogo fica como semente e histórico. As fases (colunas, cores,
frases) continuam no catálogo. Se o armazenamento não responder, a página mostra o catálogo, só leitura, com um aviso.
`densidade` (1 a 3) = cartões mais compactos conforme a coluna enche (o JS recalcula ao arrastar, incluir ou excluir).
"""

from app import config, dados
from app.apresentacoes.gestao_orcamentos import endereco_atual
from app.apresentacoes.gestao_orcamentos.iniciativas import catalogo, repositorio


def densidade(n: int) -> int:
    """Classe de densidade da coluna: até 3 cartões = 1, 4 = 2 (mais justo), 5 ou mais = 3 (compacto, nome em 1 linha)
    (o iniciativas.js usa a mesma regra).
    Meta do Caio (30/10/2026): 5 cartões inteiros sem rolar; a barra só a partir do 6º, e o mais tarde possível."""
    return 1 if n <= 3 else 2 if n == 4 else 3


def tela() -> dict:
    from app.apresentacoes.gestao_orcamentos.iniciativas.api import (
        anexo_publico,
        fotos_fixas,
    )

    n = len(catalogo.GRUPOS)
    aviso, na_semente = None, False
    try:
        q = repositorio.quadro()
        itens, anexos, na_semente = q.listar(), q.anexos(), q.na_semente()
    except repositorio.QuadroIndisponivel as e:
        dados.log("ERROR", "quadro das iniciativas indisponível; página com o catálogo", erro=str(e))
        itens, anexos = repositorio.Quadro.itens_da_semente(), []
        aviso = "Não foi possível ler o quadro salvo agora. Mostrando o catálogo, só para leitura."
    por_item: dict[str, list] = {i: fotos_fixas(i) for i in catalogo.FOTOS}  # fotos fixas primeiro (Caio, 03/11/2026)
    for a in anexos:
        por_item.setdefault(a["iniciativa_id"], []).append(anexo_publico(a))
    grupos = []
    for k, g in enumerate(catalogo.GRUPOS):
        lista = [{"id": i["id"], "sigla": i["sigla"], "nome": i["nome"], "titulo": i["sigla"] or i["nome"],
                  "texto": i["descricao"], "responsavel": i["responsavel"], "status": i["status"],
                  "proximo": i["proximo"],
                  "link": {"rotulo": i["link_rotulo"], "href": endereco_atual(i["link_href"])} if i.get("link_href") else None,
                  "anexos": por_item.get(i["id"], [])}
                 for i in itens if i["fase"] == g["chave"]]
        grupos.append({"chave": g["chave"], "titulo": g["titulo"], "sub": g["sub"], "nivel": n - k, "itens": lista,
                       "densidade": densidade(len(lista))})
    return {"grupos": grupos, "fases": n, "total": sum(len(g["itens"]) for g in grupos),
            "referencia": catalogo.REFERENCIA, "edicao": config.INICIATIVAS_EDICAO and aviso is None, "aviso": aviso,
            "na_semente": na_semente, "max_mb": repositorio.MAX_ANEXO // (1024 * 1024)}
