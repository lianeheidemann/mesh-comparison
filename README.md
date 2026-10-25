<p align="center">
  <img src="docs/assets/mesh-comparison-logo.svg" width="180" alt="Mesh Comparison logo">
</p>

<h1 align="center">Mesh Comparison: Mesh Evaluation</h1>

<p align="center">
  <a href="https://github.com/lianeheidemann/mesh-comparison/actions/workflows/ci.yml">
    <img
      src="https://img.shields.io/github/actions/workflow/status/lianeheidemann/mesh-comparison/ci.yml?branch=main&style=flat-square&logo=githubactions&logoColor=white&label=CI%20%2F%20Build&labelColor=315f7d"
      alt="CI Build Status"
    />
  </a>
</p>

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Python-3B4A5A?style=flat-square&logo=python&logoColor=white"><img src="https://img.shields.io/badge/Python-61778E?style=flat-square&logo=python&logoColor=white" alt="Python"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/NumPy-3B4A5A?style=flat-square&logo=numpy&logoColor=white"><img src="https://img.shields.io/badge/NumPy-61778E?style=flat-square&logo=numpy&logoColor=white" alt="NumPy"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Trimesh-3B4A5A?style=flat-square"><img src="https://img.shields.io/badge/Trimesh-61778E?style=flat-square" alt="Trimesh"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Open3D-3B4A5A?style=flat-square"><img src="https://img.shields.io/badge/Open3D-61778E?style=flat-square" alt="Open3D"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/PyTorch-3B4A5A?style=flat-square&logo=pytorch&logoColor=white"><img src="https://img.shields.io/badge/PyTorch-61778E?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/LPIPS-3B4A5A?style=flat-square"><img src="https://img.shields.io/badge/LPIPS-61778E?style=flat-square" alt="LPIPS"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/PySide6-3B4A5A?style=flat-square"><img src="https://img.shields.io/badge/PySide6-61778E?style=flat-square" alt="PySide6"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/PyVista-3B4A5A?style=flat-square"><img src="https://img.shields.io/badge/PyVista-61778E?style=flat-square" alt="PyVista"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/PyVistaQt-3B4A5A?style=flat-square"><img src="https://img.shields.io/badge/PyVistaQt-61778E?style=flat-square" alt="PyVistaQt"></picture>
</p>

Mesh Comparison is a **Python desktop application** for comparing a ground-truth mesh (GT) with a reconstructed mesh (RM). Its interface provides 3D visualization, geometric deviation metrics, heatmaps, and perceptual comparison across multiple camera views. It evaluates **one GT/RM pair per run**.

<p align="center">
  <img src="assets/interface/evaluate-meshe-preview-v1.webp">
</p>

### Table of contents

- [Evaluation criteria](#user-content-evaluation-criteria)
- [Example results](#user-content-example-results)
  - [Geometric metric snapshot](#user-content-geometric-metric-snapshot)
  - [Perceptual summary — desktop screenshot](#user-content-perceptual-summary--desktop-screenshot)
- [Technologies](#user-content-technologies)
- [Workspace layout](#user-content-workspace-layout)
- [Requirements](#user-content-requirements)
- [Installation](#user-content-installation)
- [Run](#user-content-run)
  - [Desktop interface](#user-content-desktop-interface)
- [Validate on Windows](#user-content-validate-on-windows)
- [Pipelines](#user-content-pipelines)
  - [Geometric evaluation](#user-content-geometric-evaluation)
  - [Perceptual evaluation](#user-content-perceptual-evaluation)
- [Parameters](#user-content-parameters)
- [Scope and limitations](#user-content-scope-and-limitations)
- [Development](#user-content-development)
  - [Agent Harness for Scientific Integrity](#user-content-agent-harness-for-scientific-integrity)
- [Troubleshooting](#user-content-troubleshooting)
- [Interface](#user-content-interface)
- [License and credits](#user-content-license-and-credits)

---

<img width="100%" src="docs/assets/how-the-code-works.svg" alt="Architecture of the geometric and perceptual evaluation pipelines used by the desktop interface">

The diagram shows the **evaluation flow**. In the desktop app, `gui/runner.py` starts a `gui/worker.py` child process for each selected pipeline; selecting both runs them sequentially.

## Evaluation criteria

| Criterion | Methods | Assesses |
| --- | --- | --- |
| **Geometric fidelity** | Chamfer, Hausdorff, RMSE (lower is better) | How closely the RM surface approximates the GT |
| **Alignment** | Conditional ICP | Pose correction before measuring; a preparation step, **not** a quality score |
| **Localized deviations** | Distance heatmap | **Where** the surfaces diverge |
| **Perceptual similarity** | PSNR, SSIM (higher is better), LPIPS (lower is better) | Visual similarity under matched camera views |

Mesh Comparison **does not generate meshes from images**; it evaluates a supplied GT/RM pair. Results are comparable only with the same GT, preparation, cameras and parameters.

## Example results

The images below are sample outputs from the geometric and perceptual pipelines. This recorded run used 100 camera views; the pre-alignment normalized MSE was below the configured threshold, so ICP alignment was skipped.

**Execution status:** Both pipelines completed without errors with the repository's example meshes. This confirms the example workflow, but does not constitute systematic validation across varied mesh conditions.

### Geometric metric snapshot

**Geometric metrics** (reported in the original GT mesh units):

| Metric | Result | Direction |
| --- | ---: | --- |
| Mean Chamfer distance | 0.00706686 | Lower is better |
| Symmetric Hausdorff distance | 0.308021 | Lower is better |
| Symmetric RMSE | 0.0322591 | Lower is better |

These values describe this example run.

### Perceptual summary — desktop screenshot

<p align="center">
  <img src="assets/interface/perceptual-summary-example.png" width="100%" alt="Screenshot of the Mesh Comparison desktop Results tab, showing LPIPS, PSNR (dB), and SSIM perceptual summary statistics across evaluated camera views">
</p>

*Screenshot of the perceptual summary for the example GT/RM mesh pair.* Lower LPIPS is better; higher PSNR and SSIM are better under comparable settings. The screenshot's rounded values differ slightly from the versioned [example results](docs/results/README.md), so treat them as separately recorded results until the respective run settings and metadata are matched.

<table>
  <tr>
    <td width="50%" align="center">
      <strong>Ground-truth mesh (GT)</strong><br>
      <img src="examples/output/renders/gt_ortho.png" width="100%" alt="Orthographic render of the ground-truth mesh">
    </td>
    <td width="50%" align="center">
      <strong>Aligned reconstructed mesh (RM)</strong><br>
      <img src="examples/output/renders/rm_aligned_ortho.png" width="100%" alt="Orthographic render of the aligned reconstructed mesh">
    </td>
  </tr>
  <tr>
    <td colspan="2" align="center">
      <strong>Geometric distance heatmap</strong><br>
      <img src="examples/output/heatmaps/gt_heatmap_ortho.png" width="70%" alt="Geometric distance heatmap on the ground-truth mesh">
    </td>
  </tr>
  <tr>
    <td colspan="2" align="center">
      <strong>Perceptual comparison — view 1</strong><br>
      <img src="examples/output/renders/pairs/pair_view001.png" width="100%" alt="Side-by-side perceptual comparison of GT and RM for view 1">
    </td>
  </tr>
</table>

The [full example report](docs/results/README.md) (currently in Portuguese) contains all metrics, metadata, and additional views.

## Technologies

| Technology | Reference version (Windows CUDA snapshot) | Purpose |
| --- | --- | --- |
| Python | 3.12 | Application runtime |
| PySide6 | 6.12.0 | Desktop interface |
| PyVista / PyVistaQt | 0.49.1 / 0.13.1 | Interactive 3D viewer |
| Trimesh / Open3D | 5.1.1 / 0.20.0 | Mesh loading and ICP alignment |
| NumPy / SciPy | 2.5.4 / 1.18.1 | Geometric and numerical calculations |
| pyrender | 0.1.45 | Rendering for visual comparison |
| PyTorch / torchvision | 2.11.0+cu128 / 0.26.0+cu128 | LPIPS computation, with CUDA support |
| LPIPS / scikit-image | 0.1.4 / 0.26.0 | Perceptual image metrics |
| Matplotlib / imageio | 3.11.2 / 2.38.1 | Heatmaps and image output |
| pandas | 3.0.6 | Metrics and CSV reports |

Versions are taken from the [Windows CUDA environment snapshot](environments/requirements-windows-cu128.txt), **not** from automatic runtime detection. The [Conda environment](environments/environment.yml) lists the general dependencies.

## Workspace layout

```text
mesh-comparison/
├── src/meshcomparison/
│   ├── common/                # Shared I/O, alignment and rendering utilities
│   ├── geometry/              # Geometric evaluation and heatmaps
│   ├── perceptual/            # Multi-view perceptual evaluation
│   └── gui/                   # Desktop interface and pipeline execution
├── data/samples/              # Sample GT and RM meshes
├── examples/output/           # Versioned example results
│   ├── aligned/
│   ├── heatmaps/
│   ├── metrics/
│   └── renders/
├── environments/              # Conda and Windows CUDA dependency files
├── assets/                    # Interface screenshots and previews
├── docs/
│   ├── harness/               # Agent Harness, scientific contracts and roadmap
│   ├── implementation/        # Existing tests, validation plan and evolution
│   ├── results/               # Recorded example run
│   ├── archived/              # Historical READMEs (not current instructions)
│   └── assets/
├── tests/                     # Automated tests
├── AGENTS.md                  # Repository-wide coding agent instructions
├── pyproject.toml
├── LICENSE
└── README.md
```

Use `data/samples/gt.stl` (GT) and `data/samples/mod.stl` (RM) to try the application. The interface saves new results to the selected output folder (default: `output/`); versioned example results are in `examples/output/`. Choose a new output folder for each experiment to avoid overwriting files.

## Requirements

Use Python 3.12 with the project dependencies and a graphical desktop environment. The interface uses PySide6/PyVistaQt; mesh evaluation requires an OpenGL-capable rendering setup.

## Installation

Open **Anaconda Prompt** in the repository folder. Create the environment only if it does not already exist:

```bat
conda env create -f environments/environment.yml
```

Then activate it and install the project:

```bat
conda activate meshEval
python -m pip install -e . --no-deps
```

If Conda reports `prefix already exists`, the environment is already there. Skip `conda env create` and run the activation and install commands above. The `environment.yml` file includes the desktop interface dependencies. The `--no-deps` option registers the project without installing its dependencies, so an older environment may still need the GUI packages:

```bat
python -m pip install PySide6 pyvista pyvistaqt
```

**For a pinned Windows CUDA 12.8 setup**, create a virtual environment with Python 3.12 and install the pip snapshot, which points to the `cu128` PyTorch wheels:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r environments/requirements-windows-cu128.txt
python -m pip install -e . --no-deps
```

The interface's **Compute device (LPIPS)** defaults to **Auto — prefer CUDA**, with CPU fallback. A CUDA-enabled PyTorch installation and compatible NVIDIA driver are required for LPIPS GPU acceleration; see the [official PyTorch installation selector](https://pytorch.org/get-started/locally/). The geometric pipeline is not accelerated by this LPIPS setting.

## Run

### Desktop interface

With the `meshEval` environment active, start the interface with:

```bat
mesh-gui
```

The window opens maximized, with the Windows title bar and taskbar visible. If that command is not found, use `python -m meshcomparison.gui`. If Python reports `No module named 'PySide6'`, install the GUI packages as described in [Installation](#user-content-installation). The GUI needs a desktop session. See [Validate on Windows](#user-content-validate-on-windows) for choosing meshes and running an evaluation.

## Validate on Windows

With the project installed, check which device PyTorch can use:

```bat
conda activate meshEval
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
mesh-gui
```

In the interface, select `data/samples/gt.stl` for **Ground truth (GT)** and `data/samples/mod.stl` for **Reconstruction (RM)**. Choose a **new output folder**, keep both **Geometric** and **Perceptual** enabled, leave **Compute device (LPIPS)** on **Auto — prefer CUDA**, and click **Run evaluation**. The viewer shows the aligned meshes and heatmap; the **Results** tab shows perceptual statistics and images.

Compare the generated CSVs in the output folder with the [recorded example metrics](examples/output/metrics/) under comparable settings. Small numerical differences, especially between CPU and GPU runs, are possible.

## Pipelines

### Geometric evaluation

The geometric pipeline (`src/meshcomparison/geometry/`) uses the shared preparation function in `src/meshcomparison/common/prepare.py` to normalize both meshes using the ground-truth bounding-box diagonal and conditionally run similarity ICP (rotation, translation, and uniform scale) when pre-alignment normalized MSE exceeds the threshold. It measures symmetric nearest-vertex distances, writes one shared-view render per mesh and a ground-truth vertex-distance heatmap.

Main outputs (relative to the output folder; the committed sample run is in `examples/output/`):

- `output/metrics/metrics_geometry.csv`: pre/post-alignment MSE, mean Chamfer distance, symmetric Hausdorff distance, symmetric RMSE, alignment status, and transform metadata. Distance metrics are reported both normalized and in the original ground-truth units.
- `output/aligned/rm_aligned.ply`: aligned reconstructed mesh, exported in the input ground-truth scale.
- `output/renders/gt_ortho.png` and `output/renders/rm_aligned_ortho.png`: orthographic renders.
- `output/heatmaps/gt_heatmap_ortho.png`: rendered distance heatmap; `gt_heatmap_colored.ply` is the colored mesh used to create it.

### Perceptual evaluation

The perceptual pipeline (`src/meshcomparison/perceptual/`) uses the same shared mesh preparation and conditional ICP alignment, then renders the meshes across a rotating set of camera azimuths. It computes masked LPIPS, PSNR, and SSIM per view and summarizes their distributions; the number of views and saved views are listed under [Parameters](#user-content-parameters).

Main outputs:

- `output/metrics/per_view_metrics.csv`: one row per view with LPIPS, PSNR, SSIM, camera angle, and framing values.
- `output/metrics/metrics_perceptual.csv`: min, max, 25th/75th percentiles, median, and mean for each perceptual metric.
- `output/metrics/run_metadata.csv`: input paths, alignment details, view settings, and the final transform.
- `output/aligned/rm_aligned.ply`: the same aligned mesh written by the geometric pipeline.
- `output/renders/gt/`, `output/renders/rm/`, and `output/renders/pairs/`: saved images for the selected views.

## Parameters

The interface shows analysis parameters as **fixed values** configured in `RunConfig` (`src/meshcomparison/gui/config.py`): ICP MSE threshold `1e-4` (alignment runs only above it), render size `1600 × 1200`, elevation `25.264°`, geometric camera azimuth `-135°`, `100` perceptual views (images saved for views `1 33 66`), camera margin `1.05` and camera radius factor `1.45`. Images are saved only for the view numbers that exist.

## Scope and limitations

- STL files do not store physical units. Geometric distances use the unit system of the GT mesh.
- CI checks code and output structure only, not metric values, CUDA or the GUI window; see [Development](#user-content-development).
- Basic unit tests already cover identical vertex clouds, a simple point offset and bounding-box scale/translation, plus perceptual helper and GUI-configuration behavior. **Systematic end-to-end validation on controlled meshes** (deformations, incomplete surfaces, different sampling densities and rendering regression) is still pending; see the [validation plan](docs/implementation/README.md).

## Development

The [documentation index](docs/README.md) describes the package structure; the [implementation guide](docs/implementation/README.md) covers existing tests and the validation plan; and [Harness documentation](docs/harness/README.md) describes the documented (not yet fully implemented) agent-development workflow.

### Agent Harness for Scientific Integrity

This project adopts an **Agent Harness** to guide AI-assisted development while safeguarding scientific integrity, methodological consistency, and reproducibility.

Codex, Claude Code and other coding agents follow repository-level instructions defined in [AGENTS.md](AGENTS.md), with the [Scientific Contracts (CC-01–CC-13)](docs/harness/CONTRATOS-CIENTIFICOS.md) serving as the mandatory methodological reference.

The harness establishes safeguards against unintended changes to geometric and perceptual metrics, alignment procedures, rendering parameters, and evaluation outputs. Methodological changes require explicit review and scientific validation. These safeguards support scientific validity but do not independently establish it; numerical equivalence and regression testing remain necessary.

`environments/environment.yml` also installs `pytest` and `ruff`. From the activated environment (with `pip install -e . --no-deps` done):

```bat
ruff check .
pytest
```

GitHub Actions (`.github/workflows/ci.yml`) runs lint, the tests and an import check of both pipelines and the worker. Its subprocess tests run the pipelines with offscreen rendering at a reduced configuration (320 × 240 px, 2 perceptual views on CPU) to check output structure only; CI does not validate metric values, the default 100-view configuration, CUDA execution or the GUI window.

## Troubleshooting

- **`pyrender` fails to create an offscreen context**: a working offscreen OpenGL setup is required. On headless Linux, install `libegl1 libgl1 libglu1-mesa libosmesa6` and set `PYOPENGL_PLATFORM=egl` (as the CI does).
- **CUDA not available**: expected on CPU-only installs; LPIPS then runs on CPU, just slower.
- **Cannot load an `.fbx` file**: FBX is rejected and is not converted by this application. Convert it outside Mesh Comparison to STL, OBJ, PLY, or another supported `trimesh` format, then load the converted file.

## Interface

<img src="assets/interface/interface-v2.png">

## License and credits

This repository is a fork of [ThiagoFigueiroRibeiro/MeshComparison](https://github.com/ThiagoFigueiroRibeiro/MeshComparison). The modifications in this fork are proprietary; see [LICENSE](LICENSE). Code derived from the original project remains the property of its author.

