# Guia de implementação e avaliação — Mesh Comparison

Esta documentação acompanha os arquivos reais `mesh_eval_pipeline.py` e `percept_eval_pipeline.py`. O objetivo é permitir compreender, reproduzir e evoluir o código, sem confundir funcionalidades **implementadas** com melhorias **propostas**.

![Pipeline](images/pipeline.svg)

## Ordem de leitura

1. [01 — Preparação do ambiente](01-preparacao-ambiente.md)
2. [02 — Arquitetura e plano de implementação](02-arquitetura-implementacao.md)
3. [03 — Importação e normalização de malhas](03-malhas-normalizacao.md)
4. [04 — Correspondência e ICP](04-alinhamento-icp.md)
5. [05 — Métricas geométricas: MSE e RMSE](05-mse-rmse.md)
6. [06 — Métricas geométricas: Chamfer e Hausdorff](06-chamfer-hausdorff.md)
7. [07 — Renderização e mapas de calor](07-renderizacao-heatmaps.md)
8. [08 — Métricas perceptuais: LPIPS, PSNR e SSIM](08-metricas-perceptuais.md)
9. [09 — Relatórios, experimentos e validação](09-relatorios-validacao.md)
10. [10 — Limitações, verificações e evolução](10-limitacoes-evolucao.md)

## Convenções

- **GT (ground truth):** modelo de referência.
- **RM (reconstructed mesh):** modelo reconstruído, identificado no repositório por `mod.stl`.
- **Implementado:** comportamento conferido nos scripts da raiz.
- **Proposto:** sugestão de alteração, ainda não integrada aos scripts.
- Fórmulas de distância descritas neste guia operam sobre **vértices**, não sobre a superfície contínua dos triângulos.
- A unidade dos arquivos STL não é autodescritiva: só interprete distâncias físicas após confirmar a unidade e a escala da entrada.

Os SVGs em [images/](images/) são diagramas esquemáticos, não resultados numéricos dos experimentos.
