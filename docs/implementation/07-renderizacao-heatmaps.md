# 07 — Criar câmera compartilhada, renders e heatmap

> **Objetivo:** implementar esta parte desde o zero, mesmo que ela já exista nos scripts de referência.

![Esquema da etapa](images/distancias.svg)

## Passo 1 — O que criar

Implemente `look_at`, `bounds_corners` e `build_shared_camera`: calcule uma única câmera ortográfica a partir da caixa envolvente conjunta GT+RM. Use `pyrender.Scene`, `OrthographicCamera` e `OffscreenRenderer` para salvar as duas vistas com enquadramento igual.

## Passo 2 — Implementação inicial

```python
# Associa a cada vértice GT uma cor proporcional à distância até a RM
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

def colorize_gt_heatmap(gt_mesh, d_gt2rm):
    colored = gt_mesh.copy()
    vmax = max(float(np.nanpercentile(d_gt2rm, 95)), 1e-12)
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)
    cmap = plt.get_cmap('RdYlGn_r')
    colored.visual.vertex_colors = (cmap(norm(d_gt2rm)) * 255).astype(np.uint8)
    return colored, norm, cmap
```

## Passo 3 — Completar, executar e validar

Renderize `gt_ortho.png`, `rm_aligned_ortho.png` e a malha colorida; acrescente uma barra de cores com Matplotlib para produzir `gt_heatmap_ortho.png`. Exporte também `gt_heatmap_colored.ply`. Observe que as cores representam somente GT→RM, não a distância simétrica.

## Passo 4 — Próxima etapa

Continue para [08 — Construir as vistas e calcular LPIPS, PSNR e SSIM](08-metricas-perceptuais.md).

**Código de referência:** [pipeline geométrico](../mesh_eval_pipeline.py) e [pipeline perceptual](../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
