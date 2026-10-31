// Roda no <head>: marca que há JavaScript (os slides viram um por vez; sem JS, ficam um embaixo do outro)
// e aplica o estado do menu lateral antes da primeira pintura (sem piscar).
document.documentElement.classList.add("js");
(function () {
  var escolha = null;
  try { escolha = localStorage.getItem("menu"); } catch (e) { /* sem armazenamento: segue o padrão */ }
  // sem escolha da pessoa: em telas até 1400 px o menu começa recolhido (mais largura para o slide)
  var recolher = escolha ? escolha === "recolhido" : (window.innerWidth < 1400 && window.innerWidth >= 900);
  if (recolher) document.documentElement.classList.add("menu-recolhido");
  // D59: página aberta dentro do quadro de tela cheia (apresentacao.js) já pinta no modo tela cheia
  try {
    if (window.frameElement && window.frameElement.hasAttribute("data-quadro-tela-cheia")) document.documentElement.classList.add("tela-cheia");
  } catch (e) { /* quadro de outra origem: não acontece */ }
})();
