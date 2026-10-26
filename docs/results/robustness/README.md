# Estudo de robustez das métricas

O estudo verifica se as métricas obedecem a três *priors* geométricos (Bronstein, Bruna, Cohen e Veličković, *Geometric Deep Learning*, arXiv:2104.13478, 2021):

- **Invariância:** a métrica não muda com a discretização da superfície.
- **Estabilidade:** distorções pequenas produzem mudanças pequenas e monotônicas.
- **Multiescala:** a curva F(τ) mostra em que escala está o erro.

As métricas de superfície são comparadas com um **baseline por vértice** (Chamfer e Hausdorff entre vértices). O estudo foi pensado como a seção de validação de métricas do artigo.

**Execução:** `python scripts/robustness_study.py --gt data/samples/gt.stl --out <pasta> --views 8`. Parâmetros em [study_parameters.csv](study_parameters.csv): GT normalizada pela diagonal, 100 000 amostras, sementes `0`/`1`, **sem ICP**, 8 vistas de 320 × 240 px.

**Limitações:** uma única GT (a peça de exemplo) e sem LPIPS (pesos indisponíveis no ambiente). Repita com as GTs do benchmark e `--lpips` antes de publicar os números.

## Invariância à triangulação

[invariance.csv](invariance.csv). A RM é a **mesma superfície** da GT, com outra discretização. Valores normalizados pela diagonal.

| Variante | Vértices | Chamfer por vértice | Hausdorff por vértice | Chamfer | HD95 | F@1 % | AUC-F | Normal consistency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cópia idêntica | 2 904 | 0 | 0 | 0,0015 | 0,0029 | 1,000 | 1,000 | 0,983 |
| Vértices permutados | 2 904 | 0 | 0 | 0,0015 | 0,0029 | 1,000 | 1,000 | 0,983 |
| Subdividida ×1 | 5 808 | 0,0048 | 0,0888 | 0,0015 | 0,0029 | 1,000 | 1,000 | 0,983 |
| Subdividida ×2 | 14 520 | 0,0058 | 0,0888 | 0,0015 | 0,0029 | 1,000 | 1,000 | 0,983 |
| Metade subdividida ×2 | 8 712 | 0,0048 | 0,0888 | 0,0015 | 0,0029 | 1,000 | 1,000 | 0,984 |

- **Baseline por vértice:** não é invariante. Para a mesma superfície, o Hausdorff vai de 0 a 8,9 % da diagonal.
- **Métricas de superfície:** não mudam.
- **Pisos:** o valor não nulo da cópia idêntica é o piso de amostragem, e a normal consistency tem piso de 0,983 por causa das arestas vivas. Os dois pisos devem ser relatados.

## Sensibilidade a perturbações controladas

[sensitivity.csv](sensitivity.csv). Base: GT subdividida até 43 560 vértices.

![Curvas de sensibilidade](sensitivity.png)

- **Monotonicidade:** todas as métricas pioram de forma monotônica nas três perturbações.
- **Ruído na direção da normal:** o Chamfer e o HD95 mudam pouco; a normal consistency cai de 0,98 para 0,77 já com σ = 0,25 %. Ela mede rugosidade e orientação, que as distâncias quase não captam.
- **Saliência local:** o Hausdorff por vértice é igual à altura da saliência. O F@1 % é o que mais separa os níveis (de 1,00 para 0,90), e o Chamfer dilui o erro local.
- **Remoção de superfície:** o F-score e a AUC-F caem quase linearmente com a fração removida. O HD95 só reage a partir de cerca de 10 %.
- **PSNR e SSIM:** são monotônicos, mas misturam silhueta e sombreamento.

## Roteiro sugerido para o artigo (IJCNN, 6 páginas)

1. Motivação: avaliar modelos *image-to-3D* (TripoSR, Stable Fast 3D, InstantMesh) exige métricas confiáveis.
2. Métricas como funções sobre variedades discretizadas: invariância, estabilidade e multiescala como requisitos.
3. Métricas ([ADRs](../../adr/)): amostragem, Chamfer, HD95, F@τ/AUC-F, normal consistency, PSNR, SSIM, LPIPS, regiões visível/oculta e escala do ICP.
4. Validação das métricas: as tabelas acima e a [incerteza de amostragem](../README.md#user-content-incerteza-de-amostragem), repetidas nas GTs do benchmark.
5. Benchmark: métricas globais, visível × oculto e correlação entre métricas geométricas e perceptuais.
6. Limitações e reprodutibilidade: câmera ortográfica, ICP local, viés de amostragem, sementes, versões e hashes.
