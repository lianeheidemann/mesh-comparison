# 04 — Alinhamento por ICP de similaridade

![Antes e depois do ICP](images/icp.svg)

## Quando é acionado?
`run_pipeline` calcula `pre_mse_norm = symmetric_mse(gt.vertices, rm.vertices)`. Se `pre_mse_norm > 1e-4` por padrão, chama `similarity_icp_align(rm.vertices, gt.vertices)`; caso contrário, preserva a transformação identidade.

O valor **1e-4 é MSE de distância normalizada ao quadrado**. Não é um limiar de distância linear.

## O que o ICP faz?
1. Amostra até 50.000 vértices de cada conjunto (`maybe_subsample`; sementes fixas 1 e 2).
2. Estima uma transformação inicial pela razão das diagonais das caixas e pela diferença dos centros médios dos vértices (`initial_similarity_from_bboxes`).
3. Executa registro ICP ponto-a-ponto com correspondências por proximidade.
4. Itera uma etapa grossa com distância máxima 0,25 e outra refinada com 0,05, até 100 iterações em cada.
5. Aplica a transformação da RM para o sistema de coordenadas da GT.

A transformação homogênea é

\[
\begin{bmatrix}p'\\1\end{bmatrix} =
\begin{bmatrix}sR&t\\0&1\end{bmatrix}
\begin{bmatrix}p\\1\end{bmatrix},
\]

onde `R` é uma rotação, `t` uma translação e `s` uma escala uniforme. `Open3D.TransformationEstimationPointToPoint(with_scaling=True)` habilita a escala.

## Interpretação
- **Fitness do ICP:** fração de correspondências consideradas dentro do limite pelo algoritmo; não é uma nota geral de qualidade.
- **inlier RMSE:** erro residual das correspondências aceitas pelo ICP; não confundir com o `symmetric_rmse` calculado em todos os vértices após registro.
- Uma correspondência ruim, oclusão, simetria ou mudança topológica pode gerar mínimos locais.

## Recomendação de validação
Comparar **MSE antes e depois**, verificar a matriz de transformação e inspecionar visualmente as malhas; o script atual não desfaz automaticamente um ICP cujo MSE pós-alinhamento ficou pior.
