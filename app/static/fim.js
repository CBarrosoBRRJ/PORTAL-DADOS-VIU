/* Encerramento (V2, Caio, 31/10/2026): o mascote do canto inferior direito (balão de conversa) acena, pisca, flutua e
   o coração pulsa em loops CONTÍNUOS, sem pausa, por animações SMIL do próprio SVG (encerramento.html; só rotação, escala
   e translação). Este arquivo:
   - começa os loops depois da entrada (ele chega, assenta e passa a acenar sem parar até a pessoa sair da página);
   - não anima nada com movimento reduzido: o mascote fica parado, sorrindo, de olhos abertos (única exceção);
   - pausa com a aba oculta (economia; não muda o que a pessoa vê) e retoma ao voltar.
   Sem JS os loops nem começam (begin="indefinite"): a composição fica parada. */
(function () {
  "use strict";
  var svg = document.querySelector(".fim-boneco");
  if (!svg || typeof svg.pauseAnimations !== "function") return;
  var reduzido = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var comecou = false, espera = null;

  function parado() { return (reduzido && reduzido.matches) || document.hidden; }

  function comecar() {
    if (comecou || parado()) return;
    comecou = true;
    Array.prototype.forEach.call(svg.querySelectorAll("animateTransform"), function (a) {
      if (typeof a.beginElement === "function") a.beginElement();
    });
  }

  function aplicar() {
    if (parado()) svg.pauseAnimations();
    else svg.unpauseAnimations();
    if (!parado() && !comecou && !espera) espera = setTimeout(function () { espera = null; comecar(); }, 1100);
  }

  document.addEventListener("visibilitychange", aplicar);
  if (reduzido) {
    if (reduzido.addEventListener) reduzido.addEventListener("change", aplicar);
    else if (reduzido.addListener) reduzido.addListener(aplicar);
  }
  aplicar();
})();
