# Resultados de exemplo

Par `data/samples/gt.stl` (GT) × `data/samples/mod.stl` (RM), versão atual dos pipelines, executado em 26/10/2026 (Linux, Python 3.13, NumPy 2.5, Trimesh 5.2, CPU).

- **Preparo:** diagonal da GT = 3,77537 unidades STL; MSE pré-alinhamento (ponto-superfície) = 6,66 × 10⁻⁵ < 10⁻⁴, então o ICP **não** foi acionado.
- **Vista de entrada:** azimute −135° e elevação 25,264°, só como **ilustração**: o par não tem imagem de entrada.
- **Dados das figuras:** [`figures/data/`](figures/data/). Para regenerar: `python scripts/plot_metrics.py --run <saída> --uncertainty`.

## Métricas geométricas

| Região | Parcela da GT | Chamfer (unid. GT) | HD95 (unid. GT) | F@1 % | F@2 % | F@5 % | AUC-F | Normal consistency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Superfície inteira | 100 % | 0,0100 | 0,0800 | 0,908 | 0,952 | 0,998 | 0,981 | 0,960 |
| Visível | 39 % | 0,0187 | 0,1195 | 0,826 | 0,914 | 0,995 | 0,963 | 0,928 |
| Oculta | 61 % | 0,0042 | 0,0261 | 0,963 | 0,978 | 1,000 | 0,992 | 0,980 |

![Métricas por região](figures/geometric_metrics.png)

![Curva F(τ)](figures/fscore_curve.png)

Neste par, o erro se concentra na região visível pela vista ilustrativa: Chamfer 4,4 vezes e HD95 4,6 vezes maiores, e F@1 % 0,14 menor que na região oculta. Com τ ≥ 5 %, praticamente todas as amostras estão dentro da tolerância (F > 0,99): as diferenças entre regiões estão abaixo de ~3 % da diagonal.

## Incerteza de amostragem

![Dispersão das métricas por número de amostras](figures/sampling_uncertainty.png)

Cinco pares de sementes por N (média ± desvio padrão):

- **Sem viés:** com a distância ponto-superfície ([ADR 0004](../adr/0004-point-to-surface.md)), as médias de Chamfer (0,0026 normalizado), F@1 % (0,908) e normal consistency (0,960) são constantes de 10³ a 3 × 10⁵ amostras. Só o HD95, que é um percentil, ainda se desloca abaixo de ~10⁴ amostras.
- **Variação entre sementes:** cai com N; com N = 10⁵, o coeficiente de variação é de 0,8 % (Chamfer), 1,0 % (HD95) e ≤ 0,1 % (F-score, AUC-F, normal consistency).

## Métricas perceptuais

100 vistas, 1600 × 1200 px, elevação 25,264°.

| Métrica | Mín. | P25 | Mediana | P75 | Máx. | Média (IC 95 % bootstrap) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PSNR (dB) | 13,72 | 15,57 | 15,90 | 16,24 | 17,44 | 15,73 (15,56–15,88) |
| SSIM | 0,9186 | 0,9279 | 0,9310 | 0,9382 | 0,9445 | 0,9322 (0,9310–0,9334) |

![Métricas perceptuais por vista](figures/perceptual_views.png)

O **LPIPS não foi calculado** nesta execução, porque os pesos da AlexNet não puderam ser baixados no ambiente. O PSNR e o SSIM não dependem dele. O PSNR cai nas vistas em torno de 150°–190°, a mesma faixa em que o SSIM é mínimo.

## Alinhamento

O ICP não foi acionado neste par. A recuperação de transformações conhecidas e o raio de convergência estão na [validação do ICP](icp/README.md).

## Registro anterior

`examples/output/` guarda uma execução da **versão anterior** (métricas entre vértices; PSNR dividido por N, 4,77 dB abaixo do atual). Esses números não são comparáveis com os acima; as renderizações da GT e da RM continuam válidas como ilustração.
