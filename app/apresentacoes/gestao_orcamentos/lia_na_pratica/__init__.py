"""A LIA na prática (V2, 30/10/2026; PRD "Slide A LIA na prática (vídeo)" de @cris adaptado).

Vídeo curto da LIA trabalhando, ao lado das etapas que ele percorre. Conteúdo fixo, sem leitura de dados.
V2 (Caio, 30/10/2026): o vídeo abre no pop-up do botão "Ver a LIA na prática" da página LIA (lia/template.html); esta
página ficou oculta (endereço mantido, destino do botão sem JS). As constantes abaixo são a fonte das duas.
Para incluir o vídeo: salvar o MP4 em app/static/video/ (lia-na-pratica.mp4) e preencher ARQUIVO; CAPA (imagem de
abertura) e LEGENDAS (.vtt em pt-BR) são opcionais, na mesma pasta (LEIA-ME.md lá). Sem ARQUIVO, o pop-up e a página
mostram o espaço reservado ("Vídeo a incluir"), sem player quebrado.
"""

PASTA = "video"  # app/static/video/
ARQUIVO = "lia-na-pratica.mp4"  # Caio, 03/11/2026: "fluxo LIA.mp4" renomeado (H.264 1920×1080, 1min47s, 40 MB)
CAPA = ""  # ex.: "lia-na-pratica.jpg" (opcional)
LEGENDAS = ""  # ex.: "lia-na-pratica.vtt" (opcional, pt-BR)

# roteiro do vídeo, na ordem; tem de bater com o que o vídeo mostra. Sigla = iniciativa responsável (iniciativas/catalogo.py)
ETAPAS = (
    {"titulo": "O e-mail chega", "texto": "O pedido entra na caixa do talento.", "sigla": "LIA"},
    {"titulo": "A LIA lê e classifica", "texto": "Não lead, lead ou validação.", "sigla": "LIA"},
    {"titulo": "Registra no monday", "texto": "O lead entra no board já preenchido.", "sigla": "LIA"},
    {"titulo": "Cria a pasta", "texto": "Estrutura padrão no SharePoint, com os modelos.", "sigla": "GPS"},
    {"titulo": "Preenche a planilha de valoração", "texto": "Valores pela tabela de preços.", "sigla": "Orça+AI"},
    {"titulo": "Gera a carta orçamento", "texto": "Escopo, entregáveis e valores na carta.", "sigla": "COP.IA"},
)


def tela() -> dict:
    from app.apresentacoes.gestao_orcamentos.iniciativas import catalogo

    grupo = {i["sigla"]: g for g in catalogo.GRUPOS for i in g["itens"]}
    # Caio, 03/11/2026: etapa de iniciativa em produção = concluída (ícone ✓); as demais = em andamento (ampulheta e
    # selo com texto: "Em teste" na fase de testes)
    etapas = []
    for e in ETAPAS:
        chave = grupo[e["sigla"]]["chave"] if e["sigla"] in grupo else ""
        etapas.append({**e, "fase": grupo[e["sigla"]]["titulo"] if chave else "", "concluida": chave == "producao",
                       "selo": "" if chave == "producao" else "Em teste" if chave == "testes" else "Em andamento"})
    caminho = lambda nome: f"/static/{PASTA}/{nome}" if nome else ""
    return {"arquivo": caminho(ARQUIVO), "capa": caminho(CAPA), "legendas": caminho(LEGENDAS), "etapas": etapas}
