# 01 — Preparar o projeto e instalar as dependências

> **Status: parcialmente concluída.** Ambiente local criado com Python 3.12.15 e instalação das dependências concluída, conforme saída do terminal informada em 17/10/2026. Ainda faltam validar as importações, executar os pipelines e registrar um ambiente reproduzível.

Este passo prepara o ambiente para executar e validar os pipelines que já existem no repositório.

![Esquema da etapa](../images/pipeline.svg)

## Passo 1 — Preparar o ambiente do projeto existente

No Windows 64 bits, use o Miniconda3 e abra o **Anaconda Prompt** na raiz da cópia local do repositório. O ambiente registrado usa Conda **25.11.1**; essa é a versão observada, não um requisito obrigatório.

Execute cada bloco separadamente. Copie somente os comandos, sem URLs, textos explicativos ou o prefixo do terminal.

```bat
conda create -n meshEval python=3.12.15
```

Quando aparecer `Proceed ([y]/n)?`, digite apenas `y` e pressione Enter. Aguarde a instalação terminar e o prompt retornar antes de executar:

```bat
conda activate meshEval
python --version
```

O início da linha deve mostrar `(meshEval)`. A versão confirmada neste ambiente foi **Python 3.12.15**. Se o ambiente já existe, basta ativá-lo; não é necessário criá-lo novamente.

## Passo 2 — Instalar as dependências

Com o ambiente ativo:

```bat
python -m pip install numpy pandas trimesh pyrender open3d matplotlib imageio scipy scikit-image torch torchvision lpips
```

### Versões registradas em 17/10/2026

| Tecnologia | Versão instalada informada |
| --- | --- |
| Python | 3.12.15 |
| Conda | 25.11.1 |
| NumPy | 2.5.4 |
| pandas | 3.0.6 |
| Trimesh | 5.1.1 |
| pyrender | 0.1.45 |
| Open3D | 0.20.0 |
| Matplotlib | 3.11.2 |
| imageio | 2.38.1 |
| SciPy | 1.18.1 |
| scikit-image | 0.26.0 |
| PyTorch (torch) | 2.14.1 |
| torchvision | 0.29.1 |
| LPIPS | 0.1.4 |
| PyOpenGL | 3.1.0 |
| pyglet | 2.1.19 |
| Pillow | 13.0.0 |

O pip informou `Successfully installed`. Isso confirma a instalação relatada, mas ainda não comprova compatibilidade em execução, renderização ou aceleração CUDA. Essas versões não identificam o ambiente que gerou os resultados já existentes no repositório. O comando acima não fixa versões e poderá instalar versões diferentes no futuro.

## Passo 3 — Conferir o ambiente e executar os scripts

Primeiro, confira as importações:

```bat
python -c "import numpy, pandas, trimesh, pyrender, open3d, matplotlib, imageio, scipy, skimage, torch, torchvision, lpips; print('OK: bibliotecas carregadas')"
```

Se o teste terminar sem erro, execute a avaliação geométrica:

```bat
python mesh_eval_pipeline.py --gt gt.stl --rm mod.stl --out output
```

Após verificar esse resultado, execute a avaliação perceptual:

```bat
python percept_eval_pipeline.py --gt gt.stl --rm mod.stl --out output
```

O repositório já contém `gt.stl` e `mod.stl` para execução de exemplo. Os comandos podem substituir arquivos existentes em `output/`. Para modelos FBX, converta antes para um formato aceito pelo Trimesh. O renderizador offscreen pode exigir configuração gráfica específica do sistema.

### Validação pendente

- [x] Ambiente Conda criado e ativado, conforme terminal informado.
- [x] Python 3.12.15 confirmado.
- [x] Instalação das dependências concluída, conforme saída do pip.
- [ ] Importações verificadas sem erro.
- [ ] Pipeline geométrico executado e resultados conferidos neste ambiente.
- [ ] Pipeline perceptual executado e resultados conferidos neste ambiente.
- [ ] Disponibilidade de CUDA verificada, caso se pretenda usar GPU.
- [ ] Dependências registradas em arquivo reproduzível após a validação.

## Passo 4 — Próxima etapa

Continue para [02 — Conferir os programas e a interface de linha de comando](02-arquitetura-implementacao.md).

**Código de referência:** [pipeline geométrico](../../../mesh_eval_pipeline.py) e [pipeline perceptual](../../../percept_eval_pipeline.py). Os scripts já existem; esta etapa registra a preparação e a validação do ambiente local.
