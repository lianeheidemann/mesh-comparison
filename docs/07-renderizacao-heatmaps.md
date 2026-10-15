# 07 — Renderização ortográfica e mapa de calor

![Distâncias e malhas](images/distancias.svg)

## Câmera compartilhada
`build_shared_camera` calcula limites das duas malhas normalizadas (GT e RM alinhada), centro e diagonal, depois uma pose `look_at`. Os limites projetados dos oito cantos da bounding box determinam `xmag` e `ymag` de `pyrender.OrthographicCamera`.

O pipeline geométrico usa por padrão azimute **−135°** e elevação **25,264°**, com imagens de **1600 × 1200 pixels**. Renderiza GT e RM na mesma pose, impedindo que mudança de enquadramento produza comparação injusta.

## Mapa de calor
`colorize_gt_heatmap` associa a **cada vértice GT** a distância até o vértice RM alinhado mais próximo (`d_gt2rm`). Aplica `matplotlib` com colormap `RdYlGn_r`: próximo de zero tende a verde; distâncias maiores tendem a amarelo/vermelho. O limite máximo da escala é o **percentil 95**, que reduz a influência de valores extremos na aparência (valores acima dele saturam na mesma extremidade).

Arquivos:
- `output/heatmaps/gt_heatmap_colored.ply`: vértices coloridos.
- `output/heatmaps/gt_heatmap_ortho.png`: renderização com escala lateral.
- `output/renders/gt_ortho.png` e `rm_aligned_ortho.png`.

## Interpretação e limites
O mapa mostra **GT → RM**, não o erro simétrico completo. Um componente extra existente só na RM pode não aparecer com destaque no heatmap GT. O heatmap mede erro **geométrico por vértice**, não textura nem percepção visual.

## Checklist de implementação
1. Usar uma câmera para ambas as malhas.
2. Calcular distâncias GT → RM após o eventual alinhamento.
3. Normalizar valores para a paleta (registrar o percentil e a unidade).
4. Atribuir `vertex_colors` e exportar o PLY.
5. Renderizar e anexar uma legenda com unidades.
