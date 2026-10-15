# 03 — Importação e normalização das malhas

## Geometria de entrada
`load_mesh(path)` usa `trimesh.load(..., force='scene', process=False, maintain_order=True)`. Se obtiver uma cena, percorre geometrias e nós, aplica as transformações registradas e concatena os componentes em uma malha. Depois remove vértices não referenciados. O resultado é um `trimesh.Trimesh`; os dois pipelines rejeitam `.fbx`.

## Normalização pela diagonal da GT
Se a caixa delimitadora da GT tiver mínimo `b_min` e máximo `b_max`:

\[
D_{GT}=\lVert b_{max}-b_{min}\rVert_2,\quad s=1/D_{GT}
\]

Cada coordenada em **ambas** as malhas passa a `p' = s p`. A GT fica com diagonal igual a 1; a RM mantém suas diferenças relativas de escala até um possível ICP.

### Por que usar a diagonal da referência?
Permite comparar casos com dimensões globais diferentes usando uma medida adimensional consistente **dentro de cada par**. Não significa que um resultado normalizado represente milímetros.

### Volta às unidades de entrada
- Distância: `d_original = d_normalizada × D_GT`.
- MSE: `MSE_original = MSE_normalizado × D_GT²`.
- A malha alinhada é reescalada antes de exportar `output/aligned/rm_aligned.ply`.

## Cuidados técnicos
- O código verifica `D_GT < 1e-12` e aborta para uma referência degenerada.
- Não há centragem global das duas malhas antes do cálculo inicial: deslocamento/orientação afetam o MSE e podem disparar ICP.
- Modelos com unidades inconsistentes exigem inspeção prévia.
- Escala uniforme permitida no ICP pode **ocultar um erro dimensional real** de reconstrução. Para estudos de fidelidade de tamanho, medir também antes de permitir escala.
