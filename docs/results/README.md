# Resultados de exemplo — registro histórico

> As seções "Resumo da execução", "Métricas geométricas" e "Métricas perceptuais" e os arquivos em `examples/output/` foram gerados pela **versão anterior** dos pipelines (métricas geométricas entre vértices; PSNR com divisão por N). Eles **não** são comparáveis com as saídas atuais. Os valores da versão atual para o mesmo par estão em [Métricas da versão atual](#user-content-métricas-da-versão-atual-do-mesmo-par).

## Resumo da execução

- O pipeline geométrico e o pipeline perceptual foram executados com os arquivos de exemplo.
- O MSE simétrico antes do alinhamento foi **0,0000730103** em coordenadas normalizadas, abaixo do limiar configurado de **0,0001**. O alinhamento foi, portanto, ignorado.
- A diagonal da caixa delimitadora da GT foi **3,77537 unidades STL**. Como os arquivos STL não registram unidade física, os valores em unidades originais devem ser interpretados na unidade usada ao criar as malhas.
- O pipeline perceptual avaliou **100 vistas** e salvou imagens de comparação das vistas **1, 33 e 66**.

## Métricas geométricas

| Métrica | Resultado normalizado | Resultado nas unidades originais da GT |
| --- | ---: | ---: |
| MSE simétrico antes do alinhamento | 0,0000730103 | 0,00104065 unidade² |
| MSE simétrico após o alinhamento | 0,0000730103 | 0,00104065 unidade² |
| Chamfer médio | 0,00187183 | 0,00706686 unidade |
| Hausdorff simétrico | 0,0815869 | 0,308021 unidade |
| RMSE simétrico | 0,00854461 | 0,0322591 unidade |

## Métricas perceptuais

Resumo das 100 vistas calculadas:

| Métrica | Mínimo | Mediana | Média | Máximo |
| --- | ---: | ---: | ---: | ---: |
| LPIPS | 0,0995203 | 0,112826 | 0,114771 | 0,138245 |
| PSNR (dB) | 8,94537 | 11,1308 | 10,9587 | 12,6710 |
| SSIM | 0,918553 | 0,930943 | 0,932160 | 0,944466 |

Os valores perceptuais descrevem as renderizações geradas pelo pipeline e dependem da câmera, do enquadramento e das configurações registradas nos arquivos de métricas. Devem ser comparados usando as mesmas configurações.

## Visualizações geradas

As imagens estão organizadas em duas colunas para facilitar a comparação e reduzir o espaço vertical ocupado no relatório.

<table>
  <tr>
    <td width="50%" align="center">
      <strong>Render ortográfico da referência (GT)</strong><br>
      <img src="../../examples/output/renders/gt_ortho.png" width="100%" alt="Render ortográfico da GT">
    </td>
    <td width="50%" align="center">
      <strong>Render ortográfico da malha avaliada (RM)</strong><br>
      <img src="../../examples/output/renders/rm_aligned_ortho.png" width="100%" alt="Render ortográfico da RM">
    </td>
  </tr>
  <tr>
    <td colspan="2" align="center">
      <strong>Heatmap geométrico</strong><br>
      <img src="../../examples/output/heatmaps/gt_heatmap_ortho.png" width="50%" alt="Heatmap geométrico">
    </td>
  </tr>
</table>

### Renders multivista da GT e da RM

As renderizações da mesma vista aparecem lado a lado para comparar a GT e a RM.

<table>
  <tr>
    <td width="50%" align="center">
      <strong>Vista 1 — GT</strong><br>
      <img src="../../examples/output/renders/gt/gt_view001.png" width="100%" alt="Render da GT na vista 1">
    </td>
    <td width="50%" align="center">
      <strong>Vista 1 — RM</strong><br>
      <img src="../../examples/output/renders/rm/rm_view001.png" width="100%" alt="Render da RM na vista 1">
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <strong>Vista 33 — GT</strong><br>
      <img src="../../examples/output/renders/gt/gt_view033.png" width="100%" alt="Render da GT na vista 33">
    </td>
    <td width="50%" align="center">
      <strong>Vista 33 — RM</strong><br>
      <img src="../../examples/output/renders/rm/rm_view033.png" width="100%" alt="Render da RM na vista 33">
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <strong>Vista 66 — GT</strong><br>
      <img src="../../examples/output/renders/gt/gt_view066.png" width="100%" alt="Render da GT na vista 66">
    </td>
    <td width="50%" align="center">
      <strong>Vista 66 — RM</strong><br>
      <img src="../../examples/output/renders/rm/rm_view066.png" width="100%" alt="Render da RM na vista 66">
    </td>
  </tr>
</table>

### Comparações perceptuais

Cada imagem já mostra GT e RM lado a lado.

<p align="center">
  <strong>Vista 1</strong><br>
  <img src="../../examples/output/renders/pairs/pair_view001.png" width="100%" alt="Comparação perceptual da vista 1">
</p>

<p align="center">
  <strong>Vista 33</strong><br>
  <img src="../../examples/output/renders/pairs/pair_view033.png" width="100%" alt="Comparação perceptual da vista 33">
</p>

<p align="center">
  <strong>Vista 66</strong><br>
  <img src="../../examples/output/renders/pairs/pair_view066.png" width="100%" alt="Comparação perceptual da vista 66">
</p>

## Métricas da versão atual do mesmo par

Os valores abaixo vêm do pipeline geométrico atual ([ADR 0003](../adr/0003-single-metric-standard.md)) com o mesmo par (`gt.stl` × `mod.stl`), executado em 26/10/2026 em Linux (Python 3.13, NumPy 2.5, Trimesh 5.2). Parâmetros: 100 000 amostras por malha, sementes `0`/`1`. O MSE pré-alinhamento sobre as amostras foi 6,95 × 10⁻⁵, abaixo do limiar de 10⁻⁴, então o ICP não foi acionado.

| Métrica (superfície inteira) | Normalizado | Unidades da GT |
| --- | ---: | ---: |
| Chamfer | 0,0038869 | 0,0146744 |
| HD95 | 0,0213188 | 0,0804864 |
| F-score @1 % / @2 % / @5 % | 0,9073 / 0,9521 / 0,9980 | — |
| AUC-F (τ de 0,5 % a 10 %) | 0,9804 | — |
| Normal consistency | 0,9445 | — |

**Leitura:** o Chamfer atual (0,0039) é cerca de duas vezes o da versão anterior (0,0019). Na métrica por vértice, os vértices que coincidem nas duas malhas contribuem com distância zero; isso depende da triangulação, não da superfície (ver o [estudo de robustez](robustness/README.md)).

**Regiões, só como ilustração:** este par não tem imagem de entrada. Com uma vista hipotética em azimute −135° e elevação 25,264°, 39,1 % da superfície da GT fica visível (Chamfer 0,0060; F@1 % 0,824) e 60,9 % fica oculta (Chamfer 0,0025; F@1 % 0,963). Neste par, o erro se concentra no lado visível dessa vista.

## Arquivos de saída

- [`metrics_geometry.csv`](../../examples/output/metrics/metrics_geometry.csv): métricas geométricas agregadas.
- [`metrics_perceptual.csv`](../../examples/output/metrics/metrics_perceptual.csv): resumo estatístico das métricas por vista.
- [`per_view_metrics.csv`](../../examples/output/metrics/per_view_metrics.csv): valores de LPIPS, PSNR e SSIM para cada uma das 100 vistas.
- [`run_metadata.csv`](../../examples/output/metrics/run_metadata.csv): parâmetros e caminhos usados na execução perceptual.
- [`aligned/rm_aligned.ply`](../../examples/output/aligned/rm_aligned.ply): malha avaliada exportada pelo pipeline geométrico.
- [`heatmaps/gt_heatmap_colored.ply`](../../examples/output/heatmaps/gt_heatmap_colored.ply): malha com cores do heatmap.

Os CSVs de execução registram caminhos locais das malhas; eles podem variar em outra máquina. [`environment.yml`](../../environments/environment.yml) lista as dependências gerais, enquanto [`environment-lock.yml`](../../environments/environment-lock.yml) fixa as versões exportadas do ambiente Windows `meshEval`. Esse ambiente usa PyTorch CPU-only, sem CUDA; portanto, a aceleração CUDA não foi testada. O pipeline perceptual executou em CPU. A execução de exemplo não é uma validação end-to-end desses cenários. Há testes unitários de pontos idênticos, deslocamento e transformações, mas a análise sistemática de malhas deslocadas, redimensionadas, com buracos ou densidades diferentes continua pendente no [plano de validação](../implementation/README.md). As instruções de instalação estão na seção [Installation](../../README.md#user-content-installation) do README principal.
