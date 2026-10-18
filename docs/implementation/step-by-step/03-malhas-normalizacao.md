# 03 — Importar e normalizar duas malhas

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — O que criar

Implemente `load_mesh(path)` usando `trimesh.load(path, force='scene', process=False, maintain_order=True)`. Se o retorno for uma cena, percorra as instâncias e aplique as transformações do grafo antes de concatenar as geometrias. Remova vértices não referenciados e rejeite `.fbx` explicitamente.

## Passo 2 — Implementação inicial

```python
# Normaliza as duas malhas usando a mesma escala derivada da referência
import numpy as np

gt = load_mesh(gt_path)
rm = load_mesh(rm_path)
diagonal_gt = np.linalg.norm(gt.bounds[1] - gt.bounds[0])
if diagonal_gt < 1e-12:
    raise ValueError('Malha GT degenerada')
scale = 1.0 / diagonal_gt
gt.apply_scale(scale)
rm.apply_scale(scale)
```

## Passo 3 — Completar, executar e validar

Teste com duas cópias idênticas de um STL: após normalizar, as coordenadas devem continuar coincidentes. Não normalize cada malha por sua própria diagonal: isso apagaria diferenças de tamanho antes da avaliação.

## Passo 4 — Próxima etapa

Continue para [04 — Construir a correspondência e o ICP](04-alinhamento-icp.md).

**Código de referência:** [pipeline geométrico](../../../mesh_eval_pipeline.py) e [pipeline perceptual](../../../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
