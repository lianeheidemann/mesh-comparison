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
</p>

This workspace compares a ground-truth mesh (GT) with a reconstructed mesh (RM), combining geometric distance metrics with perceptual image metrics across multiple camera views. Convert FBX models to STL (or another supported `trimesh` format) before running the evaluation scripts; they do not load FBX directly.

**Quick links:** [Example results](#example-results) · [Installation](#installation) · [Run the pipelines](#run) · [Implementation details](#pipelines) · [Limitations](#scope-and-limitations)

### Table of contents

- [Example results](#example-results)
- [Technologies](#technologies)
- [Workspace layout](#workspace-layout)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run](#run)
- [Pipelines](#pipelines)
- [Options](#options)
- [Scope and limitations](#scope-and-limitations)
- [Development](#development)
- [License and credits](#license-and-credits)

---

<img width="100%" src="docs/assets/how-the-code-works.svg">

## Example results

The images below are sample outputs from the geometric and perceptual pipelines. This recorded run used 100 camera views; the pre-alignment normalized MSE was below the configured threshold, so ICP alignment was skipped.

**Execution status:** both pipelines completed without errors with the repository's example meshes. This confirms the example workflow in the recorded Windows environment; it is not a systematic test of varied mesh conditions. That environment uses CPU-only PyTorch, so CUDA acceleration was unavailable and was not tested.

### Metric snapshot

**Geometric metrics** (reported in the original GT mesh units):

| Metric | Result | Direction |
| --- | ---: | --- |
| Mean Chamfer distance | 0.00706686 | Lower is better |
| Symmetric Hausdorff distance | 0.308021 | Lower is better |
| Symmetric RMSE | 0.0322591 | Lower is better |

**Perceptual metrics** (median across 100 views):

| Metric | Result | Direction |
| --- | ---: | --- |
| LPIPS | 0.112826 | Lower is better |
| PSNR | 11.1308 dB | Higher is better |
| SSIM | 0.930943 | Higher is better |

These values describe this example run. Compare results only when the inputs, camera views, and pipeline settings are consistent. STL files do not store physical units, so geometric values use the unit system of the GT mesh.

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

| Technology | Installed version (reported 2026-10-17) | Role in the project |
| --- | --- | --- |
| Python | 3.12.15 | Main language for both evaluation pipelines. |
| Conda | 25.11.1 (Windows win-64) | Isolated Python environment and dependency management. |
| NumPy | 2.5.4 | Numerical operations on coordinates, arrays, and distances. |
| Trimesh | 5.1.1 | Loading, inspecting, transforming, and exporting 3D meshes. |
| Open3D | 0.20.0 | Iterative Closest Point (ICP) mesh alignment. |
| SciPy (cKDTree) | 1.18.1 | Efficient nearest-neighbor searches for geometric metrics. |
| pyrender | 0.1.45 | Offscreen rendering of meshes for image-based comparison. |
| Matplotlib | 3.11.2 | Geometric distance visualization and heatmap color mapping. |
| imageio | 2.38.1 | Writing rendered images to disk. |
| PyTorch | 2.14.1 | Neural-network execution for perceptual evaluation, with optional CUDA acceleration. |
| torchvision | 0.29.1 | Vision models and utilities used by LPIPS. |
| LPIPS | 0.1.4 | Learned perceptual similarity between rendered views. |
| scikit-image | 0.26.0 | Structural Similarity Index (SSIM) calculation. |
| pandas | 3.0.6 | Tabular metrics, summaries, and CSV exports. |

These versions were reported from the local Windows `meshEval` environment on 2026-10-17. Imports and both example pipelines were confirmed in that environment. PyTorch reports `2.14.1+cpu`; CUDA is unavailable, so perceptual evaluation runs on CPU. [`environments/environment-lock.yml`](environments/environment-lock.yml) records the installed Conda and pip package versions for recreating this Windows environment. [`environments/environment.yml`](environments/environment.yml) remains the general, unpinned dependency list. These observed versions do not identify the environment that produced older outputs already in the repository. The installer’s base Python version is independent of the project environment.

## Workspace layout

```text
mesh-comparison/
├── README.md  LICENSE  pyproject.toml
├── src/meshcomparison/            # Python package
│   ├── common/                    # Shared: mesh I/O, transforms, distances, ICP alignment, rendering
│   ├── geometry/                  # Geometric evaluation (pipeline, metrics, heatmap, CLI)
│   └── perceptual/                # Multi-view perceptual evaluation (cameras, PSNR/SSIM/LPIPS, CLI)
├── scripts/                       # Launchers (.bat for Windows, .sh for Linux/macOS)
├── data/samples/                  # gt.stl (ground truth) and mod.stl (reconstructed mesh)
├── environments/                  # environment.yml (general) and environment-lock.yml (Windows snapshot)
├── examples/output/               # Committed results of the sample run
│   ├── aligned/                   # Aligned reconstructed mesh exports
│   ├── heatmaps/                  # Geometric distance heatmap assets
│   ├── metrics/                   # CSV metric reports
│   └── renders/                   # Mesh and view renders (gt/, rm/, pairs/)
├── docs/                          # Guides, results report, logo and diagrams (docs/assets/)
└── tests/                         # pytest suite
```

The launchers in `scripts/` use `data/samples/gt.stl` as the ground truth and `data/samples/mod.stl` as the reconstructed mesh, and write results to a local `output/` folder (git-ignored). The results committed in `examples/output/` come from the sample run. Runs may replace files with the same names in the output folders.

## Requirements

Use Python in a Conda environment named `meshEval` to run the supplied launchers. The package imports NumPy, pandas, trimesh, pyrender, Open3D, Matplotlib, imageio, and SciPy. The perceptual pipeline additionally imports scikit-image, PyTorch, and LPIPS. A working offscreen-rendering setup is needed for `pyrender`; the perceptual pipeline uses CUDA when available and otherwise runs LPIPS on CPU.

## Installation

Run these commands separately in Anaconda Prompt from the repository root. Choose **one** environment file:

- `environments/environment.yml` is the general setup with unpinned dependencies.
- `environments/environment-lock.yml` reproduces the recorded Windows environment and package versions.

For the general setup:

```bat
conda env create -f environments/environment.yml
conda activate meshEval
pip install -e . --no-deps
```

To recreate the recorded Windows environment instead, use:

```bat
conda env create -f environments/environment-lock.yml
conda activate meshEval
pip install -e . --no-deps
```

If `meshEval` already exists, activate it instead of creating it again. The [environment preparation guide](docs/implementation/step-by-step/01-preparacao-ambiente.md) records validation details. `pip install -e . --no-deps` registers the `meshcomparison` package (dependencies come from the environment file). Verify imports before running the pipelines:

```bat
python -c "import numpy, pandas, trimesh, pyrender, open3d, matplotlib, imageio, scipy, skimage, torch, torchvision, lpips; print('OK: libraries loaded')"
```

The recorded local validation used CPU-only PyTorch. For GPU-accelerated LPIPS, install a PyTorch build that matches your CUDA version using the official PyTorch installation instructions.

## Run

From the repository root on Windows, double-click either launcher or run it in a Command Prompt:

```bat
scripts\run_mesh_eval.bat
scripts\run_percept_eval.bat
```

On Linux/macOS use `scripts/run_mesh_eval.sh` and `scripts/run_percept_eval.sh`. To choose other input or output paths, call the package directly (or use the `mesh-eval` and `percept-eval` commands installed with it):

```bat
python -m meshcomparison.geometry --gt data/samples/gt.stl --rm data/samples/mod.stl --out output
python -m meshcomparison.perceptual --gt data/samples/gt.stl --rm data/samples/mod.stl --out output
```

Both commands require `--gt` and `--rm`; `--out` defaults to `output`.

## Pipelines

### Geometric evaluation

The geometric pipeline (`src/meshcomparison/geometry/`) normalizes both meshes using the ground-truth bounding-box diagonal. It measures symmetric nearest-vertex distances, and runs similarity ICP (rotation, translation, and uniform scale) when the pre-alignment normalized MSE exceeds the configured threshold. It writes one shared-view render per mesh and a ground-truth vertex-distance heatmap.

Main outputs (relative to `--out`; the committed sample run is in `examples/output/`):

- `output/metrics/metrics_geometry.csv`: pre/post-alignment MSE, mean Chamfer distance, symmetric Hausdorff distance, symmetric RMSE, alignment status, and transform metadata. Distance metrics are reported both normalized and in the original ground-truth units.
- `output/aligned/rm_aligned.ply`: aligned reconstructed mesh, exported in the input ground-truth scale.
- `output/renders/gt_ortho.png` and `output/renders/rm_aligned_ortho.png`: orthographic renders.
- `output/heatmaps/gt_heatmap_ortho.png`: rendered distance heatmap; `gt_heatmap_colored.ply` is the colored mesh used to create it.

### Perceptual evaluation

The perceptual pipeline (`src/meshcomparison/perceptual/`) uses the same normalization and conditional ICP alignment, then renders the meshes across a rotating set of camera azimuths. It computes masked LPIPS, PSNR, and SSIM per view and summarizes their distributions. By default, it evaluates 100 views and saves views 1, 33, and 66.

Main outputs:

- `output/metrics/per_view_metrics.csv`: one row per view with LPIPS, PSNR, SSIM, camera angle, and framing values.
- `output/metrics/metrics_perceptual.csv`: min, max, 25th/75th percentiles, median, and mean for each perceptual metric.
- `output/metrics/run_metadata.csv`: input paths, alignment details, view settings, and the final transform.
- `output/aligned/rm_aligned.ply`: aligned reconstructed mesh in the ground-truth input scale.
- `output/renders/gt/`, `output/renders/rm/`, and `output/renders/pairs/`: saved images for the selected views.


## Options

Both commands accept `--mse-threshold` (default `1e-4`), which controls whether alignment is run, plus `--width` and `--height` (defaults `1600` and `1200`). Use `--help` after the module name to see all options.

The geometric pipeline also accepts `--azimuth` (default `-135`) and `--elevation` (default `25.264`). The perceptual pipeline accepts `--elevation` (default `25.264`), `--num-views` (default `100`), `--save-views` (default `1 33 66`), `--camera-margin` (default `1.05`), and `--radius-factor` (default `1.45`).

## Scope and limitations

- STL files do not store physical units. Geometric distances use the unit system of the GT mesh.
- The GitHub Actions workflow checks linting, tests, and the command-line help output. It does not run offscreen rendering or validate CUDA execution.
- LPIPS runs on CPU when CUDA is unavailable; results can depend on camera, framing, and pipeline settings.
- Systematic validation of identical, translated, resized, incomplete, and differently sampled meshes is still pending; see the [validation plan](docs/implementation/step-by-step/10-limitacoes-evolucao.md).

## Development

`environments/environment.yml` also installs `pytest` and `ruff`. From the activated environment (with `pip install -e . --no-deps` done):

```bat
ruff check .
pytest
```

GitHub Actions (`.github/workflows/ci.yml`) runs lint, the tests, and the `--help` of both commands. It does not run the rendering or CUDA parts of the pipelines.

## Troubleshooting

- **`pyrender` fails to create an offscreen context**: a working offscreen OpenGL setup is required. On headless Linux, install `libegl1 libgl1 libglu1-mesa libosmesa6` and set `PYOPENGL_PLATFORM=egl` (as the CI does).
- **CUDA not available**: expected on CPU-only installs; LPIPS then runs on CPU, just slower.
- **Cannot load an `.fbx` file**: the pipelines do not read FBX directly; convert it to STL, PLY, or OBJ first.

## License and credits

This repository is a fork of [ThiagoFigueiroRibeiro/MeshComparison](https://github.com/ThiagoFigueiroRibeiro/MeshComparison). The modifications in this fork are proprietary; see [LICENSE](LICENSE). Code derived from the original project remains the property of its author.

