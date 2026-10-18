# 02 — Arquitetura atual, CLI e diretórios de saída

> **Status: implementado no código.** A branch atual organiza processamento e GUI em um pacote Python, não em scripts independentes na raiz.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — Identificar os módulos reais

| Local | Função |
| --- | --- |
| [`common/io.py`](../../../src/meshcomparison/common/io.py) | Carrega malhas com Trimesh, rejeita FBX e cria pastas de saída |
| [`common/alignment.py`](../../../src/meshcomparison/common/alignment.py) | ICP com escala uniforme via Open3D |
| [`common/device.py`](../../../src/meshcomparison/common/device.py) | Identifica CPU/CUDA para LPIPS |
| [`geometry/cli.py`](../../../src/meshcomparison/geometry/cli.py) | Argumentos para o pipeline geométrico |
| [`geometry/pipeline.py`](../../../src/meshcomparison/geometry/pipeline.py) | Métricas, renderizações, heatmap e exportação |
| [`perceptual/cli.py`](../../../src/meshcomparison/perceptual/cli.py) | Argumentos para o pipeline perceptual |
| [`perceptual/pipeline.py`](../../../src/meshcomparison/perceptual/pipeline.py) | Renderização multivista, LPIPS/PSNR/SSIM e relatórios |
| [`gui/`](../../../src/meshcomparison/gui/) | Desktop Qt/PyVista e execução em subprocessos |

As dependências e os comandos registrados pelo pacote estão em [`pyproject.toml`](../../../pyproject.toml).

## Passo 2 — Entender o código de preparação das saídas

Os módulos chamam a função **`ensure_dirs(base_out, subdirs)`**, compartilhada em `common/io.py`, com conjuntos diferentes de subpastas conforme o pipeline. Este exemplo é didático, mas corresponde à assinatura usada:

```python
# Demonstra como o módulo compartilhado cria diretórios de saída
from meshcomparison.common.io import ensure_dirs

paths = ensure_dirs("output", {
    "renders": ("renders",),
    "metrics": ("metrics",),
    "aligned": ("aligned",),
    "heatmaps": ("heatmaps",),
})
```

O pipeline perceptual também cria `renders/gt`, `renders/rm` e `renders/pairs`. O diretório de saída é passado pelo parâmetro `--out` e **não é fixo no código**.

## Passo 3 — Instalar o pacote e verificar as CLIs

```bat
conda activate meshEval
python -m pip install -e . --no-deps
python -m meshcomparison.geometry --help
python -m meshcomparison.perceptual --help
```

Executar o pipeline geométrico com arquivos de exemplo:

```bat
python -m meshcomparison.geometry --gt data/samples/gt.stl --rm data/samples/mod.stl --out output/geometry-check
```

O pacote também define `mesh-eval`, `percept-eval` e `mesh-gui` (ou `python -m meshcomparison.gui`). Consulte os comandos detalhados no [README principal](../../../README.md).

## Passo 4 — Distinguir processamento e interface

A GUI usa [`config.py`](../../../src/meshcomparison/gui/config.py) para preparar argumentos e [`runner.py`](../../../src/meshcomparison/gui/runner.py) para iniciar processos filhos. A visualização utiliza PyVistaQt em [`viewer3d.py`](../../../src/meshcomparison/gui/viewer3d.py). Nenhuma dessas camadas altera por si só os cálculos científicos dos pipelines.

Os scripts em `scripts/` chamam os módulos usando as malhas em `data/samples/`. Os resultados locais padrão ficam em `output/`; os exemplos versionados em `examples/output/` são **um registro histórico**.

**Próximo passo:** [03 — Carregamento e normalização](03-malhas-normalizacao.md) · [Guia desktop](../../gui/README.md).
