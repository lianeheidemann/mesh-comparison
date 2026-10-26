# Documentação — Mesh Comparison

| Documento | Conteúdo |
| --- | --- |
| [README principal](../README.md) | Visão geral, métricas, instalação, uso, saídas e limitações |
| [ADRs](adr/) | Definição e justificativa das métricas: [0001](adr/0001-evaluation-v2.md) amostras de superfície, [0002](adr/0002-robustness-study.md) normal consistency, F(τ) e estudo de robustez, [0003](adr/0003-single-metric-standard.md) padrão único, [0004](adr/0004-point-to-surface.md) distâncias ponto-superfície, [0005](adr/0005-icp-global-start.md) inicialização global do ICP |
| [Implementação e validação](implementation/README.md) | Testes existentes e validação pendente |
| [Escolha das GTs](gt/README.md) | Como escolher e limpar malhas de referência sem contaminação do treino; manifesto e verificador |
| [Resultados de exemplo](results/README.md) | Métricas e gráficos do par de exemplo |
| [Estudo de robustez](results/robustness/README.md) | Invariância à triangulação e sensibilidade das métricas; roteiro do artigo |
| [Validação do ICP](results/icp/README.md) | Recuperação de rotação, escala e translação conhecidas, antes e depois da inicialização global |
| [Agent Harness](harness/README.md) | Desenvolvimento assistido por agentes: estado, fluxo e referências |
| [Artigo e referências](https://github.com/lianeheidemann/mesh-comparison-article) | Repositório privado `mesh-comparison-article` |

## Arquitetura

```mermaid
flowchart LR
    IN["GT + RM"] --> PREP["Preparação: normalização pela diagonal da GT, amostragem de superfície, ICP condicional"]
    GUI["GUI PySide6 → worker por pipeline"] --> PREP
    PREP --> GEO["Geometria: Chamfer, HD95, F-score, AUC-F, normal consistency, regiões visível/oculta, heatmap"]
    PREP --> PER["Percepção: renderizações multivista, LPIPS, PSNR, SSIM"]
    GEO --> OUT["CSV · PLY · PNG · figuras"]
    PER --> OUT
    OUT --> VIEW["GUI: visualizador 3D, tabelas, imagens e figuras"]
    OUT --> FIG["scripts/plot_metrics.py: regenera as figuras e a dispersão de amostragem"]
```

## Módulos (`src/meshcomparison/`)

| Pacote | Responsabilidade |
| --- | --- |
| `common/` | Leitura de malhas e cenas (`io.py`: só malhas triangulares entram; câmeras, luzes e linhas ficam de fora e são listadas), amostragem de superfície (`sampling.py`), distâncias (`distances.py`: KD-tree e ponto-superfície via Open3D), preparo compartilhado (`prepare.py`: normalização, MSE ponto-superfície, ICP sobre amostras, exportação), transformações, renderização, dispositivo do LPIPS |
| `geometry/` | Métricas (`metrics.py`), visibilidade pela vista de entrada (`visibility.py`), heatmap, renderização e pipeline |
| `perceptual/` | Câmeras, máscaras e crop, LPIPS/PSNR/SSIM e pipeline multivista |
| `analysis/` | Verificação das GTs (`gt_check.py`), estudos de validação (`robustness.py`: perturbações, baseline por vértice, dispersão de amostragem, recuperação de transformações pelo ICP) e gráficos (`plots.py`) |
| `gui/` | Janela, painéis, configuração (`RunConfig`), execução em subprocesso, leitura das saídas (`outputs.py`, `gallery.py`), abas de resultados (`results_view.py`: tabelas, imagens, figuras) e visualizador PyVistaQt |

Scripts em `scripts/`: `fetch_gso.py` (baixa a seleção do GSO e escreve o manifesto), `check_gt.py` (verificação das GTs), `plot_metrics.py` (regenera as figuras de uma execução; `--uncertainty` acrescenta a dispersão de amostragem), `robustness_study.py` (estudo de robustez) e `icp_study.py` (validação do ICP).
