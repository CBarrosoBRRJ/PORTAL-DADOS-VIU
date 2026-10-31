// LIA (V2, Caio, 30/10/2026): o botão "Ver a LIA na prática" abre o vídeo num pop-up (<dialog> #lia-video, showModal:
// o navegador prende o foco no painel). Mesmo gesto do painel de imagens do Roadmap (roadmap.js): o painel cresce a
// partir do botão (~420 ms) e volta para ele ao fechar; com movimento reduzido, abre e fecha sem animação.
// - Fecha com o botão Fechar, Esc ou clique no fundo; o vídeo pausa ao fechar; o foco volta ao botão.
// - Sem autoplay: o play é da pessoa (controls, preload="metadata").
// - As setas e o espaço dentro do pop-up não trocam de página (o diálogo segura as teclas).
// Sem JS, o botão é um link para a página antiga do vídeo (/viu-agenciamento/lia-na-pratica, oculta da navegação).
(function () {
  "use strict";
  var dlg = document.getElementById("lia-video");
  var botao = document.querySelector("[data-lia-video]");
  if (!dlg || !botao || typeof dlg.showModal !== "function") return;
  var fechar = dlg.querySelector("[data-lia-fechar]");
  var video = dlg.querySelector("video");
  var movimento = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: no-preference)") : null;
  var fechando = false;
  var EASE = "cubic-bezier(0.2, 0.8, 0.2, 1)";

  function anima() { return movimento && movimento.matches && typeof dlg.animate === "function"; }
  function deOrigem() {  // transformação que leva o painel até o retângulo do botão
    var o = botao.getBoundingClientRect(), p = dlg.getBoundingClientRect();
    if (!o.width || !p.width) return null;
    var s = Math.max(0.08, o.width / p.width);
    return "translate(" + (o.left + o.width / 2 - (p.left + p.width / 2)) + "px," + (o.top + o.height / 2 - (p.top + p.height / 2)) + "px) scale(" + s + ")";
  }

  function abrir() {
    dlg.classList.remove("lia-fechando");
    dlg.showModal();
    fechar.focus();
    if (anima()) {
      var de = deOrigem();
      if (de) dlg.animate([{ transform: de, opacity: 0.35 }, { transform: "none", opacity: 1 }], { duration: 420, easing: EASE });
    }
  }

  function fecharPainel() {
    if (!dlg.open || fechando) return;
    if (video && !video.paused) video.pause();
    var de = anima() ? deOrigem() : null;
    if (!de) { dlg.close(); return; }
    fechando = true;
    dlg.classList.add("lia-fechando");
    var a = dlg.animate([{ transform: "none", opacity: 1 }, { transform: de, opacity: 0.2 }], { duration: 320, easing: EASE, fill: "forwards" });
    a.onfinish = function () { dlg.close(); a.cancel(); dlg.classList.remove("lia-fechando"); fechando = false; };
  }

  botao.addEventListener("click", function (ev) {
    if (ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) return;  // nova aba: comportamento normal
    ev.preventDefault();
    abrir();
  });
  fechar.addEventListener("click", fecharPainel);
  dlg.addEventListener("cancel", function (ev) { ev.preventDefault(); fecharPainel(); });  // Esc
  dlg.addEventListener("click", function (ev) { if (ev.target === dlg) fecharPainel(); });   // clique no fundo
  dlg.addEventListener("close", function () { if (video && !video.paused) video.pause(); botao.focus(); });
  dlg.addEventListener("keydown", function (ev) {
    if (["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", "Escape", " "].indexOf(ev.key) >= 0) ev.stopPropagation();
  });
})();
