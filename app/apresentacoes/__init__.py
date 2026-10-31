"""Apresentações como módulos (D11, D13, D17).

Cada pasta app/apresentacoes/<pasta>/ tem apresentacao.py (APRESENTACAO) e uma subpasta por seção
(<pasta>/<secao>/template.html + cálculos). O menu lateral lista as apresentações; o navegador no topo da lâmina lista
as seções da apresentação aberta. Apresentação nova = pasta nova; seção nova = subpasta nova + uma linha em `secoes`.
"""

import importlib
import pkgutil
from dataclasses import dataclass, replace
from typing import Callable

from app import config


@dataclass(frozen=True)
class Secao:
    slug: str  # endereço: /<apresentação>/<seção>
    titulo: str  # nome completo: menu lateral, leitor de tela (a aba do navegador é só "ViU Agenciamento", 31/10/2026)
    montar: Callable[[dict], dict]  # parâmetros da URL -> contexto do template
    tabelas: tuple[str, ...] = ()
    icone: str = "grafico"  # nome de um ícone de templates/icones.html
    rotulo: str = ""  # nome curto nas abas do topo e na barra do celular (vazio = titulo)
    pergunta: str = ""  # pergunta que a seção responde ("próxima pergunta" e página "O que falta")
    estado: str = "pronta"  # pronta | parcial (parte em máscara) | pendente (só máscara): ver pendencias.py (D30)
    na_reuniao: bool = True  # False = some no modo apresentação (MODO=apresentacao), sem mexer no código (D30)
    oculta: bool = False  # True = fora da navegação (menu, abas, barra, sequência) em qualquer modo; o endereço direto
    #                       continua abrindo (D59: Resultado e Qualidade fora do relatório, por ora)
    nota_estado: str = ""  # o que ainda falta numa seção pronta ("O que falta": "Pronta · meta a oficializar"; batalha 2, G2-4)
    filtro_talentos: bool = False  # aceita ?talentos=: abas, menu e "Próxima pergunta" levam o filtro atual (batalha 2, G4-N1)
    montar_estudo: Callable[[dict], dict] | None = None  # subpágina "Como medimos" (/<seção>/como-medimos), se houver
    antes_do_inicio: bool = False  # V2 (Caio, 30/10/2026): abre o relatório entre a capa e a página inicial (Linha do tempo)

    @property
    def curto(self) -> str:
        return self.rotulo or self.titulo


@dataclass(frozen=True)
class Apresentacao:
    slug: str
    titulo: str  # nome curto no menu lateral (uma linha: o menu vai ter muitas áreas)
    cabecalho: str  # tema que aparece ao lado do logo, no topo dos slides
    ordem: int
    secoes: tuple[Secao, ...]
    icone: str = "maleta"  # ícone da área no menu (templates/icones.html)
    inicio: Callable[[dict], dict] | None = None  # parâmetros da URL -> contexto da página inicial (<pasta>/inicio.html)
    tabelas_inicio: tuple[str, ...] = ()  # tabelas da página inicial (status dos dados); vazio = todas
    perfis: tuple[str, ...] = ("leitor", "admin")
    pasta: str = ""  # nome da pasta (preenchido por descobrir); o endereço (slug) pode ser diferente

    pendencias: tuple = ()  # o que falta para completar a área (pendencias.py): máscaras e página "O que falta"
    pedidos: tuple = ()  # pedidos de decisão do fecho ("O que falta"): (o quê, por quê, quem)
    pergunta_inicio: str = ""  # pergunta da página inicial, para a "próxima pergunta" da última seção voltar a ela
    rotulo_inicio: str = "Início"  # nome da página inicial nas abas e na sequência (D59: "Demanda", com a capa antes)
    # D59 (Caio, 27/10/2026): capa (/<área>/capa) antes da primeira análise e encerramento (/<área>/encerramento) depois
    # da última seção; dicionários com os textos (templates capa.html e encerramento.html). None = sem a página
    capa: dict | None = None
    encerramento: dict | None = None
    capas_secao: dict | None = None  # D61: {slug ("" = página inicial): {titulo, sub}} — capa de seção entre páginas

    def disponiveis(self) -> tuple[Secao, ...]:
        """Seções que existem nesta execução (rotas): todas no computador; no modo apresentação, só as marcadas
        na_reuniao (ou as listadas em SECOES_VISIVEIS) (D30)."""
        if not config.MODO_APRESENTACAO:
            return self.secoes
        if config.SECOES_VISIVEIS:
            return tuple(s for s in self.secoes if s.slug in config.SECOES_VISIVEIS)
        return tuple(s for s in self.secoes if s.na_reuniao)

    def visiveis(self) -> tuple[Secao, ...]:
        """Seções da navegação (menu, abas, barra do celular, sequência): as disponíveis menos as ocultas (D59)."""
        return tuple(s for s in self.disponiveis() if not s.oculta)

    def abertura(self) -> tuple[Secao, ...]:
        """Seções visíveis que vêm antes da página inicial (capa → abertura → Início → análises)."""
        return tuple(s for s in self.visiveis() if s.antes_do_inicio)

    def analises(self) -> tuple[Secao, ...]:
        """Seções visíveis depois da página inicial."""
        return tuple(s for s in self.visiveis() if not s.antes_do_inicio)

    def secao(self, slug: str | None) -> Secao | None:
        if slug is None:
            visiveis = self.visiveis()
            return visiveis[0] if visiveis else None
        return next((s for s in self.disponiveis() if s.slug == slug), None)

    def vizinhas(self, secao: Secao | None) -> tuple[dict | None, dict | None]:
        """Anterior e próxima na ordem da reunião: Início → seções visíveis → "O que falta". Cada uma é
        {href, rotulo, pergunta}; None nas pontas."""
        base = f"/{self.slug}"
        ordem = [{"href": f"{base}/capa", "rotulo": "Capa", "pergunta": self.capa["titulo"], "slug": "capa"}] if self.capa else []
        ordem += [{"href": f"{base}/{s.slug}#1", "rotulo": s.curto, "pergunta": s.pergunta or s.titulo, "slug": s.slug,
                   "filtro": s.filtro_talentos} for s in self.abertura()]
        ordem += [{"href": base, "rotulo": self.rotulo_inicio, "pergunta": self.pergunta_inicio, "slug": None}]
        for s in self.analises():
            ordem.append({"href": f"{base}/{s.slug}#1", "rotulo": s.curto, "pergunta": s.pergunta or s.titulo,
                          "slug": s.slug, "filtro": s.filtro_talentos})
            # D62 (Caio, 27/10/2026): o estudo "Como medimos" entra na sequência logo depois da sua seção (SLA → estudo →
            # Previsão), a mesma ordem da cola do apresentador: as setas levam os dois ao mesmo lugar
            if s.montar_estudo:
                ordem.append({"href": f"{base}/{s.slug}/como-medimos#1", "rotulo": "Como medimos",
                              "pergunta": "E como chegamos a esse número?", "slug": f"{s.slug}/como-medimos",
                              "filtro": s.filtro_talentos})
        # D59 (Caio, 27/10/2026): depois da última seção (Previsão), o encerramento; "O que falta" sai da sequência
        # (a página continua no endereço)
        if self.encerramento:
            ordem.append({"href": f"{base}/encerramento", "rotulo": "Encerramento",
                          "pergunta": self.encerramento["gancho"], "slug": "encerramento"})
        # D61: capa de seção de cada página de análise ("Parte n" na ordem da reunião)
        parte = 0
        for o in ordem:
            chave = "" if o["slug"] is None else o["slug"]
            if self.capas_secao and chave in self.capas_secao:
                parte += 1
                o["capa_secao"] = {"parte": parte, **self.capas_secao[chave]}
        atual = secao if isinstance(secao, str) or secao is None else secao.slug
        # O estudo é um aprofundamento pelo botão, não uma etapa da sequência principal.
        # Ao abri-lo, preservamos sua volta ao SLA e sua saída para a Previsão.
        if not (isinstance(atual, str) and atual.endswith('/como-medimos')):
            ordem = [o for o in ordem if not (o['slug'] or '').endswith('/como-medimos')]
        i = next((i for i, o in enumerate(ordem) if o["slug"] == atual), None)
        if i is None:  # seção oculta aberta pelo endereço (D59): fora da sequência
            return None, None
        return (ordem[i - 1] if i > 0 else None), (ordem[i + 1] if i + 1 < len(ordem) else None)

    def pendencias_de(self, slug: str) -> tuple:
        return tuple(p for p in self.pendencias if p.secao == slug)

    def template(self, secao: Secao) -> str:
        return f"{self.pasta}/{secao.slug.replace('-', '_')}/template.html"


def descobrir() -> list[Apresentacao]:
    lista = []
    for modulo in pkgutil.iter_modules(__path__):
        if modulo.ispkg:
            a = importlib.import_module(f"{__name__}.{modulo.name}.apresentacao").APRESENTACAO
            lista.append(replace(a, pasta=modulo.name))
    return sorted(lista, key=lambda a: a.ordem)
