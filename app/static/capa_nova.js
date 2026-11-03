/* Proposta de capa nova (Caio, 03/11/2026): o fluxo contínuo do desenho roda por SMIL no SVG (capa_nova.html; só
   posição e opacidade). Este arquivo só pausa o SVG:
   - com movimento reduzido (o CSS também esconde as partículas e o pulso): a composição fica parada e completa;
   - com a aba oculta (economia); ao voltar, retoma. */
(function () {
  "use strict";
  var svg = document.querySelector(".cn-desenho svg");
  if (!svg || typeof svg.pauseAnimations !== "function") return;
  var reduzido = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;

  function aplicar() {
    if ((reduzido && reduzido.matches) || document.hidden) svg.pauseAnimations();
    else svg.unpauseAnimations();
  }

  document.addEventListener("visibilitychange", aplicar);
  if (reduzido) {
    if (reduzido.addEventListener) reduzido.addEventListener("change", aplicar);
    else if (reduzido.addListener) reduzido.addListener(aplicar);
  }
  aplicar();
})();
