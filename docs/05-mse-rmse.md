# 05 — MSE e RMSE simétricos entre vértices

![Distâncias entre vértices](images/distancias.svg)

## Etapa 1: distância direcionada
Para um vértice `a` da GT, o algoritmo encontra o vértice mais próximo da RM:

\[
d(a,B)=\min_{b\in B}\lVert a-b\rVert_2
\]

O mesmo é calculado de RM para GT. `nn_distances` implementa essa operação usando `scipy.spatial.cKDTree`.

## MSE simétrico
Com `A` = vértices GT e `B` = vértices RM:

\[
MSE_{sym}(A,B)=\frac12\left(\frac1{|A|}\sum_{a\in A}d(a,B)^2+\frac1{|B|}\sum_{b\in B}d(b,A)^2\right)
\]

É implementado em `symmetric_mse`; valores menores indicam correspondência geométrica mais próxima. A unidade é **comprimento²**. O código registra MSE antes/depois do ICP em unidades normalizadas e em unidades originais quadráticas.

## RMSE simétrico
\[
RMSE_{sym}=\sqrt{MSE_{sym}}
\]

Implementado em `compute_metrics` e salvo como `symmetric_rmse_normalized` e `symmetric_rmse_gt_units`. A unidade é **comprimento**.

### Exemplo didático
Se todas as distâncias direcionadas fossem `0,1` na escala normalizada, então `MSE = 0,01` e `RMSE = 0,1`. Um único vértice com erro muito alto aumenta bastante o MSE por causa do quadrado.

## Como implementar e testar
1. Validar vértices não vazios e coordenadas finitas.
2. Construir uma `cKDTree` para a nuvem de destino e buscar `k=1`.
3. Repetir no sentido inverso; calcular as médias separadas e depois a média das duas.
4. Criar testes com conjuntos idênticos (zero), translados conhecidos e outliers.
5. Não confundir MSE geométrico (distância 3D) com MSE de imagens (pixel RGB), usado no PSNR.

**Limitação:** amostragem de vértices não é uniforme sobre a área da malha; triangulações diferentes podem alterar a pontuação sem alterar muito a superfície física.
