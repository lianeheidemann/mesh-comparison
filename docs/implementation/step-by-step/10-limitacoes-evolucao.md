# 10 — Validar os limites antes de ampliar o projeto

> **Objetivo:** implementar esta parte desde o zero, mesmo que ela já exista nos scripts de referência.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — O que criar

Monte casos controlados: malhas idênticas, deslocadas, escaladas, com vértices extras, buracos e densidades diferentes. Execute o pipeline completo e registre os resultados esperados para cada métrica.

## Passo 2 — Implementação inicial

```python
# Verifica um caso mínimo de consistência das métricas geométricas
import numpy as np

points = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
result = compute_metrics(points, points.copy())
assert np.isclose(result['chamfer_mean'], 0.0)
assert np.isclose(result['hausdorff'], 0.0)
assert np.isclose(result['rmse'], 0.0)
```

## Passo 3 — Completar, executar e validar

Depois de reproduzir o comportamento atual, considere implementar amostragem uniforme de superfícies, inspeção de topologia, testes automatizados, opção de ICP sem escala, PSNR RGB convencional e separação de módulos. Essas são **etapas futuras**, não recursos existentes. Documente as diferenças de metodologia antes de comparar novos resultados com CSVs antigos.

## Passo 4 — Próxima etapa

Continue para a revisão do roteiro em [docs/README.md](../README.md).

**Código de referência:** [pipeline geométrico](../../../mesh_eval_pipeline.py) e [pipeline perceptual](../../../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
