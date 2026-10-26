# ADR 0003 — Padrão único de métricas e fim dos contratos científicos

- **Estado:** aceito pela pessoa responsável pelo projeto (26/10/2026). Substitui em parte os ADRs [0001](0001-evaluation-v2.md) e [0002](0002-robustness-study.md): as definições das métricas continuam as mesmas, mas deixam de ser calculadas "ao lado do legado".

## Contexto

Os ADRs 0001 e 0002 criaram as métricas sobre amostras de superfície ao lado das métricas herdadas do código original (ThiagoFigueiroRibeiro/MeshComparison), protegidas por "contratos científicos". A pessoa responsável decidiu que preservar o comportamento do código original deixa de ser uma restrição, e que manter dois conjuntos de métricas complica o código, as saídas e a interpretação.

## Decisão

1. **Um único conjunto de métricas.** Ficam as métricas sobre amostras de superfície: Chamfer, HD95, F@τ, curva F(τ)/AUC-F, normal consistency, regiões visível/oculta e `icp_scale`.
   - **Removidas:** as métricas por vértice (Chamfer, Hausdorff e RMSE entre vértices) e o PSNR com divisão por `N`.
   - **Novo nome:** `psnr` passa a ser o PSNR padrão (divisão por `3N`).
2. **Pré-alinhamento e ICP sobre amostras.**
   - O MSE simétrico que decide o ICP (limiar `1e-4`) é calculado sobre as amostras de superfície (100 000 por malha, sementes `0`/`1`).
   - O ICP de similaridade recebe essas amostras em vez dos vértices.
3. **Heatmap.** A cor de cada vértice da GT é a distância até a superfície amostrada da RM alinhada. O topo da escala (P95) é gravado no CSV (`heatmap_vmax_gt_units`) e lido pela GUI.
4. **Saídas.**
   - `metrics/metrics_geometry.csv` traz uma linha por região, com as configurações da execução repetidas em cada linha.
   - `metrics/fscore_curve.csv` traz a curva F(τ).
   - Os arquivos `_v2`, a coluna `protocol` e a coluna/linha `psnr_standard` deixam de existir.
5. **Documentação.** O documento de contratos científicos foi removido, assim como as regras de preservação do `AGENTS.md`. As mudanças futuras de métricas são registradas em ADRs.

## Consequências

- No par de exemplo (`data/samples`), CD, HD95, F@τ, AUC-F, normal consistency e a curva F(τ) são **idênticos** aos valores do protocolo v2 (diferença 0). O MSE pré-alinhamento passou de 7,30e-5 (vértices) para 6,95e-5 (amostras); como continua abaixo do limiar, o ICP segue não acionado. O PSNR é idêntico ao antigo `psnr_standard`.
- Em pares em que o ICP é acionado, o alinhamento pode mudar um pouco, porque o ICP passa a usar amostras uniformes por área.
- Os resultados em `examples/output/` foram gerados pela versão anterior e **não** são comparáveis com as saídas atuais; ficam como registro histórico.
- O estudo de robustez mantém um **baseline por vértice** (`analysis/robustness.py:vertex_baseline`), só para comparação.

## Rollback

Reverter os commits deste ADR no branch `evaluation-v2`.
