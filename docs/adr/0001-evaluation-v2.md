# ADR 0001 — Métricas sobre amostras de superfície

- **Estado:** aceito (26/10/2026). Substituído em parte pelo [ADR 0003](0003-single-metric-standard.md), que remove as métricas anteriores e mantém estas como padrão único.

## Contexto

O artigo compara reconstruções de imagem única (TripoSR, Stable Fast 3D, InstantMesh). As métricas herdadas tinham quatro problemas:

- **Dependência da triangulação:** distâncias entre vértices mudam com a densidade da malha, mesmo quando a superfície é a mesma.
- **Hausdorff instável:** o valor máximo é decidido por um único ponto espúrio.
- **Completude não medida:** o Chamfer médio não capta partes ausentes.
- **PSNR fora da convenção:** dividia por N, e não por 3N.

## Decisão

| Item | Definição |
| --- | --- |
| Amostragem | 100 000 pontos por malha, uniformes por área (face ∝ área, baricêntricas com `√r1`), sementes `0` (GT) e `1` (RM), espaço normalizado pela diagonal da GT |
| Chamfer | ½ [mean d(G→R) + mean d(R→G)] |
| HD95 | max(P95 d(G→R), P95 d(R→G)) |
| F-score @τ | precisão = fração de amostras da RM com d < τ; cobertura = idem para a GT; F = 2PR/(P+R); τ = 1, 2, 5 % da diagonal |
| PSNR | 10·log10(1/MSE), MSE sobre os 3N valores RGB dos N pixels da união das máscaras |
| Regiões | Com a vista de entrada (azimute/elevação, z para cima), as amostras da GT são classificadas por z-buffer ortográfico (1024², tolerância 0,005 da diagonal); cada amostra da RM herda a região da amostra da GT mais próxima |
| Escala do ICP | `icp_scale = det(R_s)^(1/3)`, registrada como diagnóstico |

**Sem métricas pré-ICP:** em imagem única, a escala absoluta e o referencial de saída de cada modelo são arbitrários. O ICP com escala **uniforme** não corrige erros de proporção, que continuam penalizados.

## Consequências

- **Piso de amostragem:** com distâncias entre amostras, duas amostragens da mesma superfície davam Chamfer > 0 e F@1 % < 1. O [ADR 0004](0004-point-to-surface.md) resolveu isso com distâncias ponto-superfície.
- **Câmera de entrada:** a câmera ortográfica aproxima a perspectiva real, e a convenção de eixos deve ser conferida para cada conjunto de dados.
- **ICP:** é local.
- **SSIM e LPIPS:** usam o crop com o fundo zerado, que participa das janelas e convoluções.
