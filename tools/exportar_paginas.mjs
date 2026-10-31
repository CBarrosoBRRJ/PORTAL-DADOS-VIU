// Captura das páginas do portal para o PDF e o PowerPoint enviados com o link (D66, 31/10/2026).
// Somente leitura: abre o servidor num Chrome headless (CDP), sem movimento (estado final das animações), e grava um
// PNG por página na ordem da apresentação. Uso (Node 22+, com o servidor rodando):
//   node tools/exportar_paginas.mjs [http://127.0.0.1:8400] [pasta_saida]
// Depois: python tools/montar_pdf_ppt.py <pasta_saida> <destino> (monta o PDF e o .pptx com as capturas).
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const ARGS = process.argv.slice(2);
const BASE = (ARGS[0] || "http://127.0.0.1:8400").replace(/\/$/, "");
const SAIDA = ARGS[1] || join(tmpdir(), "viu-agenciamento-capturas");
const [W, H, DPR] = [1600, 900, 1.5];
const A = "/viu-agenciamento";
// ordem da apresentação: Capa → Roadmap → Demanda → Talentos → SLA (+ estudo) → LIA → Iniciativas → Previsão → Encerramento
const PAGINAS = [
  ["01_capa", `${A}/capa`], ["02_roadmap", `${A}/roadmap`], ["03_demanda", `${A}`], ["04_talentos", `${A}/talentos`],
  ["05_sla", `${A}/sla`], ["estudo", `${A}/sla/como-medimos`], ["07_lia", `${A}/lia`],
  ["08_iniciativas", `${A}/iniciativas`], ["09_previsao", `${A}/previsao`], ["10_encerramento", `${A}/encerramento`],
];
const espera = (ms) => new Promise((r) => setTimeout(r, ms));
mkdirSync(SAIDA, { recursive: true });

const porta = 9400 + Math.floor(Math.random() * 400);
const chrome = spawn("C:/Program Files/Google/Chrome/Application/chrome.exe", ["--headless=new", "--disable-gpu",
  "--hide-scrollbars", "--force-prefers-reduced-motion", `--remote-debugging-port=${porta}`,
  `--user-data-dir=${mkdtempSync(join(tmpdir(), "exportar-"))}`, "about:blank"]);
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

await cmd("Page.enable");
await cmd("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: DPR, mobile: false });
await cmd("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });

async function abrir(url) {
  await cmd("Page.navigate", { url });
  for (let i = 0; i < 200 && (await avaliar("document.readyState")) !== "complete"; i++) await espera(50);
  await avaliar("document.fonts.ready.then(() => true)");
  await espera(1500);
}

// controles que só fazem sentido na tela (setas, fechar, tela cheia, lupa, nova iniciativa): somem da captura.
// Pelo element.style (a CSP do portal barra <style> injetado)
const SEM_CONTROLES = `document.querySelectorAll('.cab-passos, .tela-cheia-botao, .estudo-lupa, .ini-nova, .sla-lupa,
  [class*="lupa"], .fechar-estudo, .controles-centro').forEach((e) => { e.style.visibility = 'hidden'; }); true`;

async function capturar(nome) {
  await avaliar(SEM_CONTROLES);
  // página mais alta que a janela: captura inteira (o PPT encaixa na lâmina); senão, só a janela
  const altura = await avaliar("Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)");
  const alto = altura > H + 4;
  const r = await cmd("Page.captureScreenshot", { format: "png", captureBeyondViewport: alto,
    clip: { x: 0, y: 0, width: W, height: alto ? altura : H, scale: 1 } });
  writeFileSync(join(SAIDA, `${nome}.png`), Buffer.from(r.result.data, "base64"));
  console.log(`${nome}.png ${alto ? `(página inteira, ${altura}px)` : ""}`);
}

for (const [nome, caminho] of PAGINAS) {
  await abrir(`${BASE}${caminho}`);
  if (nome !== "estudo") { await capturar(nome); continue; }
  const total = (await avaliar("document.querySelectorAll('section.slide-estudo').length")) || 1;
  for (let n = 1; n <= total; n++) {
    await avaliar(`location.hash = '#${n}'`);
    await espera(1200);
    await capturar(`06_estudo_${n}`);
  }
}
ws.close(); chrome.kill();
console.log(`Capturas em ${SAIDA}`);
