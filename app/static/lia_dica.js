// LIA (Caio, 30/10/2026): a dica de cada semana abre ao lado da coluna (mouse ou foco, só CSS); Esc a fecha até o mouse
// sair da coluna ou o foco mudar. O Esc do pop-up do vídeo é dele.
(function () {
  "use strict";
  var semanas = Array.prototype.slice.call(document.querySelectorAll(".lia-sem"));
  if (!semanas.length) return;
  function reabre(ev) { ev.currentTarget.classList.remove("lia-dica-fechada"); }
  semanas.forEach(function (s) { s.addEventListener("blur", reabre); s.addEventListener("mouseleave", reabre); });
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    var dlg = document.getElementById("lia-video");
    if (dlg && dlg.open) return;
    semanas.forEach(function (s) {
      if (s === document.activeElement || s.matches(":hover")) s.classList.add("lia-dica-fechada");
    });
  });
})();
