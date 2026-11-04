// Iniciativas (PRD @cris; redesenho de 30/10/2026; dados no servidor a partir de 30/10/2026, noite).
// Os quadros são <details>, então abrem e fecham sem JS, e a página chega pronta do servidor (lida do quadro salvo).
// Aqui se acrescenta, em camadas:
// 1. Detalhe: um aberto por vez (RF5); fecha ao clicar fora, com Esc ou pelo botão Fechar, devolvendo o foco (RF6).
// 2. Galeria: miniaturas em carrossel no detalhe (setas e rolagem); clicar abre o VISOR (<dialog>, showModal) com a
//    imagem grande (ou o PDF num quadro do próprio site), anterior/próximo, ← →, contador "3 de 7", legenda e Esc.
//    "Expandir" abre a VISÃO AMPLIADA (<dialog>) com descrição, responsável, status, próximo passo e a galeria grande.
// 3. Ferramenta do quadro (só com data-ini-edicao="on"): arrastar (Pointer Events), Alt + setas, lápis, ✕, "+ Nova" e
//    anexos no pop-up. Tudo é gravado no SERVIDOR pela API (/viu-agenciamento/iniciativas/api; o endereço vem de data-ini-api), com o cabeçalho
//    X-Requested-With (proteção mínima contra CSRF). Estados: "Salvando…", "Salvo" e erro (aviso flutuante em
//    aria-live; no pop-up, mensagem em role="alert"). Falhou mover ou excluir: o quadro volta ao que está no servidor.
// 4. Importação única: se este navegador guardou alterações da versão anterior (localStorage "ini-quadro:v1") e o quadro
//    do servidor ainda está na semente, aparece "Importar alterações deste navegador"; depois, a chave é apagada.
// Sem JS: só leitura. Movimento só com prefers-reduced-motion: no-preference. A cópia que segue o ponteiro usa
// element.style (CSSOM), aceito pela CSP (style-src-attr 'none').
(function () {
  "use strict";
  var raiz = document.querySelector("[data-iniciativas]");
  if (!raiz) return;
  var API = raiz.getAttribute("data-ini-api") || "/" + location.pathname.split("/")[1] + "/iniciativas/api";
  var EDICAO = raiz.getAttribute("data-ini-edicao") === "on";
  var MAX_MB = parseInt(raiz.getAttribute("data-ini-max-mb"), 10) || 10;
  var CHAVE_ANTIGA = "ini-quadro:v1";
  var CAMPOS = ["sigla", "nome", "desc", "resp", "status", "prox"];
  var MAX = { sigla: 40, nome: 120, desc: 400, resp: 80, status: 120, prox: 120 };
  var EXT_OK = /\.(png|jpe?g|webp|gif|pdf)$/i;
  var movimento = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: no-preference)") : null;
  var anuncio = raiz.querySelector("[data-ini-anuncio]");
  var estadoEl = raiz.querySelector("[data-ini-estado]");
  var comDialogo = typeof document.createElement("dialog").showModal === "function";

  function todos(sel, base) { return [].slice.call((base || raiz).querySelectorAll(sel)); }
  function quadros() { return todos("details.ini-quadro"); }
  function algumDialogo() { return !!document.querySelector("dialog[open]"); }
  function anunciar(texto) {
    if (!anuncio) return;
    anuncio.textContent = "";
    window.setTimeout(function () { anuncio.textContent = texto; }, 40);
  }
  var timerEstado = 0;
  function estado(texto, tipo) {  // tipo: salvando | ok | erro
    if (!estadoEl) return;
    window.clearTimeout(timerEstado);
    estadoEl.textContent = texto;
    estadoEl.className = "ini-estado ini-estado-" + tipo;
    estadoEl.hidden = false;
    if (tipo !== "salvando") timerEstado = window.setTimeout(function () { estadoEl.hidden = true; }, tipo === "ok" ? 1800 : 7000);
  }

  // ---------------------------------------------------------------- 1. detalhe: um por vez, fechar
  function fecharOutros(atual) { quadros().forEach(function (q) { if (q !== atual && q.open) q.open = false; }); }
  function fechar(q) { q.open = false; q.querySelector("summary").focus(); }
  todos("[data-ini-fechar]").forEach(function (b) { b.hidden = false; });
  raiz.addEventListener("toggle", function (e) {
    var q = e.target;
    if (q.matches && q.matches("details.ini-quadro") && q.open) {
      fecharOutros(q);
      verSetasGaleria(q.querySelector("[data-ini-galeria]"));
    }
  }, true);
  raiz.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-ini-fechar]");
    if (b) fechar(b.closest("details.ini-quadro"));
  });
  // clique dentro de um pop-up (inclusive no botão Fechar ou no fundo dele) não fecha o detalhe: o pop-up já se fechou
  // quando o clique chega aqui, e o foco precisa voltar ao que estava no detalhe (validação de 03/11/2026)
  document.addEventListener("click", function (e) {
    if (algumDialogo() || (e.target.closest && e.target.closest("dialog"))) return;
    if (!e.target.closest("details.ini-quadro")) fecharOutros(null);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape" || algumDialogo()) return;  // com pop-up aberto, o Esc é dele
    var aberto = quadros().filter(function (q) { return q.open; })[0];
    if (!aberto) return;
    e.stopPropagation();
    fechar(aberto);
  }, true);

  // ---------------------------------------------------------------- estado lido da página (vindo do servidor)
  var itens = {}, dados = {}, anexos = {};
  var raias = todos(".ini-raia[data-ini-fase]");
  var tituloFase = {};
  function lis(r) { return todos(".ini-lista > li.ini-item", r); }
  function lista(r) { return r.querySelector(".ini-lista"); }
  function fase(r) { return r.getAttribute("data-ini-fase"); }
  function raiaDe(li) { return li.closest(".ini-raia"); }
  function raiaDaFase(f) { return raias.filter(function (r) { return fase(r) === f; })[0]; }
  function titulo(d) { return d.sigla || d.nome; }
  function sumario(li) { return li.querySelector("summary"); }
  function idDe(li) { return li.getAttribute("data-ini-id"); }
  function plural(n) { return n === 1 ? " iniciativa" : " iniciativas"; }
  function limpo(d) {
    var c = {};
    CAMPOS.forEach(function (k) { c[k] = typeof d[k] === "string" ? d[k].trim().slice(0, MAX[k]) : ""; });
    return c;
  }
  function anexosDoDom(li) {
    return todos("[data-ini-anexo]", li).map(function (a) {
      var tipo = a.getAttribute("data-ini-anexo-tipo");
      return { id: a.getAttribute("data-ini-anexo"), nome: a.getAttribute("data-ini-anexo-nome"), tipo: tipo,
               url: a.getAttribute("href"), imagem: tipo.indexOf("image/") === 0, fixo: a.hasAttribute("data-ini-anexo-fixo") };
    });
  }
  raias.forEach(function (r) {
    tituloFase[fase(r)] = r.querySelector(".ini-fase-nome").textContent.trim();
    lis(r).forEach(function (li) {
      var id = idDe(li), desc = li.querySelector(".ini-caixa-desc");
      itens[id] = li;
      dados[id] = { sigla: li.getAttribute("data-ini-sigla") || "", nome: li.getAttribute("data-ini-nome") || "",
                    desc: desc && desc.textContent.trim() !== "Sem descrição." ? desc.textContent.trim() : "",
                    resp: li.getAttribute("data-ini-resp") || "", status: li.getAttribute("data-ini-status") || "",
                    prox: li.getAttribute("data-ini-prox") || "" };
      anexos[id] = anexosDoDom(li);
    });
  });

  // ---------------------------------------------------------------- API
  function mensagemErro(status, corpo) {
    if (corpo && typeof corpo.detail === "string") return corpo.detail;
    if (status === 422) return "Dados inválidos. Confira os campos.";
    if (status === 413) return "Arquivo acima de " + MAX_MB + " MB.";
    return "Não foi possível salvar (erro " + status + "). Tente de novo.";
  }
  function api(metodo, caminho, corpo) {
    var op = { method: metodo, credentials: "same-origin",
               headers: { "X-Requested-With": "iniciativas", "Accept": "application/json" } };
    if (corpo instanceof FormData) op.body = corpo;
    else if (corpo !== undefined) { op.headers["Content-Type"] = "application/json"; op.body = JSON.stringify(corpo); }
    return window.fetch(API + caminho, op).then(function (r) {
      if (r.status === 204) return null;
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) { var e = new Error(mensagemErro(r.status, j)); e.status = r.status; throw e; }
        return j;
      });
    }, function () { throw new Error("Sem conexão com o servidor. Confira a rede e tente de novo."); });
  }

  // ---------------------------------------------------------------- 2. galeria no detalhe
  function verSetasGaleria(gal) {
    if (!gal) return;
    var ul = gal.querySelector("[data-ini-galeria-lista]"), mais = ul.scrollWidth - ul.clientWidth > 2;
    todos("[data-ini-gal-passo]", gal).forEach(function (b) {
      b.hidden = !mais;
      var passo = +b.getAttribute("data-ini-gal-passo");
      b.disabled = passo < 0 ? ul.scrollLeft <= 1 : ul.scrollLeft >= ul.scrollWidth - ul.clientWidth - 1;
    });
  }
  var molDoc = raiz.querySelector(".ini-mini-ic");
  function iconeDoc() {
    if (molDoc) return molDoc.cloneNode(true);
    var NS = "http://www.w3.org/2000/svg", svg = document.createElementNS(NS, "svg"), p = document.createElementNS(NS, "path");
    svg.setAttribute("class", "icone ini-mini-ic"); svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("aria-hidden", "true");
    p.setAttribute("d", "M6.5 3.5h7.5l4 4v13h-11.5zM13.5 3.5v4.5h4.5M9.5 12.5h5M9.5 16h5");
    svg.appendChild(p);
    return svg;
  }
  function miniatura(a, k, n, classe) {
    var link = document.createElement("a");
    link.className = classe + (a.imagem ? "" : " ini-mini-doc");
    link.href = a.url;
    link.setAttribute("data-ini-anexo", a.id);
    link.setAttribute("data-ini-anexo-tipo", a.tipo);
    link.setAttribute("data-ini-anexo-nome", a.nome);
    if (a.fixo) link.setAttribute("data-ini-anexo-fixo", "");
    link.setAttribute("aria-label", (a.imagem ? "Imagem " : "Documento ") + (k + 1) + " de " + n + ": " + a.nome);
    if (a.imagem) {
      var img = document.createElement("img");
      img.src = a.url; img.alt = ""; img.loading = "lazy"; img.decoding = "async";
      link.appendChild(img);
    } else {
      link.appendChild(iconeDoc());
      var s = document.createElement("span");
      s.className = "ini-mini-nome";
      s.textContent = a.nome;
      link.appendChild(s);
    }
    return link;
  }
  function pintarGaleria(li) {
    var gal = li.querySelector("[data-ini-galeria]");
    if (!gal) return;
    var lst = anexos[idDe(li)] || [], ul = gal.querySelector("[data-ini-galeria-lista]");
    ul.textContent = "";
    lst.forEach(function (a, k) {
      var item = document.createElement("li");
      item.appendChild(miniatura(a, k, lst.length, "ini-mini"));
      ul.appendChild(item);
    });
    gal.querySelector("[data-ini-galeria-n]").textContent = lst.length;
    gal.hidden = !lst.length;
    verSetasGaleria(gal);
  }
  raiz.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-ini-gal-passo]");
    if (!b) return;
    var ul = b.closest("[data-ini-galeria]").querySelector("[data-ini-galeria-lista]");
    ul.scrollBy({ left: +b.getAttribute("data-ini-gal-passo") * ul.clientWidth * 0.8,
                  behavior: movimento && movimento.matches ? "smooth" : "auto" });
  });
  raiz.addEventListener("scroll", function (e) {
    var ul = e.target;
    if (ul.matches && ul.matches("[data-ini-galeria-lista]")) verSetasGaleria(ul.closest("[data-ini-galeria]"));
  }, true);
  window.addEventListener("resize", function () { todos("[data-ini-galeria]").forEach(verSetasGaleria); });

  // ---------------------------------------------------------------- 2b. visor (pop-up grande)
  var visor = raiz.querySelector("[data-ini-visor]");
  var noVisor = { lista: [], k: 0, volta: null };
  function midiaVisor(a) {
    var caixa = visor.querySelector("[data-ini-v-midia]");
    caixa.textContent = "";
    if (a.imagem) {
      var img = document.createElement("img");
      img.className = "ini-v-img"; img.src = a.url; img.alt = a.nome;
      caixa.appendChild(img);
    } else {
      var f = document.createElement("iframe");
      f.className = "ini-v-pdf"; f.src = a.url; f.title = "Documento: " + a.nome;
      caixa.appendChild(f);
    }
  }
  function mostrar(k) {
    var n = noVisor.lista.length;
    noVisor.k = (k + n) % n;
    var a = noVisor.lista[noVisor.k];
    midiaVisor(a);
    visor.querySelector("[data-ini-v-conta]").textContent = (noVisor.k + 1) + " de " + n;
    visor.querySelector("[data-ini-v-legenda]").textContent = a.nome;
    visor.querySelector("[data-ini-v-abrir]").href = a.url;
    todos("[data-ini-v-passo]", visor).forEach(function (b) { b.hidden = n < 2; });
  }
  function abrirVisor(lst, k, volta) {
    if (!visor || !comDialogo || !lst.length) return false;
    noVisor = { lista: lst, k: k, volta: volta };
    mostrar(k);
    visor.showModal();
    var prox = visor.querySelector('[data-ini-v-passo="1"]');
    (prox && !prox.hidden ? prox : visor.querySelector("[data-ini-v-fechar]")).focus();
    return true;
  }
  if (visor && comDialogo) {
    visor.addEventListener("click", function (e) {
      if (e.target === visor) { visor.close(); return; }
      var b = e.target.closest("[data-ini-v-passo]");
      if (b) mostrar(noVisor.k + +b.getAttribute("data-ini-v-passo"));
      if (e.target.closest("[data-ini-v-fechar]")) visor.close();
    });
    visor.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        e.preventDefault();
        if (noVisor.lista.length > 1) mostrar(noVisor.k + (e.key === "ArrowRight" ? 1 : -1));
      }
      // dentro do pop-up as setas não trocam de página do portal
      if (/^(Arrow|Page|Home|End)/.test(e.key)) e.stopPropagation();
    });
    visor.addEventListener("close", function () {
      visor.querySelector("[data-ini-v-midia]").textContent = "";  // para o PDF e libera a imagem
      var v = noVisor.volta;
      if (v && v.isConnected) v.focus();
    });
  }

  // ---------------------------------------------------------------- 2c. visão ampliada ("Expandir")
  var ampliado = raiz.querySelector("[data-ini-ampliado]"), ampliadoId = null, ampliadoVolta = null;
  var edicaoPronta = false;
  var abrirEdicao = function () {};
  // clicar numa miniatura (no detalhe ou na visão ampliada) abre o visor; sem <dialog>, o link abre o arquivo
  raiz.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-ini-anexo]");
    if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.button > 0) return;
    var li = a.closest("li.ini-item"), id = li ? idDe(li) : ampliadoId;
    var lst = anexos[id] || [], k = lst.map(function (x) { return x.id; }).indexOf(a.getAttribute("data-ini-anexo"));
    if (k < 0) return;
    if (abrirVisor(lst, k, a)) e.preventDefault();
  });
  function meta(dl, rotulo, valor) {
    var div = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd");
    dt.textContent = rotulo;
    dd.textContent = valor;
    div.appendChild(dt);
    div.appendChild(dd);
    dl.appendChild(div);
  }
  function pintarAmpliado() {
    var li = itens[ampliadoId];
    if (!li) { ampliado.close(); return; }
    var d = dados[ampliadoId], lst = anexos[ampliadoId] || [], r = raiaDe(li);
    var faseEl = ampliado.querySelector("[data-ini-a-fase]");
    faseEl.textContent = "";
    faseEl.appendChild(r.querySelector(".ini-raia-topo .ini-medidor").cloneNode(true));
    faseEl.style.setProperty("--ini-cor", window.getComputedStyle(r).getPropertyValue("--ini-cor"));  // cor da fase
    var sp = document.createElement("span");
    sp.textContent = tituloFase[fase(r)];
    faseEl.appendChild(sp);
    ampliado.querySelector("[data-ini-a-titulo]").textContent = titulo(d);
    var nome = ampliado.querySelector("[data-ini-a-nome]");
    nome.textContent = d.sigla ? d.nome : "";
    nome.hidden = !d.sigla;
    ampliado.querySelector("[data-ini-a-desc]").textContent = d.desc || "Sem descrição.";
    var dl = ampliado.querySelector("[data-ini-a-meta]");
    dl.textContent = "";
    meta(dl, "Responsável", d.resp || "a definir");
    if (d.status) meta(dl, "Status", d.status);
    if (d.prox) meta(dl, "Próximo passo", d.prox);
    var acoes = ampliado.querySelector("[data-ini-a-acoes]"), link = li.querySelector(".ini-caixa-acoes a.ini-botao");
    acoes.textContent = "";
    if (link) acoes.appendChild(link.cloneNode(true));
    if (edicaoPronta) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "ini-botao"; b.setAttribute("data-ini-a-editar", "");
      b.textContent = "Editar e anexar";
      acoes.appendChild(b);
    }
    acoes.hidden = !acoes.childNodes.length;
    var ul = ampliado.querySelector("[data-ini-a-lista]");
    ul.textContent = "";
    lst.forEach(function (a, k) {
      var item = document.createElement("li");
      item.appendChild(miniatura(a, k, lst.length, "ini-a-mini"));
      ul.appendChild(item);
    });
    ampliado.querySelector("[data-ini-a-n]").textContent = lst.length;
    ampliado.querySelector("[data-ini-a-vazio]").hidden = lst.length > 0;
  }
  function abrirAmpliado(li, volta) {
    ampliadoId = idDe(li);
    ampliadoVolta = volta;
    pintarAmpliado();
    ampliado.showModal();
    ampliado.querySelector("[data-ini-a-fechar]").focus();
  }
  if (ampliado && comDialogo) {
    todos("[data-ini-expandir]").forEach(function (b) { b.hidden = false; });
    raiz.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest("[data-ini-expandir]");
      if (b) abrirAmpliado(b.closest("li.ini-item"), b);
    });
    ampliado.addEventListener("click", function (e) {
      if (e.target === ampliado || e.target.closest("[data-ini-a-fechar]")) ampliado.close();
      else if (e.target.closest("[data-ini-a-editar]") && itens[ampliadoId]) abrirEdicao({ li: itens[ampliadoId], deAmpliado: true });
    });
    ampliado.addEventListener("keydown", function (e) { if (/^(Arrow|Page|Home|End)/.test(e.key)) e.stopPropagation(); });
    ampliado.addEventListener("close", function () {
      ampliadoId = null;
      if (ampliadoVolta && ampliadoVolta.isConnected) ampliadoVolta.focus();
    });
  }

  // ---------------------------------------------------------------- 3. ferramenta do quadro (edição no servidor)
  var dialogo = raiz.querySelector("[data-ini-dialogo]");
  if (!EDICAO || !comDialogo || !dialogo || !window.fetch) return;  // só leitura

  var form = dialogo.querySelector("[data-ini-form]");
  var bExcluirD = dialogo.querySelector("[data-ini-d-excluir]");
  var bSalvar = form.querySelector('button[type="submit"]');
  var erro = dialogo.querySelector("#ini-d-erro");
  var falha = dialogo.querySelector("[data-ini-d-falha]");
  var arquivo = dialogo.querySelector("#ini-d-arquivo");
  var erroArquivo = dialogo.querySelector("[data-ini-d-arquivo-erro]");
  var listaAnexosD = dialogo.querySelector("[data-ini-d-anexos-lista]");
  var arrasto = null, pressao = null, edicao = null;
  var primeiroLi = raiz.querySelector(".ini-lista > li.ini-item");
  var modelo = primeiroLi ? primeiroLi.cloneNode(true) : null;  // molde limpo para os quadros incluídos

  // ---------- pintar quadro, detalhe e contagens ----------
  function trocarFilho(pai, depoisDe, classe, tag, texto) {
    var el = pai.querySelector("." + classe);
    if (texto) {
      if (!el) { el = document.createElement(tag); el.className = classe; depoisDe.insertAdjacentElement("afterend", el); }
      el.textContent = texto;
    } else if (el) el.remove();
  }
  function pintar(li) {
    var id = idDe(li), d = dados[id], t = titulo(d);
    ["sigla", "nome", "resp", "status", "prox"].forEach(function (k) { li.setAttribute("data-ini-" + k, d[k] || ""); });
    var sigla = li.querySelector("summary .ini-sigla");
    sigla.textContent = t;
    trocarFilho(sumario(li), sigla, "ini-nome", "span", d.sigla ? d.nome : "");
    var caixa = li.querySelector(".ini-caixa");
    caixa.setAttribute("aria-label", "Descrição: " + t);
    var cs = caixa.querySelector(".ini-caixa-sigla");
    cs.textContent = t;
    trocarFilho(caixa, cs, "ini-caixa-nome", "p", d.sigla ? d.nome : "");
    caixa.querySelector(".ini-caixa-desc").textContent = d.desc || "Sem descrição.";
    var dl = caixa.querySelector(".ini-caixa-meta");
    dl.textContent = "";
    meta(dl, "Responsável", d.resp || "a definir");
    if (d.status) meta(dl, "Status", d.status);
    if (d.prox) meta(dl, "Próximo passo", d.prox);
    li.querySelector("[data-ini-editar]").setAttribute("aria-label", "Editar iniciativa: " + t);
    li.querySelector("[data-ini-excluir]").setAttribute("aria-label", "Excluir do quadro: " + t);
    pintarGaleria(li);
  }
  function pintarFase(li) {
    var r = raiaDe(li), alvo = li.querySelector(".ini-caixa-fase");
    if (!r || !alvo) return;
    var medidor = r.querySelector(".ini-raia-topo .ini-medidor").cloneNode(true), rotulo = document.createElement("span");
    rotulo.textContent = tituloFase[fase(r)];
    alvo.textContent = "";
    alvo.appendChild(medidor);
    alvo.appendChild(rotulo);
  }
  function densidade(n) { return n <= 3 ? 1 : n === 4 ? 2 : 3; }  // mesma regra de iniciativas/__init__.py
  function verRolagem(ul) { ul.classList.toggle("ini-mais", ul.scrollHeight - ul.clientHeight - ul.scrollTop > 2); }
  function contar() {
    var total = 0;
    raias.forEach(function (r) {
      var n = lis(r).length, num = r.querySelector(".ini-num"), leitor = num.nextElementSibling;
      total += n;
      num.textContent = n;
      if (leitor && leitor.classList.contains("so-leitor")) leitor.textContent = plural(n);
      lista(r).setAttribute("data-densidade", densidade(n));
      verRolagem(lista(r));
    });
    var pnum = raiz.querySelector(".ini-painel-num");
    if (pnum) {
      pnum.textContent = total;
      if (pnum.nextSibling && pnum.nextSibling.nodeType === 3) pnum.nextSibling.nodeValue = plural(total);
    }
  }
  function mexido() { raiz.classList.add("ini-mexido"); }
  function fecharAbertos() { todos("details.ini-quadro[open]").forEach(function (q) { q.open = false; }); }
  // FLIP: os quadros que mudam de lugar deslizam até a nova posição (só o summary, para não mexer no detalhe)
  function comFlip(fn) {
    if (!movimento || !movimento.matches || !Element.prototype.animate) { fn(); return; }
    var sums = todos(".ini-lista > li.ini-item > details > summary");
    var antes = sums.map(function (s) { return s.getBoundingClientRect(); });
    fn();
    sums.forEach(function (s, k) {
      if (!s.isConnected) return;
      var r = s.getBoundingClientRect(), dx = antes[k].left - r.left, dy = antes[k].top - r.top;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
      s.animate([{ transform: "translate(" + dx + "px, " + dy + "px)" }, { transform: "none" }],
                { duration: 180, easing: "cubic-bezier(0.2, 0.7, 0.2, 1)" });
    });
  }

  // ---------- quadros incluídos ----------
  function ligar(li) {
    var s = sumario(li);
    s.setAttribute("aria-keyshortcuts", "Alt+ArrowLeft Alt+ArrowRight Alt+ArrowUp Alt+ArrowDown");
    s.setAttribute("aria-describedby", "ini-ajuda-teclado");
    li.querySelector("[data-ini-ferramentas]").hidden = false;
    li.querySelector("[data-ini-editar]").addEventListener("click", function () { abrirEdicao({ li: li }); });
    li.querySelector("[data-ini-excluir]").addEventListener("click", function () { excluir(li); });
  }
  function criarItem(id) {
    var li = modelo.cloneNode(true);
    li.setAttribute("data-ini-id", id);
    ["sigla", "nome", "resp", "status", "prox"].forEach(function (k) { li.setAttribute("data-ini-" + k, ""); });
    li.querySelector("details").open = false;
    var link = li.querySelector(".ini-caixa-acoes a.ini-botao");
    if (link) link.remove();
    li.querySelector("[data-ini-fechar]").hidden = false;
    var bx = li.querySelector("[data-ini-expandir]");
    if (bx) bx.hidden = !(ampliado && comDialogo);
    itens[id] = li;
    anexos[id] = anexos[id] || [];
    ligar(li);
    return li;
  }
  function deServidor(i) {
    return limpo({ sigla: i.sigla, nome: i.nome, desc: i.descricao, resp: i.responsavel, status: i.status, prox: i.proximo });
  }
  // põe o quadro igual ao do servidor (depois de uma falha, ou da importação)
  function sincronizar(resp) {
    var fases = {}, vistos = {};
    raias.forEach(function (r) { fases[fase(r)] = []; });
    resp.iniciativas.forEach(function (i) {
      if (!fases[i.fase]) return;
      if (!itens[i.id]) {
        if (!modelo) { window.location.reload(); return; }
        criarItem(i.id);
      }
      dados[i.id] = deServidor(i);
      anexos[i.id] = resp.anexos[i.id] || [];
      fases[i.fase].push(i.id);
      vistos[i.id] = true;
    });
    Object.keys(itens).forEach(function (id) {
      if (!vistos[id]) { itens[id].remove(); delete itens[id]; delete dados[id]; delete anexos[id]; }
    });
    raias.forEach(function (r) { fases[fase(r)].forEach(function (id) { lista(r).appendChild(itens[id]); }); });
    Object.keys(itens).forEach(function (id) { pintar(itens[id]); pintarFase(itens[id]); });
    contar();
  }
  function recarregar(motivo) {
    return api("GET", "/iniciativas").then(function (r) {
      sincronizar(r);
      if (motivo) estado(motivo, "erro");
    }, function (e) { estado(e.message, "erro"); });
  }
  function falhou(e) {  // mover/excluir falhou: volta ao que o servidor tem e avisa
    anunciar(e.message);
    recarregar(e.message + " O quadro voltou ao que está salvo.");
  }

  // ---------- liga a ferramenta ----------
  var ajuda = document.createElement("p");
  ajuda.id = "ini-ajuda-teclado";
  ajuda.className = "so-leitor";
  ajuda.textContent = "Alt e seta para a esquerda ou para a direita muda a fase; Alt e seta para cima ou para baixo muda a ordem. " +
                      "As alterações são salvas no servidor e valem para todos.";
  raiz.appendChild(ajuda);
  raiz.classList.add("ini-editavel");
  edicaoPronta = true;
  Object.keys(itens).forEach(function (id) { ligar(itens[id]); });
  raias.forEach(function (r) {
    var b = r.querySelector("[data-ini-nova]"), ul = lista(r);
    if (b) { b.hidden = false; b.addEventListener("click", function () { abrirEdicao({ raia: r, botao: b }); }); }
    ul.addEventListener("scroll", function () { verRolagem(ul); }, { passive: true });
  });
  window.addEventListener("resize", function () { raias.forEach(function (r) { verRolagem(lista(r)); }); });
  contar();

  // ---------- gravações ----------
  function salvarPosicao(li) {
    var r = raiaDe(li), k = lis(r).indexOf(li), id = idDe(li);
    estado("Salvando…", "salvando");
    return api("POST", "/iniciativas/" + encodeURIComponent(id) + "/mover", { fase: fase(r), posicao: k })
      .then(function () { estado("Salvo", "ok"); }, falhou);
  }
  // devolve o vizinho que recebe o foco; undefined = a pessoa desistiu na confirmação
  function excluir(li, semFoco) {
    var id = idDe(li), t = titulo(dados[id]), irmaos = lis(raiaDe(li)), k = irmaos.indexOf(li);
    var foco = irmaos[k + 1] || irmaos[k - 1] || null;
    if (!window.confirm("Excluir “" + t + "” do quadro? A iniciativa sai para todos que abrirem o portal.")) return undefined;
    li.querySelector("details").open = false;
    mexido();
    comFlip(function () { li.remove(); });
    delete itens[id];
    contar();
    estado("Salvando…", "salvando");
    api("DELETE", "/iniciativas/" + encodeURIComponent(id)).then(function () {
      estado("Salvo", "ok");
      anunciar(t + " excluída do quadro.");
    }, falhou);
    if (semFoco) return foco;
    if (foco) sumario(foco).focus();
    else { var b = raiz.querySelector("[data-ini-nova]:not([hidden])"); if (b) b.focus(); }
    return foco;
  }

  // ---------- pop-up de edição, inclusão e anexos ----------
  function campo(k) { return form.elements[k]; }
  function limparErros() {
    erro.hidden = true;
    falha.hidden = true;
    erroArquivo.hidden = true;
    ["sigla", "nome"].forEach(function (k) { campo(k).removeAttribute("aria-invalid"); campo(k).removeAttribute("aria-describedby"); });
  }
  function pintarAnexosDialogo() {
    var id = edicao && edicao.li ? idDe(edicao.li) : null, lst = id ? anexos[id] || [] : [];
    dialogo.querySelector("[data-ini-d-anexos-nova]").hidden = !!id;
    dialogo.querySelector("[data-ini-d-anexar]").hidden = !id;
    listaAnexosD.textContent = "";
    lst.forEach(function (a) {
      var item = document.createElement("li"), nome = document.createElement("span"), b = document.createElement("button");
      item.className = "ini-d-anexo";
      if (a.imagem) {
        var img = document.createElement("img");
        img.src = a.url; img.alt = ""; img.loading = "lazy";
        item.appendChild(img);
      } else item.appendChild(iconeDoc());
      nome.className = "ini-d-anexo-nome";
      nome.textContent = a.nome;
      b.type = "button";
      b.className = "ini-d-link ini-d-remover";
      b.textContent = "Remover";
      b.setAttribute("aria-label", "Remover anexo: " + a.nome);
      b.addEventListener("click", function () { removerAnexo(id, a, b); });
      item.appendChild(nome);
      if (!a.fixo) item.appendChild(b);  // foto fixa do catálogo (Caio, 03/11/2026): não sai pela tela
      listaAnexosD.appendChild(item);
    });
    listaAnexosD.hidden = !lst.length;
  }
  abrirEdicao = function (op) {  // op: {li} para editar ou {raia, botao} para incluir
    fecharAbertos();
    edicao = op;
    var d = op.li ? dados[idDe(op.li)] : limpo({});
    CAMPOS.forEach(function (k) { campo(k).value = d[k] || ""; });
    campo("fase").value = fase(op.li ? raiaDe(op.li) : op.raia);
    dialogo.querySelector("#ini-d-titulo").textContent = op.li ? "Editar " + titulo(d) : "Nova iniciativa";
    bExcluirD.hidden = !op.li;
    bSalvar.disabled = false;
    limparErros();
    pintarAnexosDialogo();
    dialogo.showModal();
    campo("sigla").focus();
    campo("sigla").select();
  };
  function fecharDialogo() { if (dialogo.open) dialogo.close(); }
  dialogo.addEventListener("close", function () {  // Esc, Cancelar ou Salvar: o foco volta de onde veio
    var op = edicao;
    edicao = null;
    if (!op) return;
    if (op.deAmpliado && ampliado && ampliado.open) { pintarAmpliado(); return; }
    var volta = op.focoFinal || (op.li && op.li.isConnected ? sumario(op.li) : op.botao);
    if (volta && volta.isConnected) volta.focus();
  });
  dialogo.addEventListener("keydown", function (e) {
    if (/^(Arrow|Page)/.test(e.key)) e.stopPropagation();  // dentro do pop-up as setas não trocam de página
    if (e.key === "Enter" && !e.shiftKey && e.target.tagName === "TEXTAREA") {  // Enter salva; Shift + Enter quebra
      e.preventDefault();
      if (form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event("submit", { cancelable: true }));
    }
  });
  dialogo.addEventListener("click", function (e) { if (e.target === dialogo) fecharDialogo(); });  // clique no fundo
  dialogo.querySelector("[data-ini-d-cancelar]").addEventListener("click", fecharDialogo);
  bExcluirD.addEventListener("click", function () {
    var op = edicao;
    if (!op || !op.li) return;
    var foco = excluir(op.li, true);
    if (foco === undefined) return;  // desistiu na confirmação
    op.focoFinal = foco ? sumario(foco) : raiz.querySelector("[data-ini-nova]:not([hidden])");
    op.deAmpliado = false;
    if (ampliado && ampliado.open) ampliado.close();
    fecharDialogo();
  });
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var op = edicao;
    if (!op || bSalvar.disabled) return;
    var v = {};
    CAMPOS.forEach(function (k) { v[k] = campo(k).value; });
    v = limpo(v);
    limparErros();
    if (!v.sigla && !v.nome) {
      erro.hidden = false;
      ["sigla", "nome"].forEach(function (k) { campo(k).setAttribute("aria-invalid", "true"); campo(k).setAttribute("aria-describedby", "ini-d-erro"); });
      campo("sigla").focus();
      return;
    }
    var corpo = { sigla: v.sigla, nome: v.nome, fase: campo("fase").value, responsavel: v.resp, descricao: v.desc,
                  status: v.status, proximo: v.prox };
    bSalvar.disabled = true;
    estado("Salvando…", "salvando");
    var pedido = op.li ? api("PUT", "/iniciativas/" + encodeURIComponent(idDe(op.li)), corpo) : api("POST", "/iniciativas", corpo);
    pedido.then(function (i) {
      var li = op.li, destino = raiaDaFase(i.fase);
      mexido();
      if (li) {
        dados[i.id] = deServidor(i);
        pintar(li);
        if (destino && destino !== raiaDe(li)) comFlip(function () { lista(destino).appendChild(li); });
        anunciar("Iniciativa " + titulo(dados[i.id]) + " atualizada: " + tituloFase[i.fase] + ".");
      } else {
        if (!modelo) { window.location.reload(); return; }
        li = criarItem(i.id);
        dados[i.id] = deServidor(i);
        pintar(li);
        comFlip(function () { lista(destino || op.raia).appendChild(li); });
        anunciar("Nova iniciativa " + titulo(dados[i.id]) + " incluída em " + tituloFase[i.fase] + ".");
      }
      pintarFase(li);
      contar();
      estado("Salvo", "ok");
      op.focoFinal = sumario(li);
      fecharDialogo();
      li.scrollIntoView({ block: "nearest" });
    }, function (err) {
      bSalvar.disabled = false;
      falha.textContent = err.message;
      falha.hidden = false;
      estado(err.message, "erro");
    });
  });

  // ---------- anexos (no pop-up de edição; enviam na hora) ----------
  function erroDeArquivo(texto) {
    erroArquivo.textContent = texto;
    erroArquivo.hidden = !texto;
  }
  function atualizarGalerias(id) {
    if (itens[id]) pintarGaleria(itens[id]);
    pintarAnexosDialogo();
    if (ampliado && ampliado.open && ampliadoId === id) pintarAmpliado();
  }
  arquivo.addEventListener("change", function () {
    var op = edicao, arquivos = [].slice.call(arquivo.files || []);
    arquivo.value = "";
    if (!op || !op.li || !arquivos.length) return;
    var id = idDe(op.li), problemas = [], enviados = 0;
    erroDeArquivo("");
    var fila = arquivos.filter(function (f) {
      if (!EXT_OK.test(f.name)) { problemas.push(f.name + ": tipo não aceito (use PNG, JPEG, WebP, GIF ou PDF)"); return false; }
      if (f.size > MAX_MB * 1024 * 1024) { problemas.push(f.name + ": acima de " + MAX_MB + " MB"); return false; }
      return true;
    });
    function proximo() {
      if (!fila.length) {
        if (problemas.length) erroDeArquivo(problemas.join(". ") + ".");
        if (enviados) estado(enviados === 1 ? "Anexo salvo" : enviados + " anexos salvos", "ok");
        else if (problemas.length) estado("Nenhum anexo enviado.", "erro");
        return;
      }
      var f = fila.shift(), fd = new FormData();
      fd.append("arquivo", f, f.name);
      estado("Enviando " + f.name + "…", "salvando");
      api("POST", "/iniciativas/" + encodeURIComponent(id) + "/anexos", fd).then(function (a) {
        enviados += 1;
        (anexos[id] = anexos[id] || []).push(a);
        atualizarGalerias(id);
        anunciar("Anexo enviado: " + a.nome + ".");
        proximo();
      }, function (err) {
        problemas.push(f.name + ": " + err.message.replace(/\.$/, ""));
        proximo();
      });
    }
    proximo();
  });
  function removerAnexo(id, a, botao) {
    if (!window.confirm("Remover o anexo “" + a.nome + "”? O arquivo sai para todos.")) return;
    botao.disabled = true;
    estado("Salvando…", "salvando");
    api("DELETE", "/anexos/" + encodeURIComponent(a.id)).then(function () {
      anexos[id] = (anexos[id] || []).filter(function (x) { return x.id !== a.id; });
      atualizarGalerias(id);
      estado("Anexo removido", "ok");
      anunciar("Anexo removido: " + a.nome + ".");
      arquivo.focus();
    }, function (err) {
      botao.disabled = false;
      erroDeArquivo(err.message);
      estado(err.message, "erro");
    });
  }

  // ---------- teclado: Alt + setas move o quadro em foco ----------
  raiz.addEventListener("keydown", function (e) {
    if (!e.altKey || e.ctrlKey || e.metaKey || e.shiftKey || arrasto || algumDialogo()) return;
    var passo = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -1, ArrowDown: 1 }[e.key];
    if (!passo) return;
    var li = e.target.closest && e.target.closest("li.ini-item");
    if (!li) return;
    e.preventDefault();
    e.stopPropagation();
    var r = raiaDe(li), irmaos = lis(r), k = irmaos.indexOf(li), t = titulo(dados[idDe(li)]);
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      var destino = raias[raias.indexOf(r) + passo];
      if (!destino) { anunciar(t + " já está em " + tituloFase[fase(r)] + ", a fase da ponta."); return; }
      var outros = lis(destino);
      mexido();
      comFlip(function () { lista(destino).insertBefore(li, outros[Math.min(k, outros.length)] || null); });
    } else {
      var vizinho = irmaos[k + passo];
      if (!vizinho) { anunciar(t + " já é " + (passo < 0 ? "o primeiro" : "o último") + " de " + tituloFase[fase(r)] + "."); return; }
      mexido();
      comFlip(function () { lista(r).insertBefore(li, passo < 0 ? vizinho : vizinho.nextElementSibling); });
    }
    pintarFase(li);
    contar();
    salvarPosicao(li);
    var agora = lis(raiaDe(li));
    anunciar(t + ": " + tituloFase[fase(raiaDe(li))] + ", posição " + (agora.indexOf(li) + 1) + " de " + agora.length + ".");
    sumario(li).focus();
    li.scrollIntoView({ block: "nearest" });
  });

  // ---------- arrastar e soltar (Pointer Events) ----------
  function cancelarPressao() {
    if (pressao) window.clearTimeout(pressao.timer);
    pressao = null;
  }
  function marcarAlvo(r) { raias.forEach(function (x) { x.classList.toggle("ini-alvo", x === r); }); }
  function posicionar(x, y) { arrasto.fantasma.style.transform = "translate(" + (x - arrasto.dx) + "px, " + (y - arrasto.dy) + "px)"; }
  function iniciar(x, y) {
    var li = pressao.li, ret = li.getBoundingClientRect();
    window.clearTimeout(pressao.timer);
    fecharAbertos();
    mexido();
    var fantasma = li.cloneNode(true);
    fantasma.className = "ini-fantasma";
    fantasma.removeAttribute("data-ini-id");
    fantasma.setAttribute("aria-hidden", "true");
    fantasma.style.width = ret.width + "px";
    fantasma.style.fontSize = window.getComputedStyle(li).fontSize;
    (document.fullscreenElement || document.body).appendChild(fantasma);
    arrasto = { li: li, id: pressao.id, fantasma: fantasma, dx: pressao.x - ret.left, dy: pressao.y - ret.top,
                ul: li.parentNode, prox: li.nextSibling, fase0: fase(raiaDe(li)), k0: lis(raiaDe(li)).indexOf(li) };
    pressao = null;
    li.classList.add("ini-vaga");
    document.documentElement.classList.add("ini-arrastando");
    posicionar(x, y);
    marcarAlvo(raiaDe(li));
  }
  function mover(x, y) {
    posicionar(x, y);
    var el = document.elementFromPoint(x, y), r = el && el.closest && el.closest(".ini-raia[data-ini-fase]");
    if (!r || !raiz.contains(r)) return;  // fora das colunas: a vaga fica onde está
    marcarAlvo(r);
    var li = arrasto.li, ul = lista(r), antesDe = null, borda = ul.getBoundingClientRect();
    if (ul.scrollHeight > ul.clientHeight) {  // coluna que rola: perto da borda, rola junto
      if (y < borda.top + 28) ul.scrollTop -= 12;
      else if (y > borda.bottom - 28) ul.scrollTop += 12;
    }
    var outros = lis(r).filter(function (o) { return o !== li; });
    for (var k = 0; k < outros.length; k++) {
      var ret = outros[k].getBoundingClientRect();
      if (y < ret.top + ret.height / 2) { antesDe = outros[k]; break; }
    }
    if (li.parentNode === ul && (antesDe ? li.nextElementSibling === antesDe : !li.nextElementSibling)) return;
    comFlip(function () { ul.insertBefore(li, antesDe); });
    pintarFase(li);
    contar();
  }
  function bloquearClique() {  // o clique que vem junto com o soltar não abre o quadro
    function b(ev) { ev.preventDefault(); ev.stopPropagation(); }
    document.addEventListener("click", b, true);
    window.setTimeout(function () { document.removeEventListener("click", b, true); }, 0);
  }
  function terminar(confirmado) {
    var a = arrasto;
    arrasto = null;
    a.fantasma.remove();
    a.li.classList.remove("ini-vaga");
    document.documentElement.classList.remove("ini-arrastando");
    marcarAlvo(null);
    if (!confirmado) a.ul.insertBefore(a.li, a.prox && a.prox.parentNode === a.ul ? a.prox : null);
    pintarFase(a.li);
    contar();
    bloquearClique();
    var r = raiaDe(a.li), agora = lis(r), k = agora.indexOf(a.li), t = titulo(dados[idDe(a.li)]);
    if (confirmado && (fase(r) !== a.fase0 || k !== a.k0)) {
      salvarPosicao(a.li);
      anunciar(t + ": " + tituloFase[fase(r)] + ", posição " + (k + 1) + " de " + agora.length + ".");
    }
    sumario(a.li).focus({ preventScroll: true });
  }
  raiz.addEventListener("pointerdown", function (e) {
    if (arrasto || e.button !== 0 || !e.isPrimary) return;
    var s = e.target.closest && e.target.closest(".ini-lista > li.ini-item > details > summary");
    if (!s) return;
    var toque = e.pointerType !== "mouse";
    pressao = { li: s.closest("li.ini-item"), id: e.pointerId, x: e.clientX, y: e.clientY, toque: toque, timer: 0 };
    if (toque) pressao.timer = window.setTimeout(function () { if (pressao) iniciar(pressao.x, pressao.y); }, 350);
  });
  document.addEventListener("pointermove", function (e) {
    if (arrasto) { if (e.pointerId === arrasto.id) mover(e.clientX, e.clientY); return; }
    if (!pressao || e.pointerId !== pressao.id) return;
    var d = Math.abs(e.clientX - pressao.x) + Math.abs(e.clientY - pressao.y);
    if (pressao.toque) { if (d > 10) cancelarPressao(); return; }  // mexeu antes de segurar: é rolagem
    if (d > 6) { iniciar(pressao.x, pressao.y); mover(e.clientX, e.clientY); }  // limiar: abaixo disso é clique
  });
  document.addEventListener("pointerup", function (e) {
    if (pressao && e.pointerId === pressao.id) cancelarPressao();
    if (arrasto && e.pointerId === arrasto.id) terminar(true);
  });
  document.addEventListener("pointercancel", function (e) {
    if (pressao && e.pointerId === pressao.id) cancelarPressao();
    if (arrasto && e.pointerId === arrasto.id) terminar(false);
  });
  document.addEventListener("keydown", function (e) {
    if (arrasto && e.key === "Escape") { e.preventDefault(); e.stopPropagation(); terminar(false); }
  }, true);
  raiz.addEventListener("touchmove", function (e) { if (arrasto) e.preventDefault(); }, { passive: false });
  raiz.addEventListener("contextmenu", function (e) { if (arrasto || (pressao && pressao.toque)) e.preventDefault(); });
  raiz.addEventListener("dragstart", function (e) { if (e.target.closest && e.target.closest(".ini-lista")) e.preventDefault(); });
  window.addEventListener("blur", function () { cancelarPressao(); if (arrasto) terminar(false); });

  // ---------- 4. importação única do que este navegador guardou na versão anterior ----------
  (function importacao() {
    var guardado = null;
    try { guardado = JSON.parse(window.localStorage.getItem(CHAVE_ANTIGA) || "null"); } catch (e) { guardado = null; }
    if (!guardado || typeof guardado !== "object" || raiz.getAttribute("data-ini-semente") !== "1") return;
    var caixa = raiz.querySelector("[data-ini-importar]"), botao = raiz.querySelector("[data-ini-importar-botao]");
    if (!caixa || !botao) return;
    caixa.hidden = false;
    botao.addEventListener("click", function () {
      if (!window.confirm("Levar ao servidor as alterações que este navegador guardou (fases, ordem, textos, inclusões e " +
                          "exclusões)? Elas passam a valer para todos.")) return;
      botao.disabled = true;
      estado("Importando…", "salvando");
      api("POST", "/importar", guardado).then(function (r) {
        try { window.localStorage.removeItem(CHAVE_ANTIGA); } catch (e) { /* segue */ }
        caixa.hidden = true;
        estado("Importado: " + r.incluidas + " incluídas, " + r.editadas + " editadas, " + r.excluidas + " excluídas", "ok");
        mexido();
        return api("GET", "/iniciativas").then(sincronizar);
      }).catch(function (e) {
        botao.disabled = false;
        if (e.status === 409) {
          try { window.localStorage.removeItem(CHAVE_ANTIGA); } catch (x) { /* segue */ }
          caixa.hidden = true;
        }
        estado(e.message, "erro");
      });
    });
  })();
})();
