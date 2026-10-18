# Mesh Comparison — implementar e evoluir o projeto existente

Este guia parte do estado atual do repositório. Os pipelines geométrico e perceptual já estão implementados em [`mesh_eval_pipeline.py`](../../mesh_eval_pipeline.py) e [`percept_eval_pipeline.py`](../../percept_eval_pipeline.py). Use as etapas para entender a implementação, executá-la, validar seu comportamento e então desenvolver melhorias sem recriar o que já existe.

![Visão geral](images/pipeline.svg)

## Status das etapas

1. [x] [Preparar o ambiente](step-by-step/01-preparacao-ambiente.md) — pipelines executados, versões fixadas em `environment-lock.yml`; ambiente CPU-only, sem CUDA.
2. [x] [Programas, CLI e diretórios](step-by-step/02-arquitetura-implementacao.md)
3. [x] [Carregamento e normalização das malhas](step-by-step/03-malhas-normalizacao.md)
4. [x] [Correspondência e alinhamento ICP](step-by-step/04-alinhamento-icp.md)
5. [x] [MSE e RMSE](step-by-step/05-mse-rmse.md)
6. [x] [Chamfer e Hausdorff](step-by-step/06-chamfer-hausdorff.md)
7. [x] [Câmera, renders e heatmap](step-by-step/07-renderizacao-heatmaps.md)
8. [x] [Renderização multivista, LPIPS, PSNR e SSIM](step-by-step/08-metricas-perceptuais.md)
9. [x] [CSVs, exportação PLY e execução](step-by-step/09-relatorios-validacao.md)
10. [ ] [Validação sistemática e evolução](step-by-step/10-limitacoes-evolucao.md) — plano de testes e melhorias futuras.

**Como ler os passos:** os trechos de código são recortes didáticos dos scripts atuais. Nas etapas concluídas, confira a implementação existente e execute ou adapte o pipeline; não crie uma segunda cópia dos recursos. A etapa 10 reúne validações ainda não automatizadas e evoluções propostas.

**Convenção:** GT é a malha de referência; RM é a malha avaliada. As métricas geométricas atuais calculam vizinhos mais próximos entre vértices. O ICP atual pode corrigir escala; leve isso em conta ao interpretar diferenças dimensionais.
