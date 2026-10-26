# ADR 0003 — Padrão único de métricas

- **Estado:** aceito (26/10/2026). Substitui em parte os ADRs [0001](0001-evaluation-v2.md) e [0002](0002-robustness-study.md).

## Contexto

As métricas dos ADRs 0001 e 0002 eram calculadas ao lado das métricas herdadas do projeto original. Preservar o comportamento original deixou de ser um requisito, e manter dois conjuntos complicava o código, as saídas e a interpretação.

## Decisão

1. **Métricas:** ficam só as dos ADRs 0001 e 0002. Saem Chamfer, Hausdorff e RMSE entre vértices e o PSNR dividido por N; `psnr` passa a ser o PSNR padrão.
2. **Alinhamento:** o MSE pré-alinhamento (limiar `1e-4`) e o ICP de similaridade usam as amostras de superfície.
3. **Heatmap:** a cor de cada vértice da GT é a distância até a superfície amostrada da RM alinhada. O P95 é gravado no CSV (`heatmap_vmax_gt_units`).
4. **Saídas:** `metrics_geometry.csv` (uma linha por região, mais as configurações da execução) e `fscore_curve.csv`.
5. **Documentação:** o documento de contratos e as regras de preservação do `AGENTS.md` foram removidos; mudanças de métricas passam a ser registradas em ADRs.

## Consequências

- **Par de exemplo:** métricas e curva F(τ) idênticas às dos ADRs 0001–0002 (diferença 0). O MSE pré-alinhamento passou de 7,30 × 10⁻⁵ (vértices) para 6,95 × 10⁻⁵ (amostras); o ICP continua não acionado.
- **Pares com ICP acionado:** o alinhamento pode mudar um pouco, porque o ICP passa a usar amostras uniformes por área.
- **Registro antigo:** `examples/output/` é da versão anterior e não é comparável.
