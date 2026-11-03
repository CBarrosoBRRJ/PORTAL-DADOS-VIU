// Roadmap, PROPOSTA (03/11/2026): painel das imagens, a partir de roadmap.js (o validado segue com o dele). Sem JS, cada
// miniatura é só um link para a (primeira) imagem grande. Com JS, o clique abre o <dialog> #rm-dialogo (showModal: o
// navegador prende o foco no painel):
// - as imagens vêm do atributo data-rm-galeria do link (JSON: titulo, legenda, alt, src, w, h, alta, aw, ah); com mais
//   de uma, botões ‹ › e contador "1 de 3" no topo, e as setas ← → trocam a imagem;
// - ao abrir (e ao trocar de imagem) a imagem aparece INTEIRA, contida na área (object-fit: contain, sem cortar);
// - "Ver em 100%" troca para a versão em alta resolução (a "-alta", quando existe), no tamanho real, com rolagem dentro
//   da área a partir do canto superior esquerdo; o botão vira "Caber na tela" e volta à visão inteira. Clicar na
//   imagem também alterna (no 100%, centrado no ponto clicado); arrastar ou rolar percorre a imagem;
// - entrada "de dentro da miniatura" (Web Animations, ~420 ms) e saída de volta para ela; com movimento reduzido, abre
//   e fecha sem animação;
// - Enter ou Espaço na miniatura abrem; Esc ou clique no fundo fecham; as teclas do painel não chegam à troca de
//   páginas (apresentacao.js); o foco volta a quem abriu.
(function () {
  "use strict";
  var dlg = document.getElementById("rm-dialogo");
  if (!dlg || typeof dlg.showModal !== "function") return;
  var quadro = dlg.querySelector(".rm-dlg-quadro"), titulo = dlg.querySelector(".rm-dlg-titulo");
  var legenda = dlg.querySelector(".rm-dlg-legenda");
  var zoom = dlg.querySelector("[data-rm-zoom]"), fechar = dlg.querySelector("[data-rm-fechar]");
  var dica = dlg.querySelector("[data-rm-dica]"), nav = dlg.querySelector("[data-rm-navegacao]");
  var anterior = dlg.querySelector("[data-rm-anterior]"), proxima = dlg.querySelector("[data-rm-proxima]");
  var contador = dlg.querySelector("[data-rm-contador]");
  var movimento = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: no-preference)") : null;
  var origem = null, itens = [], atual = 0, img = null, real = false, fechando = false, arrasto = null;
  var EASE = "cubic-bezier(0.2, 0.8, 0.2, 1)";

  function anima() { return movimento && movimento.matches && typeof dlg.animate === "function"; }
  function deOrigem() {  // transformação que leva o painel até o retângulo de quem abriu
    var o = origem.getBoundingClientRect(), p = dlg.getBoundingClientRect();
    if (!o.width || !p.width) return null;
    var s = Math.max(0.08, o.width / p.width);
    return "translate(" + (o.left + o.width / 2 - (p.left + p.width / 2)) + "px," + (o.top + o.height / 2 - (p.top + p.height / 2)) + "px) scale(" + s + ")";
  }

  // cheia = 100% (alta resolução, tamanho real, rolável); px/py = ponto a centralizar (fração da imagem) ou nada para
  // começar do canto superior esquerdo
  function visao(cheia, px, py) {
    var x = itens[atual];
    var w = (cheia ? x.aw || x.w : x.w) || 0, h = (cheia ? x.ah || x.h : x.h) || 0;
    real = cheia;
    quadro.classList.toggle("rm-dlg-real", cheia);
    img.src = cheia ? x.alta || x.src : x.src;
    img.setAttribute("width", w); img.setAttribute("height", h);
    zoom.setAttribute("aria-pressed", cheia ? "true" : "false");
    zoom.querySelector("span").textContent = cheia ? "Caber na tela" : "Ver em 100%";
    dica.hidden = !cheia;
    quadro.scrollLeft = 0; quadro.scrollTop = 0;
    if (cheia && px != null) {
      quadro.scrollLeft = Math.max(0, px * w - quadro.clientWidth / 2);
      quadro.scrollTop = Math.max(0, py * h - quadro.clientHeight / 2);
    }
  }

  function mostrar(i) {  // troca a imagem da galeria (volta à visão inteira)
    atual = (i + itens.length) % itens.length;
    var x = itens[atual];
    img = document.createElement("img");
    img.className = "rm-dlg-img";
    img.alt = x.alt || "";
    img.decoding = "async";
    img.draggable = false;
    quadro.replaceChildren(img);
    titulo.textContent = x.titulo || "";
    legenda.textContent = x.legenda || "";
    legenda.hidden = !legenda.textContent;
    contador.textContent = (atual + 1) + " de " + itens.length;
    visao(false);
  }

  function ampliar(link) {
    try { itens = JSON.parse(link.getAttribute("data-rm-galeria") || "[]"); } catch (e) { itens = []; }
    if (!itens.length) return false;
    origem = link;
    nav.hidden = itens.length < 2;
    mostrar(0);
    dlg.classList.remove("rm-fechando");
    dlg.showModal();
    (itens.length > 1 ? proxima : fechar).focus();
    if (anima()) {
      var de = deOrigem();
      if (de) dlg.animate([{ transform: de, opacity: 0.35 }, { transform: "none", opacity: 1 }], { duration: 420, easing: EASE });
    }
    return true;
  }

  function fecharPainel() {
    if (!dlg.open || fechando) return;
    var de = anima() ? deOrigem() : null;
    if (!de) { dlg.close(); return; }
    fechando = true;
    dlg.classList.add("rm-fechando");
    var a = dlg.animate([{ transform: "none", opacity: 1 }, { transform: de, opacity: 0.2 }], { duration: 320, easing: EASE, fill: "forwards" });
    a.onfinish = function () { dlg.close(); a.cancel(); dlg.classList.remove("rm-fechando"); fechando = false; };
  }

  document.querySelectorAll("[data-rm-galeria]").forEach(function (link) {
    link.addEventListener("click", function (ev) {
      if (ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) return;  // nova aba: comportamento normal
      if (ampliar(link)) ev.preventDefault();
    });
    link.addEventListener("keydown", function (ev) {  // Espaço também abre (Enter já abre, como em todo link)
      if (ev.key !== " ") return;
      ev.preventDefault();
      ev.stopPropagation();
      ampliar(link);
    });
  });
  fechar.addEventListener("click", fecharPainel);
  anterior.addEventListener("click", function () { mostrar(atual - 1); });
  proxima.addEventListener("click", function () { mostrar(atual + 1); });
  zoom.addEventListener("click", function () { visao(!real); });
  dlg.addEventListener("cancel", function (ev) { ev.preventDefault(); fecharPainel(); });  // Esc
  dlg.addEventListener("click", function (ev) { if (ev.target === dlg) fecharPainel(); });   // clique no fundo
  dlg.addEventListener("close", function () { if (origem) origem.focus(); });
  dlg.addEventListener("keydown", function (ev) {
    if (itens.length > 1 && !real && (ev.key === "ArrowRight" || ev.key === "ArrowLeft")) {
      ev.preventDefault();
      mostrar(atual + (ev.key === "ArrowRight" ? 1 : -1));
    }
    if (["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", "PageUp", "PageDown", "Escape", " "].indexOf(ev.key) >= 0) ev.stopPropagation();
  });

  // clique na imagem alterna a visão; arrastar (no 100%) percorre a imagem
  quadro.addEventListener("pointerdown", function (ev) {
    if (ev.button !== 0) return;
    arrasto = { x: ev.clientX, y: ev.clientY, l: quadro.scrollLeft, t: quadro.scrollTop, moveu: false };
    if (real) quadro.setPointerCapture(ev.pointerId);
  });
  quadro.addEventListener("pointermove", function (ev) {
    if (!arrasto) return;
    var dx = ev.clientX - arrasto.x, dy = ev.clientY - arrasto.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) arrasto.moveu = true;
    if (real && arrasto.moveu) { quadro.scrollLeft = arrasto.l - dx; quadro.scrollTop = arrasto.t - dy; }
  });
  quadro.addEventListener("pointerup", function (ev) {
    var a = arrasto; arrasto = null;
    if (!a || a.moveu || !img || ev.target !== img) return;
    if (real) { visao(false); return; }
    var x = itens[atual], r = img.getBoundingClientRect();  // visão inteira: imagem contida (object-fit: contain) no retângulo
    var esc = Math.min(r.width / x.w, r.height / x.h);
    var w = x.w * esc, h = x.h * esc, x0 = r.left + (r.width - w) / 2, y0 = r.top + (r.height - h) / 2;
    visao(true, Math.min(1, Math.max(0, (ev.clientX - x0) / w)), Math.min(1, Math.max(0, (ev.clientY - y0) / h)));
  });
  quadro.addEventListener("pointercancel", function () { arrasto = null; });
})();
