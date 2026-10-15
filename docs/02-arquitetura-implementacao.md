# 02 — Criar os programas e a interface de linha de comando

> **Objetivo:** implementar esta parte desde o zero, mesmo que ela já exista nos scripts de referência.

![Esquema da etapa](images/pipeline.svg)

## Passo 1 — O que criar

Crie `mesh_eval_pipeline.py` e `percept_eval_pipeline.py`. Em ambos, implemente primeiro a leitura de argumentos e a criação das pastas de saída.

## Passo 2 — Implementação inicial

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

## Passo 3 — Completar, executar e validar

Execute `python mesh_eval_pipeline.py --gt gt.stl --rm mod.stl --out output` e verifique se as quatro pastas foram criadas. Depois acrescente `run_pipeline(...)` e as opções de alinhamento e câmera. O script perceptual terá também subpastas `renders/gt`, `renders/rm` e `renders/pairs`.

## Passo 4 — Próxima etapa

Continue para [03 — Importar e normalizar duas malhas](03-malhas-normalizacao.md).

**Código de referência:** [pipeline geométrico](../mesh_eval_pipeline.py) e [pipeline perceptual](../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
