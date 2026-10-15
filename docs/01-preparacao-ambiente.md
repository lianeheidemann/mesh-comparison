# 01 — Preparação do ambiente

## Objetivo
Reproduzir os comandos do [README principal](../README.md) em Windows com Conda. O repositório contém dois programas Python independentes e dois inicializadores `.bat`.

## Etapas
1. Instalar Python/Conda e criar o ambiente `meshEval` com Python 3.12.
2. Instalar bibliotecas numéricas, geométricas, renderização e aprendizado profundo.
3. Manter `gt.stl` e `mod.stl` na raiz ou usar caminhos próprios.
4. Rodar primeiro o pipeline geométrico e inspecionar o CSV; depois o perceptual.

```powershell
# Cria e ativa um ambiente isolado para a avaliação
conda create -n meshEval python=3.12
conda activate meshEval
pip install numpy pandas trimesh pyrender open3d matplotlib imageio scipy scikit-image torch torchvision lpips
```

```powershell
# Executa as avaliações a partir da raiz do repositório
python mesh_eval_pipeline.py --gt gt.stl --rm mod.stl --out output
python percept_eval_pipeline.py --gt gt.stl --rm mod.stl --out output
```

**GPU:** `percept_eval_pipeline.py` escolhe CUDA quando disponível e CPU como alternativa. Para CUDA, conferir [instalação oficial do PyTorch](https://pytorch.org/get-started/locally/). Os renderizadores `pyrender.OffscreenRenderer` dependem de configuração gráfica OpenGL/EGL/OSMesa compatível com o sistema.

**FBX:** os scripts rejeitam `.fbx` explicitamente. Converter a geometria para STL, PLY ou OBJ em um aplicativo externo e conferir escala, orientação e partes antes de avaliar. STL não retém materiais nem textura.

**Verificação:** o programa deve criar `output/metrics/mesh_metrics.csv`. Em execução perceptual, deve criar `per_view_metrics.csv`, `metric_summary.csv` e `run_metadata.csv`. O nome do ambiente é relevante aos `.bat` existentes; a execução direta por Python usa o ambiente ativo.
