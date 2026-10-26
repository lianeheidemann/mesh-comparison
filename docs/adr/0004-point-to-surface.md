# ADR 0004 — Distâncias ponto-superfície

- **Estado:** aceito (26/10/2026). Altera a definição de distância dos ADRs [0001](0001-evaluation-v2.md)–[0003](0003-single-metric-standard.md); amostragem, tolerâncias, regiões e saídas não mudam.

## Contexto

Até aqui, cada amostra era medida até a **amostra** mais próxima da outra malha. O estudo de incerteza mostrou que isso cria um viés:

- **Chamfer sem convergir:** caía de 0,0039 para 0,0034 (normalizado) entre 10⁵ e 3 × 10⁵ amostras.
- **Normal consistency sem convergir:** também continuava a variar com N.
- **Piso para superfícies idênticas:** duas amostragens da mesma malha davam Chamfer de 0,0015 e normal consistency de 0,983.

Esse piso depende de N e da área da malha. Por isso, distorce a comparação entre modelos que geram malhas de tamanhos diferentes.

## Decisão

- **Distância:** d(g, R) é a distância de cada amostra g da GT até o **ponto mais próximo nos triângulos** da RM, e d(r, G) é o equivalente no sentido contrário. O cálculo usa `open3d.t.geometry.RaycastingScene.compute_closest_points` (Embree), sem dependência nova.
- **Métricas afetadas:** Chamfer, HD95, F-score, F(τ), AUC-F e o MSE simétrico que decide o ICP passam a usar essa distância.
- **Normal consistency:** compara a normal da amostra com a normal do triângulo mais próximo.
- **Heatmap:** usa a distância exata de cada vértice da GT até a superfície da RM.
- **Sem mudança:**
  - O ICP continua ponto a ponto sobre as amostras.
  - Cada amostra da RM continua herdando a região da amostra da GT mais próxima.
  - Sem malhas (conjuntos de pontos), `compute_metrics` mantém a distância até a amostra mais próxima.

## Consequências

Par de exemplo, superfície inteira. Antes: distância amostra-amostra; depois: ponto-superfície.

| Métrica | Antes | Depois |
| --- | ---: | ---: |
| Chamfer | 0,0147 | 0,0100 (−32 %) |
| HD95 | 0,0805 | 0,0800 (−0,6 %) |
| F@1% | 0,907 | 0,908 |
| AUC‑F | 0,980 | 0,981 |
| NC | 0,945 | 0,960 |
| MSE pré-alinhamento | 6,95 × 10⁻⁵ | 6,66 × 10⁻⁵ |

Chamfer e HD95 em unidades da GT; NC = normal consistency; ICP não acionado nos dois casos.

- **Chamfer na região oculta:** caiu 55 %; ali, a maior parte do erro anterior era piso.
- **Comparação entre regiões:** a razão visível/oculta do Chamfer passou de 2,4 para 4,4.
- **Convergência:** de 10³ a 3 × 10⁵ amostras, as médias de Chamfer, F@1 % e normal consistency ficam constantes. O desvio entre sementes cai com N; com 10⁵ amostras, o coeficiente de variação é de 0,8 % (Chamfer), 1,0 % (HD95) e ≤ 0,1 % (escores). O HD95 só se estabiliza a partir de ~10⁴ amostras.
- **Superfícies idênticas ou re-trianguladas:** dão 0 e 1, exceto por um arredondamento de float32 de ~10⁻⁷ (consulta do Open3D).
- **Comparabilidade:** valores calculados antes deste ADR não são comparáveis com os atuais.
