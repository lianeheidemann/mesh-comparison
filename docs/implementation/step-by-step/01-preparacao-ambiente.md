# 01 — Preparar o projeto e instalar as dependências

> **Objetivo:** implementar esta parte desde o zero, mesmo que ela já exista nos scripts de referência.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — O que criar

Crie uma pasta `mesh-comparison`, abra um terminal nela e crie um ambiente Conda Python 3.12.

## Passo 2 — Implementação inicial

```bash
# Cria e ativa o ambiente isolado
conda create -n meshEval python=3.12
conda activate meshEval
pip install numpy pandas trimesh pyrender open3d matplotlib imageio scipy scikit-image torch torchvision lpips
```

## Passo 3 — Completar, executar e validar

Confirme `python -c "import trimesh, open3d, scipy, pyrender; print('OK')"`. Coloque dois arquivos de teste `gt.stl` e `mod.stl` na raiz. Para modelos FBX, converta antes para um formato aceito pelo Trimesh. O renderizador offscreen pode exigir configuração gráfica específica do sistema.

## Passo 4 — Próxima etapa

Continue para [02 — Criar os programas e a interface de linha de comando](02-arquitetura-implementacao.md).

**Código de referência:** [pipeline geométrico](../../../mesh_eval_pipeline.py) e [pipeline perceptual](../../../percept_eval_pipeline.py). As amostras acima mostram etapas de construção; consulte as funções completas nos scripts quando houver utilitários auxiliares.
