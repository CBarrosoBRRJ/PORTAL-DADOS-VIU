// Roadmap, protótipo A (v2): tudo fica à vista; o JS só abre as miniaturas no <dialog>. Sem JS, o link abre a imagem.
(() => {
  "use strict";
  const dialogo = document.querySelector(".amplia");
  if (!dialogo || typeof dialogo.showModal !== "function") return;
  const img = dialogo.querySelector(".amplia-img");
  const tit = dialogo.querySelector("#amplia-titulo");
  const leg = dialogo.querySelector(".amplia-legenda");
  const alta = dialogo.querySelector(".amplia-alta");
  const fechar = dialogo.querySelector(".amplia-fechar");
  let origem = null;

  document.querySelectorAll("a.mini").forEach((link) => {
    link.addEventListener("click", (ev) => {
      ev.preventDefault();
      origem = link;
      img.src = link.getAttribute("href");
      img.alt = link.dataset.alt || "";
      tit.textContent = link.dataset.titulo || "";
      leg.textContent = link.dataset.legenda || "";
      alta.hidden = !link.dataset.alta;
      alta.href = link.dataset.alta || "#";
      dialogo.showModal();
      fechar.focus();
    });
  });
  fechar.addEventListener("click", () => dialogo.close());
  dialogo.addEventListener("click", (ev) => { if (ev.target === dialogo) dialogo.close(); });
  dialogo.addEventListener("close", () => { if (origem) origem.focus(); });
})();
