# Implementação e validação

Os testes abaixo existem em `tests/` e rodam no CI. Eles verificam fórmulas, estrutura e casos sintéticos, mas **não** validam as métricas nas malhas do benchmark.

## Testes existentes

| Área | Testes | Limite |
| --- | --- | --- |
| Métricas geométricas | [`test_metrics.py`](../../tests/test_metrics.py), [`test_common.py`](../../tests/test_common.py): distância ponto-superfície (face, aresta, vértice), ausência de piso para a mesma superfície, Chamfer independente de N, NC = cos θ, amostragem reprodutível e proporcional à área, deslocamentos conhecidos (CD = HD95 = δ, F-score em degrau), HD95 robusto a *outliers*, precisão/cobertura, regiões, escala do ICP, visibilidade de um cubo | Casos sintéticos |
| Normal consistency, F(τ), robustez | [`test_robustness.py`](../../tests/test_robustness.py): NC = cos θ em planos inclinados, F(τ) monotônica, AUC em [0,1], invariância à permutação e à re-triangulação, perturbações monotônicas, remoção reduz a cobertura | Uma malha sintética por teste |
| Gráficos e estimativas | [`test_plots.py`](../../tests/test_plots.py): intervalo bootstrap, dispersão de amostragem, escrita das figuras | Não confere o conteúdo visual |
| Preparo e alinhamento | [`test_prepare.py`](../../tests/test_prepare.py), [`test_common.py`](../../tests/test_common.py), [`test_icp.py`](../../tests/test_icp.py): ICP abaixo/acima do limiar, recuperação de rotações de até 180° com escala e translação (unitário e pelo pipeline), rotações dos eixos e eixos principais, exportação na escala da GT, MSE, subamostragem, inicialização (rotação, escala RMS, centroides) | Validado em cópias transformadas de uma GT ([estudo](../results/icp/README.md)) |
| Percepção | [`test_perceptual.py`](../../tests/test_perceptual.py): PSNR com erro conhecido, máscara, `Inf`/`NaN`, crop, estatísticas finitas | Não executa LPIPS/SSIM multivista |
| Heatmap e renderização | [`test_heatmap.py`](../../tests/test_heatmap.py), [`test_rendering.py`](../../tests/test_rendering.py): escala P95; renderer reutilizado igual a renders avulsos | `test_rendering` é ignorado sem OpenGL offscreen |
| GUI (lógica) | [`test_gui_config.py`](../../tests/test_gui_config.py), [`test_worker.py`](../../tests/test_worker.py), [`test_outputs.py`](../../tests/test_outputs.py), [`test_gallery.py`](../../tests/test_gallery.py), [`test_device.py`](../../tests/test_device.py) | Não abre a janela; CUDA simulado |
| Saídas | [`test_output_schema.py`](../../tests/test_output_schema.py): pipelines em subprocesso (320 × 240 px, 2 vistas em CPU), arquivos, colunas e regiões | Estrutura, não valores |

## Validação pendente

| Prioridade | Item |
| --- | --- |
| Alta | Malhas do benchmark (TripoSR, Stable Fast 3D, InstantMesh): identidade, transformação e escala conhecidas, deformação, incompletude e densidade |
| Alta | Estudo de robustez nas GTs do benchmark, com LPIPS |
| Alta | Convenção de eixos e câmera de entrada de cada conjunto de dados; câmera ortográfica × perspectiva |
| Alta | Alinhamento de reconstruções reais (formas diferentes da GT, simetrias): conferir a orientação escolhida pela inicialização global |
| Média | LPIPS em CUDA × CPU; teste manual ou automatizado da GUI |
