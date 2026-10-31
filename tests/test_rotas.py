"""Rotas do site (FastAPI) com os dados sintéticos: endereços, redirecionamentos, conteúdo e cabeçalhos."""

import re

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:  # roda o lifespan (carga inicial) com os dados sintéticos
        yield c


def test_raiz_e_area_abrem_a_pagina_inicial(cliente):
    r = cliente.get("/", follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"] == "/viu-agenciamento/capa"  # D59: a reunião começa na capa
    r = cliente.get("/viu-agenciamento")
    assert r.status_code == 200 and "ViU Agenciamento" in r.text and 'class="menu-status' in r.text
    assert 'class="controles"' not in r.text  # página única: sem Anterior/Próximo


def test_endereco_antigo_do_sla_redireciona_com_filtro(cliente):
    r = cliente.get("/sla?talentos=exclusivos", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/viu-agenciamento/sla?talentos=exclusivos"
    r = cliente.get("/p/visao_geral", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/"


def test_endereco_antigo_da_area_redireciona_para_viu_agenciamento(cliente):
    # Caio, 31/10/2026: /gestao-orcamentos[/...] → /viu-agenciamento[/...]; GET 301 com a query, POST/PUT/PATCH/DELETE 308
    for antigo, novo in (("/gestao-orcamentos", "/viu-agenciamento"), ("/gestao-orcamentos/", "/viu-agenciamento"),
                         ("/gestao-orcamentos/capa", "/viu-agenciamento/capa"),
                         ("/gestao-orcamentos/sla/como-medimos?passo=2&talentos=exclusivos",
                          "/viu-agenciamento/sla/como-medimos?passo=2&talentos=exclusivos"),
                         ("/gestao-orcamentos/roadmap?x=%20a", "/viu-agenciamento/roadmap?x=%20a")):
        r = cliente.get(antigo, follow_redirects=False)
        assert r.status_code == 301 and r.headers["location"] == novo, antigo
    api = "/gestao-orcamentos/iniciativas/api/iniciativas"
    for metodo in ("post", "put", "patch", "delete"):
        r = cliente.request(metodo.upper(), f"{api}/x?y=1", follow_redirects=False)
        assert r.status_code == 308 and r.headers["location"] == "/viu-agenciamento/iniciativas/api/iniciativas/x?y=1"
    assert cliente.head("/gestao-orcamentos/talentos", follow_redirects=False).status_code == 301
    assert cliente.get("/gestao-orcamentosX", follow_redirects=False).status_code == 404  # só o prefixo exato
    r = cliente.get("/gestao-orcamentos/talentos")  # seguindo o redirecionamento, a página abre no endereço novo
    assert r.status_code == 200 and str(r.url).endswith("/viu-agenciamento/talentos")
    assert "<title>ViU Agenciamento</title>" in r.text
    # links já gravados no quadro das Iniciativas com o endereço antigo saem no novo
    from app.apresentacoes.gestao_orcamentos import endereco_atual
    assert endereco_atual("/gestao-orcamentos/lia#1") == "/viu-agenciamento/lia#1"
    assert endereco_atual("/gestao-orcamentosX") == "/gestao-orcamentosX" and endereco_atual("https://x/") == "https://x/"


def test_slide_sla_mostra_os_numeros_do_grupo(cliente):
    r = cliente.get("/viu-agenciamento/sla")
    assert r.status_code == 200
    assert "15&nbsp;h" in r.text  # mediana 14,5 h → "15 h"
    assert "1,8 dia útil" in r.text and "resposta na terça à tarde" in r.text and "Como a meta é calculada" not in r.text  # C3c (D54)
    assert 'aria-current="true"' in r.text and "?talentos=exclusivos#1" in r.text
    r = cliente.get("/viu-agenciamento/sla?talentos=exclusivos")
    assert "8&nbsp;h" in r.text and "nos talentos exclusivos" in r.text
    r = cliente.get("/viu-agenciamento/sla?talentos=invalido")
    assert r.status_code == 200 and "15&nbsp;h" in r.text  # grupo desconhecido cai em "todos"


def test_regras_e_404(cliente):
    # 2ª leva da batalha 2: /regras retirada (301), com o mesmo filtro
    r = cliente.get("/viu-agenciamento/sla/regras?talentos=exclusivos", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/viu-agenciamento/sla/como-medimos?talentos=exclusivos#1"
    r = cliente.get("/viu-agenciamento/atendimento/regras", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/viu-agenciamento/atendimento"
    assert cliente.get("/nao-existe").status_code == 404
    assert cliente.get("/viu-agenciamento/nao-existe").status_code == 404
    saude = cliente.get("/saude").json()
    assert saude["ok"] is True and "tabelas" in saude and "dados_prontos" in saude


def test_sem_dados_responde_503_sem_numeros(cliente, monkeypatch):
    from app import dados

    def indisponivel(forcar=False):
        raise dados.DadosIndisponiveis("BigQuery fora do ar")

    monkeypatch.setattr(dados.sla, "df", indisponivel)
    r = cliente.get("/viu-agenciamento/sla")
    assert r.status_code == 503 and r.headers["retry-after"].isdigit()
    assert "Os dados não estão disponíveis agora" in r.text and "&nbsp;h</span>" not in r.text
    monkeypatch.setattr(dados.entrada, "df", indisponivel)
    r = cliente.get("/viu-agenciamento")
    assert r.status_code == 503 and 'href="/viu-agenciamento#1"' in r.text


def test_janeiro_sem_mes_completo(cliente, movimentos, monkeypatch):
    import pandas as pd

    from app import dados, sla
    from app.apresentacoes.gestao_orcamentos.sla import calculos

    jan = movimentos.copy()
    jan["_processado_em"] = pd.Timestamp("2027-01-05 12:00", tz="UTC")
    jan.attrs["versao"] = 99
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: jan)
    calculos._cache.clear()
    sla._cache.clear()
    r = cliente.get("/viu-agenciamento/sla")
    assert r.status_code == 200
    assert "ainda não há meses completos em 2027" in r.text and "Sem mês completo em 2027" in r.text
    assert "%</strong>" not in r.text.split("Orçamentos prontos")[1].split("</figcaption>")[0]  # legenda sem % vazio


def test_cabecalhos_de_seguranca_e_cache(cliente):
    r = cliente.get("/viu-agenciamento/sla")
    csp = r.headers["content-security-policy"]
    assert "default-src 'self'" in csp and "style-src-attr 'none'" in csp and "'unsafe-inline'" not in csp
    nonce = re.search(r"'nonce-([^']+)'", csp).group(1)
    assert f'<style nonce="{nonce}">' in r.text and ' style="' not in r.text  # sem estilo inline; bloco assinado
    assert nonce not in cliente.get("/viu-agenciamento/sla").headers["content-security-policy"]  # nonce novo a cada resposta
    # D59: só o próprio site se emoldura (quadro da tela cheia); sites de fora continuam bloqueados
    assert r.headers["x-frame-options"] == "SAMEORIGIN" and "frame-ancestors 'self'" in csp
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["cache-control"] == "private, no-store"  # páginas com dados internos nunca ficam guardadas
    r = cliente.get("/static/estilo.css?v=1")
    assert r.status_code == 200 and "immutable" in r.headers["cache-control"]
    r = cliente.get("/static/viu_logo.jpg")
    assert r.headers["cache-control"] == "public, max-age=86400"


def test_acessibilidade_basica_do_html(cliente):
    html = cliente.get("/viu-agenciamento/sla").text
    assert 'lang="pt-BR"' in html and 'class="pular"' in html  # idioma e link "pular para o conteúdo"
    assert html.count("<h1") == 1 and "<h2" in html  # um título principal; o slide tem h2
    assert 'aria-label="Tela cheia"' in html and 'aria-label="Recolher menu"' in html
    assert 'aria-roledescription="slide"' in html  # Prazo em uma página só (24/10): sem contador de slides
    imagens = re.findall(r"<img[^>]*>", html)
    assert imagens and all(" alt=" in tag for tag in imagens)  # toda imagem tem alt (vazio quando é decorativa)
    botoes_sem_nome = [b for b in re.findall(r"<button[^>]*>", html) if "aria-label" not in b and "data-abrir-menu" not in b]
    assert not [b for b in botoes_sem_nome if "data-tela-cheia" in b or "data-recolher" in b]  # botões só com ícone têm nome



def test_secoes_preparadas_e_nomes_curtos(cliente):
    r = cliente.get("/viu-agenciamento/negocios-fechados")
    assert r.status_code == 200 and "Aguardando dados" in r.text and "PD05" in r.text  # máscara (D30)
    assert '<span class="menu-texto">Orçamentos</span>' in r.text  # nome curto da área; o cabeçalho segue completo
    # D59: oculta da navegação (menu e abas), a página abre pelo endereço
    assert '<span class="menu-texto">Resultado: negócios fechados</span>' not in r.text and "<span>Resultado</span>" not in r.text
    assert '<span class="menu-texto">SLA de entrega</span>' in r.text and 'title="SLA de entrega"' in r.text  # nomes completo e curto
    r = cliente.get("/viu-agenciamento/previsao")  # D47: com o contrato do job, sem máscara
    assert r.status_code == 200 and "Aguardando dados" not in r.text and 'id="pv-t-mercado"' in r.text


def test_previsao_sem_tela_ficticia(cliente):
    r = cliente.get("/viu-agenciamento/previsao?exemplo=1")  # D47: o exemplo inventado saiu
    assert "Exemplo com dados fictícios" not in r.text and "?exemplo=1" not in r.text


def test_qualidade(cliente):
    r = cliente.get("/viu-agenciamento/qualidade")
    assert r.status_code == 200 and "Operacional" in r.text and "Pontos de atenção" not in r.text


def test_inicio_com_entrada_por_tipo(cliente):
    r = cliente.get("/viu-agenciamento")
    assert r.status_code == 200 and "Quantos pedidos de orçamento chegaram ao longo de 2026 até o momento?" in r.text  # o ano vem dos dados
    assert ">22<" in r.text and "em 2026, até 20 de outubro" in r.text  # E4 (D52: nuvem "Chegaram 22 pedidos de orçamento em 2026, até …")
    assert "janeiro: 16 pedidos, entregues no mês 13, entregues depois 2, saíram sem entrega 1." in r.text  # leitor de tela
    assert "Por tipo: Mercado 10, Inbound 6." in r.text
    assert 'style="' not in r.text and "rotulo-anos" not in r.text and "?ano=" not in r.text  # sem seletor de ano (E0)
    assert 'aria-describedby="tipos-internos"' in r.text and 'id="tipos-internos" role="tooltip"' in r.text
    # E5: só Internos tem dica (GRUPOS_COM_DICA); os demais nomes são texto simples, sem botão nem dica
    assert 'aria-describedby="tipos-mercado"' not in r.text and 'id="tipos-sem-tipo"' not in r.text
    assert '<span class="tipo-nome"><span class="chave t-mercado" aria-hidden="true"></span>Mercado</span>' in r.text
    assert "no mesmo período de 2025." not in r.text  # a comparação com o ano anterior fica só nas colunas da tabela
    assert "Em 2025" in r.text and "13 no mesmo período" in r.text  # E8: base 13 < 30 → só a referência, sem %
    assert 'class="tipos-total"' in r.text and "<td>22</td>" in r.text and "<td>13</td>" in r.text  # linha de total (E9)
    assert "Janeiro de 2025" in r.text  # comparação do mês na dica
    assert ">22<" in cliente.get("/viu-agenciamento?ano=2025").text  # ?ano= é ignorado: sempre o ano da carga


def test_extrato_do_mes(cliente, entrada_diaria, monkeypatch):
    from app import dados
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    # Fevereiro é recente nesta fotografia; outubro ainda não ocorreu.
    recente = entrada_diaria.loc[entrada_diaria["data"].astype(str) < "2026-03"].copy()
    ent._cache.clear()
    monkeypatch.setattr(dados.entrada, "df", lambda: recente)
    r = cliente.get("/viu-agenciamento?ano=2026&mes=2026-02")
    assert r.status_code == 200 and "Fevereiro de 2026" in r.text and "Voltar ao ano" in r.text
    assert "Janeiro: 1 represados, 1 entregues, 0 saíram sem entrega, 0 em aberto." in r.text  # leitor: frase por linha
    assert "Janeiro de 2026" not in r.text and 'role="table"' not in r.text  # dica só com o mês; grade só visual
    assert 'class="dica-tabela" aria-hidden="true"' in r.text
    assert 'id="novos-tipos"' in r.text and "dica-novos-so-atual" in r.text  # fev/2025 sem pedidos: só o mês
    assert "dica-novos-meta" not in r.text and "dica-novos-nota" not in r.text  # dica só com título e tabela (Caio)
    assert 'class="mes mes' in r.text and "mes-selecionado" in r.text
    assert 'aria-describedby="represados-inicio"' in r.text and "Represados do início do mês" in r.text  # E7: fila
    assert "pedidos na demanda do mês" in r.text and "dos novos pedidos (67% deles)" in r.text
    assert "Represados hoje" in r.text and "Represados no fim do mês" not in r.text  # fevereiro é o mês parcial aqui
    assert "Fevereiro de 2026" not in cliente.get("/viu-agenciamento?ano=2026&mes=2026-11").text  # mês sem pedidos: ignora
    assert "Fevereiro de 2026" not in cliente.get("/viu-agenciamento?ano=2026&mes=xx").text


def test_mes_antigo_so_tem_fotografia(cliente, entrada_diaria, monkeypatch):
    from app import dados
    from tests.conftest import com_dias
    # mai–out/2026 com pedidos: fevereiro fica fora dos 6 meses mais recentes com pedidos (E7)
    densa = com_dias(entrada_diaria, ["2026-05-05", "2026-06-05", "2026-07-06", "2026-08-05", "2026-09-04"])
    monkeypatch.setattr(dados.entrada, "df", lambda: densa)
    def proibido():
        raise AssertionError("Meses antigos não devem carregar o fluxo detalhado")
    monkeypatch.setattr(dados.fluxo, "df", proibido)
    r = cliente.get("/viu-agenciamento?ano=2026&mes=2026-02")
    assert r.status_code == 200
    assert 'aria-label="Ver a situação de fevereiro"' in r.text
    assert "Fevereiro de 2026" not in r.text
    assert "?mes=2026-02" not in r.text
    assert "?mes=2026-10" in r.text


def test_extrato_divergente_nao_apresenta_numeros(cliente, monkeypatch, fluxo_mensal):
    from app import dados
    fluxo = fluxo_mensal.copy()
    fluxo["mes_entrada"] = fluxo["mes_entrada"].map(lambda d: d.replace(month=10))
    monkeypatch.setattr(dados.fluxo, "df", lambda: fluxo)
    r = cliente.get("/viu-agenciamento?mes=2026-10")
    assert r.status_code == 200 and "O extrato está sendo atualizado" in r.text
    assert 'id="extrato-titulo"' not in r.text


def test_pagina_atendimento(cliente):
    r = cliente.get("/viu-agenciamento/atendimento")
    assert r.status_code == 200 and "A equipe está dando conta da demanda?" in r.text
    # 24/10/2026: conteúdo apagado para recomeçar; fica só a moldura (cabeçalho, carimbo e título)
    assert 'class="nivel">Gerencial' in r.text and 'style="' not in r.text
    assert "Recebidos em" in r.text and "Entregues ao cliente" in r.text and "Em andamento" in r.text  # big numbers (D53)
    assert "Resolvidos" not in r.text  # D53: resolvido = entregue ao cliente
    assert "<span>Atendimento</span>" not in cliente.get("/viu-agenciamento").text  # V2: fora da navegação; endereço abre


def test_comparacao_do_topo_segue_o_numero(cliente, base_um):
    """Relatório vivo: com base suficiente, a frase diz "a mais" com seta e o percentual sem sinal."""
    r = cliente.get("/viu-agenciamento")
    assert "69%</strong>" in r.text and "a mais que em 2025" in r.text and "▲" in r.text  # 22 ÷ 13 − 1
    # decisão 3 (25/10/2026): seta pastel + tamanho da variação; o leitor ouve "alta de"
    assert '<td class="coluna-variacao"><span class="var-seta var-alta" aria-hidden="true">▲</span><span class="so-leitor">alta de </span>69%</td>' in r.text


def test_dica_dos_novos_por_tipo(cliente, entrada_diaria, fluxo_mensal, base_um, monkeypatch):
    """Dica dos novos (extrato de janeiro): só a tabela (sem barras), grade só visual e uma frase por tipo para o leitor."""
    import pandas as pd
    from app import dados
    recente = entrada_diaria.loc[entrada_diaria["data"].astype(str) < "2026-03"].copy()
    extra = fluxo_mensal.iloc[[2]].copy()  # +14 entregues de janeiro: a fila de janeiro bate com os 16 da coluna
    extra["mes_evento"], extra["quantidade"] = extra["mes_entrada"], 14
    fluxo = pd.concat([fluxo_mensal, extra], ignore_index=True)
    monkeypatch.setattr(dados.entrada, "df", lambda: recente)
    monkeypatch.setattr(dados.fluxo, "df", lambda: fluxo)
    r = cliente.get("/viu-agenciamento?mes=2026-01")
    assert r.status_code == 200 and 'id="novos-tipos"' in r.text and "dica-novos-so-atual" not in r.text
    assert 'class="dica-novos-visual" aria-hidden="true"' in r.text and 'style="' not in r.text
    assert "<svg" not in r.text.split('id="novos-tipos"')[1].split("</li>")[0]  # sem barras 100%
    assert 'class="dica-novos-ano">jan/26<' in r.text and 'class="dica-novos-ano dica-novos-ano-ant">jan/25<' in r.text
    assert 'class="dica-novos-c2">Pedidos<' in r.text and 'class="dica-novos-c5">Pedidos<' in r.text  # cabeçalho em 2 níveis
    assert "comparado a janeiro de 2025." in r.text and "dica-novos-meta" not in r.text  # mês fechado: sem linha de período
    assert '<span class="dica-novos-tipo">Total</span><span>16</span><span>100%</span>' in r.text  # total sem serifa
    assert "Total: 16 em jan/26, 5 em jan/25, variação +220%." in r.text


def test_como_medimos(cliente):
    """Subpágina do SLA: abre pelo botão, guarda o filtro de talentos na volta; só existe no SLA."""
    r = cliente.get("/viu-agenciamento/sla?talentos=exclusivos")
    assert "/viu-agenciamento/sla/como-medimos?talentos=exclusivos" in r.text and "Estudo: como chegamos a esse valor" in r.text
    r = cliente.get("/viu-agenciamento/sla/como-medimos?talentos=exclusivos")
    assert r.status_code == 200 and "Como chegamos ao tempo da equipe</h2>" in r.text and "Exploração dos dados" in r.text and "data-sempre" in r.text
    assert "/viu-agenciamento/sla?talentos=exclusivos#1" in r.text
    assert cliente.get("/viu-agenciamento/atendimento/como-medimos").status_code == 404


def test_exemplo_do_dia(movimentos):
    """E1–E3: exemplo do mês vigente, estável no dia, caminho limpo, mesma soma de C2; espera em aberto aceita;
    sem candidato no mês vigente, volta ao mês anterior."""
    from datetime import date
    from app.apresentacoes.gestao_orcamentos.sla import calculos as c

    dia = date(2026, 10, 24)
    x = c.exemplo(movimentos, "2026-10", "todos", dia)
    assert x == c.exemplo(movimentos, "2026-10", "todos", dia)
    assert x["nome"] == "[Teste] P6"  # outubro (mês vigente): P6, 8 h, ainda aguardando o cliente
    assert [t["nome"] for t in x["etapas"]] == ["Entrada", "Elaboração"] and x["trabalho"] == "8h00"
    assert x["aberto"] and x["fim"]["status"] == "em aberto" and x["pronto"] == "06/10 · 10:00"
    e = c.entregas(movimentos).set_index("projeto_id")["h_trabalho"]
    assert abs(sum(t["h"] for t in x["etapas"]) - e["P6"]) < 1e-9
    # abril como mês vigente: P5 (16 h), com o passo seguinte ao Aguardando registrado
    y = c.exemplo(movimentos, "2026-04", "todos", dia)
    assert y["nome"] == "[Teste] P5" and not y["aberto"] and y["fim"]["status"] == "Em revisão" and y["dias_decisao"] == "3 dias"
    # não exclusivos: só P2 (março, 16 h) — o mês vigente não tem, volta até março
    z = c.exemplo(movimentos, "2026-10", "nao-exclusivos", dia)
    assert z["nome"] == "[Teste] P2" and z["aberto"]
