"""AUTH=iap: conferência do cabeçalho assinado pelo Identity-Aware Proxy (exceção temporária à D10, 30/10/2026).

Contexto: publicação temporária para o gerente apresentar, com o Cloud Run atrás do IAP (só e-mails autorizados). O
controle de acesso próprio (fase 2) ainda não existe e AUTH=off continua recusado em produção. Com AUTH=iap, o app
não confia só na rede: toda requisição precisa do JWT que o IAP assina (`x-goog-iap-jwt-assertion`, ES256), com
emissor `https://cloud.google.com/iap` e o público `IAP_AUDIENCE`. Sem o cabeçalho, ou com um inválido, a resposta é
401 (fecha por padrão: quem chegar ao serviço sem passar pelo IAP não vê nada).

Chaves públicas do IAP (F06, auditoria Codex de 31/10/2026):
- renovadas **fora do caminho da requisição**: passada 1 h da última busca, uma thread em segundo plano busca de novo
  (uma por vez, com retentativa); a requisição segue com as chaves que já tem;
- se a renovação falhar, as chaves anteriores continuam valendo por até 24 h desde a última busca bem-sucedida (o
  token continua sempre verificado pela assinatura; nunca se aceita token sem verificação criptográfica);
- só quando não há chave utilizável (partida a frio ou mais de 24 h sem conseguir renovar) a busca é feita na hora,
  e mesmo assim o middleware chama `autenticar` em `run_in_threadpool` (nada de rede síncrona no event loop); depois
  de uma falha, novas buscas na hora só a cada 60 s (as requisições do meio recebem 503 sem esperar);
- token assinado por uma chave nova (`kid` fora do cache): uma renovação imediata, no máximo uma a cada 60 s;
- "chaves indisponíveis" (503, com log) é diferente de "token inválido" (401).
"""

from __future__ import annotations

import base64
import json
import threading
import time
from typing import NamedTuple

from app import config

CHAVES_URL = "https://www.gstatic.com/iap/verify/public_key"
EMISSOR = "https://cloud.google.com/iap"
CABECALHO = "x-goog-iap-jwt-assertion"
RENOVAR_APOS_S = 3600  # idade das chaves a partir da qual a renovação em segundo plano começa
VALIDADE_MAX_S = 24 * 3600  # sem renovar, as chaves anteriores ainda valem até aqui
INTERVALO_FALHA_S = 60  # depois de uma renovação que falhou, nova tentativa só depois disto
TENTATIVAS = 3
ESPERA_S = (0.5, 1.5)  # entre as tentativas de uma mesma renovação
TIMEOUT_S = 5

_cache = {"chaves": None, "em": 0.0}  # "em" = monotonic da última busca bem-sucedida
_estado = {"renovando": False, "falhou_em": None, "kid_renovado_em": None}
_trava = threading.Lock()  # protege _cache e _estado
_trava_busca = threading.Lock()  # uma busca por vez (single flight)


class ChavesIndisponiveis(Exception):
    """Não há chave pública do IAP utilizável (busca falhou e o cache está vazio ou vencido há mais de 24 h)."""


class Resultado(NamedTuple):
    status: int  # 200 (ok), 401 (token ausente ou inválido), 503 (chaves indisponíveis)
    email: str | None


def _log(nivel: str, msg: str, **campos) -> None:
    from app import dados  # import tardio: dados importa bibliotecas pesadas

    dados.log(nivel, msg, **campos)


def _recente(momento: float | None, agora: float) -> bool:
    return momento is not None and agora - momento < INTERVALO_FALHA_S


def _buscar_chaves() -> dict:
    import requests  # vem com o google-auth (dependência do cliente BigQuery)

    r = requests.get(CHAVES_URL, timeout=TIMEOUT_S)
    r.raise_for_status()
    chaves = r.json()
    if not isinstance(chaves, dict) or not chaves:
        raise ValueError("resposta sem chaves")
    return chaves


def renovar() -> bool:
    """Busca as chaves com retentativa e atualiza o cache. Em falha, mantém as anteriores. Devolve se renovou."""
    with _trava_busca:
        erro = None
        for k in range(TENTATIVAS):
            try:
                chaves = _buscar_chaves()
            except Exception as e:  # noqa: BLE001 (rede, HTTP, JSON)
                erro = e
                if k < TENTATIVAS - 1:
                    time.sleep(ESPERA_S[min(k, len(ESPERA_S) - 1)])
                continue
            with _trava:
                _cache.update(chaves=chaves, em=time.monotonic())
                _estado["falhou_em"] = None
            return True
        with _trava:
            _estado["falhou_em"] = time.monotonic()
            idade = time.monotonic() - _cache["em"] if _cache["chaves"] else None
        _log("ERROR", "IAP: não foi possível renovar as chaves públicas", erro=f"{type(erro).__name__}: {erro}"[:200],
             idade_chaves_s=None if idade is None else int(idade))
        return False


def _renovar_em_segundo_plano() -> None:
    try:
        renovar()
    finally:
        with _trava:
            _estado["renovando"] = False


def iniciar_renovacao() -> bool:
    """Dispara uma renovação em segundo plano, se nenhuma estiver em curso. Devolve se disparou."""
    with _trava:
        if _estado["renovando"]:
            return False
        _estado["renovando"] = True
    threading.Thread(target=_renovar_em_segundo_plano, name="iap-chaves", daemon=True).start()
    return True


def chaves() -> dict:
    """Chaves utilizáveis. Renovação antecipada em segundo plano; busca na hora só sem chave utilizável.
    Levanta ChavesIndisponiveis se nem isso der certo."""
    agora = time.monotonic()
    with _trava:
        atuais, idade = _cache["chaves"], agora - _cache["em"]
        falha_recente = _recente(_estado["falhou_em"], agora)
    if atuais is not None and idade <= VALIDADE_MAX_S:
        if idade > RENOVAR_APOS_S and not falha_recente:
            iniciar_renovacao()
        return atuais
    if falha_recente:  # sem chave utilizável e a última busca falhou há pouco: não prende a requisição de novo
        raise ChavesIndisponiveis("busca das chaves falhou há menos de 60 s")
    if not renovar():  # quem chama já está fora do event loop (run_in_threadpool)
        raise ChavesIndisponiveis("chaves públicas do IAP indisponíveis")
    with _trava:
        return _cache["chaves"]


def _kid(token: str) -> str | None:
    try:
        cabeca = token.split(".", 1)[0]
        return json.loads(base64.urlsafe_b64decode(cabeca + "=" * (-len(cabeca) % 4))).get("kid")
    except Exception:  # noqa: BLE001 (token malformado: a verificação recusa)
        return None


def _decodificar(token: str, certs: dict) -> str | None:
    from google.auth import jwt

    try:
        dados = jwt.decode(token, certs=certs, audience=config.IAP_AUDIENCE)
    except Exception:  # noqa: BLE001 (assinatura, validade, público, token malformado)
        return None
    if dados.get("iss") != EMISSOR:
        return None
    return str(dados.get("email") or "").removeprefix("accounts.google.com:") or None


def autenticar(token: str | None) -> Resultado:
    """Confere o token do IAP. Bloqueante (pode buscar chaves): no middleware, chamar com run_in_threadpool."""
    if not token or not config.IAP_AUDIENCE:
        return Resultado(401, None)
    try:
        certs = chaves()
        kid = _kid(token)
        if kid and kid not in certs:
            # o IAP pode ter trocado a chave: uma renovação imediata, no máximo uma por minuto
            agora = time.monotonic()
            with _trava:
                pode = not _recente(_estado["kid_renovado_em"], agora)
                if pode:
                    _estado["kid_renovado_em"] = agora
            if pode and renovar():
                certs = chaves()
    except ChavesIndisponiveis as e:
        _log("ERROR", "IAP: chaves indisponíveis; requisição recusada com 503", erro=str(e))
        return Resultado(503, None)
    email = _decodificar(token, certs)
    return Resultado(200, email) if email else Resultado(401, None)


def verificar(token: str | None) -> str | None:
    """E-mail do usuário autenticado pelo IAP, ou None se o token faltar, não valer ou as chaves faltarem."""
    r = autenticar(token)
    return r.email if r.status == 200 else None
