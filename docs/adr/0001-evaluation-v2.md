# ADR 0001 — Protocolo de métricas `evaluation-v2`

- **Estado:** aceito pela pessoa responsável pelo projeto (26/10/2026), para uso nos experimentos com TripoSR, Stable Fast 3D e InstantMesh. A validação científica em dados reais ainda **não** foi feita.
- **Contratos afetados:** novos CC-14 a CC-17 em [CONTRATOS-CIENTIFICOS.md](../harness/CONTRATOS-CIENTIFICOS.md). CC-01 a CC-13 (legado) **não mudam**.

## Contexto

O artigo compara reconstruções 3D geradas por diferentes modelos a partir da mesma imagem. As métricas legadas (CC-03, CC-05, CC-09) foram revisadas:

1. **Distâncias entre vértices dependem da triangulação.** Os modelos geram malhas com densidades muito diferentes da GT (por exemplo, *marching cubes* denso contra malhas CAD esparsas). O Chamfer e o Hausdorff entre vértices mudam com essa densidade mesmo quando a superfície é a mesma (CC-05 já alertava).
2. **O Hausdorff máximo depende de um único ponto.** Um fragmento espúrio, comum em reconstruções de imagem única, determina o valor.
3. **O Chamfer médio não mede a completude.** Tatarchenko et al. (CVPR 2019) mostram que, em reconstrução de imagem única, o F-score com tolerância é mais informativo.
4. **O PSNR legado não usa a convenção usual** (soma RGB / N em vez de / 3N), o que impede a comparação direta com a literatura.
5. **A pergunta "o que acontece fora da vista de entrada"** não era respondida.

## Decisão

Criar o protocolo **`evaluation-v2`**, calculado **ao lado** do legado, sem alterar nenhum nome ou valor legado.

| Item | Definição |
| --- | --- |
| Amostragem | `100 000` pontos por malha, uniformes por área (face ∝ área, baricêntricas `√r1`), implementação NumPy própria; sementes `0` (GT) e `1` (RM alinhada); espaço normalizado pela diagonal da GT (CC-02), **após** o ICP condicional (CC-04). |
| Chamfer | `½[mean d(G→R) + mean d(R→G)]` sobre as amostras (média de distâncias, como no legado). |
| HD95 | `max(P95 d(G→R), P95 d(R→G))` (percentil linear do NumPy). |
| F-score@τ | precisão = fração das amostras RM com `d(R→G) < τ`; cobertura = fração das amostras GT com `d(G→R) < τ`; `F = 2PR/(P+R)` (0 se `P+R = 0`); τ ∈ {1 %, 2 %, 5 %} da diagonal da GT. |
| PSNR padrão | `10·log10(1/MSE)`, com MSE = soma dos erros RGB² na união das máscaras / `3N`; mesmo crop/máscara do legado (CC-08). Na mesma máscara, `PSNR_padrão = PSNR_legado + 10·log10(3)`. |
| Regiões | Opcional: com a vista da imagem de entrada (azimute/elevação no referencial da GT, z para cima), as amostras GT são classificadas como visíveis/ocultas por z-buffer ortográfico (`1024²`, tolerância `0,005` da diagonal). Cada amostra RM herda a região da amostra GT mais próxima. As métricas são calculadas por região. |
| Escala do ICP | `s = det(R_s)^(1/3)` da matriz final, registrada como diagnóstico. |

**Saídas:** `metrics/metrics_geometry_v2.csv` (uma linha por região: `all`, `visible`, `hidden`); a coluna `psnr_standard` é acrescentada **ao final** de `per_view_metrics.csv`, e a linha `psnr_standard` é acrescentada em `metrics_perceptual.csv`. A GUI mostra a aba "Geometric summary" e as linhas "PSNR legacy / PSNR standard" no resumo perceptual.

## Alternativas consideradas

- **Substituir as métricas legadas:** rejeitado por `AGENTS.md` e para manter a comparabilidade com os resultados anteriores.
- **Métricas v2 também antes do ICP:** rejeitado. Em imagem única, a escala absoluta e o referencial de saída de cada modelo são arbitrários, por isso os números pré-ICP medem a convenção de saída, não a qualidade. A distorção de escala fica visível em `icp_scale`, e o ICP com escala **uniforme** não corrige erros de proporção (anisotrópicos), que continuam penalizados. O MSE pré-alinhamento legado continua disponível.
- **RMSE v2:** não criado, porque é redundante com o Chamfer.
- **Visibilidade por *ray casting* (Trimesh):** rejeitada em favor do z-buffer, porque o pacote já depende de `pyrender` e o *ray casting* puro em Python é lento para 10⁵ raios sem Embree.
- **Normal consistency:** útil, mas fora do escopo pedido; pode entrar em uma v3.

## Consequências e limitações

- Amostragem estocástica: os resultados dependem de `N` e das sementes, que são fixas e registradas no CSV. A variação entre sementes deve ser medida antes do benchmark.
- GT com faces internas (CAD) recebe amostras internas; a GT precisa ser uma superfície "limpa".
- A câmera de entrada é aproximada por uma câmera **ortográfica** (a real é perspectiva); a diferença aparece perto das silhuetas. A convenção de eixos (z para cima) precisa ser conferida para cada conjunto de dados.
- O ICP é local: rotações grandes entre os referenciais dos modelos podem não convergir. É preciso conferir `alignment_triggered`, o MSE pós-alinhamento e o heatmap.
- SSIM e LPIPS não mudam (CC-10). Se GT e RM forem renderizadas uma com cor e a outra sem, as métricas perceptuais misturam textura e forma.

## Rollback

Ignorar ou remover `metrics_geometry_v2.csv`, a coluna e a linha `psnr_standard`, e reverter os commits do protocolo. As saídas legadas não dependem do v2.
