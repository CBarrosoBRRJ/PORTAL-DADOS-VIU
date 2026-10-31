// D62 (Caio, 27/10/2026): portal e cola do apresentador (porta 8200) andam juntos. O portal avisa em /sinc a página em
// que está (inclusive o slide do estudo, que troca o # sem recarregar) e, a cada 600 ms, confere se a cola pediu outra
// página; se pediu, vai até ela. Mesma normalização da cola: sem a query, sem o # (menos no estudo, onde o # é o slide).
// Em tela cheia quem sincroniza é a página dentro do quadro; a janela de fora fica quieta. Página pré-carregada (o
// navegador prepara a próxima ao parar o mouse num link) só começa quando é de fato aberta.
(function () {
  var quadro = null;
  try { quadro = window.frameElement; } catch (e) { quadro = null; }
  if (quadro && !quadro.hasAttribute("data-quadro-tela-cheia")) return;

  // no slide 2 do estudo o quadro (?passo=, Formato/Sino/Faixas) também é posição: "…#2:N" (N = 1 sem passo)
  function normal(url) {
    var u = new URL(url, location.href);
    var base = u.pathname.replace(/\/+$/, "") || "/";
    if (!/\/como-medimos$/.test(base) || !u.hash) return base;
    return u.hash === "#2" ? base + "#2:" + (u.searchParams.get("passo") || "1") : base + u.hash;
  }
  function aqui() { return location.pathname + location.search + location.hash; }
  function emQuadro() { return !!document.querySelector("iframe[data-quadro-tela-cheia]"); }

  var versao = -1, sessao = null, publicado = null, ocupado = false;

  // o servidor reiniciou (outra sessão): a versão recomeçou do zero; esquece a que já tinha visto
  function ler(r) {
    return r.ok ? r.json().then(function (s) {
      if (s && s.sessao !== sessao) { sessao = s.sessao; versao = -1; }
      return s;
    }) : null;
  }
  function enviar() {
    publicado = normal(aqui());
    return fetch("/sinc", { method: "POST", headers: { "Content-Type": "text/plain" }, cache: "no-store",
                            credentials: "same-origin", body: JSON.stringify({ url: aqui(), origem: "portal" }) })
      .then(ler).then(function (s) { if (s) versao = s.versao; });
  }
  function ir(url) {
    var alvo = new URL(url, location.href);
    if (alvo.pathname === location.pathname && alvo.hash) {
      // estudo: mesmo endereço, outro slide → só o # (o slide troca sem recarregar)
      if (alvo.hash !== location.hash) location.hash = alvo.hash;
      // slide 2: o quadro pedido (Formato/Sino/Faixas) → o ponto do painel, sem recarregar
      var passo = alvo.searchParams.get("passo");
      var ponto = alvo.hash === "#2" && passo && document.querySelector('[data-explora-ir="' + passo + '"]');
      if (ponto) ponto.click();
      return;
    }
    location.assign(alvo.pathname + alvo.search + alvo.hash);
  }
  function ciclo() {
    if (ocupado || emQuadro()) return;
    ocupado = true;
    var passo = normal(aqui()) !== publicado ? enviar() :
      fetch("/sinc", { cache: "no-store", credentials: "same-origin" }).then(ler).then(function (s) {
        if (!s) return;
        if (s.versao > versao && s.origem === "cola" && s.url && normal(s.url) !== normal(aqui())) {
          versao = s.versao;
          publicado = normal(s.url);
          ir(s.url);
        } else if (s.versao > versao) versao = s.versao;
      });
    passo.catch(function () { /* portal sem /sinc ou fora do ar: tenta de novo no próximo ciclo */ })
      .then(function () { ocupado = false; });
  }
  function comecar() {
    enviar().catch(function () {}).then(function () { setInterval(ciclo, 600); });
  }
  if (document.prerendering) document.addEventListener("prerenderingchange", comecar, { once: true });
  else comecar();
})();
