# Resultados de exemplo

Par `data/samples/gt.stl` (GT) × `data/samples/mod.stl` (RM), versão atual dos pipelines, executado em 26/10/2026 (Linux, Python 3.13, NumPy 2.5, Trimesh 5.2, CPU).

- **Preparo:** diagonal da GT = 3,77537 unidades STL; MSE pré-alinhamento sobre amostras = 6,95 × 10⁻⁵ < 10⁻⁴, então o ICP **não** foi acionado.
- **Vista de entrada:** azimute −135° e elevação 25,264°, só como **ilustração**: o par não tem imagem de entrada.
- **Dados das figuras:** [`figures/data/`](figures/data/). Para regenerar: `python scripts/plot_metrics.py --run <saída> --uncertainty`.

## Métricas geométricas

| Região | Parcela da GT | Chamfer (unid. GT) | HD95 (unid. GT) | F@1 % | F@2 % | F@5 % | AUC-F | Normal consistency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Superfície inteira | 100 % | 0,0147 | 0,0805 | 0,907 | 0,952 | 0,998 | 0,980 | 0,945 |
| Visível | 39 % | 0,0226 | 0,1197 | 0,824 | 0,914 | 0,995 | 0,963 | 0,909 |
| Oculta | 61 % | 0,0094 | 0,0270 | 0,963 | 0,978 | 1,000 | 0,992 | 0,968 |

![Métricas por região](figures/geometric_metrics.png)

![Curva F(τ)](figures/fscore_curve.png)

Neste par, o erro se concentra na região visível pela vista ilustrativa: HD95 4,4 vezes maior e F@1 % 0,14 menor que na região oculta. Com τ ≥ 5 %, praticamente todas as amostras estão dentro da tolerância (F > 0,99): as diferenças entre regiões estão abaixo de ~3 % da diagonal.

## Incerteza de amostragem

![Dispersão das métricas por número de amostras](figures/sampling_uncertainty.png)

Cinco pares de sementes por N (média ± desvio padrão):

- **Variação entre sementes:** com N = 10⁵, o coeficiente de variação é 0,5 % (Chamfer), 1,0 % (HD95) e ≤ 0,1 % (F-score, AUC-F, normal consistency).
- **Viés:** o Chamfer (0,0039 → 0,0034 normalizado de 10⁵ para 3 × 10⁵) e a normal consistency (0,945 → 0,951) **ainda não convergiram**. A distância entre amostras inclui o espaçamento da amostragem. HD95 e F@1 % já estão estáveis a partir de ~3 × 10⁴.
- **Consequência:** compare modelos sempre com o mesmo N (padrão: 10⁵). Os valores absolutos de Chamfer contêm um piso que depende de N e da área da malha.

## Métricas perceptuais

100 vistas, 1600 × 1200 px, elevação 25,264°.

| Métrica | Mín. | P25 | Mediana | P75 | Máx. | Média (IC 95 % bootstrap) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PSNR (dB) | 13,72 | 15,57 | 15,90 | 16,24 | 17,44 | 15,73 (15,56–15,88) |
| SSIM | 0,9186 | 0,9279 | 0,9310 | 0,9382 | 0,9445 | 0,9322 (0,9310–0,9334) |

![Métricas perceptuais por vista](figures/perceptual_views.png)

O **LPIPS não foi calculado** nesta execução, porque os pesos da AlexNet não puderam ser baixados no ambiente. O PSNR e o SSIM não dependem dele. O PSNR cai nas vistas em torno de 150°–190°, a mesma faixa em que o SSIM é mínimo.

## Registro anterior

`examples/output/` guarda uma execução da **versão anterior** (métricas entre vértices; PSNR dividido por N, 4,77 dB abaixo do atual). Esses números não são comparáveis com os acima; as renderizações da GT e da RM continuam válidas como ilustração.
