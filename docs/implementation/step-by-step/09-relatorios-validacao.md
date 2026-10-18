# 09 — Conferir os resultados exportados

> **Status: concluída.** Os scripts já exportam métricas, metadados, renders e a malha alinhada.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — Conferir os resultados exportados

Depois de calcular as métricas, o pipeline geométrico já grava `output/metrics/metrics_geometry.csv`. O fluxo perceptual já grava uma linha por vista em `per_view_metrics.csv` e estatísticas de mínimo, máximo, percentis 25/75, mediana e média em `metrics_perceptual.csv`. Ele também gera `run_metadata.csv`.

## Passo 2 — Exemplo de estrutura dos resultados

```python
# Exporta métricas e devolve a malha alinhada à unidade de entrada
import pandas as pd

pd.DataFrame([{
    'chamfer_mean_normalized': metrics['chamfer_mean'],
    'hausdorff_normalized': metrics['hausdorff'],
    'rmse_normalized': metrics['rmse'],
}]).to_csv('output/metrics/metrics_geometry.csv', index=False)
rm_export = rm_aligned.copy()
rm_export.apply_scale(diagonal_gt)
rm_export.export('output/aligned/rm_aligned.ply')
```

## Passo 3 — Executar e conferir

Os scripts já criam os diretórios, incluem os campos de métricas e convertem distâncias normalizadas para as unidades da GT; MSE é convertido com `diagonal_gt²`. Execute os dois scripts e confira os CSVs, PNGs e PLYs. Atenção: ambos gravam `rm_aligned.ply` no mesmo caminho e podem sobrescrevê-lo.

## Passo 4 — Próxima etapa

Continue para [10 — Planejar a validação e a evolução](10-limitacoes-evolucao.md).

**Código de referência:** [pipeline geométrico](../../../mesh_eval_pipeline.py) e [pipeline perceptual](../../../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
