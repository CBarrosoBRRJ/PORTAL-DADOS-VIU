// Apresentação: slides (botões, setas, deslizar o dedo, link direto #2), navegador das seções e tela cheia.
(function () {
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  if (!slides.length) return;
  var raiz = document.documentElement;
  var area = document.querySelector("[data-slides]");
  var anterior = document.querySelector("[data-anterior]");  // páginas sem controles (ex.: início) não têm
  var proximo = document.querySelector("[data-proximo]");
  var posicao = document.querySelector("[data-posicao]");
  var progresso = document.querySelector("[data-progresso]");
  var atual = -1;
  // batalha 2 (G4-N1): com um grupo de talentos escolhido (SLA, estudo, Previsão), os links para as outras páginas que
  // aceitam o filtro (data-filtro-talentos: abas, menu, "Próxima pergunta", barra do celular) levam o mesmo grupo
  var talentosAtual = new URLSearchParams(location.search).get("talentos");
  if (talentosAtual === "exclusivos" || talentosAtual === "nao-exclusivos") {
    document.querySelectorAll("a[data-filtro-talentos]").forEach(function (a) {
      var u = new URL(a.getAttribute("href"), location.href);
      u.searchParams.set("talentos", talentosAtual);
      a.setAttribute("href", u.pathname + u.search + u.hash);
    });
  }
  var aoMostrar = null; // decisão 14: reposiciona o rodapé no slide visível (celular), definido no fim do arquivo
  var preferencia = window.matchMedia("(prefers-reduced-motion: reduce)");
  var semMovimento = preferencia.matches;
  // Uma aba aberta acompanha novas cargas. A consulta passa pelo cache do backend,
  // só ocorre com a aba visível e não interrompe leitura de tooltip/seleção/menu.
  var versaoDados = document.querySelector('meta[name="relatorio-versao"]');
  var intervaloDados = document.querySelector('meta[name="relatorio-intervalo"]');
  var verificandoDados = false;
  if (versaoDados && intervaloDados) setInterval(function () {
    if (document.hidden || verificandoDados || trocando || raiz.classList.contains('menu-aberto')) return;
    if (document.querySelector('.ae-detalhes[open]')) return;
    if (document.activeElement && document.activeElement.closest('.tipo-info, .extrato-voltar')) return;
    if (window.getSelection && window.getSelection().toString()) return;
    verificandoDados = true;
    fetch(location.href.split('#')[0], {credentials: 'same-origin', cache: 'no-store'})
      .then(function (r) { if (!r.ok) throw new Error('verificacao'); return r.text(); })
      .then(function (html) {
        var nova = html.match(/<meta name="relatorio-versao" content="([a-f0-9]+)"/);
        if (nova && nova[1] !== versaoDados.content) dadosNovos();
      })
      .catch(function () { /* mantém a última fotografia; retenta no próximo intervalo */ })
      .finally(function () { verificandoDados = false; });
  }, Math.max(60, Number(intervaloDados.content) || 300) * 1000);
  // carga nova (batalha 2, G1-N8): no modo apresentação a tela não recarrega sozinha na frente da diretoria; um aviso
  // (aria-live) oferece "Atualizar". Fora dele, recarrega como antes, mas com a página pronta (sem repetir a entrada)
  var modoReuniao = !!document.querySelector('meta[name="relatorio-modo"][content="apresentacao"]');
  var avisoNovo = null;
  function dadosNovos() {
    if (!modoReuniao) {
      try { sessionStorage.setItem(SEM_ENTRADA, JSON.stringify({ t: Date.now(), p: location.pathname, teclado: false })); } catch (e) { /* ok */ }
      location.reload();
      return;
    }
    if (avisoNovo) return;
    avisoNovo = document.createElement("p");
    avisoNovo.className = "aviso-novo";
    avisoNovo.setAttribute("role", "status");
    var texto = document.createElement("span");
    texto.textContent = "Há dados novos na base.";
    var botao = document.createElement("button");
    botao.type = "button";
    botao.textContent = "Atualizar";
    botao.addEventListener("click", function () { location.reload(); });
    avisoNovo.appendChild(texto);
    avisoNovo.appendChild(botao);
    var palcoAviso = document.querySelector(".palco");
    if (palcoAviso) palcoAviso.insertBefore(avisoNovo, palcoAviso.firstChild);
  }
  function finalizarMovimentos() {
    if (trocaSlide) trocaSlide.skipTransition();
    // WAAPI não acompanha @media automaticamente; concluir mantém o desenho final.
    if (document.getAnimations) document.getAnimations().forEach(function (a) {
      try { if (a.effect && a.effect.getTiming().iterations !== Infinity) a.finish(); } catch (e) { a.cancel(); }
    });
  }
  if (preferencia.addEventListener) preferencia.addEventListener("change", function (ev) {
    semMovimento = ev.matches;
    if (semMovimento) finalizarMovimentos();
  });
  window.addEventListener("beforeprint", finalizarMovimentos);
  // tempos do movimento vêm dos tokens do CSS (:root): JS e CSS não divergem
  function tempo(nome, padrao) {
    var v = getComputedStyle(raiz).getPropertyValue(nome).trim(), n = parseFloat(v);
    return isNaN(n) ? padrao : (/ms$/.test(v) ? n : n * 1000);
  }
  // foco programático sem rolar a lâmina; no celular (coluna única) traz o alvo para a tela se ele ficou fora
  function trazer(el) {
    var r = el.getBoundingClientRect();
    if (r.top < 0 || r.bottom > window.innerHeight) el.scrollIntoView({ block: "nearest", behavior: semMovimento ? "auto" : "smooth" });
  }

  // seção com um slide só: sem Anterior/Próximo (a barra volta sozinha quando houver 2 ou mais)
  var controles = document.querySelector(".controles");
  if (controles && slides.length < 2 && !controles.hasAttribute("data-sempre")) controles.hidden = true;  // estudo: sempre

  // estudo, slide 2 (V2, 30/10/2026, Caio): um passo só; o painel de três quadros (?passo=) saiu — código em
  // _descartados/2026-10-30/app/static/apresentacao_passos_slide2.js. Um ?passo= antigo na URL é ignorado.

  // ---------- navegador das seções ----------
  // pílula azul na aba atual: ao chegar de outra aba, desliza da anterior para a atual; reflexo claro segue o mouse
  // vale para o navegador das seções e para o seletor de talentos (data-chave separa a memória de cada um)
  function colocar(marca, aba) {
    // Menu oculto no celular ou slide ainda invisível: medir só quando houver caixa de layout.
    if (!marca || !aba || !aba.offsetParent) return;
    marca.style.setProperty("--x", aba.offsetLeft + "px");
    marca.style.setProperty("--l", aba.offsetWidth + "px");
    // borda direita: o traço do navegador anima left/right para poder "esticar"; offsetParent = o próprio nav
    marca.style.setProperty("--r", (aba.offsetParent.clientWidth - aba.offsetLeft - aba.offsetWidth) + "px");
  }
  function prepararNavegador(nav) {
    var abas = Array.prototype.slice.call(nav.querySelectorAll("a"));
    var pilula = nav.querySelector(".navegador-pilula"), reflexo = nav.querySelector(".navegador-reflexo");
    var ativa = nav.querySelector("a[aria-current]");
    var CHAVE = "navegador-de:" + (nav.dataset.chave || "secoes");
    if (!pilula || !ativa) return;
    nav._posicionar = function () { colocar(pilula, ativa); };

    var de = null;
    try { de = sessionStorage.getItem(CHAVE); sessionStorage.removeItem(CHAVE); } catch (e) { /* sem armazenamento */ }
    var origem = abas.filter(function (a) { return a.getAttribute("href") === de; })[0];
    if (origem && ativa && origem !== ativa) nav.dataset.ida = origem.offsetLeft < ativa.offsetLeft ? "direita" : "esquerda";
    // com View Transitions entre páginas, o próprio navegador faz a pílula "voar": começa já na aba atual
    if (nav.classList.contains("navegador") && "onpagereveal" in window) origem = null;
    colocar(pilula, origem && origem !== ativa ? origem : ativa);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        nav.classList.add("pronto");  // liga as transições só depois da posição inicial
        colocar(pilula, ativa);
      });
    });

    abas.forEach(function (a) {
      function mirar() { colocar(reflexo, a); nav.classList.toggle("passando", a !== ativa); }
      a.addEventListener("mouseenter", mirar);
      a.addEventListener("focus", mirar);
      a.addEventListener("click", function () {
        try { sessionStorage.setItem(CHAVE, ativa.getAttribute("href")); } catch (e) { /* ok */ }
      });
    });
    nav.addEventListener("mouseleave", function () { nav.classList.remove("passando"); });
    nav.addEventListener("focusout", function (ev) { if (!nav.contains(ev.relatedTarget)) nav.classList.remove("passando"); });
  }
  var navegadores = Array.prototype.slice.call(document.querySelectorAll("[data-navegador]"));
  // só depois de "pronto": antes disso a pílula está na aba de origem e não pode pular para a atual sem animar
  function reposicionar() {
    navegadores.forEach(function (n) { if (n._posicionar && n.classList.contains("pronto") && n.offsetParent) n._posicionar(); });
  }
  window.addEventListener("resize", reposicionar);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(reposicionar);  // larguras mudam com a fonte

  // ---------- entrada do slide ----------
  // D46 no portal (batalha 2, 26/10/2026): o número grande já está no valor final desde o 1º quadro (a contagem a partir
  // de zero mostrava valores que nunca existiram ao lado do texto final); o movimento fica no CSS, um gesto por página.
  // D46: a troca do grupo de talentos recarrega a página; o clique deixa um aviso para a página nova abrir pronta, sem
  // repetir a entrada (e devolver o foco ao grupo, se veio do teclado). Vale para o estudo "Como medimos" e, desde a
  // batalha 2 (G4-N15), para qualquer seletor de talentos ([data-chave="talentos"], página do SLA) e para a recarga por
  // carga nova. O aviso só vale na mesma página e por 10 s
  var estudo = !!document.querySelector(".slide-estudo");
  var SELETOR_GRUPOS = '.estudo-grupos a, [data-chave^="talentos"] a';
  var SEM_ENTRADA = "estudo-sem-entrada", semEntrada = null;
  try {
    semEntrada = JSON.parse(sessionStorage.getItem(SEM_ENTRADA) || "null");
    sessionStorage.removeItem(SEM_ENTRADA);
  } catch (e) { semEntrada = null; /* sem armazenamento: a entrada roda normalmente */ }
  if (!semEntrada || !(Date.now() - semEntrada.t < 10000) || (semEntrada.p && semEntrada.p !== location.pathname)) semEntrada = null;
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest ? ev.target.closest(SELETOR_GRUPOS) : null;
    if (!a || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.button) return;
    try { sessionStorage.setItem(SEM_ENTRADA, JSON.stringify({ t: Date.now(), p: location.pathname, teclado: ev.detail === 0 })); } catch (e) { /* ok */ }
  });
  if (estudo) {
    // slide 7: onda curta das barras, uma posição por linha da tabela (até 10)
    document.querySelectorAll(".slide-tipo .tq-tabela").forEach(function (t) {
      t.querySelectorAll(".tq-linha").forEach(function (tr, k) { tr.style.setProperty("--k", Math.min(k, 10)); });
    });
  }
  // tira e repõe a classe para a sequência do CSS rodar de novo a cada visita. No estudo (D46), só na 1ª visita do
  // slide: ao voltar a ele, ou ao chegar pela troca de grupo, o slide aparece pronto (.revisto desliga a entrada). Nas
  // páginas (batalha 2), o mesmo ao chegar pela troca de grupo ou pela recarga de carga nova
  function entrar(s) {
    var doEstudo = s.classList.contains("slide-estudo");
    if ((doEstudo && s.dataset.visto) || semEntrada) {
      s.dataset.visto = "1";
      s.classList.add("entrou", "revisto");
      if (semEntrada && semEntrada.teclado) {
        var grupo = s.querySelector('.estudo-grupos a[aria-current], [data-chave^="talentos"] a[aria-current]');
        if (grupo) requestAnimationFrame(function () { grupo.focus({ preventScroll: true }); });
      }
      semEntrada = null;
      return;
    }
    if (doEstudo) s.dataset.visto = "1";
    s.classList.remove("entrou");
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { s.classList.add("entrou"); });
    });
  }

  // ---------- slides ----------
  // D46: no estudo, a troca de slide é uma View Transition no mesmo documento, no sentido da navegação (CSS:
  // html[data-ida]); a moldura fica parada. Sem suporte ou com movimento reduzido, troca direta como antes
  var trocaSlide = null;
  function mostrar(i, focar) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    if (i === atual) return;
    var antes = atual;
    atual = i;  // já aqui: teclas seguidas durante a transição contam a partir do slide novo
    if (estudo && antes >= 0 && !semMovimento && document.startViewTransition) {
      if (trocaSlide) trocaSlide.skipTransition();  // cliques rápidos: encerra a anterior
      raiz.dataset.ida = i > antes ? "frente" : "tras";
      var vt = trocaSlide = document.startViewTransition(function () { if (i === atual) exibir(i, focar); });
      // skipTransition rejeita ready em navegação rápida; isso é cancelamento esperado.
      vt.ready.catch(function () {});
      var terminarTroca = function () { if (trocaSlide === vt) { trocaSlide = null; delete raiz.dataset.ida; } };
      vt.finished.then(terminarTroca, terminarTroca);
    } else exibir(i, focar);
  }
  function exibir(i, focar) {
    slides.forEach(function (s, j) {
      s.hidden = j !== i;
      s.setAttribute("aria-label", (j + 1) + " de " + slides.length);
    });
    entrar(slides[i]);
    if (aoMostrar) aoMostrar();
    slides[i].scrollTop = 0;
    var novos = Array.prototype.filter.call(slides[i].querySelectorAll("[data-navegador]"), function (n) { return !n.classList.contains("pronto"); });
    if (novos.length) novos.forEach(prepararNavegador);
    else reposicionar();
    if (posicao) {
      posicao.textContent = (i + 1) + " de " + slides.length;
      progresso.style.width = ((i + 1) / slides.length * 100) + "%";
      anterior.disabled = i === 0;
      // V2 (30/10/2026): no último slide, o Próximo segue para a próxima página (a mesma da seta →, D62)
      proximo.disabled = i === slides.length - 1 && !document.querySelector("[data-pagina-proxima]");
    }
    if (slides.length > 1 && location.hash !== "#" + (i + 1)) history.replaceState(null, "", "#" + (i + 1));
    if (focar) area.focus({ preventScroll: true });
  }

  function doEndereco() {
    var n = parseInt(location.hash.slice(1), 10);
    return isNaN(n) ? 0 : n - 1;
  }

  if (anterior) {
    anterior.addEventListener("click", function () { mostrar(atual - 1); });
    proximo.addEventListener("click", function () {
      var fora = atual === slides.length - 1 && document.querySelector("[data-pagina-proxima]");
      if (fora) { location.assign(fora.href); return; }
      mostrar(atual + 1);
    });
  }
  window.addEventListener("hashchange", function () { mostrar(doEndereco()); });

  // D61 (Caio, 27/10/2026): capa da próxima seção entre as páginas, só pelas setas. → mostra a capa; → (ou Enter) de
  // novo entra na página; ← ou Esc voltam à página atual; clique na capa também entra. Abas, gancho e clique vão direto
  var capaSecao = document.querySelector("[data-capa-secao]");
  function entrarNaSecao() {
    var destino = document.querySelector("[data-pagina-proxima]");
    if (destino) location.assign(destino.href);
  }
  function abrirCapaSecao() {
    capaSecao.hidden = false;
    raiz.classList.add("com-capa-secao");
    requestAnimationFrame(function () { capaSecao.classList.add("aberta"); });
    capaSecao.focus({ preventScroll: true });
  }
  function fecharCapaSecao() {
    capaSecao.classList.remove("aberta");
    capaSecao.hidden = true;
    raiz.classList.remove("com-capa-secao");
    area.focus({ preventScroll: true });
  }
  if (capaSecao) capaSecao.addEventListener("click", entrarNaSecao);

  document.addEventListener("keydown", function (ev) {
    var alvo = ev.target.tagName;
    if (ev.altKey || ev.ctrlKey || ev.metaKey || alvo === "INPUT" || alvo === "SELECT" || alvo === "TEXTAREA") return;
    if (capaSecao && !capaSecao.hidden) {
      if (["ArrowRight", "PageDown", "Enter", " "].indexOf(ev.key) >= 0) { ev.preventDefault(); entrarNaSecao(); }
      else if (["ArrowLeft", "PageUp", "Escape"].indexOf(ev.key) >= 0) { ev.preventDefault(); fecharCapaSecao(); }
      return;
    }
    if (ev.key === "Escape") {
      if (raiz.classList.contains("menu-aberto")) { fecharMenu(); return; }
      document.querySelectorAll('.ae-detalhes[open]').forEach(function (el) { el.removeAttribute('open'); });
      // fecha a dica aberta pelo mouse ou pelo foco (WCAG 1.4.13), sem tirar o foco; volta na próxima passagem ou foco
      var abertas = document.querySelectorAll(".mes:hover, .mes:focus-within, .extrato-lista li:hover, .extrato-lista li.dica-aberta, .talentos-lista li:hover, .talentos-lista li:focus-within, .talentos-lista li.dica-aberta, .tipo-info:hover, .tipo-info:focus");
      abertas.forEach(function (el) { el.classList.add("dica-fechada"); });
      return;
    }
    // D59 (Caio, 27/10/2026): as setas também trocam de PÁGINA — numa página de um slide só, → / PageDown vão à próxima
    // da sequência e ← / PageUp à anterior; no estudo (vários slides), as setas trocam o slide e, nas pontas, voltam à
    // seção (o mesmo link do "Fechar"). Não age dentro de áreas que rolam para o lado (o quadro no celular)
    // Revisão de 03/11/2026: com um pop-up (<dialog>) aberto, as setas não trocam de página nem de slide (na Previsão,
    // a → com "Modelos comparados" aberto levava ao Encerramento)
    var dialogoAberto = !!document.querySelector("dialog[open]");
    var paraFrente = ev.key === "ArrowRight" || ev.key === "PageDown", paraTras = ev.key === "ArrowLeft" || ev.key === "PageUp";
    if ((paraFrente || paraTras) && !dialogoAberto && !(ev.target.closest && ev.target.closest('[role="region"], .quadro-caixa'))) {
      // V2 (30/10/2026): o slide 2 tem um passo só; as setas trocam de slide direto
      var pagina = null;
      if (paraFrente && slides.length < 2 && capaSecao) { ev.preventDefault(); abrirCapaSecao(); return; }  // D61
      // D62: no estudo, as pontas seguem a sequência da reunião (← no 1º slide volta ao SLA, → no último vai à Previsão)
      if (slides.length < 2 || (paraFrente && atual === slides.length - 1) || (paraTras && atual === 0)) {
        pagina = document.querySelector(paraFrente ? "[data-pagina-proxima]" : "[data-pagina-anterior]");
      }
      if (pagina) { ev.preventDefault(); location.assign(pagina.href); return; }
    }
    if (slides.length < 2 || dialogoAberto) return;
    if (paraFrente) { mostrar(atual + 1, true); ev.preventDefault(); }
    else if (paraTras) { mostrar(atual - 1, true); ev.preventDefault(); }
    else if (ev.key === "Home") { mostrar(0, true); ev.preventDefault(); }
    else if (ev.key === "End") { mostrar(slides.length - 1, true); ev.preventDefault(); }
  });

  // deslizar na horizontal troca de slide; na vertical, o slide rola normalmente
  var x0 = null, y0 = null;
  area.addEventListener("touchstart", function (ev) { x0 = ev.touches[0].clientX; y0 = ev.touches[0].clientY; }, { passive: true });
  area.addEventListener("touchend", function (ev) {
    if (x0 === null) return;
    var dx = ev.changedTouches[0].clientX - x0, dy = ev.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) mostrar(atual + (dx < 0 ? 1 : -1));
    x0 = y0 = null;
  }, { passive: true });

  // ---------- tela cheia (onde o navegador permite) ----------
  // D59 (27/10/2026): trocar de página recarrega o documento, e o navegador sai da tela cheia a cada documento novo. Por
  // isso a tela cheia vai para um QUADRO (iframe da mesma origem) com a página atual: a navegação acontece dentro dele e
  // o quadro continua em tela cheia. Ao sair (botão ou Esc), a janela de fora abre a página em que o quadro estava
  var botoesTelaCheia = Array.prototype.slice.call(document.querySelectorAll("[data-tela-cheia]"));
  var meuQuadro = null;
  try { meuQuadro = window.frameElement && window.frameElement.hasAttribute("data-quadro-tela-cheia") ? window.frameElement : null; } catch (e) { meuQuadro = null; }
  function rotularTelaCheia(ativo) {
    botoesTelaCheia.forEach(function (b) {
      var rotulo = ativo ? "Sair da tela cheia" : "Tela cheia";
      b.setAttribute("aria-label", rotulo);
      b.title = rotulo;
    });
  }
  if (meuQuadro) {
    // dentro do quadro: a página já está em tela cheia (html.tela-cheia vem do inicio.js); o botão sai dela
    botoesTelaCheia.forEach(function (b) {
      b.hidden = false;
      b.addEventListener("click", function () { window.parent.document.exitFullscreen(); });
    });
    rotularTelaCheia(true);
    meuQuadro.title = document.title;
    window.focus();  // setas e PageDown funcionam sem clicar antes
  } else if (botoesTelaCheia.length && document.fullscreenEnabled) {
    var abrirQuadro = function () {
      var q = document.createElement("iframe");
      q.className = "quadro-tela-cheia";
      q.setAttribute("data-quadro-tela-cheia", "");
      q.setAttribute("allow", "fullscreen");
      q.title = document.title;
      q.src = location.href;
      document.body.appendChild(q);
      // o pedido precisa sair no mesmo clique; sem o quadro (navegador recusou), tela cheia simples como antes
      q.requestFullscreen().catch(function () { q.remove(); raiz.requestFullscreen(); });
      q.addEventListener("load", function () { try { q.contentWindow.focus(); } catch (e) { /* ok */ } });
    };
    botoesTelaCheia.forEach(function (b) {
      b.hidden = false;
      b.addEventListener("click", function () {
        if (document.fullscreenElement) document.exitFullscreen();
        else abrirQuadro();
      });
    });
    document.addEventListener("fullscreenchange", function () {
      var q = document.querySelector("iframe[data-quadro-tela-cheia]");
      if (q && !document.fullscreenElement) {
        var onde = null;
        try { onde = q.contentWindow.location.href; } catch (e) { onde = null; }
        q.remove();
        if (onde && onde !== location.href) { location.assign(onde); return; }  // fica na página em que estava
      }
      if (q) return;  // o quadro está em tela cheia; esta janela fica por baixo, como estava
      // só a página em tela cheia conta (o vídeo da LIA em tela cheia pelo player não marca o portal; revisão de 03/11)
      var ativo = document.fullscreenElement === raiz;
      raiz.classList.toggle("tela-cheia", ativo);
      rotularTelaCheia(ativo);
      setTimeout(reposicionar, 50);  // a lâmina muda de tamanho
    });
  }

  // ---------- menu lateral: recolher / abrir (a escolha fica neste navegador) ----------
  var recolher = document.querySelector("[data-recolher]");
  function rotuloRecolher() {
    var recolhido = raiz.classList.contains("menu-recolhido");
    recolher.setAttribute("aria-label", recolhido ? "Abrir menu" : "Recolher menu");
    recolher.title = recolhido ? "Abrir menu" : "Recolher menu";
    recolher.setAttribute("aria-expanded", String(!recolhido));
  }
  if (recolher) {
    rotuloRecolher();
    recolher.addEventListener("click", function () {
      var recolhido = raiz.classList.toggle("menu-recolhido");
      try { localStorage.setItem("menu", recolhido ? "recolhido" : "aberto"); } catch (e) { /* ok */ }
      rotuloRecolher();
      setTimeout(reposicionar, 320);  // a lâmina muda de tamanho junto com a transição do menu
    });
  }

  // ---------- árvore do menu: o nome da área abre/fecha as páginas; a escolha fica neste navegador ----------
  document.querySelectorAll("[data-area]").forEach(function (no) {
    var botao = no.querySelector("[data-alternar-area]"), caixa = no.querySelector(".menu-secoes-caixa");
    var chave = "arvore:" + no.dataset.area;
    function aplicar(aberta) {
      no.classList.toggle("fechada", !aberta);
      botao.setAttribute("aria-expanded", String(aberta));
      caixa.inert = !aberta;  // fechada: páginas fora do Tab e do leitor de tela
    }
    try { var salvo = localStorage.getItem(chave); if (salvo) aplicar(salvo === "aberta"); } catch (e) { /* padrão do servidor */ }
    botao.addEventListener("click", function () {
      if (raiz.classList.contains("menu-recolhido") && window.innerWidth > 900) {
        // na régua de ícones, clicar na área abre o menu inteiro com a área aberta
        raiz.classList.remove("menu-recolhido");
        try { localStorage.setItem("menu", "aberto"); } catch (e) { /* ok */ }
        if (recolher) rotuloRecolher();
        aplicar(true);
        setTimeout(reposicionar, 320);
        return;
      }
      var aberta = no.classList.contains("fechada");
      aplicar(aberta);
      try { localStorage.setItem(chave, aberta ? "aberta" : "fechada"); } catch (e) { /* ok */ }
    });
  });

  // ---------- gaveta no celular: um diálogo modal (foco contido, fundo inerte, Esc e botão fecham) ----------
  var botaoMenu = document.querySelector("[data-abrir-menu]");
  var menu = document.getElementById("menu");
  var palco = document.querySelector(".palco");
  var FOCAVEIS = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';
  function focaveisDoMenu() {
    return Array.prototype.filter.call(menu.querySelectorAll(FOCAVEIS), function (el) { return el.offsetParent !== null && !el.closest("[inert]"); });
  }
  function fecharMenu() {
    if (!botaoMenu || !raiz.classList.contains("menu-aberto")) return;
    raiz.classList.remove("menu-aberto");
    menu.removeAttribute("role");
    menu.removeAttribute("aria-modal");
    palco.inert = false;
    botaoMenu.setAttribute("aria-expanded", "false");
    botaoMenu.focus();
  }
  function abrirMenu() {
    raiz.classList.add("menu-aberto");
    menu.setAttribute("role", "dialog");
    menu.setAttribute("aria-modal", "true");
    palco.inert = true;  // o conteúdo de fundo sai da ordem de foco e do leitor de tela
    botaoMenu.setAttribute("aria-expanded", "true");
    // espera o menu ficar visível (a transição troca a visibilidade) antes de levar o foco para dentro
    requestAnimationFrame(function () { requestAnimationFrame(function () { (focaveisDoMenu()[0] || menu).focus(); }); });
  }
  if (botaoMenu) {
    window.addEventListener("resize", function () { if (window.innerWidth > 900) fecharMenu(); });
    botaoMenu.addEventListener("click", function () { raiz.classList.contains("menu-aberto") ? fecharMenu() : abrirMenu(); });
    var fechar = document.querySelector("[data-fechar-menu]");
    if (fechar) fechar.addEventListener("click", fecharMenu);
    document.addEventListener("click", function (ev) {
      if (raiz.classList.contains("menu-aberto") && !menu.contains(ev.target) && !botaoMenu.contains(ev.target)) fecharMenu();
    });
    menu.addEventListener("keydown", function (ev) {  // Tab circula dentro da gaveta
      if (ev.key !== "Tab" || !raiz.classList.contains("menu-aberto")) return;
      var itens = focaveisDoMenu(), primeiro = itens[0], ultimo = itens[itens.length - 1];
      if (ev.shiftKey && document.activeElement === primeiro) { ultimo.focus(); ev.preventDefault(); }
      else if (!ev.shiftKey && document.activeElement === ultimo) { primeiro.focus(); ev.preventDefault(); }
    });
  }

  // dica da legenda fechada com Esc: volta a abrir no próximo foco ou passagem do mouse
  function prepararDicas(raiz) {
    raiz.querySelectorAll(".tipo-info").forEach(function (b) {
      ["blur", "mouseleave"].forEach(function (ev) { b.addEventListener(ev, function () { b.classList.remove("dica-fechada"); }); });
    });
    // A26 (D53): no quadro do Atendimento a dica abre pelo foco do botão; o Safari não foca botão no toque, então o
    // toque foca explicitamente (tocar fora tira o foco e fecha)
    raiz.querySelectorAll(".quadro-extrato .tipo-info, .kpi-entrega .tipo-info").forEach(function (b) {
      b.addEventListener("click", function () { b.focus(); });
    });
    // extrato: a dica abre pelo quadradinho da linha; fechada com Esc, volta quando o mouse sai da linha
    raiz.querySelectorAll(".extrato-lista li, .talentos-lista li").forEach(function (li) {
      li.addEventListener("mouseleave", function () { li.classList.remove("dica-fechada"); });
      // toque (sem mouse): tocar no quadradinho ou no nome abre/fecha a dica; o estado é lido no pointerdown, antes do
      // blur do botão, para o segundo toque fechar mesmo quando o foco sai
      if (!li.querySelector(".dica-tipos, .dica-top")) return;
      var estava = false;
      li.addEventListener("pointerdown", function () { estava = li.classList.contains("dica-aberta"); });
      li.addEventListener("click", function (ev) {
        if (!semMouse.matches || !ev.target.closest(".chave, .tipo-info")) return;
        document.querySelectorAll(".extrato-lista li.dica-aberta, .talentos-lista li.dica-aberta").forEach(function (o) { o.classList.remove("dica-aberta"); });
        li.classList.remove("dica-fechada");
        if (!estava) li.classList.add("dica-aberta");
      });
      li.addEventListener("focusout", function (ev) {
        if (!li.contains(ev.relatedTarget)) li.classList.remove("dica-aberta", "dica-fechada");
      });
    });
  }
  var semMouse = window.matchMedia("(hover: none)");
  // toque fora da linha fecha a dica aberta pelo toque
  document.addEventListener("click", function (ev) {
    document.querySelectorAll(".extrato-lista li.dica-aberta, .talentos-lista li.dica-aberta").forEach(function (li) {
      if (!li.contains(ev.target)) li.classList.remove("dica-aberta");
    });
  });
  prepararDicas(document);
  document.querySelectorAll(".mes").forEach(function (mes) {
    mes.addEventListener("click", function () { mes.classList.remove("dica-fechada"); });
    ["focusout", "mouseleave"].forEach(function (ev) {
      mes.addEventListener(ev, function () { mes.classList.remove("dica-fechada"); });
    });
  });

  // ---------- extrato do mês (Início): troca só a caixa da esquerda, sem recarregar a página ----------
  // O servidor continua montando tudo (mesmo HTML do link); aqui só se busca a página do mês e se troca a caixa.
  // Efeito "foco no mês": a caixa antiga sai para a esquerda, a nova entra linha a linha e, no gráfico, os outros meses
  // esmaecem (CSS em .meses:has(.mes-selecionado)). Sem fetch/história ou em erro, segue o link normal.
  var caixa = document.querySelector("[data-caixa-troca]");
  if (caixa && window.fetch && window.DOMParser && history.pushState) {
    var trocando = false, pendente = null, navegando = false, timerRevelar = 0;
    var esperar = function (ms) { return new Promise(function (ok) { setTimeout(ok, ms); }); };
    // aviso para leitor de tela fora da caixa (a caixa é recriada a cada troca)
    var aviso = document.createElement("p");
    aviso.className = "so-leitor";
    aviso.setAttribute("aria-live", "polite");
    caixa.parentNode.insertBefore(aviso, caixa.nextSibling);

    // revisão de 03/11/2026: o DOMParser aplicava os <style nonce> da resposta buscada (nonce de outra resposta) e o
    // console registrava um erro de CSP. Antes de interpretar, cada <style> vira <template data-estilo> (inerte); o CSS
    // é lido de template.content em aplicar()
    var neutralizarEstilos = function (html) {
      return html.replace(/<style\b/gi, "<template data-estilo").replace(/<\/style>/gi, "</template>");
    };
    var aplicar = function (doc, url, empilhar) {
      var nova = doc.querySelector("[data-caixa-troca]");
      if (!nova) throw new Error("caixa ausente");
      caixa.innerHTML = nova.innerHTML;
      var metaNova = doc.querySelector('meta[name="relatorio-versao"]');
      if (versaoDados && metaNova) versaoDados.content = metaNova.content;
      prepararDicas(caixa);
      // larguras das barras do extrato ficam no <style> do gráfico (CSP: só com nonce). Recria o bloco com o nonce
      // desta página; o nonce da resposta buscada não vale aqui
      // (a resposta chega com os <style> trocados por <template data-estilo>: ver neutralizarEstilos)
      var estiloAtual = document.querySelector("figure.colunas style"), estiloNovo = doc.querySelector("figure.colunas template[data-estilo]");
      if (estiloAtual && estiloNovo) {
        var bloco = document.createElement("style");
        bloco.nonce = estiloAtual.nonce;
        bloco.textContent = estiloNovo.content.textContent;
        estiloAtual.replaceWith(bloco);
      }
      // estado dos meses (selecionado, destino e nome do link) vem da mesma página do servidor
      document.querySelectorAll(".meses > li[id]").forEach(function (li) {
        var outro = doc.getElementById(li.id);
        if (!outro) return;
        li.className = outro.className;
        var a = li.querySelector("a.mes-link"), b = outro.querySelector("a.mes-link");
        if (a && b) ["href", "aria-label", "aria-current"].forEach(function (at) {
          var v = b.getAttribute(at);
          if (v === null) a.removeAttribute(at); else a.setAttribute(at, v);
        });
      });
      if (empilhar) history.pushState({ caixa: true }, "", url);
    };

    // linhas da caixa nova surgem em sequência (--k = posição; CSSOM não é bloqueado pela CSP, ao contrário de style="")
    var revelar = function () {
      var linhas = caixa.querySelectorAll(".extrato > *, .extrato li, .tipos-ano tr");
      linhas.forEach(function (el, k) { el.style.setProperty("--k", Math.min(k, 14)); });
      caixa.classList.add("caixa-entrando");
      timerRevelar = setTimeout(function () {  // fim da onda: 15 passos + a barra mais lenta
        caixa.classList.remove("caixa-entrando", "caixa-volta");
        linhas.forEach(function (el) { el.style.removeProperty("--k"); });
      }, tempo("--dur-xl", 800) + 15 * tempo("--passo", 35));
    };

    // uma troca por vez; pedidos durante a troca (cliques, Voltar/Avançar) ficam guardados e o último vence
    var trocar = function (url, empilhar, foco) {
      if (navegando) return;
      if (trocando) { pendente = { url: url, empilhar: empilhar, foco: foco }; return; }
      trocando = true;
      clearTimeout(timerRevelar);  // a entrada anterior não pode mexer nesta troca
      caixa.classList.remove("caixa-entrando");
      var focoDentro = caixa.contains(document.activeElement);  // o nó focado vai ser recriado
      var mesAntes = document.querySelector(".mes-selecionado a.mes-link");
      var pedido = fetch(url.split("#")[0], { credentials: "same-origin" })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); });
      // abrir = avançar (sai pela esquerda, entra da esquerda); fechar = voltar (sai pela direita, tabela entra inteira)
      caixa.classList.toggle("caixa-volta", !/[?&]mes=/.test(url));
      if (!semMovimento) caixa.classList.add("caixa-saindo");
      Promise.all([pedido, semMovimento ? null : esperar(tempo("--dur-s", 180))]).then(function (res) {
        var doc = new DOMParser().parseFromString(neutralizarEstilos(res[0]), "text/html");
        var fotoAtual = document.querySelector('[data-fotografia]');
        var fotoNova = doc.querySelector('[data-fotografia]');
        if (fotoAtual && fotoNova && fotoAtual.dataset.fotografia !== fotoNova.dataset.fotografia) {
          navegando = true;
          window.location.assign(url); // totais, gráfico, extrato e rodapé mudam juntos
          return;
        }
        aplicar(doc, url, empilhar);
        caixa.classList.remove("caixa-saindo");
        if (!semMovimento) revelar();
      }).then(function () {
        // teclado: ao abrir, o foco vai para o título do extrato; ao fechar, volta ao mês que estava aberto.
        // Se o foco estava dentro da caixa (ex.: clique em Fechar), ele não cai no <body>
        var titulo = caixa.querySelector("#extrato-titulo");
        var alvo = foco === "titulo" ? titulo : foco;
        if (!alvo && focoDentro) alvo = titulo || mesAntes;
        if (alvo && alvo.focus && document.contains(alvo)) {
          if (alvo === titulo) alvo.setAttribute("tabindex", "-1");
          alvo.focus({ preventScroll: true });
          trazer(alvo);
        }
        // anúncio só quando o foco não foi para o título (ele já se anuncia)
        if (alvo !== titulo && !caixa.querySelector("[role=status]")) {
          aviso.textContent = titulo ? "Extrato de " + titulo.textContent.trim() + " aberto." : "Extrato fechado.";
        }
      }).catch(function () {
        navegando = true;
        caixa.classList.remove("caixa-saindo", "caixa-entrando");
        if (url === location.href) location.reload(); else location.href = url;
      }).then(function () {
        trocando = false;
        var p = pendente; pendente = null;
        if (p && !navegando) trocar(p.url, p.empilhar, p.foco);
      });
    };
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest ? ev.target.closest("a.mes-link, a.extrato-voltar") : null;
      if (!a || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey || ev.button) return;
      ev.preventDefault();
      if (ev.detail > 1) return;  // duplo clique: só o primeiro conta
      var teclado = ev.detail === 0;
      var foco = null;
      if (teclado && a.classList.contains("extrato-voltar")) foco = document.querySelector(".mes-selecionado a.mes-link");
      else if (teclado && !a.hasAttribute("aria-current")) foco = "titulo";
      else if (teclado) foco = a;
      trocar(a.href, true, foco);
    });
    window.addEventListener("popstate", function (ev) { if (ev.state && ev.state.caixa) trocar(location.href, false, null); });
    history.replaceState({ caixa: true }, "", location.href);
  }

  // decisão 14 (25/10/2026): no celular, "Próxima pergunta" e o rodapé datado seguem o conteúdo, no fim do slide; no
  // computador, voltam ao lugar congelado da moldura. Página com vários slides (estudo "Como medimos", 25/10/2026): só
  // o rodapé vai para o fim do slide visível e acompanha a troca de slide. Sem JS, a página já rola inteira
  (function () {
    var proximaNav = document.querySelector(".palco > nav.proxima");
    var rodape = document.querySelector(".palco > .rodape-dados");
    var varios = slides.length > 1;
    var moveis = (varios ? [rodape] : [proximaNav, rodape]).filter(Boolean);
    if (!moveis.length) return;
    var estreito = window.matchMedia("(max-width: 900px)");
    var marco = document.createComment("lugar da próxima pergunta e do rodapé");
    moveis[0].parentNode.insertBefore(marco, moveis[0]);
    function posicionar() {
      var depois = marco;
      var alvo = slides[Math.max(0, atual)];
      moveis.forEach(function (el) {
        if (estreito.matches) { alvo.appendChild(el); return; }
        depois.parentNode.insertBefore(el, depois.nextSibling);
        depois = el;
      });
    }
    posicionar();
    if (varios) aoMostrar = posicionar;
    if (estreito.addEventListener) estreito.addEventListener("change", posicionar);
  })();

  // ---------- D51 (26/10/2026, Caio): Talentos — exceção à D46/D49 só nesta página ----------
  // ABERTURA (e troca de filtro): a barra do ano cresce da esquerda para a direita e os números contam de 0 ao valor
  // (barra, número grande da resposta, células e coluna Ano), com o top 10 PARADO nas posições finais.
  // BOTÃO PLAY (só ícone, redondo, na linha da legenda da barra; nome "Ver a subida e descida das posições ao longo do
  // ano"; vira ■ "Parar" e volta a ▶ ao terminar): a "corrida do ano", calma (D51 revista, 26/10): o tempo do ano anda
  // mês a mês com easing suave e um respiro no fim de cada mês; uma moldura desliza pela coluna do mês e o mês aparece
  // grande no canto do quadro (crossfade); as células do mês acendem e o número delas e o do Ano contam. O lugar sai do
  // acumulado entre TODOS os que passaram pelos 10 no ano (data-corrida-extras; empate = lugar no ano), com HISTERESE:
  // diferenças de até MARGEM (0,5 pedido ou 2% do líder) não trocam ninguém, e a nova ordem só vale se persistir por
  // TEMPOS.histerese (nada de troca a cada quadro nos empates dos não exclusivos); aí entra inteira, de uma vez. As
  // linhas seguem a posição com mola criticamente amortecida (sem passar do alvo; quem vai mais longe leva mais tempo);
  // quem sobe passa por cima com leve elevação e sombra. A numeração 1–10 fica FIXA (nunca dois "10"). Quem entra
  // surge de baixo com fade; quem sai desce meia linha e some. No fim, a ordem exata do ano e a tabela do servidor.
  // Como: tudo acontece numa CÓPIA da tabela (aria-hidden, inert) sobreposta à original, que fica só transparente
  // (o leitor de tela lê sempre os valores finais; nada é anunciado). Ao fim, a cópia sai e fica o HTML do servidor.
  // Só transform/opacidade/texto/classe por quadro; posições medidas uma vez. Sem JS: botão escondido. Movimento
  // reduzido: nada se mexe e o botão fica desabilitado, com o motivo. Interrompem (vão ao final): "Parar", Esc e outras
  // teclas (menos Tab, modificadoras e Enter/Espaço no próprio botão), clique/roda/toque na tabela ou na barra, troca de aba,
  // mudança real de largura e impressão. O foco não é movido (o botão continua no lugar).
  (function talentosD51() {
    var corpo = document.querySelector(".talentos-corpo");
    if (!corpo) return;
    var tabela = corpo.querySelector(".mapa-tabela[data-corrida]");
    var barra = corpo.querySelector(".divisao-barra");
    var play = corpo.querySelector("[data-corrida-play]"), ajuda = document.getElementById("corrida-ajuda");
    var ajudaOriginal = ajuda ? ajuda.textContent : "";
    var rotulo = corpo.querySelector(".corrida-rotulo");
    var NOME_PLAY = "Ver a subida e descida das posições ao longo do ano";
    var podeMover = !semMovimento && !!Element.prototype.animate;
    if (play && tabela) {
      play.hidden = false;
      if (!podeMover) {
        play.disabled = true;
        play.title = "Animação desligada: o sistema pede movimento reduzido";
        if (ajuda) ajuda.textContent = "Animação desligada porque o sistema pede movimento reduzido; a tabela mostra o resultado do ano.";
      }
    }
    // Inicializar os controles mesmo no modo reduzido permite acompanhar mudanças sem recarregar a página.
    if (!podeMover && !Element.prototype.animate) return;
    // TEMPOS DA D51 (ms): o único lugar para acelerar ou desacelerar (ficha docs/paginas/talentos.md, D51).
    // barra = barra + contagens de cima; numeros = contagem das células e do Ano na abertura. Corrida (play):
    // mes = o tempo de um mês andar (easing suave); respiro = pausa no fim de cada mês (corrida ≈ meses × (mes +
    // respiro): 10 meses ≈ 10,4 s); acender = célula do mês ganhando o tom; deslize = tempo da mola das linhas;
    // histerese = quanto tempo alguém precisa ficar à frente do vizinho para trocar; rotulo = crossfade do mês no canto;
    // assentar = limite de espera no fim, depois do último mês
    var TEMPOS = { barra: 600, numeros: 700, mes: 780, respiro: 260, acender: 420, deslize: 260, histerese: 340, rotulo: 380, assentar: 2200 };
    var MARGEM = 0.5, MARGEM_REL = 0.02;  // vantagem mínima para trocar de lugar: 0,5 pedido ou 2% do líder (histerese)
    var NIVEIS = 6;  // os mesmos 6 tons do servidor (T10)
    var EASE_SAI = "cubic-bezier(0.33, 1, 0.68, 1)";
    function limita(x) { return Math.min(1, Math.max(0, x)); }
    function sai(t) { t = limita(t); return 1 - Math.pow(1 - t, 3); }                                       // easeOutCubic
    function entraSai(t) { t = limita(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }  // easeInOutCubic
    function suave(t) { t = limita(t); return 0.5 - 0.5 * Math.cos(Math.PI * t); }                           // easeInOutSine
    function br(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "."); }  // inteiro pt-BR: 3.451
    function inteiro(txt) { return parseInt(String(txt).replace(/\./g, ""), 10); }
    corpo.classList.add("d51");  // desliga a onda de tons da D50 (a contagem a substitui); fica até sair da página
    var M = tabela ? +tabela.dataset.corridaMeses : 0;
    var finais = tabela ? Array.prototype.slice.call(tabela.tBodies[0].rows).map(function (tr) {
      return (tr.dataset.corridaPedidos || "").split(",").map(Number);
    }) : [];
    var extras = [];
    try { extras = tabela ? JSON.parse(tabela.dataset.corridaExtras || "[]") : []; } catch (e) { extras = []; }
    var valido = M > 0 && finais.length > 1 && finais.every(function (p, i) {
      var total = tabela.tBodies[0].rows[i].querySelector(".mapa-total");
      return p.length === M && total && p.reduce(function (a, b) { return a + b; }, 0) === inteiro(total.textContent);
    });
    extras = extras.filter(function (x) { return x && x.p && x.p.length === M && x.pos > finais.length; });

    // ---- palco: cópia decorativa da tabela por cima da original (a original só fica transparente) ----
    var palco = null;
    function montarPalco() {
      var rol = tabela.parentNode, copia = tabela.cloneNode(true);
      copia.removeAttribute("data-corrida");
      copia.removeAttribute("data-corrida-extras");
      var cap = copia.querySelector("caption");
      if (cap) cap.remove();
      var p = document.createElement("div");
      p.className = "corrida-palco";
      p.setAttribute("aria-hidden", "true");
      p.inert = true;
      p.style.left = tabela.offsetLeft + "px";
      p.style.top = tabela.offsetTop + "px";
      p.style.width = tabela.offsetWidth + "px";
      p.style.height = tabela.offsetHeight + "px";
      p.appendChild(copia);
      rol.appendChild(p);
      tabela.classList.add("corrida-escondida");
      palco = { el: p, copia: copia, linhas: Array.prototype.slice.call(copia.tBodies[0].rows) };
      return palco;
    }
    function desmontarPalco() {
      if (!palco) return;
      palco.el.remove();
      palco = null;
      tabela.classList.remove("corrida-escondida");
    }

    // ---- laço único: um "modo" por vez (abertura ou corrida) ----
    var modo = null, quadro = 0;
    function parar() {  // leva o modo atual ao estado final (o HTML do servidor)
      if (!modo) return;
      cancelAnimationFrame(quadro);
      var m = modo;
      modo = null;
      m.fim();
      desmontarPalco();
      if (rotulo) rotulo.textContent = "";
      botao(false);
    }
    function rodar(m) {
      modo = m;
      m.t0 = performance.now();
      m.antes = m.t0;
      quadro = requestAnimationFrame(function tique(agora) {
        if (modo !== m) return;
        var dt = Math.max(0, Math.min(100, agora - m.antes));
        m.antes = agora;
        if (m.quadro(agora - m.t0, dt)) { parar(); return; }
        quadro = requestAnimationFrame(tique);
      });
    }
    function botao(rodando) {  // só ícone: o nome (aria-label) e a dica (title) dizem o que ele faz
      if (!play) return;
      var nome = rodando ? "Parar" : NOME_PLAY;
      play.querySelector(".corrida-icone").textContent = rodando ? "■" : "▶";
      play.setAttribute("aria-label", nome);
      play.title = nome;
      play.classList.toggle("corrida-rodando", rodando);
    }

    // ---- ABERTURA: barra + números contando; linhas paradas ----
    function abertura() {
      var contas = [], restaurar = [], anim = null;
      if (barra) {
        anim = barra.animate([{ clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0 0 0)" }], { duration: TEMPOS.barra, easing: EASE_SAI });
        barra.querySelectorAll(".divisao-pct, .divisao-n").forEach(function (el) {  // a barra já é aria-hidden no HTML
          var no = el.firstChild;
          if (!no || no.nodeType !== 3 || isNaN(inteiro(no.nodeValue))) return;
          var original = no.nodeValue;
          contas.push({ no: no, valor: inteiro(original), sufixo: el.classList.contains("divisao-pct") ? "%" : "", dur: TEMPOS.barra, de: -1 });
          restaurar.push(function () { no.nodeValue = original; });
        });
      }
      var heroi = corpo.querySelector(".talentos-frase .f-numero");
      if (heroi && /^\d+%$/.test(heroi.textContent.trim())) {
        var copia = document.createElement("span");  // cópia aria-hidden por cima; o texto real (final) fica transparente
        copia.className = "d51-conta";
        copia.setAttribute("aria-hidden", "true");
        copia.appendChild(document.createTextNode(""));
        var v = parseInt(heroi.textContent, 10);
        heroi.appendChild(copia);
        heroi.classList.add("d51-contando");
        contas.push({ no: copia.firstChild, valor: v, sufixo: "%", dur: TEMPOS.barra, de: -1 });
        restaurar.push(function () { heroi.classList.remove("d51-contando"); copia.remove(); });
      }
      if (valido) {
        montarPalco().copia.querySelectorAll("tbody .hm-num, tbody .mapa-total").forEach(function (el) {
          if (el.firstChild && el.firstChild.nodeType === 3) contas.push({ no: el.firstChild, valor: inteiro(el.textContent), sufixo: "", dur: TEMPOS.numeros, de: -1 });
        });
      }
      contas.forEach(function (c) { c.no.nodeValue = "0" + c.sufixo; });
      rodar({
        quadro: function (t) {
          var vivo = false;
          contas.forEach(function (c) {
            var f = sai(t / c.dur), n = Math.round(c.valor * f);
            if (n !== c.de) { c.no.nodeValue = br(n) + c.sufixo; c.de = n; }
            if (f < 1) vivo = true;
          });
          return !vivo && t >= TEMPOS.barra;
        },
        fim: function () {
          if (anim) try { anim.cancel(); } catch (e) { /* já terminou */ }
          restaurar.forEach(function (f) { f(); });
        }
      });
    }

    // ---- CORRIDA (botão play) ----
    function corrida() {
      var p = montarPalco(), copia = p.copia, el = p.el;
      var maior = +tabela.dataset.corridaMaior || 1;
      var origem = Array.prototype.slice.call(tabela.tBodies[0].rows);
      var alturaLinha = origem[0].offsetHeight, cab = tabela.tHead.rows[0].offsetHeight;
      var slots = origem.map(function (tr) { return tr.offsetTop; });  // as 10 posições da tabela final
      var S = slots.length, passo = S > 1 ? slots[1] - slots[0] : alturaLinha;
      var ultimo = slots[S - 1], fora = ultimo + passo * 0.6;  // quem sai desce ~meia linha e some (sem corte)
      el.classList.add("corrida-ativa");
      el.style.height = (tabela.offsetHeight + passo * 0.6) + "px";
      el.style.setProperty("--corrida-acende", TEMPOS.acender + "ms");
      // linhas de quem entra e sai: cópia da última linha com nome, células e Ano trocados
      var modelo = p.linhas[p.linhas.length - 1];
      extras.forEach(function (x) {
        var tr = modelo.cloneNode(true);
        var nome = tr.querySelector(".mapa-talento");
        nome.textContent = x.t;
        nome.title = x.t;
        Array.prototype.slice.call(tr.querySelectorAll("td.hm")).slice(0, M).forEach(function (td, k) {
          var v = x.p[k], nivel = v ? Math.min(NIVEIS, Math.max(1, Math.ceil(NIVEIS * v / maior))) : 0;
          td.className = td.className.replace(/\bhm-n\d\b/, "hm-n" + nivel);
        });
        copia.tBodies[0].appendChild(tr);
        p.linhas.push(tr);
      });
      copia.style.height = "auto";  // linhas com a altura da tabela final (as extras não espremem as 10)
      copia.tHead.rows[0].style.height = cab + "px";
      var dados = p.linhas.map(function (tr, i) {
        var ped = i < finais.length ? finais[i] : extras[i - finais.length].p, cum = [0];
        ped.forEach(function (v, k) { cum.push(cum[k] + v); });
        tr.style.height = alturaLinha + "px";
        var cel = Array.prototype.slice.call(tr.querySelectorAll("td.hm")).slice(0, M);
        cel.forEach(function (td) { td.classList.add("corrida-apagada"); });
        return { tr: tr, ordem: i < finais.length ? i : extras[i - finais.length].pos - 1, p: ped, cum: cum, y: null, v: 0,
                 idx: 0, vis: -1, so: -1, sobe: false, mostrado: -1, total: tr.querySelector(".mapa-total"),
                 cel: cel, num: cel.map(function (td) { var n = td.querySelector(".hm-num"); if (n) n.textContent = ""; return n; }),
                 cn: cel.map(function () { return -1; }), aceso: cel.map(function () { return false; }) };
      });
      var naturais = dados.map(function (d) { return d.tr.offsetTop; });  // medida única (offsetTop ignora transform)
      var base = el.getBoundingClientRect();
      var cabs = Array.prototype.slice.call(copia.querySelectorAll("thead th.mapa-mes")).slice(0, M);
      var colunas = cabs.map(function (th) { var r = th.getBoundingClientRect(); return { x: r.left - base.left, w: r.width, y: r.top - base.top }; });
      var linha0 = p.linhas[0], rLinha = linha0.getBoundingClientRect();
      var rNome = linha0.querySelector(".mapa-nome").getBoundingClientRect(), rTotal = linha0.querySelector(".mapa-total").getBoundingClientRect();
      // sombra de cada linha (cartão branco sob quem sobe): mesma posição natural, mesmo translate da linha
      dados.forEach(function (d, i) {
        var s = document.createElement("span");
        s.className = "corrida-sombra";
        s.style.left = (rNome.left - base.left - 4) + "px";
        s.style.width = (rTotal.right - rNome.left + 8) + "px";
        s.style.top = naturais[i] + "px";
        s.style.height = alturaLinha + "px";
        el.appendChild(s);
        d.sombra = s;
      });
      // numeração fixa 1–10 (as linhas trocam de lugar; os números, não)
      var pos0 = linha0.querySelector(".mapa-pos"), rPos = pos0 ? pos0.getBoundingClientRect() : null;
      if (rPos && rPos.width > 0) {
        el.classList.add("corrida-numerada");
        var fonte = getComputedStyle(pos0);
        slots.forEach(function (s, i) {
          var n = document.createElement("span");
          n.className = "corrida-num";
          n.textContent = String(i + 1);
          n.style.left = (rPos.left - base.left) + "px";
          n.style.top = (s + rPos.top - rLinha.top) + "px";
          n.style.width = rPos.width + "px";
          n.style.height = rPos.height + "px";
          n.style.fontSize = fonte.fontSize;
          n.style.lineHeight = fonte.lineHeight;
          el.appendChild(n);
        });
      }
      // moldura do mês corrente: da altura do cabeçalho ao pé do 10º
      var cursor = document.createElement("span");
      cursor.className = "corrida-cursor";
      cursor.style.left = "-4px";
      cursor.style.top = (colunas[0].y - 4) + "px";
      cursor.style.width = (colunas[0].w + 8) + "px";
      cursor.style.height = (ultimo + alturaLinha - colunas[0].y + 7) + "px";
      cursor.style.opacity = "0";
      el.appendChild(cursor);
      // mês grande no canto do quadro: dois rótulos alternando (crossfade)
      var mesesTxt = cabs.map(function (th) { return (th.querySelector("abbr") || th).textContent.trim(); });
      var rot = [];
      if (rotulo) {
        rotulo.textContent = "";
        rotulo.style.setProperty("--corrida-troca", TEMPOS.rotulo + "ms");
        rot = [0, 1].map(function () { var s = document.createElement("span"); rotulo.appendChild(s); return s; });
      }
      var rotAtivo = 0;
      function mostrarMes(txt) {
        if (!rot.length) return;
        var velho = rot[rotAtivo];
        rotAtivo = 1 - rotAtivo;
        var novo = rot[rotAtivo];
        novo.textContent = txt;
        velho.classList.remove("visivel");
        if (txt) novo.classList.add("visivel");
      }
      // começa na ordem do fim de janeiro (todos com 0; empate = lugar no ano): o 1º mês não embaralha a tabela inteira
      var ordem = dados.slice().sort(function (a, b) { return (b.p[0] - a.p[0]) || (a.ordem - b.ordem); });
      var slot = TEMPOS.mes + TEMPOS.respiro, total = M * slot, mesAtual = -1, fechou = false, espera = 0;
      botao(true);
      rodar({
        quadro: function (tc, dt) {
          // tempo do ano: mês k anda em TEMPOS.mes (easeInOutSine) e respira TEMPOS.respiro
          tc = Math.max(0, tc);  // o 1º quadro do rAF pode vir com hora anterior ao clique
          var k = Math.min(M - 1, Math.floor(tc / slot)), u = limita((tc - k * slot) / TEMPOS.mes);
          var frac = tc >= total ? 1 : suave(u);
          dados.forEach(function (d) { d.agora = d.cum[k] + d.p[k] * frac; });
          if (tc < total) {
            // lugar com histerese: diferença de até "margem" mantém a ordem atual; a nova ordem só vale se continuar
            // diferente por TEMPOS.histerese, e aí entra inteira (cada linha faz UMA viagem até o lugar novo)
            var margem = Math.max(MARGEM, MARGEM_REL * ordem[0].agora);
            ordem.forEach(function (d, i) { d.idx = i; });
            var cand = ordem.slice().sort(function (a, b) { var df = b.agora - a.agora; return Math.abs(df) > margem ? df : a.idx - b.idx; });
            if (cand.some(function (d, i) { return d !== ordem[i]; })) {
              espera += dt;
              if (espera >= TEMPOS.histerese) { ordem = cand; espera = 0; }
            } else espera = 0;
          } else if (!fechou) {  // fim: a ordem exata do ano (empate = lugar no ano), igual à tabela do servidor
            fechou = true;
            ordem.sort(function (a, b) { return (b.agora - a.agora) || (a.ordem - b.ordem); });
            cursor.classList.add("corrida-sai");
            cursor.style.opacity = "0";
            mostrarMes("");
          }
          var omega = 2 / TEMPOS.deslize, x = omega * dt, amortece = 1 / (1 + x + 0.48 * x * x + 0.235 * x * x * x);
          var parado = true;
          ordem.forEach(function (d, lugar) { d.lugar = lugar; });
          dados.forEach(function (d, i) {
            var alvo = (d.lugar < S ? slots[d.lugar] : fora) - naturais[i];
            if (d.y === null) d.y = alvo;  // 1º quadro: cada um já no seu lugar (os de fora, escondidos embaixo)
            // mola criticamente amortecida (SmoothDamp): velocidade contínua, sem passar do alvo
            var dif = d.y - alvo, tmp = (d.v + omega * dif) * dt;
            d.v = (d.v - omega * tmp) * amortece;
            var y = alvo + (dif + tmp) * amortece;
            if ((dif > 0) !== (y - alvo > 0)) { y = alvo; d.v = 0; }
            d.y = y;
            if (Math.abs(alvo - d.y) > 0.3 || Math.abs(d.v) > 0.002) parado = false;
            var elev = limita((-d.v * TEMPOS.deslize / passo - 0.15) / 0.5);  // só quem sobe de verdade ganha elevação
            if ((d.v < -0.01) !== d.sobe)  /* quem sobe, mesmo devagar, passa por cima de quem desce */ { d.sobe = !d.sobe; d.tr.classList.toggle("corrida-sobe", d.sobe); }
            var topo = naturais[i] + d.y, vis = Math.round((1 - entraSai((topo - ultimo) / (fora - ultimo))) * 100) / 100;
            var tf = "translateY(" + d.y.toFixed(2) + "px)";
            d.tr.style.transform = tf;
            d.sombra.style.transform = tf;
            if (vis !== d.vis) { d.tr.style.opacity = String(vis); d.vis = vis; }
            var se = Math.round(suave(elev) * vis * 100) / 100;
            if (se !== d.so) { d.sombra.style.opacity = String(se); d.so = se; }
            var n = Math.round(d.agora);
            if (n !== d.mostrado) { d.total.textContent = br(n); d.mostrado = n; }
            d.cel.forEach(function (td, j) {  // meses passados: valor; mês corrente: conta; meses adiante: apagados
              var acende = j < k || (j === k && (u > 0 || tc >= total));
              if (acende !== d.aceso[j]) { d.aceso[j] = acende; td.classList.toggle("corrida-apagada", !acende); }
              var cn = j < k ? d.p[j] : j === k && acende ? Math.round(d.p[j] * frac) : -1;
              if (cn !== d.cn[j] && d.num[j]) { d.num[j].textContent = cn < 0 ? "" : br(cn); d.cn[j] = cn; }
            });
          });
          // moldura: desliza para a coluna do mês na 1ª metade do mês; aparece no começo
          var xa = k > 0 ? colunas[k - 1].x : colunas[0].x, xm = xa + (colunas[k].x - xa) * suave(u * 2);
          cursor.style.transform = "translateX(" + xm.toFixed(2) + "px)";
          if (!fechou) cursor.style.opacity = String(Math.round(limita(tc / 300) * 100) / 100);
          if (k !== mesAtual) {
            mesAtual = k;
            cabs.forEach(function (th, j) { th.classList.toggle("corrida-mes", j === k); th.classList.toggle("corrida-adiante", j > k); });
            mostrarMes(mesesTxt[k]);
          }
          return tc >= total + TEMPOS.rotulo && (parado || tc >= total + TEMPOS.assentar);
        },
        tipo: "corrida",
        fim: function () { /* a cópia sai em parar(); a tabela do servidor volta a aparecer */ }
      });
    }

    // ---- gatilhos ----
    if (play) play.addEventListener("click", function () {
      if (!valido || semMovimento) return;
      var rodando = !!(modo && modo.tipo === "corrida");
      parar();  // abertura em curso ou corrida: vai ao final
      if (!rodando) corrida();
    });
    // no próprio botão, só Enter e Espaço ficam com o click (que já alterna); o Esc e as outras teclas param (revisão de 03/11)
    function interromper(ev) {
      if (modo && !(play && play.contains(ev.target) && (ev.type !== "keydown" || ev.key === "Enter" || ev.key === " "))) parar();
    }
    [barra, tabela && tabela.closest("figure")].forEach(function (el) {
      if (el) ["pointerdown", "wheel", "touchstart"].forEach(function (nome) { el.addEventListener(nome, interromper, { passive: true }); });
    });
    if (tabela) tabela.parentNode.addEventListener("scroll", function (ev) { interromper(ev); }, { passive: true });
    window.addEventListener("keydown", function (ev) {
      if (/^(Tab|Shift|Alt|Control|Meta)$/.test(ev.key)) return;
      interromper(ev);
    }, true);
    window.addEventListener("beforeprint", parar);
    window.addEventListener("pagehide", parar);
    if (preferencia.addEventListener) preferencia.addEventListener("change", function (ev) {
      if (ev.matches) parar();
      if (play) {
        play.disabled = ev.matches;
        play.title = ev.matches ? "Animação desligada: o sistema pede movimento reduzido" : NOME_PLAY;
      }
      if (ajuda) ajuda.textContent = ev.matches ?
        "Animação desligada porque o sistema pede movimento reduzido; a tabela mostra o resultado do ano." : ajudaOriginal;
    });
    document.addEventListener("visibilitychange", function () { if (document.hidden) parar(); });
    var largura0 = window.innerWidth;  // só mudança real de largura (barra de rolagem que some ≈ 16 px não conta)
    window.addEventListener("resize", function () { if (Math.abs(window.innerWidth - largura0) > 40) parar(); largura0 = window.innerWidth; });
    if (podeMover) abertura();
  })();
  // ---------- fim D51 ----------

  // ---------- D56 (Previsão, 26/10/2026): diálogo nativo aberto por um botão [data-dialogo="id"] ----------
  // Navegadores com "invoker commands" (commandfor/command no botão) abrem sozinhos; nos outros, showModal() aqui. O
  // navegador prende o foco no diálogo e o Esc fecha; o botão Fechar é um <form method="dialog">. Clicar fora (no fundo)
  // também fecha, e o foco volta ao botão que abriu.
  document.querySelectorAll("[data-dialogo]").forEach(function (botao) {
    var dlg = document.getElementById(botao.getAttribute("data-dialogo"));
    if (!dlg || typeof dlg.showModal !== "function") return;
    if (!("command" in HTMLButtonElement.prototype)) {
      botao.addEventListener("click", function () { if (!dlg.open) dlg.showModal(); });
    }
    dlg.addEventListener("click", function (ev) { if (ev.target === dlg) dlg.close(); });
    dlg.addEventListener("close", function () { botao.focus(); });
  });

  mostrar(doEndereco());

})();

// Estudo "Como medimos", slide 2 (Caio, 03/11/2026): a lupa do "Fora da curva" abre a lista dos pedidos num pop-up
// (<dialog> #estudo-fora, showModal: o navegador prende o foco). Fecha com o botão Fechar, Esc ou clique no fundo; o
// foco volta à lupa. As setas e o espaço dentro do pop-up não trocam de slide. Sem JS a lupa fica escondida.
(function () {
  "use strict";
  var dlg = document.getElementById("estudo-fora");
  var botao = document.querySelector("[data-ef-abrir]");
  if (!botao) return;
  if (!dlg || typeof dlg.showModal !== "function") { botao.hidden = true; return; }
  var fechar = dlg.querySelector("[data-ef-fechar]");
  var rolagem = dlg.querySelector(".ef-rolagem");

  botao.addEventListener("click", function () {
    dlg.showModal();
    if (rolagem) rolagem.scrollTop = 0;
    fechar.focus();
  });
  fechar.addEventListener("click", function () { dlg.close(); });
  dlg.addEventListener("click", function (ev) { if (ev.target === dlg) dlg.close(); });  // clique no fundo
  dlg.addEventListener("close", function () { botao.focus(); });
  dlg.addEventListener("keydown", function (ev) {  // dentro do pop-up as teclas não navegam entre slides
    if (ev.key !== "Escape") ev.stopPropagation();
  });
})();
