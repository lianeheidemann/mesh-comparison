# Implementação e validação

Os testes abaixo existem em `tests/` e rodam no CI. Eles verificam fórmulas, estrutura e casos sintéticos, mas **não** validam as métricas nas malhas do benchmark.

## Testes existentes

Entre parênteses, o número de testes de cada arquivo (111 no total).

| Área | Testes | Limite |
| --- | --- | --- |
| Métricas geométricas | [`test_metrics.py`](../../tests/test_metrics.py) (16), [`test_common.py`](../../tests/test_common.py) (6): distância ponto-superfície (face, aresta, vértice), sem piso para a mesma superfície, Chamfer independente de N, deslocamentos conhecidos (CD = HD95 = δ, F em degrau), HD95 robusto a *outliers*, precisão/cobertura, regiões, amostragem reprodutível e proporcional à área | Casos sintéticos |
| NC, F(τ) e robustez | [`test_robustness.py`](../../tests/test_robustness.py) (8): NC = cos θ, F(τ) monotônica, AUC em [0, 1], invariância à permutação e à re-triangulação, perturbações monotônicas | Uma malha sintética por teste |
| Preparo e alinhamento | [`test_prepare.py`](../../tests/test_prepare.py) (3), [`test_icp.py`](../../tests/test_icp.py) (7): ICP abaixo/acima do limiar, rotações de até 180° com escala e translação, exportação na escala da GT; inicialização em `test_common.py` | Cópias transformadas de uma GT ([estudo](../results/icp/README.md)) |
| Leitura de cenas | [`test_io.py`](../../tests/test_io.py) (4): glTF com objeto, chão, linha, câmera e luz; só as malhas entram, a linha é listada | Esqueleto e animação não testados |
| GTs e manifesto | [`test_gt_check.py`](../../tests/test_gt_check.py) (6): objeto limpo aprovado; base, casca interna, buracos, arquivo ilegível e formato não suportado detectados; manifesto (`datasets/manifest.py`) com campo vazio, arquivo ausente e data anterior ao corte | Limites são gatilhos de revisão |
| Download do GSO | [`test_fetch_gso.py`](../../tests/test_fetch_gso.py) (5): Fuel simulado; suplente no lugar de objeto ausente, textura junto do `.mtl`, manifesto válido, rede fora do ar interrompe | Download real não testado (Fuel bloqueado aqui) |
| Percepção | [`test_perceptual.py`](../../tests/test_perceptual.py) (7): PSNR com erro conhecido, máscara, `Inf`/`NaN`, crop, estatísticas finitas | Sem LPIPS/SSIM multivista |
| Heatmap e renderização | [`test_heatmap.py`](../../tests/test_heatmap.py) (1), [`test_rendering.py`](../../tests/test_rendering.py) (1): escala P95; renderer reutilizado igual a renders avulsos | `test_rendering` exige OpenGL *offscreen* |
| Gráficos | [`test_plots.py`](../../tests/test_plots.py) (5): intervalo bootstrap, dispersão de amostragem, figuras escritas, métrica sem valores finitos omitida | Não confere o conteúdo visual |
| GUI (lógica) | [`test_gui_config.py`](../../tests/test_gui_config.py) (10), [`test_worker.py`](../../tests/test_worker.py) (1), [`test_outputs.py`](../../tests/test_outputs.py) (4), [`test_gallery.py`](../../tests/test_gallery.py) (4), [`test_device.py`](../../tests/test_device.py) (6), [`test_view_geometry.py`](../../tests/test_view_geometry.py) (9): comandos, notas da aba geométrica, galerias, dispositivo do LPIPS (CUDA simulado), câmera e chão do visualizador 3D | Não abre a janela |
| Linhas de comando | [`test_cli.py`](../../tests/test_cli.py) (5): cada ferramenta abre a ajuda como `scripts/<nome>.py` e como `python -m meshcomparison.cli.<nome>` | Só a inicialização |
| Saídas | [`test_output_schema.py`](../../tests/test_output_schema.py) (3): pipelines em subprocesso (320 × 240 px, 2 vistas em CPU): arquivos, colunas, regiões e figuras | Estrutura, não valores |

## Validação pendente

| Prioridade | Item |
| --- | --- |
| Alta | Malhas do benchmark (TripoSR, Stable Fast 3D, InstantMesh, TRELLIS): identidade, transformação e escala conhecidas, deformação, incompletude e densidade |
| Alta | Estudo de robustez nas GTs do benchmark, com LPIPS |
| Alta | Convenção de eixos e câmera de entrada de cada conjunto de dados; câmera ortográfica × perspectiva |
| Alta | Alinhamento de reconstruções reais (formas diferentes da GT, simetrias): conferir a orientação escolhida pela inicialização global |
| Alta | CI do branch `evaluation-v2`: ainda não executado (só roda em PRs e em `main`) |
| Média | LPIPS em CUDA × CPU |
| Média | GUI no Windows e o painel da vista de entrada (no Linux, abas de resultados e visualizador 3D já conferidos) |
