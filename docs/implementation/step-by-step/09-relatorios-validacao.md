# 09 — Conferir os resultados exportados

> **Status: concluída.** Os scripts já exportam métricas, metadados, renders e a malha alinhada.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — Conferir os resultados exportados

Depois de calcular as métricas, o pipeline geométrico grava `metrics/metrics_geometry.csv` **dentro de `--out`**. O fluxo perceptual grava uma linha por vista em `metrics/per_view_metrics.csv` e estatísticas de mínimo, máximo, percentis 25/75, mediana e média em `metrics/metrics_perceptual.csv`. O pipeline perceptual gera `metrics/run_metadata.csv` e o geométrico gera `metrics/run_metadata_geometry.csv`; ambos registram parâmetros e o ambiente da execução (versões do projeto, Python e PyTorch/CUDA, e data/hora UTC). O CSV geométrico de métricas continua incluindo seus parâmetros e os componentes da transformação.

## Passo 2 — Ler os resultados gerados pela versão atual

Depois de executar os **dois comandos** da seção [Validate on Windows](../../../README.md#validate-on-windows), use os caminhos reais dos CSVs:

```python
# Lê e mostra os campos efetivamente exportados pelos dois pipelines
from pathlib import Path
import pandas as pd

base = Path('output/windows-validation')
geom = pd.read_csv(base / 'geometry/metrics/metrics_geometry.csv')
percep = pd.read_csv(base / 'perceptual/metrics/metrics_perceptual.csv')
print(geom[['mean_chamfer_gt_units', 'symmetric_hausdorff_gt_units',
            'symmetric_rmse_gt_units']].to_string(index=False))
print(percep[['metric', 'median', 'mean']].to_string(index=False))
```

As colunas geométricas reais são, entre outras, `mean_chamfer_normalized`, `symmetric_hausdorff_normalized`, `symmetric_rmse_normalized` e os equivalentes com sufixo `_gt_units`. Os nomes antigos `chamfer_mean_normalized`, `hausdorff_normalized` e `rmse_normalized` do exemplo anterior **não são colunas emitidas por esta versão**. O alinhamento é exportado em `aligned/rm_aligned.ply`, reescalado para a unidade da GT.

## Passo 3 — Executar e conferir

Os scripts criam os diretórios dentro do caminho informado por `--out`, incluem os campos de métricas e convertem distâncias normalizadas para as unidades da GT; MSE é convertido com o quadrado da diagonal da GT. Confira CSVs, PNGs e PLYs. **Ambos os pipelines gravam `aligned/rm_aligned.ply` no respectivo `--out`**: se a mesma pasta for usada, um arquivo pode sobrescrever o outro. Para reproduzir ou comparar experimentos, prefira diretórios separados, como no roteiro do Windows. Os resultados de exemplo já versionados ficam em [`examples/output/`](../../../examples/output/), e não devem ser substituídos durante a verificação.

## Passo 4 — Próxima etapa

Continue para [10 — Planejar a validação e a evolução](10-limitacoes-evolucao.md).

**Código de referência:** [pipeline geométrico](../../../src/meshcomparison/geometry/pipeline.py) e [pipeline perceptual](../../../src/meshcomparison/perceptual/pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
