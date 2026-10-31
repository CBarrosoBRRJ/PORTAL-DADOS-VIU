// Roadmap, protótipo A: etapas como abas (mouse, foco, clique ou setas), ampliação das miniaturas e pausa do movimento.
(() => {
  "use strict";
  const raiz = document.documentElement;
  raiz.classList.add("js");

  const abas = [...document.querySelectorAll('.marcos [role="tab"]')];
  const paineis = abas.map((a) => document.getElementById(a.getAttribute("aria-controls")));
  const caixa = document.querySelector(".detalhes");
  if (!abas.length || paineis.some((p) => !p) || !caixa) return;

  let ativa = Math.max(0, abas.findIndex((a) => a.getAttribute("aria-selected") === "true"));

  function abrir(i, focar) {
    if (i < 0 || i >= abas.length) return;
    abas.forEach((a, k) => {
      const sim = k === i;
      a.setAttribute("aria-selected", String(sim));
      a.tabIndex = sim ? 0 : -1;
      paineis[k].hidden = !sim;
    });
    caixa.classList.remove(`ativa-${ativa + 1}`);
    caixa.classList.add(`ativa-${i + 1}`);
    ativa = i;
    if (focar) abas[i].focus();
  }
  abrir(ativa, false);

  abas.forEach((a, i) => {
    a.addEventListener("click", () => abrir(i, false));
    a.addEventListener("focus", () => abrir(i, false));
    // passar o mouse mostra a etapa (só com ponteiro fino, para não brigar com o toque)
    a.addEventListener("pointerenter", (ev) => { if (ev.pointerType === "mouse" && i !== ativa) abrir(i, false); });
  });
  document.querySelector(".marcos").addEventListener("keydown", (ev) => {
    const mapa = { ArrowRight: ativa + 1, ArrowLeft: ativa - 1, ArrowDown: ativa + 1, ArrowUp: ativa - 1, Home: 0, End: abas.length - 1 };
    if (!(ev.key in mapa)) return;
    ev.preventDefault();
    ev.stopPropagation();
    abrir((mapa[ev.key] + abas.length) % abas.length, true);
  });

  // ampliação das miniaturas
  const dialogo = document.querySelector(".amplia");
  if (dialogo && typeof dialogo.showModal === "function") {
    const img = dialogo.querySelector(".amplia-img");
    const tit = dialogo.querySelector("#amplia-titulo");
    const leg = dialogo.querySelector(".amplia-legenda");
    const alta = dialogo.querySelector(".amplia-alta");
    let origem = null;
    document.querySelectorAll(".mini[data-grande]").forEach((b) => {
      b.addEventListener("click", () => {
        origem = b;
        img.src = b.dataset.grande;
        img.alt = b.dataset.alt || "";
        tit.textContent = b.dataset.titulo || "";
        leg.textContent = b.dataset.legenda || "";
        alta.href = b.dataset.alta || "#";
        alta.hidden = !b.dataset.alta;
        dialogo.showModal();
        dialogo.querySelector(".amplia-fechar").focus();
      });
    });
    dialogo.querySelector(".amplia-fechar").addEventListener("click", () => dialogo.close());
    dialogo.addEventListener("click", (ev) => { if (ev.target === dialogo) dialogo.close(); });
    dialogo.addEventListener("close", () => { if (origem) origem.focus(); });
  }

  // pausar / retomar o movimento contínuo
  const mov = document.querySelector(".movimento");
  if (mov) {
    mov.addEventListener("click", () => {
      const parado = raiz.classList.toggle("parado");
      mov.textContent = parado ? "Retomar o movimento" : "Pausar o movimento";
    });
  }
})();
