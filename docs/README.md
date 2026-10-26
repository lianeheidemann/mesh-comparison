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
| `analysis/` | Verificação das GTs (`gt_check.py`), estudos de validação (`robustness.py`: perturbações, baseline por vértice, linhas de invariância e sensibilidade, dispersão de amostragem, recuperação de transformações pelo ICP) e gráficos (`plots.py`, inclusive o da sensibilidade) |
| `datasets/` | Manifesto das GTs (`manifest.py`: colunas, arquivos de malha, problemas de cada linha) e download do Google Scanned Objects pelo Gazebo Fuel (`gso.py`) |
| `cli/` | Linhas de comando finas (argumentos, chamadas e impressão), uma por ferramenta: `check_gt`, `fetch_gso`, `plot_metrics`, `robustness_study`, `icp_study` |
| `gui/` | Janela, painéis, configuração (`RunConfig`), execução em subprocesso, leitura das saídas (`outputs.py`, `gallery.py`); resultados: abas (`results_view.py`), tabelas (`result_tables.py`) e galeria (`image_gallery.py`); visualizador PyVistaQt (`viewer3d.py`), sua barra de controles (`viewer_toolbar.py`) e a geometria de câmera, limites e chão sem Qt (`view_geometry.py`) |

Cada ferramenta de `cli/` é instalada como comando `mesh-*` (`mesh-check-gt`, `mesh-fetch-gso`, `mesh-plot-metrics`, `mesh-robustness-study`, `mesh-icp-study`) e também roda como `python scripts/<nome>.py`, um atalho de poucas linhas. Ferramentas: `fetch_gso.py` (baixa a seleção do GSO e escreve o manifesto), `check_gt.py` (verificação das GTs), `plot_metrics.py` (regenera as figuras de uma execução; `--uncertainty` acrescenta a dispersão de amostragem), `robustness_study.py` (estudo de robustez) e `icp_study.py` (validação do ICP).
