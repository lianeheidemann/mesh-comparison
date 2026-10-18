# 02 — Conferir os programas e a interface de linha de comando

> **Status: concluída.** Os dois pipelines, suas interfaces de linha de comando e a criação das pastas de saída já estão implementados.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — Conferir a arquitetura existente

Os pacotes `src/meshcomparison/geometry/` e `src/meshcomparison/perceptual/` já existem (módulos `cli.py` e `pipeline.py`, com utilitários compartilhados em `src/meshcomparison/common/`). Confira neles a leitura de argumentos, a criação das pastas e a função `run_pipeline`.

## Passo 2 — Trecho da implementação atual

```python
# Lê os caminhos de entrada e prepara as pastas do experimento
import argparse
from pathlib import Path

def ensure_dirs(base_out):
    paths = {name: Path(base_out) / name for name in ('renders', 'heatmaps', 'metrics', 'aligned')}
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths

parser = argparse.ArgumentParser()
parser.add_argument('--gt', required=True)
parser.add_argument('--rm', required=True)
parser.add_argument('--out', default='output')
args = parser.parse_args()
paths = ensure_dirs(args.out)
```

## Passo 3 — Executar e conferir

Execute `python -m meshcomparison.geometry --gt data/samples/gt.stl --rm data/samples/mod.stl --out output` e confira os arquivos gerados. A função `run_pipeline(...)`, as opções de alinhamento e câmera e as pastas específicas do fluxo perceptual já estão implementadas; não é necessário adicioná-las novamente.

## Passo 4 — Próxima etapa

Continue para [03 — Conferir o carregamento e a normalização das malhas](03-malhas-normalizacao.md).

**Código de referência:** [pipeline geométrico](../../../src/meshcomparison/geometry/pipeline.py) e [pipeline perceptual](../../../src/meshcomparison/perceptual/pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
