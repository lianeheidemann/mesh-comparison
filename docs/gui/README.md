# Interface desktop — PySide6 + PyVistaQt

> **Estado:** interface **implementada no código** da branch `harness-documentation-and-new-interface`. Este documento foi conferido contra os módulos `src/meshcomparison/gui/`; **não** representa um teste executado da janela num computador local.

A GUI permite escolher a **malha de referência (GT)** e a **malha reconstruída (RM)**, configurar parâmetros dos pipelines, visualizar modelos 3D e consultar os resultados CSV/PNG. Usa **PySide6** para a aplicação desktop, **PyVista + PyVistaQt (VTK)** para o viewer e executa os scripts científicos em **processos Python separados**, via `QProcess`.

## 1. Instalar e abrir

No Windows, abra o **Anaconda Prompt** na pasta do projeto (a pasta que contém `pyproject.toml`). Se ainda não tiver o ambiente, crie-o uma vez:

```bat
conda env create -f environments/environment.yml
```

Ative o ambiente e instale o projeto:

```bat
conda activate meshEval
python -m pip install -e . --no-deps
```

Se aparecer `prefix already exists`, o ambiente já existe: pule a criação e execute os dois comandos acima. O arquivo `environment.yml` inclui os pacotes da interface. Como `--no-deps` não instala dependências, um ambiente antigo pode precisar dos pacotes gráficos:

```bat
python -m pip install PySide6 pyvista pyvistaqt
```

Abra a interface:

```bat
mesh-gui
```

Se `mesh-gui` não for reconhecido, use `python -m meshcomparison.gui`. Se aparecer `No module named 'PySide6'`, instale os pacotes gráficos com o comando acima. A interface precisa de uma sessão desktop; não abre em um terminal sem ambiente gráfico.

## 2. Escolher arquivos e formatos

Na lateral **Meshes**, selecione GT e RM, e escolha a pasta de saída. A interface anuncia **STL, OBJ, PLY, OFF, GLB/GLTF**. O carregamento usa [`trimesh`](../../src/meshcomparison/common/io.py), que aceita formatos conforme a versão e as dependências instaladas; **nem todo arquivo com uma dessas extensões é garantido**. Teste com malhas válidas.

**FBX não é suportado diretamente.** Converta para STL, OBJ ou PLY (ou outro formato testado) antes de executar. A GUI também valida existência dos caminhos, a seleção de pelo menos um pipeline e algumas opções numéricas.

Os arquivos de demonstração são [`data/samples/gt.stl`](../../data/samples/gt.stl) e [`data/samples/mod.stl`](../../data/samples/mod.stl). Escolha **uma pasta de saída nova** ao comparar experimentos; a ferramenta pode sobrescrever arquivos com nomes iguais.

## 3. Executar as análises

| Controle | Função |
| --- | --- |
| **Geometric** | Chamfer, Hausdorff, RMSE, renderizações e heatmap |
| **Perceptual** | LPIPS, PSNR e SSIM em várias vistas |
| **MSE threshold (ICP)** | Limiar normalizado que decide se o alinhamento ICP é acionado |
| **Azimuth / Elevation** | Orientação de câmera (azimute para o pipeline geométrico; elevação) |
| **Render width / height** | Resolução das imagens geradas |
| **Views (perceptual)** | Número de perspectivas avaliadas |
| **Camera margin / radius factor** | Enquadramento da câmera perceptual |
| **Compute device (LPIPS)** | `auto` prefere CUDA se PyTorch disponibilizar, `cuda` exige CUDA, `cpu` força CPU |

Clique em **Run evaluation**. A aba *Log* mostra a saída dos processos e a interface apresenta a estimativa de progresso. **Cancel** encerra a execução em andamento; podem permanecer arquivos parciais na pasta de saída. Selecionar ambos os pipelines significa duas execuções sequenciais, não avaliação distribuída/paralela.

### GPU e CUDA

Somente a parte de inferência de **LPIPS** escolhe CPU/CUDA. A GPU **não** acelera automaticamente o pipeline geométrico nem transforma o renderer OpenGL em um pipeline CUDA. A interface detecta a configuração de PyTorch e exibe avisos, mas testes com *mock* de GPU não comprovam execução CUDA num notebook real.

Para conferir a instalação:

```bat
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
```

Consulte o [seletor oficial do PyTorch](https://pytorch.org/get-started/locally/) para a instalação compatível com o driver; evite copiar um índice de CUDA sem verificar suporte.

## 4. Visualizar os modelos e resultados

Na aba **3D view**, o [`MeshViewer`](../../src/meshcomparison/gui/viewer3d.py) disponibiliza:

- Camadas independentes para **GT**, **RM alinhada** e **heatmap de desvio** (quando disponível).
- Rotação, pan e zoom da câmera, com opção **Reset view**.
- Controle da opacidade da RM e alternância de linhas das arestas (**Edges**).
- **Save image…** para salvar uma captura PNG do viewer.
- Sobreposição de camadas no mesmo viewer. **Não há, no código atual, três viewports independentes com câmeras sincronizadas**; não confundir com visualização lado a lado.

A aba **Results** usa [`ResultsView`](../../src/meshcomparison/gui/results_view.py) para carregar os CSVs produzidos e a galeria de PNGs. A aba **Log** mostra a execução. O menu **View → Dark theme** alterna o tema da aplicação Qt. *Esse controle de tema não é a mesma coisa que as duas imagens claro/escuro no README do GitHub.*

### Saídas esperadas

```text
output/
├── aligned/rm_aligned.ply
├── heatmaps/gt_heatmap_colored.ply
├── heatmaps/gt_heatmap_ortho.png
├── metrics/metrics_geometry.csv
├── metrics/metrics_perceptual.csv
├── metrics/per_view_metrics.csv
├── metrics/run_metadata.csv
└── renders/
    ├── gt_ortho.png
    ├── rm_aligned_ortho.png
    ├── gt/
    ├── rm/
    └── pairs/
```

Algumas pastas só aparecem quando o respectivo pipeline é executado. Ambos os pipelines podem gravar `aligned/rm_aligned.ply` no **mesmo diretório**; use pastas separadas quando precisar preservar resultados distintos. Os exemplos commitados estão em [`examples/output/`](../../examples/output/), e não são atualizados pela GUI automaticamente.

## 5. Limites e testes

O projeto já tem [testes de lógica Qt-free](../../tests/test_gui_config.py) para validação, construção de comandos e progresso, mas **ainda é necessário comprovar manualmente ou automatizar** a inicialização da janela, interação 3D, cancelamento, carregamento real de arquivos e alternância de tema em sistemas suportados.

Checklist de validação:

- [ ] A interface abre e carrega GT/RM de exemplo num sistema com Qt/VTK.
- [ ] Preview 3D, opacidade, arestas, câmera e screenshot funcionam.
- [ ] Cada pipeline executa e permite visualizar suas saídas.
- [ ] Um cancelamento intencional não corrompe entradas nem resultados de referência.
- [ ] Erros de entrada e de renderização são reportados sem sucesso falso.
- [ ] O status da GPU/CPU observado bate com `torch.cuda.is_available()`.

Consulte a [instalação](../implementation/step-by-step/01-preparacao-ambiente.md), o [roteiro completo de validação no Windows](../../README.md#validate-on-windows) (incluindo CUDA e comparação com os CSVs de exemplo), os [testes pendentes](../implementation/step-by-step/10-limitacoes-evolucao.md) e o [README do projeto](../../README.md).
