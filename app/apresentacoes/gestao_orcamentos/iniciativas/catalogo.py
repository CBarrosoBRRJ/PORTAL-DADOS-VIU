"""Catálogo das iniciativas de automação e IA do Agenciamento (PRD Iniciativas, @cris, 30/10/2026).

Fonte: planilha iniciativasVIU-automacao-ia.xlsx, curada à mão (não vem do BigQuery). Este arquivo é a fonte da verdade
do slide: incluir um projeto = copiar um item e preencher; a coluna da fase cresce sozinha. Fase nova =
incluir um grupo e definir a cor da chave no CSS (.ini-<chave> { --ini-cor: … }).

Grupo: chave (cor), titulo, sub, itens. Item: sigla (pode ficar vazia: o nome vira o título do quadro), nome, curta
(resumo; usado na caixinha só quando desc está vazia), desc (o que abre ao clicar) e, opcional, link (rótulo e
endereço de uma página do portal com os resultados; vira um botão no detalhe). Opcionais também: responsavel (pessoa
ou área; vazio = "a definir" no detalhe), status (observação curta) e proximo (próximo passo).
"""

from app.apresentacoes.gestao_orcamentos import SLUG

GRUPOS = (
    {"chave": "producao", "titulo": "Em produção", "sub": "Já rodando no dia a dia", "itens": (
        {"sigla": "LIA", "nome": "Leitura Inteligente Automatizada", "curta": "Lê e-mails e cria leads no monday",
         "desc": "Robô que lê a caixa de e-mail do talento, classifica as mensagens e preenche no monday se for um lead.",
         "link": {"rotulo": "Ver resultados", "href": f"/{SLUG}/lia#1"}},
        {"sigla": "GPS", "nome": "Geração de pastas no SharePoint", "curta": "Pastas padrão para cada lead",
         "desc": "Cria a estrutura padrão de pastas do projeto, com os modelos de carta e planilhas, após a LIA "
                 "identificar um novo lead."},
        {"sigla": "MIA", "nome": "Monitoramento Inteligente Automatizado", "curta": "Revisa e corrige o board todo dia",
         "desc": "Robô que revisa o board do Backlog todos os dias e corrige no monday.com o que foi preenchido "
                 "errado. Guarda o valor original e manda para revisão o que tem dúvida."},
    )},
    {"chave": "testes", "titulo": "Fase de testes", "sub": "Validando para ir ao ar", "itens": (
        {"sigla": "Orça+AI", "nome": "Precificação automática", "curta": "Planilha de precificação preenchida",
         "desc": "Preenche a planilha de precificação com as informações do briefing e calcula os valores pela tabela "
                 "de preços."},
        {"sigla": "COP.IA", "nome": "Carta-orçamento automática", "curta": "Carta gerada a partir do escopo",
         "desc": "Gera a carta-orçamento a partir do escopo, dos entregáveis e dos valores já calculados."},
    )},
    {"chave": "desenvolvimento", "titulo": "Em desenvolvimento", "sub": "Sendo construídas", "itens": (
        {"sigla": "FILA", "nome": "Priorização da demanda", "curta": "Prioriza a demanda de orçamentos",
         "desc": "Prioriza a demanda de orçamentos que chega à área, cruzando histórico de fechamento, relacionamento "
                 "marca × talento e dados de orçamento."},
        {"sigla": "CACHÊ", "nome": "Estimativa de cachê", "curta": "Estimativa de cachê a partir do e-mail",
         "desc": "Lê o e-mail, extrai escopo, marca, talento e valor, salva esses dados e gera uma estimativa de "
                 "cachê."},
        {"sigla": "G1.IA", "nome": "Revisão de matérias publicitárias", "curta": "Revisa as matérias das afiliadas",
         "desc": "Agente de IA que revisa e valida textos de branded content e conteúdos publicitários publicados nos "
                 "ambientes Globo (Branded Content Afiliadas)."},
    )},
    {"chave": "esteira", "titulo": "Na esteira", "sub": "Próximas a entrar", "itens": (
        {"sigla": "Salesforce", "nome": "Oportunidade automática", "curta": "Oportunidade criada por frentes",
         "desc": "Cria a oportunidade já estruturada por frentes (conteúdo, mídia, TV, digital) a partir da triagem "
                 "do e-mail ou do briefing."},
        {"sigla": "MATCH", "nome": "Score de fit marca × talento", "curta": "Recomenda talentos por aderência",
         "desc": "Pontua a aderência entre marca ou briefing e os talentos agenciados, para recomendar os de maior "
                 "potencial."},
        {"sigla": "Auto+", "nome": "Contratos e pagamentos", "curta": "Solicitações com status acompanhado",
         "desc": "Encaminha as solicitações às áreas responsáveis e permite acompanhar o status de cada pedido."},
        {"sigla": "GUIA+", "nome": "RAGs executivos e de suporte", "curta": "Assistentes de IA da base do Agenciamento",
         "desc": "Assistentes de IA que consultam a base do Agenciamento para responder a executivos e apoiar "
                 "analistas."},
        {"sigla": "Raio-X", "nome": "Raio-X dos talentos", "curta": "Características e dados de cada talento",
         "desc": "Reúne num só lugar as características e os dados de cada talento agenciado, para consultar o perfil "
                 "e o histórico de cada um antes de indicar ou negociar."},
    )},
)

# nota no rodapé do slide (RF9); vazia = sem nota
REFERENCIA = ""
