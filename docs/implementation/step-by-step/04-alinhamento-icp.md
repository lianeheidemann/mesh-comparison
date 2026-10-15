# 04 — Construir a correspondência e o ICP

> **Objetivo:** implementar esta parte desde o zero, mesmo que ela já exista nos scripts de referência.

![Esquema da etapa](../images/icp.svg)

## Passo 1 — O que criar

Primeiro crie `nn_distances` com `scipy.spatial.cKDTree` para localizar o vértice de destino mais próximo de cada vértice de origem. Calcule o MSE simétrico pré-alinhamento. Quando superar `1e-4`, aplique ICP à RM, mantendo GT fixa.

## Passo 2 — Implementação inicial

```python
# Calcula vizinhos mais próximos e configura o estimador ICP com escala uniforme
from scipy.spatial import cKDTree
import open3d as o3d

def nn_distances(src, dst):
    return cKDTree(dst).query(src, k=1)

estimator = o3d.pipelines.registration.TransformationEstimationPointToPoint(with_scaling=True)
```

## Passo 3 — Completar, executar e validar

Para completar `similarity_icp_align`, converta os vértices em `o3d.geometry.PointCloud`, limite a amostra a 50 mil pontos, estime escala e translação iniciais pelas caixas envolventes e execute `registration_icp` em duas passagens (limiares 0,25 e 0,05, até 100 iterações cada). Aplique a matriz 4×4 resultante à RM. Teste com uma malha deslocada e verifique a queda do MSE. O ICP atual também pode corrigir escala: documente essa decisão antes de interpretar diferenças dimensionais.

## Passo 4 — Próxima etapa

Continue para [05 — Implementar MSE e RMSE simétricos](05-mse-rmse.md).

**Código de referência:** [pipeline geométrico](../../mesh_eval_pipeline.py) e [pipeline perceptual](../../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
