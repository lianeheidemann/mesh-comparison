# 01 — Preparar o projeto e instalar as dependências

> **Status: parcialmente concluída.** As instruções de instalação estão documentadas, mas ainda falta registrar as dependências em um arquivo reproduzível. Os scripts de avaliação já existem.

Este passo prepara o ambiente para executar e validar os pipelines que já existem no repositório.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — Preparar o ambiente do projeto existente

Na cópia local do repositório, abra um terminal na raiz do projeto e crie um ambiente Conda com Python 3.12.

## Passo 2 — Instalar as dependências

```bash
# Cria e ativa o ambiente isolado
conda create -n meshEval python=3.12
conda activate meshEval
pip install numpy pandas trimesh pyrender open3d matplotlib imageio scipy scikit-image torch torchvision lpips
```

## Passo 3 — Conferir o ambiente e executar os scripts

Confirme `python -c "import trimesh, open3d, scipy, pyrender; print('OK')"`. O repositório já contém `gt.stl` e `mod.stl` para execução de exemplo. Para modelos FBX, converta antes para um formato aceito pelo Trimesh. O renderizador offscreen pode exigir configuração gráfica específica do sistema.

## Passo 4 — Próxima etapa

Continue para [02 — Conferir os programas e a interface de linha de comando](02-arquitetura-implementacao.md).

**Código de referência:** [pipeline geométrico](../../../mesh_eval_pipeline.py) e [pipeline perceptual](../../../percept_eval_pipeline.py). A instalação é uma orientação documentada; ainda falta incluir um arquivo de dependências reproduzível. Os trechos de código são exemplos, enquanto os scripts são a implementação completa.
