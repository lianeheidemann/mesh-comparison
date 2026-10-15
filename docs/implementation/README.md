# Mesh Comparison — tutorial de implementação do zero

Este material ensina a **construir o projeto desde o primeiro arquivo**, inclusive todas as funcionalidades que já existem nos scripts. Leia em ordem e implemente uma etapa antes de avançar. Os arquivos `mesh_eval_pipeline.py` e `percept_eval_pipeline.py` são referências do resultado esperado, não pré-requisitos para seguir o tutorial.

![Visão geral](images/pipeline.svg)

## Roteiro de construção

1. [Preparar o projeto e instalar bibliotecas](step-by-step/01-preparacao-ambiente.md)
2. [Criar os arquivos, CLI e diretórios](step-by-step/02-arquitetura-implementacao.md)
3. [Importar e normalizar as malhas](step-by-step/03-malhas-normalizacao.md)
4. [Implementar correspondência e alinhamento ICP](step-by-step/04-alinhamento-icp.md)
5. [Implementar MSE e RMSE](step-by-step/05-mse-rmse.md)
6. [Implementar Chamfer e Hausdorff](step-by-step/06-chamfer-hausdorff.md)
7. [Implementar câmera, renders e heatmap](step-by-step/07-renderizacao-heatmaps.md)
8. [Implementar renderização multivista, LPIPS, PSNR e SSIM](step-by-step/08-metricas-perceptuais.md)
9. [Salvar CSVs, exportar PLY e validar](step-by-step/09-relatorios-validacao.md)
10. [Testar limitações e planejar evolução](step-by-step/10-limitacoes-evolucao.md)

**Convenção:** GT é a malha de referência; RM é a malha a avaliar. As métricas geométricas atuais usam vizinhos mais próximos **entre vértices**. Cada etapa mostra o que criar, como implementar e como testar; não é uma lista de funcionalidades prontas.
