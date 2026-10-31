/* Capa (V2, Caio, 30/10/2026): fluxo contínuo da ilustração "dados → área". As partículas andam por animações SMIL
   do próprio SVG (capa.html; só transform e opacity). Animação contínua por decisão do Caio; o botão de pausa foi
   retirado por decisão dele em 30/10/2026. Este arquivo só para a animação:
   - com movimento reduzido (o CSS também esconde as partículas): a composição fica parada;
   - com a aba oculta (economia); ao voltar, retoma. */
(function () {
  "use strict";
  var svg = document.querySelector(".capa-desenho svg");
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
