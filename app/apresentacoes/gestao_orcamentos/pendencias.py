"""O que falta para completar a área (D30): fonte única das máscaras das telas e da página "O que falta".

Cada pendência diz o dado que falta, onde buscar, como calcular e quem responde. A tela com máscara lista as
pendências da própria seção; a página /viu-agenciamento/o-que-falta lista todas. O prompt para o projeto da gold
(docs/prompt_dados_pendentes.md) usa os mesmos códigos: mudou aqui, atualize lá e na ficha docs/paginas/o_que_falta.md
(seções 3 e 4), que tests/test_documentacao.py compara com este arquivo.

O que NÃO entra aqui: as decisões internas do Caio (vencedor do Mercado, nov/dez como cenário, régua do Atendimento,
recorte do slide 6, veredito da meta…), que ficam no PRD, seção 9.7 (DC1–DC16). Na tela da diretoria elas aparecem só
como a nota de estado da seção (`Secao.nota_estado` em apresentacao.py: "meta a oficializar", "2 decisões abertas").
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pendencia:
    codigo: str  # PDxx: o mesmo no site, no PRD e no prompt
    secao: str  # slug da seção onde a resposta vai aparecer ("fora" = fora do escopo atual da área)
    dado: str  # o que falta, em linguagem de quem lê a tela
    onde: str  # tabela, planilha ou sistema de origem
    como: str  # regra de cálculo, em uma frase
    quem: str  # quem tem a resposta


PENDENCIAS = (
    Pendencia("PD19", "atendimento", "Data das saídas e identificação da carga",
              "gold de entradas e fluxo, a partir dos eventos da silver",
              "Mesmo corte e carga nas tabelas; sinalizar saídas sem data e separar atribuição de evento observado",
              "Caio (gold)"),
    Pendencia("PD20", "talentos", "Continuidade dos dados na virada do ano",
              "gold de talentos com anos e identidade estável dos pedidos",
              "Conciliar entradas e talentos sem trocar manualmente o board; preservar origem e exclusividade histórica",
              "Caio (gold)"),
    Pendencia("PD01", "talentos", "Exclusividade do talento na base de entradas",
              "silver 2026 (exclusivo, talento) levada para a gold de entradas",
              "Pedidos por mês e grupo (exclusivo, não exclusivo, sem talento), com as regras de data do Início",
              "Caio (gold)"),
    Pendencia("PD02a", "talentos", "Ranking dos exclusivos lido da gold (hoje a dica lê a silver)",
              "gold de PD01 + cadastro de talentos exclusivos (39 nomes)",
              "Pedidos por talento no período, pela exclusividade na data do pedido; mesmo top 10 da dica",
              "Caio (gold)"),
    Pendencia("PD02b", "talentos", "Cadastro limpo de talentos não exclusivos",
              "monday (interveniência) e padronização de nomes na silver",
              "Padronizar as grafias e só então ranquear, com mínimo de 10 pedidos",
              "Equipe de Talentos"),
    Pendencia("PD03", "talentos", "Lista de exclusivos de 2025 com vigência",
              "board 2025 e cadastro de talentos exclusivos (início e fim do contrato)",
              "Mesma regra de 2026: exclusivo = na lista vigente na data do pedido",
              "Equipe de Agenciamento"),
    Pendencia("PD05", "negocios-fechados", "Contratações fechadas: talentos, volume e ticket médio",
              "planilha de contratações (Mayara), a subir para o BigQuery; vendido? do board como conferência",
              "Fechamentos por mês, talento e tipo; ticket médio = valor ÷ contratos; conversão sobre entregues",
              "Mayara + Caio"),
    Pendencia("PD06", "negocios-fechados", "Regra do que acontece depois da entrega",
              "gold do SLA (status atual, alerta, encerrado sem entrega)",
              "Entregues por destino: aguardando, em alerta, encerrado sem retorno, declinado",
              "Caio + equipe de orçamentos"),
    Pendencia("PD18", "negocios-fechados", "Prazo de pagamento dos intervenientes",
              "contratos e pagamentos (sistema financeiro)",
              "Dias do contrato assinado até o pagamento, por mês",
              "Financeiro + Caio"),
    Pendencia("PD07", "atendimento", "Motivo de quem saiu sem entrega",
              "gold fluxo mensal (status no evento)",
              "Separar declinado, standby e encerrado por mês",
              "Caio (gold)"),
    Pendencia("PD08", "atendimento", "Regra de entrega sem histórico de status",
              "gold de entradas + decisão da equipe (185 entregas só com data de saída)",
              "Contar ou não como entrega; nota na ficha",
              "Equipe de orçamentos"),
    # D48 (26/10/2026): execução mensal; o registro é um por retrato (mês fechado), gravado pelo job (P7 de ml/previsao.py)
    Pendencia("PD09", "previsao", "Acerto da previsão fora do teste, mês a mês",
              "registro de uma previsão oficial por retrato mensal (ml/saida/historico_previsoes.jsonl e retratos/<mês>.json, já gravados) + gold de entradas",
              "A cada mês fechado (out/26 é o 1º), comparar com o previsto no retrato anterior; decidir se o Mercado mantém a rede neural (vence o teste jun–set, perde da ingênua em jan–mai)",
              "Caio (critério)"),
    # batalha 2 (G1-N11, G4-N13, 26/10/2026)
    Pendencia("PD22", "previsao", "Previsão na virada do ano",
              "retratos de out a dez/2026 (horizonte de 3 meses chega a jan/27) e PD20",
              "Decidir o que a tela mostra em nov/dez (eixo só 2026 hoje; os meses de 2027 já saem com o ano, \"jan/27\") e quando o eixo passa a 2027",
              "Caio (decisão)"),
    Pendencia("PD23", "previsao", "Job mensal da previsão em produção",
              "hoje roda no computador do Caio (ml/, rotina disparada pelo site local); em produção: Cloud Run Job + bucket",
              "Rodar a rotina mensal fora do site, gravar previsao.json, retratos e histórico num bucket e ler de lá; comandos de GCP com o Caio",
              "Caio (GCP)"),
    Pendencia("PD10", "previsao", "Datas reais de 2025 para confirmar o efeito de fim de ano",
              "gold de entradas: 17% a 25% das datas de 2025 são estimadas (PD03/F10)",
              "Com as datas reais, medir de novo a queda de nov/dez (2025: −31% a −59% sobre out); a janela de 12 meses não aprende fim de ano",
              "Caio (gold)"),
    Pendencia("PD12", "qualidade", "Evolução das pendências de preenchimento",
              "silver de qualidade e pendências diárias (desde 21/10), levadas para uma gold",
              "Abertas por dia e categoria; corrigidas; tempo até a correção",
              "Caio (gold)"),
    Pendencia("PD13", "qualidade", "Foto de fim de mês da base",
              "gold com o mês de referência guardado",
              "Diferença entre a foto do mês e a leitura de hoje",
              "Caio (gold)"),
    # D55 (26/10/2026): regra do Caio — não existe Inbound de talento não exclusivo; o que aparece assim é erro de cadastro
    Pendencia("PD24", "qualidade", "Inbound marcado como talento não exclusivo",
              "silver 2026 (TAB_TALENTO_ORIGEM, mesmo critério de app/sql/talentos_ano.sql): pedidos de Inbound cujo talento "
              "está como não exclusivo; contados por mês em ml/dados/exclusividade.csv e no bloco \"qualidade\" do previsao.json",
              "Corrigir o cadastro na origem (talento ou tipo de input) e alarmar na gold; até lá a Previsão conta esses "
              "pedidos como exclusivos e o filtro \"Não exclusivos\" do Inbound fica \"Não se aplica\"",
              "Caio (gold) + equipe de orçamentos"),
    Pendencia("PD15", "sla", "SLA de entrega em 2025",
              "não existe: o board de 2025 não guardou o histórico de status",
              "Sem cálculo possível; comparação com o ano anterior começa em 2027",
              "Não disponível"),
    # D-SLA-5 (25/10/2026): o site recalcula hoje regras que deveriam vir prontas da gold
    Pendencia("PD21", "sla", "Tempo da equipe pronto na gold",
              "fase própria para o Retorno Marca; manter quem já teve a 1ª entrega e voltou à equipe; coluna de "
              "pacote/lote; relógio para cards criados direto em elaboração/revisão; pedidos em andamento; v2 sem almoço",
              "SLA lido direto da gold, sem recálculo no site; mediana sem viés dos que ainda não foram entregues",
              "Caio (gold)"),
    Pendencia("PD16", "fora", "Análise por marca, cliente e setor",
              "catálogo de marcas no monday, CNPJ e setor no Salesforce (aguarda liberação)",
              "Cruzar pelo CNPJ, que resolve nomes diferentes da mesma marca",
              "Caio + Salesforce"),
)


def da_secao(slug: str) -> tuple[Pendencia, ...]:
    return tuple(p for p in PENDENCIAS if p.secao == slug)

# Pedidos de decisão que fecham a reunião (página "O que falta", 1º slide). Curtos: um verbo e quem decide.
PEDIDOS = (
    ("Oficializar a meta do SLA", "metade dos orçamentos prontos em até 2 dias de trabalho (16 h); hoje uma sugestão", "Diretoria"),
    ("Subir a planilha de contratações para o BigQuery", "abre a tela de Resultado (talentos contratados, volume e ticket médio)", "Mayara + Caio"),
    ("Levar a exclusividade do talento para a base de entradas", "abre a divisão por mês e os rankings da tela de Talentos", "Caio (gold)"),
    ("Validar com a equipe as regras de entrega e de encerramento", "o que conta como entrega sem histórico e o que é “Encerrado”", "Equipe de orçamentos"),
)
