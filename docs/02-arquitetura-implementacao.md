# 02 — Arquitetura e plano de implementação

![Etapas de processamento](images/pipeline.svg)

## Código existente
- `mesh_eval_pipeline.py`: carrega GT/RM, normaliza, avalia MSE inicial, opcionalmente executa ICP, calcula Chamfer/Hausdorff/RMSE, renderiza e salva CSV/PLY/PNG.
- `percept_eval_pipeline.py`: repete a preparação geométrica e realiza renderização multivista, PSNR, SSIM e LPIPS.
- `run_mesh_eval.bat` e `run_percept_eval.bat`: inicializadores Windows.
- `output/`: resultados, que podem ser sobrescritos nas próximas execuções.

## Sequência para reproduzir a implementação
1. **Entrada e validação:** implementar `load_mesh(path)`, distinguir malha/cena, aplicar as transformações da cena e excluir vértices sem faces.
2. **Escala:** copiar ambas as malhas e dividir coordenadas pela diagonal da caixa delimitadora da GT.
3. **Comparação inicial:** calcular vizinho mais próximo nos dois sentidos e o MSE simétrico.
4. **Alinhamento:** se o MSE normalizado superar `--mse-threshold`, executar ICP de similaridade RM → GT em duas fases.
5. **Métricas finais:** recomputar distâncias e agregações geométricas com a malha alinhada.
6. **Visualização:** compartilhar câmera ortográfica e produzir mapa de calor nas posições GT.
7. **Comparação perceptual:** amostrar azimutes, renderizar cada par de vistas, recortar região relevante, computar LPIPS/PSNR/SSIM.
8. **Persistência:** registrar CSVs, `rm_aligned.ply`, mapas de calor e renders.

## Mapeamento de funções
| Responsabilidade | Funções do código |
|---|---|
| Diretórios | `ensure_dirs` |
| Importação | `load_mesh` |
| Pontos próximos | `nn_distances`, `symmetric_vertex_errors` |
| Erro inicial | `symmetric_mse` |
| ICP | `initial_similarity_from_bboxes`, `similarity_icp_align` |
| Métricas geométricas | `compute_metrics` (pipeline geométrico) |
| Câmera e render | `look_at`, `build_shared_camera` ou `build_tight_ortho_camera`, `render_mesh` |
| Cores por erro | `colorize_gt_heatmap`, `save_heatmap_figure` |
| Perceptual | `masked_psnr`, `masked_ssim`, `masked_lpips` |
| Agregação | `summarize_stats` |

## Proposta futura: modularizar sem alterar o comportamento
Extrair `mesh_io.py`, `normalization.py`, `registration.py`, `geometry_metrics.py`, `rendering.py`, `perceptual_metrics.py`, `reports.py`; criar `tests/` antes de mudar os pipelines. **Essa estrutura ainda não existe no repositório.** Priorizar testes de regressão com os CSVs atuais e explicar diferenças de tolerância numérica.
