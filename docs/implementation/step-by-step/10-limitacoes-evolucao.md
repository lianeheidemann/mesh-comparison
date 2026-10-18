# 10 — Planejar a validação e a evolução

> **Status: pendente de validação sistemática.** Esta etapa organiza testes que ainda precisam ser executados e melhorias propostas; não é uma funcionalidade já concluída.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — Planejar os testes que faltam

Ainda falta executar e registrar casos controlados para: malhas idênticas, deslocadas, escaladas, com vértices extras, buracos e densidades diferentes. Execute o pipeline completo e registre os resultados esperados para cada métrica.

## Passo 2 — Caso mínimo de referência

```python
# Verifica um caso mínimo de consistência das métricas geométricas
import numpy as np

points = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
result = compute_metrics(points, points.copy())
assert np.isclose(result['chamfer_mean'], 0.0)
assert np.isclose(result['hausdorff'], 0.0)
assert np.isclose(result['rmse'], 0.0)
```

## Passo 3 — Separar validações pendentes de melhorias futuras

A validação sistemática ainda está pendente: o repositório não possui uma suíte automatizada para esses casos. Como melhorias futuras, considere amostragem uniforme de superfícies, inspeção de topologia, opção de ICP sem escala, PSNR RGB convencional e separação em módulos. Essas mudanças alteram a metodologia ou a organização do código; documente-as antes de comparar resultados novos com CSVs antigos.

## Passo 4 — Próxima etapa

Depois de executar e documentar os testes, atualize o status desta etapa e a revisão do roteiro em [docs/README.md](../README.md).

**Código de referência:** [pipeline geométrico](../../../mesh_eval_pipeline.py) e [pipeline perceptual](../../../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
