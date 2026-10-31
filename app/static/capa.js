// Capa da reunião (D61, 27/10/2026): a jornada de um pedido avança sozinha, uma etapa a cada 1,3–1,9 s; o medidor de
// horas acompanha e para no típico do SLA (data-horas) quando a proposta chega ao cliente; no desfecho, o status muda a
// cada volta. Clique numa etapa: vai direto a ela, pausa e retoma depois de 7 s. Só roda com a capa visível e a aba
// em primeiro plano. Movimento reduzido: fica parada na etapa da entrega (o estado que o servidor já desenhou).
(function () {
  var jornada = document.querySelector("[data-capa-jornada]");
  if (!jornada) return;
  var etapas = Array.prototype.slice.call(jornada.querySelectorAll(".capa-etapa"));
  if (!etapas.length) return;
  var horas = parseFloat(jornada.dataset.horas);
  var numero = jornada.querySelector("[data-capa-horas]");
  var roleta = jornada.querySelector("[data-capa-roleta]");
  var barra = jornada.querySelector("[data-capa-barra]");
  var reduzir = window.matchMedia("(prefers-reduced-motion: reduce)");
  var atual = etapas.findIndex(function (e) { return e.classList.contains("ativa"); });
  var timer = 0, retomar = 0, quadro = 0, visivel = true, volta = 0, mostrado = null;

  function medir(f, animar) {
    if (barra) barra.style.width = (f * 100) + "%";  // CSSOM: permitido pela CSP
    if (!numero || isNaN(horas)) return;
    var alvo = Math.round(f * horas);
    var de = mostrado === null ? alvo : mostrado;
    cancelAnimationFrame(quadro);
    if (!animar || reduzir.matches || de === alvo) { numero.textContent = alvo; mostrado = alvo; return; }
    var t0 = performance.now(), dur = 600;
    quadro = requestAnimationFrame(function passo(agora) {
      var t = Math.min(1, (agora - t0) / dur), e = 1 - Math.pow(1 - t, 3);
      mostrado = Math.round(de + (alvo - de) * e);
      numero.textContent = mostrado;
      if (t < 1) quadro = requestAnimationFrame(passo);
    });
  }

  // Roleta (Caio, 27/10/2026): a frase da etapa ao lado das horas. A antiga sobe e sai; a nova entra de baixo, letra por
  // letra em cascata (cada letra num span; só transform/opacidade, WAAPI). Sem movimento: troca o texto direto
  function girar(frase, animar) {
    if (!roleta || !frase) return;
    var antiga = roleta.querySelector(".capa-roleta-texto:last-child");
    if (antiga && antiga.textContent === frase) return;
    var nova = document.createElement("span");
    nova.className = "capa-roleta-texto";
    if (!animar || reduzir.matches || !nova.animate) {
      nova.textContent = frase;
      roleta.replaceChildren(nova);
      return;
    }
    var n = 0;  // as letras vêm agrupadas por palavra: a frase só quebra entre palavras
    frase.split(" ").forEach(function (palavra, p) {
      if (p) nova.appendChild(document.createTextNode(" "));
      var bloco = document.createElement("span");
      bloco.className = "capa-roleta-palavra";
      Array.prototype.forEach.call(palavra, function (letra) {
        var s = document.createElement("span");
        s.className = "capa-roleta-letra";
        s.textContent = letra;
        bloco.appendChild(s);
        s.animate([{ transform: "translateY(110%)", opacity: 0 }, { transform: "none", opacity: 1 }],
          { duration: 380, delay: 120 + n++ * 16, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "backwards" });
      });
      nova.appendChild(bloco);
    });
    roleta.querySelectorAll(".capa-roleta-texto").forEach(function (velha) {
      velha.classList.add("saindo");
      var a = velha.animate([{ transform: "none", opacity: 1 }, { transform: "translateY(-110%)", opacity: 0 }],
        { duration: 260, easing: "cubic-bezier(0.55, 0, 1, 0.45)", fill: "forwards" });
      a.onfinish = function () { velha.remove(); };
    });
    roleta.appendChild(nova);
  }

  function ativar(k, animar) {
    atual = k;
    etapas.forEach(function (e, n) {
      e.classList.toggle("ativa", n === k);
      e.classList.toggle("feita", n < k);
      var b = e.querySelector(".capa-etapa-botao");
      if (n === k) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
    });
    var etapa = etapas[k];
    if (etapa.dataset.variacoes) {  // desfecho: um status diferente a cada volta
      var opcoes = etapa.dataset.variacoes.split("|");
      var rotulo = etapa.querySelector("[data-capa-status]");
      if (rotulo) rotulo.textContent = opcoes[volta % opcoes.length];
      volta += 1;
    }
    medir(parseFloat(etapa.dataset.f) || 0, animar);
    girar(etapa.dataset.frase, animar);
  }

  function agendar() {
    clearTimeout(timer);
    if (reduzir.matches || document.hidden || !visivel) return;
    timer = setTimeout(function () { ativar((atual + 1) % etapas.length, true); agendar(); }, 1300 + Math.random() * 600);
  }

  etapas.forEach(function (e, n) {
    e.querySelector(".capa-etapa-botao").addEventListener("click", function () {
      clearTimeout(timer); clearTimeout(retomar);
      ativar(n, true);
      retomar = setTimeout(agendar, 7000);
    });
  });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (itens) {
      visivel = itens[0].isIntersecting;
      if (visivel) agendar(); else clearTimeout(timer);
    }).observe(jornada);
  }
  document.addEventListener("visibilitychange", function () { if (document.hidden) clearTimeout(timer); else agendar(); });
  if (reduzir.addEventListener) reduzir.addEventListener("change", function () {
    if (reduzir.matches) { clearTimeout(timer); ativar(etapas.length - 2, false); } else agendar();
  });

  // estado inicial: com movimento, a jornada começa do pedido que chega; sem movimento, fica na entrega (servidor)
  if (reduzir.matches) { medir(parseFloat(etapas[atual].dataset.f) || 0, false); return; }
  ativar(0, false);
  agendar();
})();
