// Roadmap — protótipo B: etapa em foco (abas), ciclo lento automático com pausa, visor das imagens.
// Sem JS a página mostra todas as etapas; com JS vira lâmina com uma etapa por vez.
(() => {
  "use strict";
  document.documentElement.classList.add("js");

  const DUR = 9000; // ms por etapa no ciclo automático
  const calmo = window.matchMedia("(prefers-reduced-motion: reduce)");

  const iniciar = () => {
    const lamina = document.getElementById("lamina");
    const lista = lamina.querySelector(".marcos");
    const marcos = [...lista.querySelectorAll(".marco")];
    const nos = marcos.map((m) => m.querySelector(".no"));
    const paineis = marcos.map((m) => document.getElementById("etapa-" + m.dataset.etapa));
    const palco = lamina.querySelector(".palco");
    const numeral = palco.querySelector(".numeral");
    const controles = palco.querySelector(".controles");
    const btPausa = controles.querySelector('[data-ctl="pausa"]');
    const tempo = controles.querySelector(".tempo");
    const visor = lamina.querySelector(".visor");

    let atual = 0;
    let pausado = calmo.matches; // movimento reduzido: o ciclo começa parado
    let segurando = 0;           // mouse/foco dentro do palco seguram o ciclo sem pausá-lo
    let relogio = null;

    // semântica de abas
    lista.setAttribute("role", "tablist");
    lista.setAttribute("aria-label", "Etapas do caminho");
    lista.setAttribute("aria-orientation", "horizontal");
    marcos.forEach((m) => m.setAttribute("role", "presentation"));
    nos.forEach((no, i) => {
      no.setAttribute("role", "tab");
      paineis[i].setAttribute("role", "tabpanel");
      paineis[i].setAttribute("tabindex", "-1");
    });
    controles.hidden = false;

    const agendar = () => {
      clearTimeout(relogio);
      tempo.classList.remove("corre");
      if (pausado || segurando > 0 || visor.open) return;
      void tempo.offsetWidth; // reinicia a barra
      tempo.classList.add("corre");
      relogio = setTimeout(() => ir((atual + 1) % marcos.length, false), DUR);
    };

    const ir = (i, doUsuario) => {
      atual = i;
      marcos.forEach((m, k) => m.classList.toggle("ativo", k === i));
      nos.forEach((no, k) => {
        no.setAttribute("aria-selected", String(k === i));
        no.tabIndex = k === i ? 0 : -1;
      });
      paineis.forEach((p, k) => {
        p.hidden = k !== i;
        p.classList.remove("entra");
      });
      void paineis[i].offsetWidth;
      paineis[i].classList.add("entra");
      numeral.textContent = String(i + 1);
      if (doUsuario) pausar(true);
      agendar();
    };

    const pausar = (sim) => {
      pausado = sim;
      lamina.classList.toggle("pausado", sim);
      btPausa.setAttribute("aria-pressed", String(sim));
      btPausa.querySelector(".ctl-txt").textContent = sim ? "Continuar" : "Pausar";
      btPausa.setAttribute("aria-label", sim ? "Continuar a apresentação automática" : "Pausar a apresentação automática");
      agendar();
    };

    nos.forEach((no, i) => no.addEventListener("click", () => ir(i, true)));
    lista.addEventListener("keydown", (ev) => {
      const n = marcos.length;
      const mapa = { ArrowRight: atual + 1, ArrowUp: atual + 1, ArrowLeft: atual - 1, ArrowDown: atual - 1, Home: 0, End: n - 1 };
      if (!(ev.key in mapa)) return;
      ev.preventDefault();
      const alvo = (mapa[ev.key] + n) % n;
      ir(alvo, true);
      nos[alvo].focus();
    });

    controles.addEventListener("click", (ev) => {
      const bt = ev.target.closest("[data-ctl]");
      if (!bt) return;
      const n = marcos.length;
      if (bt.dataset.ctl === "pausa") pausar(!pausado);
      if (bt.dataset.ctl === "anterior") ir((atual - 1 + n) % n, true);
      if (bt.dataset.ctl === "proxima") ir((atual + 1) % n, true);
    });

    // segurar o ciclo enquanto a pessoa lê ou navega pelo palco
    const segura = (d) => { segurando = Math.max(0, segurando + d); agendar(); };
    palco.addEventListener("mouseenter", () => segura(1));
    palco.addEventListener("mouseleave", () => segura(-1));
    palco.addEventListener("focusin", (ev) => { if (!controles.contains(ev.target) && !palco.dataset.foco) { palco.dataset.foco = "1"; segura(1); } });
    palco.addEventListener("focusout", (ev) => {
      if (palco.dataset.foco && !palco.contains(ev.relatedTarget)) { delete palco.dataset.foco; segura(-1); }
    });

    // visor das imagens
    const vImg = visor.querySelector(".visor-img");
    palco.addEventListener("click", (ev) => {
      const tela = ev.target.closest(".tela");
      if (!tela) return;
      ev.preventDefault();
      const mini = tela.querySelector("img");
      vImg.src = tela.getAttribute("href");
      vImg.alt = mini.alt;
      visor.querySelector(".visor-titulo").textContent = tela.dataset.titulo;
      visor.querySelector(".visor-legenda").textContent = tela.dataset.legenda;
      visor.showModal();
      agendar();
    });
    visor.querySelector("[data-fechar]").addEventListener("click", () => visor.close());
    visor.addEventListener("click", (ev) => { if (ev.target === visor) visor.close(); });
    visor.addEventListener("close", agendar);

    calmo.addEventListener("change", () => { if (calmo.matches) pausar(true); });

    const pedido = Number(new URLSearchParams(location.search).get("etapa"));
    lamina.classList.toggle("pausado", pausado);
    pausar(pausado);
    ir(pedido >= 1 && pedido <= marcos.length ? pedido - 1 : 0, false);
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
