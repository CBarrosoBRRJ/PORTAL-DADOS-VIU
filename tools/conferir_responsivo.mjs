// Varredura de responsividade do portal (31/10/2026, antes do deploy da reunião). Somente leitura: abre o servidor
// LOCAL num Chrome headless (CDP, emulação de dispositivo, mesmo padrão do conferir_layout.mjs) e mede cada página em
// 14 telas (mesa, 4K, ultrawide, tablet, celular e zoom do Windows de 125%/150% simulado por viewport + DPR).
// Uso (Node 22+, servidor no ar):  node tools/conferir_responsivo.mjs [http://127.0.0.1:8400] [--capturas PASTA] [--so 1920x1080,390x844]
// Falha (saída 1) se: a página rola para o lado; algum elemento visível sai da tela na horizontal sem estar dentro de
// uma caixa que corta/rola; algum controle de navegação visível (‹ › ✕, setas, gancho, Capa) fica fora da tela ou
// coberto por outro elemento; ou há erro no console / exceção JS. Avisos (não falham): texto < 11 px, conteúdo que
// ocupa menos de 60% da largura em telas ≥ 2560 px (4K "minúsculo no canto"), caixas de texto sobrepostas.
import { spawn } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const ARGS = process.argv.slice(2);
const opc = (n) => { const i = ARGS.indexOf(n); return i >= 0 ? ARGS[i + 1] : null; };
const CAPTURAS = opc("--capturas");
const SO = opc("--so")?.split(",");
const SO_PAG = opc("--paginas")?.split(",");
const FIM = ARGS.includes("--fim");   // rola até o fim antes de medir (celular: nada pode ficar sob a barra inferior fixa)
const BASE = (ARGS.find((a, i) => !a.startsWith("--") && !["--capturas", "--so", "--paginas"].includes(ARGS[i - 1])) || "http://127.0.0.1:8400").replace(/\/$/, "");
const A = "/viu-agenciamento";
// [nome, largura, altura, dpr, celular]
const TELAS = [
  ["1366x768", 1366, 768, 1, false], ["1440x900", 1440, 900, 1, false], ["1536x864", 1536, 864, 1, false],
  ["1920x1080", 1920, 1080, 1, false], ["2560x1440", 2560, 1440, 1, false], ["3840x2160", 3840, 2160, 1, false],
  ["3440x1440", 3440, 1440, 1, false], ["1024x768", 1024, 768, 1, true], ["768x1024", 768, 1024, 1, true],
  ["820x1180", 820, 1180, 1, true], ["390x844", 390, 844, 3, true], ["360x800", 360, 800, 3, true],
  ["zoom125", 1536, 864, 1.25, false], ["zoom150", 1280, 720, 1.5, false],
].filter((t) => !SO || SO.includes(t[0]));
// [nome, caminho, ação opcional depois de carregar]
const PAGINAS = [
  ["capa", `${A}/capa`], ["roadmap", `${A}/roadmap`],
  ["roadmap-dlg", `${A}/roadmap`, "document.querySelector('[data-rm-galeria]')?.click()"],
  ["demanda", `${A}/`], ["talentos", `${A}/talentos`], ["sla", `${A}/sla`],
  ["estudo#1", `${A}/sla/como-medimos#1`], ["estudo#2", `${A}/sla/como-medimos#2`], ["estudo#3", `${A}/sla/como-medimos#3`],
  ["estudo#4", `${A}/sla/como-medimos#4`], ["estudo#5", `${A}/sla/como-medimos#5`],
  ["lia", `${A}/lia`], ["lia-video", `${A}/lia`, "document.querySelector('[data-lia-video]')?.click()"],
  ["iniciativas", `${A}/iniciativas`], ["previsao", `${A}/previsao`], ["encerramento", `${A}/encerramento`],
].filter((p) => !SO_PAG || SO_PAG.includes(p[0]));
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

const porta = 9800 + Math.floor(Math.random() * 150);
const perfil = mkdtempSync(join(tmpdir(), "conferir-resp-"));
const chrome = spawn("C:/Program Files/Google/Chrome/Application/chrome.exe", ["--headless=new", "--disable-gpu",
  "--hide-scrollbars", "--autoplay-policy=no-user-gesture-required", `--remote-debugging-port=${porta}`, `--user-data-dir=${perfil}`, "about:blank"]);
let alvo;
for (let i = 0; i < 60 && !alvo; i++) {
  await espera(250);
  try { alvo = (await (await fetch(`http://127.0.0.1:${porta}/json`)).json()).find((t) => t.type === "page"); } catch {}
}
if (!alvo) { console.error("Chrome não abriu"); chrome.kill(); process.exit(2); }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pend = {}; let erros = [];
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend[m.id]) { pend[m.id](m); delete pend[m.id]; return; }
  if (m.method === "Runtime.exceptionThrown") erros.push("exceção: " + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text).split("\n")[0]);
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") erros.push("console: " + m.params.args.map((a) => a.value ?? a.description).join(" ").slice(0, 160));
  if (m.method === "Log.entryAdded" && m.params.entry.level === "error") erros.push("log: " + m.params.entry.text.slice(0, 160) + (m.params.entry.url ? " " + m.params.entry.url.replace(BASE, "") : ""));
});
const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
const avaliar = async (expr) => (await cmd("Runtime.evaluate", { expression: expr, returnByValue: true })).result.result?.value;
await cmd("Page.enable"); await cmd("Runtime.enable"); await cmd("Log.enable");
await cmd("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "no-preference" }] });

const MEDIR = () => `(() => {
  const W = innerWidth, H = innerHeight;
  const cache = new Map(); const estilo = (e) => { let c = cache.get(e); if (!c) { c = getComputedStyle(e); cache.set(e, c); } return c; };
  const vis = (e) => { const r = e.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false;
    if (e.closest('[hidden], .so-leitor, dialog:not([open])')) return false;
    return e.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }); };
  const nome = (e) => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + '.' + String(e.className?.baseVal ?? e.className).trim().split(/\\s+/)[0];
  // dentro de caixa que corta/rola na horizontal? (então não "sai da tela" de verdade)
  const cortado = (e) => { for (let x = e.parentElement; x && x !== document.documentElement && x !== document.body; x = x.parentElement) {
      const cs = estilo(x); if (/(hidden|auto|scroll|clip)/.test(cs.overflowX) || cs.clipPath !== 'none') { const r = x.getBoundingClientRect(); if (r.right <= W + 1 && r.left >= -1) return true; } }
    return false; };
  const dlg = document.querySelector('dialog[open]');
  const raiz = dlg || document.body;
  const todos = [...raiz.querySelectorAll('*')].filter((e) => !['SCRIPT','STYLE','svg','path','defs','g','title'].includes(e.tagName) || e.tagName === 'svg').filter(vis);
  const fora = todos.filter((e) => { const r = e.getBoundingClientRect(); return (r.right > W + 1 || r.left < -1) && r.right > -500 && !e.closest(".pular") && !cortado(e); })
    .slice(0, 4).map((e) => { const r = e.getBoundingClientRect(); return nome(e) + '[' + Math.round(r.left) + '..' + Math.round(r.right) + ']'; });
  // textos
  const tamanhos = []; const pequenos = []; let ux0 = W, ux1 = 0; const caixasTexto = [];
  for (const e of todos) {
    const txt = [...e.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(' ').trim();
    if (!txt) continue;
    let px = parseFloat(estilo(e).fontSize);
    if (e instanceof SVGElement && e.getScreenCTM) { const m = e.getScreenCTM(); if (m) px *= Math.hypot(m.a, m.b); }
    const r = e.getBoundingClientRect();
    tamanhos.push(px); if (px < 10.95) pequenos.push(nome(e) + '(' + px.toFixed(1) + '): ' + txt.slice(0, 20));
    if (r.top < H && r.bottom > 0) { ux0 = Math.min(ux0, r.left); ux1 = Math.max(ux1, r.right); }
    if (!(e instanceof SVGElement)) caixasTexto.push([e, r]);
  }
  tamanhos.sort((a, b) => a - b);
  const mediana = tamanhos.length ? tamanhos[Math.floor(tamanhos.length / 2)] : 0;
  // sobreposição de textos (folhas sem relação de parentesco), só na tela visível
  const sob = [];
  const vistos = caixasTexto.filter(([, r]) => r.top < H && r.bottom > 0).slice(0, 400);
  for (let i = 0; i < vistos.length && sob.length < 4; i++) for (let j = i + 1; j < vistos.length && sob.length < 4; j++) {
    const [a, ra] = vistos[i], [b, rb] = vistos[j];
    if (a.contains(b) || b.contains(a)) continue;
    const ix = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), iy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
    if (ix > 4 && iy > 4 && ix * iy > 0.3 * Math.min(ra.width * ra.height, rb.width * rb.height)) {
      // ignora se um está por cima de propósito (aria-hidden decorativo)
      if (a.closest('[aria-hidden="true"]') || b.closest('[aria-hidden="true"]')) continue;
      sob.push(nome(a) + ' x ' + nome(b));
    }
  }
  // controles de navegação
  const SEL = '.cab-passo, .proxima a, .fechar-estudo, .controles button, .controles a, .tela-cheia-botao, .gancho-link, .navegador a, .navegador button, [data-rm-anterior], [data-rm-proxima], [data-rm-fechar], [data-lia-fechar], .capa a, .fim a, a[href$="/capa"]';
  const nav = [];
  for (const e of raiz.querySelectorAll(SEL)) {
    if (!vis(e)) continue;
    const r = e.getBoundingClientRect(); const fixo = /fixed|sticky/.test(estilo(e).position) || [...(function* () { for (let x = e.parentElement; x; x = x.parentElement) yield x; })()].some((x) => estilo(x).position === 'fixed');
    const probs = [];
    if (r.left < -1 || r.right > W + 1) probs.push('fora na horizontal');
    if (fixo && (r.top < -1 || r.bottom > H + 1)) probs.push('fixo fora na vertical');
    if (r.width < 24 || r.height < 24) probs.push('alvo pequeno ' + Math.round(r.width) + 'x' + Math.round(r.height));
    if (r.top >= 0 && r.bottom <= H && r.left >= 0 && r.right <= W) {
      const cx = r.left + r.width / 2, cy = r.top + r.height / 2; const h = document.elementFromPoint(cx, cy);
      if (h && !e.contains(h) && !h.contains(e)) probs.push('coberto por ' + nome(h));
    }
    if (probs.length) nav.push(nome(e) + ' "' + (e.getAttribute('aria-label') || e.textContent.trim()).slice(0, 18) + '": ' + probs.join(', '));
  }
  const cobertos = [];
  if (${FIM} && !dlg) for (const e of document.querySelectorAll('.rodape-dados, .proxima a, .gancho-link, .slide:not([hidden]) .explora-gancho')) {
    if (!vis(e)) continue; const r = e.getBoundingClientRect(); if (r.bottom <= 0 || r.top >= H) { if (r.top >= H) cobertos.push(nome(e) + ' abaixo da tela (' + Math.round(r.top) + ')'); continue; }
    const h = document.elementFromPoint(r.left + Math.min(8, r.width / 2), Math.min(H - 1, r.top + r.height / 2));
    if (h && !e.contains(h) && !h.contains(e)) cobertos.push(nome(e) + ' coberto por ' + nome(h)); }
  return { cobertos, docW: document.documentElement.scrollWidth, bodyW: document.body.scrollWidth, docH: document.documentElement.scrollHeight, W, H, fora, pequenos: pequenos.length, exPeq: pequenos.slice(0, 3),
    mediana: +mediana.toFixed(1), largConteudo: Math.round(ux1 - ux0), fracConteudo: +((ux1 - ux0) / W).toFixed(2), sob, nav: nav.slice(0, 5) };
})()`;

if (CAPTURAS) mkdirSync(CAPTURAS, { recursive: true });
let falhas = 0; const resumo = [];
for (const [tela, w, h, dpr, cel] of TELAS) {
  await cmd("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: dpr, mobile: cel });
  await cmd("Emulation.setTouchEmulationEnabled", { enabled: cel });
  for (const [pag, caminho, acao] of PAGINAS) {
    erros = [];
    await cmd("Page.navigate", { url: "about:blank" }); await espera(80);
    await cmd("Page.navigate", { url: BASE + caminho });
    for (let i = 0; i < 150 && (await avaliar("document.readyState")) !== "complete"; i++) await espera(40);
    await espera(1800);
    if (acao) { await avaliar(acao); await espera(1200); }
    if (FIM) { await avaliar(`scrollTo(0, 1e7); for (const e of document.querySelectorAll('*')) { const o = getComputedStyle(e).overflowY;
      if (/(auto|scroll)/.test(o) && e.scrollHeight > e.clientHeight + 4) e.scrollTop = 1e7; }`); await espera(700); }
    const r = await avaliar(MEDIR());
    if (!r) { console.log(`ERRO  ${tela} ${pag}: medição falhou`); falhas++; continue; }
    const p = [], av = [];
    if (r.docW > r.W || r.bodyW > r.W) p.push(`rola para o lado (${Math.max(r.docW, r.bodyW)} > ${r.W})`);
    if (r.fora.length) p.push(`sai da tela: ${r.fora.join(", ")}`);
    if (r.cobertos.length) p.push(`fim da rolagem: ${r.cobertos.join(" | ")}`);
    if (r.nav.length) p.push(`navegação: ${r.nav.join(" | ")}`);
    const errosUnicos = [...new Set(erros)].filter((x) => !/favicon/.test(x));
    if (errosUnicos.length) p.push(`console: ${errosUnicos.slice(0, 3).join(" | ")}`);
    if (r.pequenos) av.push(`${r.pequenos} texto(s) < 11 px (${r.exPeq.join("; ")})`);
    if (w >= 2560 && r.fracConteudo < 0.6) av.push(`conteúdo ocupa ${Math.round(r.fracConteudo * 100)}% da largura`);
    if (r.sob.length) av.push(`sobreposição: ${r.sob.join(", ")}`);
    av.push(`texto mediano ${r.mediana}px`);
    falhas += p.length ? 1 : 0;
    resumo.push({ tela, pag, problemas: p, avisos: av, med: r });
    console.log(`${p.length ? "FALHA" : "OK   "} ${tela.padEnd(9)} ${pag.padEnd(12)}${p.length ? " — " + p.join("; ") : ""}  [${av.join("; ")}]`);
    if (CAPTURAS) {
      const cap = await cmd("Page.captureScreenshot", { format: "jpeg", quality: 60 });
      if (cap.result?.data) writeFileSync(join(CAPTURAS, `${tela}_${pag.replace("#", "-")}.jpg`), Buffer.from(cap.result.data, "base64"));
    }
  }
}
if (CAPTURAS) writeFileSync(join(CAPTURAS, "resumo.json"), JSON.stringify(resumo, null, 1));
ws.close(); chrome.kill();
await espera(500);
try { rmSync(perfil, { recursive: true, force: true }); } catch {}
console.log(falhas ? `\n${falhas} combinação(ões) com problema.` : "\nNenhuma rolagem lateral, nada fora da tela, navegação acessível, console limpo.");
process.exit(falhas ? 1 : 0);
