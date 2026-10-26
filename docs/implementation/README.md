# Implementação e validação

Os testes abaixo existem em `tests/` e rodam no CI. Eles verificam fórmulas, estrutura e casos sintéticos, mas **não** validam as métricas nas malhas do benchmark.

## Testes existentes

| Área | Testes | Limite |
| --- | --- | --- |
| Métricas geométricas | [`test_metrics.py`](../../tests/test_metrics.py), [`test_common.py`](../../tests/test_common.py): distância ponto-superfície (face, aresta, vértice), ausência de piso para a mesma superfície, Chamfer independente de N, NC = cos θ, amostragem reprodutível e proporcional à área, deslocamentos conhecidos (CD = HD95 = δ, F-score em degrau), HD95 robusto a *outliers*, precisão/cobertura, regiões, escala do ICP, visibilidade de um cubo | Casos sintéticos |
| Normal consistency, F(τ), robustez | [`test_robustness.py`](../../tests/test_robustness.py): NC = cos θ em planos inclinados, F(τ) monotônica, AUC em [0,1], invariância à permutação e à re-triangulação, perturbações monotônicas, remoção reduz a cobertura | Uma malha sintética por teste |
| Leitura de cenas | [`test_io.py`](../../tests/test_io.py): glTF com objeto, chão, linha, câmera e luz; só as malhas entram, a linha é descartada e listada, os nós aparecem com área; malha única sem aviso | Cena sintética; esqueleto e animação não testados |
| Verificação das GTs | [`test_gt_check.py`](../../tests/test_gt_check.py): objeto limpo aprovado; base, casca interna (~20 % da área), buracos, arquivo ilegível e formato não suportado detectados; manifesto com campos vazios, arquivo ausente e data anterior ao corte de treino | Malhas sintéticas; os limites são gatilhos de revisão |
| Download do GSO | [`test_fetch_gso.py`](../../tests/test_fetch_gso.py): Fuel simulado em memória; suplente no lugar de objeto ausente, textura copiada para junto do `.mtl`, manifesto aceito pelo `check_gt.py`, rede indisponível interrompe em vez de marcar objetos como ausentes | Download real não testado (Fuel bloqueado no ambiente de desenvolvimento) |
| Gráficos e estimativas | [`test_plots.py`](../../tests/test_plots.py): intervalo bootstrap, dispersão de amostragem, escrita das figuras, métrica sem valores finitos (LPIPS ausente) omitida | Não confere o conteúdo visual |
| Preparo e alinhamento | [`test_prepare.py`](../../tests/test_prepare.py), [`test_common.py`](../../tests/test_common.py), [`test_icp.py`](../../tests/test_icp.py): ICP abaixo/acima do limiar, recuperação de rotações de até 180° com escala e translação (unitário e pelo pipeline), rotações dos eixos e eixos principais, exportação na escala da GT, MSE, subamostragem, inicialização (rotação, escala RMS, centroides) | Validado em cópias transformadas de uma GT ([estudo](../results/icp/README.md)) |
| Percepção | [`test_perceptual.py`](../../tests/test_perceptual.py): PSNR com erro conhecido, máscara, `Inf`/`NaN`, crop, estatísticas finitas | Não executa LPIPS/SSIM multivista |
| Heatmap e renderização | [`test_heatmap.py`](../../tests/test_heatmap.py), [`test_rendering.py`](../../tests/test_rendering.py): escala P95; renderer reutilizado igual a renders avulsos | `test_rendering` é ignorado sem OpenGL offscreen |
| GUI (lógica) | [`test_gui_config.py`](../../tests/test_gui_config.py), [`test_worker.py`](../../tests/test_worker.py), [`test_outputs.py`](../../tests/test_outputs.py) (notas da aba geométrica: ICP, MSE, vista de entrada, aviso de cena), [`test_gallery.py`](../../tests/test_gallery.py) (imagens e figuras), [`test_device.py`](../../tests/test_device.py), [`test_view_geometry.py`](../../tests/test_view_geometry.py) (câmera, elevação limitada, limites, chão e enquadramento do visualizador 3D, com valores calculados à mão) | Não abre a janela; CUDA simulado |
| Linhas de comando | [`test_cli.py`](../../tests/test_cli.py): cada ferramenta abre a ajuda como `scripts/<nome>.py` e como `python -m meshcomparison.cli.<nome>` | Só a inicialização; a lógica é testada nos módulos |
| Saídas | [`test_output_schema.py`](../../tests/test_output_schema.py): pipelines em subprocesso (320 × 240 px, 2 vistas em CPU), arquivos, colunas, regiões e figuras | Estrutura, não valores |

## Validação pendente

| Prioridade | Item |
| --- | --- |
| Alta | Malhas do benchmark (TripoSR, Stable Fast 3D, InstantMesh): identidade, transformação e escala conhecidas, deformação, incompletude e densidade |
| Alta | Estudo de robustez nas GTs do benchmark, com LPIPS |
| Alta | Convenção de eixos e câmera de entrada de cada conjunto de dados; câmera ortográfica × perspectiva |
| Alta | Alinhamento de reconstruções reais (formas diferentes da GT, simetrias): conferir a orientação escolhida pela inicialização global |
| Alta | CI do branch `evaluation-v2`: ainda não executado (só roda em PRs e em `main`) |
| Média | LPIPS em CUDA × CPU; GUI numa janela real: abas de resultados só renderizadas com a plataforma *offscreen* do Qt; visualização 3D e painel da vista de entrada nunca abertos |
