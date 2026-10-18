# Documentação — Mesh Comparison

Esta é a navegação da documentação para a **branch `harness-documentation-and-new-interface`**, cujo código está organizado como pacote Python em `src/meshcomparison/`. Os exemplos de resultados são um registro anterior; mudanças recentes na estrutura do projeto não equivalem a uma nova execução validada.

| Área | Conteúdo | Quando consultar |
| --- | --- | --- |
| [Avaliação de malhas 3D](avaliacao-geometrica/README.md) | Conceitos, métricas geométricas e perceptuais, aplicações e limitações | Antes de interpretar métricas |
| [Implementação e evolução](implementation/README.md) | Estrutura modular, fluxo dos pipelines e tutoriais passo a passo | Ao estudar ou alterar o código |
| [Interface desktop](gui/README.md) | Instalação, execução e controles da GUI PySide6/PyVistaQt | Para inspecionar GT, RM, heatmap e relatórios |
| [Resultados de exemplo](results/README.md) | Métricas e imagens de uma execução previamente registrada | Para consultar um conjunto específico de resultados |
| [Agent Harness](harness/README.md) | Estado do desenvolvimento assistido por agentes, guardrails e roteiro reutilizável | Para organizar futuras implementações via LLM |
| [Referências sobre Harness](harness/REFERENCIAS.md) | Fontes oficiais e materiais complementares | Para fundamentar decisões e arquitetura |

## Entrada rápida para a versão atual

O pacote em `src/meshcomparison/` está dividido em:

- **`common/`** — carregamento de malhas, normalização/transformações, distâncias, ICP, renderização e escolha do dispositivo para LPIPS.
- **`geometry/`** — métricas geométricas, heatmap e pipeline.
- **`perceptual/`** — câmeras, imagens, LPIPS/PSNR/SSIM e pipeline multivista.
- **`gui/`** — interface Qt com visualizador PyVistaQt, painel de configuração, relatórios e execução em subprocessos.

Depois de preparar `meshEval` e instalar o pacote em modo editável, os comandos são:

```bash
python -m meshcomparison.geometry --help
python -m meshcomparison.perceptual --help
python -m meshcomparison.gui
```

O terceiro comando inicia uma **janela desktop** (requer PySide6/PyVista/PyVistaQt e ambiente com interface gráfica). Veja a [instalação detalhada](implementation/step-by-step/01-preparacao-ambiente.md). O CI atual executa `ruff check .`, `pytest -q` e os dois `--help`; ele não testa a janela interativa nem executa os pipelines completos com renderização.

**Convenção de status:** “implementado no código” não significa “validado em todos os ambientes”. Recursos de GUI, GPU e renderização gráfica precisam de testes próprios antes de se declarar suporte comprovado.

**Para validar no Windows:** siga a seção [Validate on Windows](../README.md#validate-on-windows) do README inicial para CUDA/PyTorch, `mesh-gui` e comparação dos CSVs dos dois pipelines. Utilize diretórios separados para as saídas de cada pipeline.
