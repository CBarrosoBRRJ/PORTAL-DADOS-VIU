// Roadmap (V2, Caio, 31/10/2026; 5ª versão): painel das imagens. Sem JS, cada miniatura é só um link para a
// (primeira) imagem grande. Com JS, o clique abre o <dialog> #rm-dialogo (showModal: o navegador prende o foco no painel)
// num painel grande sobre o fundo escurecido:
// - as imagens vêm do atributo data-rm-galeria do link (JSON: titulo, legenda, alt, src, w, h, alta, aw, ah); com mais
//   de uma, o painel vira galeria: botões ‹ › e contador "1 de 2" no topo, e as setas ← → trocam a imagem;
// - entrada "de dentro da miniatura": o painel cresce a partir da posição de quem abriu (Web Animations, ~420 ms) e, ao
//   fechar (Fechar, Esc ou clique no fundo), volta para lá; com movimento reduzido, abre e fecha sem animação;
// - "Ver em 100%" (ou clique na imagem) troca a visão inteira pela versão em alta resolução, no tamanho real, centrada
//   no ponto clicado; arrastar ou rolar percorre a imagem (aí as setas rolam a imagem); novo clique volta;
// - Enter ou Espaço na miniatura abrem o painel; as teclas do painel não chegam à troca de páginas (apresentacao.js);
//   o foco volta a quem abriu.
(function () {
  "use strict";
  var dlg = document.getElementById("rm-dialogo");
  if (!dlg || typeof dlg.showModal !== "function") return;
  var quadro = dlg.querySelector(".rm-dlg-quadro"), titulo = dlg.querySelector(".rm-dlg-titulo");
  var legenda = dlg.querySelector(".rm-dlg-legenda"), abrir = dlg.querySelector(".rm-dlg-abrir");
  var zoom = dlg.querySelector("[data-rm-zoom]"), fechar = dlg.querySelector("[data-rm-fechar]");
  var dica = dlg.querySelector("[data-rm-dica]"), nav = dlg.querySelector("[data-rm-navegacao]");
  var anterior = dlg.querySelector("[data-rm-anterior]"), proxima = dlg.querySelector("[data-rm-proxima]");
  var contador = dlg.querySelector("[data-rm-contador]");
  var movimento = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: no-preference)") : null;
  var origem = null, itens = [], atual = 0, img = null, real = false, fechando = false, arrasto = null, larg = 0, alt = 0;
  var EASE = "cubic-bezier(0.2, 0.8, 0.2, 1)";

  function anima() { return movimento && movimento.matches && typeof dlg.animate === "function"; }
  function deOrigem() {  // transformação que leva o painel até o retângulo de quem abriu
    var o = origem.getBoundingClientRect(), p = dlg.getBoundingClientRect();
    if (!o.width || !p.width) return null;
    var s = Math.max(0.08, o.width / p.width);
    return "translate(" + (o.left + o.width / 2 - (p.left + p.width / 2)) + "px," + (o.top + o.height / 2 - (p.top + p.height / 2)) + "px) scale(" + s + ")";
  }

  function visao(cheia, px, py) {  // cheia = 100% (alta resolução, rolável); px/py = ponto clicado (fração da imagem)
    var x = itens[atual];
    real = cheia;
    img.src = cheia ? x.alta : x.src;
    larg = (cheia ? x.aw : x.w) || 0;
    alt = (cheia ? x.ah : x.h) || 0;
    img.setAttribute("width", larg); img.setAttribute("height", alt);
    quadro.classList.toggle("rm-dlg-real", cheia);
    zoom.setAttribute("aria-pressed", cheia ? "true" : "false");
    zoom.querySelector("span").textContent = cheia ? "Ver inteira" : "Ver em 100%";
    dica.hidden = !cheia;
    if (cheia) {
      quadro.scrollLeft = Math.max(0, (px == null ? 0 : px) * larg - quadro.clientWidth / 2);
      quadro.scrollTop = Math.max(0, (py == null ? 0 : py) * alt - quadro.clientHeight / 2);
    } else {
      quadro.scrollLeft = 0; quadro.scrollTop = 0;
    }
  }

  function mostrar(i) {  // troca a imagem da galeria (volta à visão inteira)
    atual = (i + itens.length) % itens.length;
    var x = itens[atual];
    img = document.createElement("img");
    img.className = "rm-dlg-img";
    img.alt = x.alt || "";
    img.decoding = "async";
    quadro.replaceChildren(img);
    titulo.textContent = x.titulo || "";
    legenda.textContent = x.legenda || "";
    legenda.hidden = !legenda.textContent;
    abrir.href = x.alta || x.src;
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
  zoom.addEventListener("click", function () { visao(!real, 0.5, 0.5); });
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

  // clique na imagem alterna a visão; arrastar (na visão de 100%) percorre a imagem
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
    var r = img.getBoundingClientRect();  // visão inteira: a imagem está contida (object-fit: contain) no retângulo
    var esc = Math.min(r.width / larg, r.height / alt);
    var w = larg * esc, h = alt * esc, x0 = r.left + (r.width - w) / 2, y0 = r.top + (r.height - h) / 2;
    visao(true, Math.min(1, Math.max(0, (ev.clientX - x0) / w)), Math.min(1, Math.max(0, (ev.clientY - y0) / h)));
  });
  quadro.addEventListener("pointercancel", function () { arrasto = null; });
})();
