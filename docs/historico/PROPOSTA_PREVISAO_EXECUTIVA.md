# Proposta para a apresentação da Previsão

Proposta de 26/10/2026, para a única tela cuja forma de apresentação Caio autorizou reavaliar. **Não aplicada ao layout.** Os ajustes de movimento são uma entrega independente e preservam as páginas atuais.

## Problema de leitura

A tela atual sobrepõe três perguntas no mesmo gráfico: quanto entrou no ano, quanto o modelo acertou no teste e quanto pode entrar adiante. A comparação de modelos exige abrir um diálogo. Os seis cartões repetem previsões que reaparecem nos gráficos, enquanto “realizado até hoje” e “previsão do mês completo” têm coberturas diferentes.

Há ainda uma questão de dados, separada do desenho: a faixa do Inbound pode ficar acima do ponto previsto. Isso não se resolve reposicionando o ponto no gráfico. É necessário revisar a calibração, conforme a auditoria técnica. A nova apresentação deve tornar essa limitação visível, sem sugerir precisão inexistente.

## Composição recomendada: uma página, três leituras

Preservar marca, cores, tipografia e cabeçalho. Usar duas colunas alinhadas: Inbound e Mercado. As mesmas três leituras aparecem em ambas, na mesma ordem. Sem adicionar botões, carrossel, abas internas ou outra página para apresentar a análise. Esta proposta se refere aos controles da análise; a navegação global continua cumprindo sua função.

| Posição | Visual proposto | Como ler |
|---|---|---|
| Topo | Mês atual: barra horizontal do realizado até o corte; ao lado, ponto de fechamento previsto e intervalo | “Já chegaram X; a previsão do mês inteiro é Y.” A parcial não deve parecer o fechamento definitivo |
| Centro | Próximos dois meses: uma linha por mês, com ponto previsto e segmento da faixa na mesma escala | Substitui a repetição de cartões e facilita comparar novembro/dezembro, sem misturar o teste histórico |
| Base | Acerto: quatro pares de pontos previsto × real, por mês de teste, e resumo curto do erro | Mostra onde o modelo acertou/errou, além do percentual agregado; comparação anterior e fragilidade permanecem claras |

O histórico anual pode entrar como uma faixa de barras compacta, junto da leitura de contexto, com meses fechados e parcial claramente distintos. Ele não precisa disputar a maior área com a previsão. Se não houver altura suficiente, priorizar as três leituras acima; não reduzir textos a ponto de prejudicar a leitura na diretoria. No celular, os mesmos blocos seguem em coluna com rolagem vertical natural.

### Comparação de modelos à vista

Trocar a dependência do botão “Modelos comparados” por uma comparação compacta na própria página: modelo escolhido, referência simples e alternativa robusta, quando houver. Um gráfico de pontos com erro no teste e na verificação evita despejar 61 linhas técnicas na lâmina gerencial. Candidatos sem verificação não recebem zero nem entram como equivalentes aos que têm janela completa.

Se for necessário expor todas as famílias, usar uma tabela por série/família no fluxo vertical da mesma página, com cabeçalho explícito do período, número de meses e unidade. Manter o detalhamento completo também nos documentos de auditoria. Não anunciar que é possível apresentar todos os 61 candidatos legivelmente em uma única tela sem rolagem.

O seletor atual de exclusividade exigirá decisão de produto na implementação: manter os recortes atuais ou distribuir Todos/Exclusivos/Não exclusivos em pequenos múltiplos. Minha preferência é que a visão inicial mostre Inbound e Mercado com clareza e que os recortes venham em gráficos menores no fluxo da mesma página, se sua consulta frequente justificar a área. Isso elimina novos botões, mas exige altura e evita repetir o mesmo Inbound como se fossem séries diferentes.

## Mensagem e regras de informação

- Separar “até a data de corte” de “fechamento previsto”. Não comparar mês parcial com mês completo sem expor a diferença.
- Dizer que o erro foi medido em determinado período; “erro médio” sozinho pode parecer uma garantia futura.
- Preservar o aviso de fragilidade do Mercado e a ausência de verificação dos recortes curtos.
- A faixa representa a incerteza de cada mês. Para totalizar o restante do ano, não somar limites mensais e chamar o resultado de faixa de 80%: a dependência entre meses precisa ser considerada.
- Um eventual fechamento anual deve somar meses efetivamente fechados com as previsões dos meses ainda abertos, incluindo o vigente uma única vez. Não somar o realizado parcial do vigente ao fechamento previsto do mesmo mês.
- Não produzir dados novos apenas para completar o desenho; sem intervalo ou modelo válido, mostrar a limitação.

## Movimento proposto

Histórico aparece num fade curto; a previsão se revela logo depois, com os valores prontos. Nada de contagem de pedidos futuros, linha que pulsa ou animação contínua. Reabrir/filtar não reinicia uma apresentação longa. Quem pede movimento reduzido vê tudo pronto. Os ajustes compatíveis com o desenho atual foram aplicados apenas ao movimento; os novos gráficos acima continuam sendo uma proposta.

## Critérios para implementar posteriormente

1. Aprovar a distribuição e o tratamento dos recortes, sem mudar o protocolo de ML como parte da alteração visual.
2. Reaproveitar o contrato atual; caso falte um total anual ou intervalo conjunto, definir e testar o cálculo separadamente.
3. Comparar valores, séries, recortes e tabelas acessíveis antes/depois na mesma carga.
4. Conferir leitura no projetor, desktop e celular, foco de teclado, contraste e movimento reduzido.

Referências locais: [auditoria técnica](AUDITORIA_TECNICA_2026-10-26.md), [ficha atual da Previsão](../paginas/previsao.md) e [ganhos e lacunas da Gold](PLANO_GOLD_POR_VISUAL.md#6-qual-é-o-ganho-de-cada-tabela).
