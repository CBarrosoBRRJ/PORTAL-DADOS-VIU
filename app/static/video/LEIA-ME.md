# Vídeo "A LIA na prática"

Pasta dos arquivos do vídeo que abre no botão "Ver a LIA na prática" da página LIA (e na página antiga
`/viu-agenciamento/lia-na-pratica`, que continua abrindo pelo endereço).

1. Salve o vídeo aqui com o nome **`lia-na-pratica.mp4`** (MP4, H.264; 16:9).
2. Opcional: a capa (imagem de abertura) como `lia-na-pratica.jpg` e a legenda em português como `lia-na-pratica.vtt`.
3. Preencha as constantes em `app/apresentacoes/gestao_orcamentos/lia_na_pratica/__init__.py`:
   `ARQUIVO = "lia-na-pratica.mp4"` e, se houver, `CAPA = "lia-na-pratica.jpg"` e `LEGENDAS = "lia-na-pratica.vtt"`.
4. Rode os testes (`python -m pytest tests -q`) e confira o pop-up na página LIA.

Enquanto `ARQUIVO` estiver vazio, o pop-up mostra o espaço reservado "Vídeo a incluir".
