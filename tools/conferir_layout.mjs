// Conferência automática do layout do estudo "Como medimos" (batalha de agentes, 25/10/2026: A-N12 e B-N11).
// Somente leitura: abre o servidor LOCAL num Chrome headless (CDP, emulação de dispositivo) e mede cada slide; não
// altera nada. Uso (Node 22+, com o servidor já rodando):
//   node tools/conferir_layout.mjs [http://127.0.0.1:8096]
// Percorre todos os slides (#1 a #N, contados na página) × 3 grupos × 4 tamanhos (1920×1000, 1440×900, 1280×800 e 390×844 como celular) e falha (saída 1) se:
//   - a página rola para o lado (scrollWidth > largura da janela), em qualquer tamanho;
//   - nos três tamanhos de mesa, algum elemento do slide passa do pé da lâmina (o slide teria de rolar);
//   - algum texto de gráfico (SVG) visível tem menos de 11 px reais, medido pela escala na tela (R09).
// Texto HTML abaixo de 11 px (rótulos discretos do desenho, como "TALENTOS" e o sobretítulo) sai como AVISO, sem falhar:
// é escolha de desenho do Caio, a revisar com ele; a contagem serve para não piorar.
// A tabela do slide 5 (.mes-rolagem) rola de propósito no celular e fica fora da regra lateral.
// Movimento (batalha 2, 26/10/2026; D46 no portal): depois do layout, abre Início, Talentos, Atendimento, SLA e Previsão
// com movimento PERMITIDO (prefers-reduced-motion: no-preference, emulado) e falha se: o número grande aos ~250 ms não
// for o mesmo de 1,5 s (contagem a partir de zero); ainda houver animação/transição rodando a 1,3 s do carregamento;
// alguma animação for infinita. `node tools/conferir_layout.mjs <url> --movimento` roda só esta parte.
// Atenção: --window-size abaixo de ~500 px não serve para conferir o celular (o Chrome prende a janela); por isso a
// emulação (Emulation.setDeviceMetricsOverride).
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const ARGS = process.argv.slice(2);
const SO_MOVIMENTO = ARGS.includes("--movimento");
const BASE = (ARGS.find((a) => !a.startsWith("--")) || "http://127.0.0.1:8096").replace(/\/$/, "");
const CAMINHO = "/viu-agenciamento/sla/como-medimos";
const TAMANHOS = [[1920, 1000, false], [1440, 900, false], [1280, 800, false], [390, 844, true]];
const GRUPOS = ["todos", "exclusivos", "nao-exclusivos"];
const MIN_PX = 11;
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

const porta = 9400 + Math.floor(Math.random() * 400);
const perfil = mkdtempSync(join(tmpdir(), "conferir-layout-"));
const chrome = spawn("C:/Program Files/Google/Chrome/Application/chrome.exe", ["--headless=new", "--disable-gpu",
  "--hide-scrollbars", "--force-prefers-reduced-motion", `--remote-debugging-port=${porta}`, `--user-data-dir=${perfil}`,
  "about:blank"]);
let alvo;
for (let i = 0; i < 60 && !alvo; i++) {
  await espera(250);
  try { alvo = (await (await fetch(`http://127.0.0.1:${porta}/json`)).json()).find((t) => t.type === "page"); } catch {}
}
if (!alvo) { console.error("Chrome não abriu"); chrome.kill(); process.exit(2); }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pend = {};
ws.addEventListener("message", (e) => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) { pend[m.id](m); delete pend[m.id]; } });
const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
const avaliar = async (expr) => (await cmd("Runtime.evaluate", { expression: expr, returnByValue: true })).result.result.value;

// mede o slide visível: rolagem lateral, conteúdo abaixo da lâmina e textos pequenos
const MEDIR = (mesa) => `(() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); if (!r.width || !r.height) return false;
    for (let x = e; x; x = x.parentElement) { if (x.hidden || x.classList?.contains('so-leitor')) return false;
      const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false; }
    return true; };
  const s = [...document.querySelectorAll('section.slide-estudo')].find((x) => { const r = x.getBoundingClientRect(); return r.width && r.left > -5 && r.left < innerWidth / 2 && !x.hidden; }) || document.body;
  const lam = s.querySelector('.lamina') || s; const lr = lam.getBoundingClientRect();
  const todos = [...lam.querySelectorAll('*')].filter(vis);
  const nome = (e) => e.tagName.toLowerCase() + '.' + String(e.className?.baseVal ?? e.className).split(' ')[0];
  const fora = (e) => !!e.closest('.mes-rolagem');
  const lado = todos.filter((e) => !fora(e) && e.getBoundingClientRect().right > innerWidth + 1).slice(0, 3)
    .map((e) => nome(e) + ':' + Math.round(e.getBoundingClientRect().right));
  const pe = ${mesa} ? todos.filter((e) => e.getBoundingClientRect().bottom > lr.bottom + 1).slice(0, 3)
    .map((e) => nome(e) + ':' + Math.round(e.getBoundingClientRect().bottom) + '>' + Math.round(lr.bottom)) : [];
  const pequenos = [], pequenosHtml = [];
  for (const e of todos) {
    const txt = [...e.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(' ').trim();
    if (!txt) continue;
    let px = parseFloat(getComputedStyle(e).fontSize);
    const svg = e instanceof SVGElement;
    if (svg && e.getScreenCTM) { const m = e.getScreenCTM(); if (m) px *= Math.hypot(m.a, m.b); }
    if (px < ${MIN_PX} - 0.05) (svg ? pequenos : pequenosHtml).push(nome(e) + '(' + px.toFixed(1) + 'px): ' + txt.slice(0, 24));
  }
  return { docW: document.documentElement.scrollWidth, vw: innerWidth, lado, pe, pequenos: pequenos.slice(0, 5), npequenos: pequenos.length, nhtml: pequenosHtml.length };
})()`;

let falhas = 0;
for (const [w, h, celular] of (SO_MOVIMENTO ? [] : TAMANHOS)) {
  await cmd("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: celular });
  for (const g of GRUPOS) {
    await cmd("Page.enable");
    await cmd("Page.navigate", { url: `${BASE}${CAMINHO}?talentos=${g}#1` });
    await espera(4000);
    const total = (await avaliar("document.querySelectorAll('section.slide-estudo').length")) || 1;  // V2 (30/10/2026): 5 slides, contados na página
    for (let n = 1; n <= total; n++) {
      await avaliar(`location.hash = '#${n}'`);
      await espera(900);
      const r = await avaliar(MEDIR(!celular));
      const problemas = [];
      if (r.docW > r.vw) problemas.push(`rola para o lado (${r.docW} > ${r.vw})`);
      if (r.lado.length) problemas.push(`passa da direita: ${r.lado.join(", ")}`);
      if (r.pe.length) problemas.push(`passa do pé da lâmina: ${r.pe.join(", ")}`);
      if (r.npequenos) problemas.push(`${r.npequenos} texto(s) de gráfico < ${MIN_PX} px: ${r.pequenos.join(" | ")}`);
      falhas += problemas.length ? 1 : 0;
      const aviso = r.nhtml ? ` (aviso: ${r.nhtml} rótulo(s) HTML < ${MIN_PX} px)` : "";
      console.log(`${problemas.length ? "FALHA" : "OK   "} ${w}x${h} ${g.padEnd(14)} #${n}${problemas.length ? " — " + problemas.join("; ") : ""}${aviso}`);
    }
  }
}
// ---------- movimento das páginas (D46 no portal) ----------
const PAGINAS = ["/viu-agenciamento", "/viu-agenciamento/talentos", "/viu-agenciamento/atendimento",
  "/viu-agenciamento/sla", "/viu-agenciamento/sla?talentos=exclusivos", "/viu-agenciamento/previsao"];
const NUMEROS = `[...document.querySelectorAll('.resposta-numero, .hero-numero, .kpi-num, .pv-num-valor')].map((e) => e.textContent.trim()).join(' | ')`;
await cmd("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await cmd("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "no-preference" }] });
let falhasMov = 0;
for (const pg of PAGINAS) {
  await cmd("Page.navigate", { url: `${BASE}${pg}` });
  for (let i = 0; i < 100 && (await avaliar("document.readyState")) !== "complete"; i++) await espera(30);
  const t0 = await avaliar("performance.now()");
  const reduzido = await avaliar("matchMedia('(prefers-reduced-motion: reduce)').matches");
  await espera(250);
  const cedo = await avaliar(NUMEROS);
  await espera(1050);
  const rodando = await avaliar(`document.getAnimations().filter((a) => a.playState === 'running').map((a) =>
    (a.animationName || a.transitionProperty || 'anim') + '@' + ((a.effect && a.effect.target && a.effect.target.className && String(a.effect.target.className.baseVal ?? a.effect.target.className).split(' ')[0]) || '?'))`);
  const infinitas = await avaliar(`document.getAnimations().filter((a) => a.effect && a.effect.getTiming().iterations === Infinity).length`);
  await espera(300);
  const tarde = await avaliar(NUMEROS);
  const t1 = await avaliar("performance.now()");
  const problemas = [];
  if (reduzido) problemas.push("movimento reduzido ainda ligado (a emulação não pegou)");
  if (cedo !== tarde) problemas.push(`número muda depois do 1º quadro: "${cedo}" → "${tarde}"`);
  if (rodando.length) problemas.push(`${rodando.length} animação(ões) ainda rodando a ~${Math.round(t1 - t0 - 300)} ms: ${rodando.slice(0, 4).join(", ")}`);
  if (infinitas) problemas.push(`${infinitas} animação(ões) infinita(s)`);
  falhasMov += problemas.length ? 1 : 0;
  console.log(`${problemas.length ? "FALHA" : "OK   "} movimento ${pg}${problemas.length ? " — " + problemas.join("; ") : ""}`);
}
falhas += falhasMov;

ws.close(); chrome.kill();
await espera(500);
try { rmSync(perfil, { recursive: true, force: true }); } catch {}
console.log(falhas ? `\n${falhas} combinação(ões) com problema.` : "\nTudo cabe: nenhuma rolagem, nada abaixo da lâmina, nenhum texto de gráfico abaixo de 11 px; movimento dentro da D46.");
process.exit(falhas ? 1 : 0);
