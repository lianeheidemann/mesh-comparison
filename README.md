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

Mesh Comparison is a Python desktop application that evaluates a reconstructed mesh (RM) against a ground-truth mesh (GT): geometric accuracy and completeness on the surface, accuracy in regions hidden from the input image, and perceptual similarity over multiple rendered views. It evaluates one GT/RM pair per run; it does not reconstruct meshes.

<p align="center">
  <img src="assets/interface/interface-v2.png" width="100%" alt="Mesh Comparison desktop interface">
</p>

### Table of contents

- [How it works](#user-content-how-it-works)
- [Metrics](#user-content-metrics)
- [Example results](#user-content-example-results)
- [Installation](#user-content-installation)
- [Usage](#user-content-usage)
  - [Desktop interface](#user-content-desktop-interface)
  - [Metric figures](#user-content-metric-figures)
  - [Robustness study](#user-content-robustness-study)
- [Outputs](#user-content-outputs)
- [Limitations](#user-content-limitations)
- [Development](#user-content-development)
- [Troubleshooting](#user-content-troubleshooting)
- [License and credits](#user-content-license-and-credits)

## How it works

<img width="100%" src="docs/assets/how-the-code-works.svg" alt="Architecture of the geometric and perceptual evaluation pipelines">

1. **Preparation** (shared by both pipelines): load GT and RM, scale both by the GT bounding-box diagonal, draw 100 000 area-uniform surface samples per mesh (seeds `0`/`1`) and run similarity ICP (rotation, translation, uniform scale) on them when the symmetric point-to-surface MSE exceeds `1e-4`.
2. **Geometric pipeline:** surface metrics, optionally split into GT regions visible/hidden from the input view, plus orthographic renders and a GT heatmap of the distance to the aligned RM surface.
3. **Perceptual pipeline:** GT and aligned RM rendered from the same orthographic cameras (100 azimuths); LPIPS, PSNR and SSIM per view on the crop around the union of both masks.

The GUI runs each selected pipeline in a child process. Metric definitions and their rationale are recorded in the [ADRs](docs/adr/).

## Metrics

d(g, R) is the distance from a GT surface sample to the closest point on the RM triangles (point-to-surface, [ADR 0004](docs/adr/0004-point-to-surface.md)); d(r, G) is the reverse. Distances are fractions of the GT diagonal (columns `_normalized`) or GT units (`_gt_units`).

| Metric | Definition | Better |
| --- | --- | --- |
| Chamfer | ½ [mean d(G→R) + mean d(R→G)] over surface samples | Lower |
| HD95 | max of the two directional 95th percentiles | Lower |
| F-score @τ | harmonic mean of precision (RM samples within τ of GT) and recall (GT samples within τ of RM); τ = 1, 2, 5 % | Higher |
| AUC-F | area under F(τ) for τ = 0.5–10 %, normalized to [0, 1] | Higher |
| Normal consistency | mean \|cos\| between each sample's normal and the normal of the closest triangle on the other mesh, both directions | Higher |
| ICP scale | uniform scale applied by the alignment (diagnostic; 1 = none) | — |
| PSNR | 10·log10(1/MSE), MSE over the 3N channel values of the N union-mask pixels | Higher |
| SSIM | scikit-image SSIM on the crop with the background zeroed | Higher |
| LPIPS | AlexNet LPIPS on the same crop | Lower |

**Visible / hidden regions:** with the input-image camera (azimuth/elevation in the GT frame, z up), GT samples are classified with an orthographic z-buffer; each RM sample takes the region of its nearest GT sample.

## Example results

Sample pair `data/samples/gt.stl` × `mod.stl` (ICP not triggered; the input view −135°/25.264° is illustrative, the pair has no input image). Details and data: [example report](docs/results/README.md).

| Region | GT share | Chamfer (GT units) | HD95 (GT units) | F@1 % | AUC-F | Normal consistency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Whole surface | 100 % | 0.0100 | 0.0800 | 0.908 | 0.981 | 0.960 |
| Visible | 39 % | 0.0187 | 0.1195 | 0.826 | 0.963 | 0.928 |
| Hidden | 61 % | 0.0042 | 0.0261 | 0.963 | 0.992 | 0.980 |

<p align="center">
  <img src="docs/results/figures/geometric_metrics.png" width="100%" alt="Geometric metrics per region for the sample pair">
  <img src="docs/results/figures/sampling_uncertainty.png" width="100%" alt="Metric spread against the number of surface samples">
</p>

## Installation

Python 3.12, an OpenGL-capable renderer and, for the GUI, a desktop session. With Conda (Anaconda Prompt, repository folder):

```bat
conda env create -f environments/environment.yml
conda activate meshEval
python -m pip install -e . --no-deps
```

Pinned Windows CUDA 12.8 setup (LPIPS on GPU):

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r environments/requirements-windows-cu128.txt
python -m pip install -e . --no-deps
```

Reference versions are listed in [requirements-windows-cu128.txt](environments/requirements-windows-cu128.txt).

## Usage

### Desktop interface

```bat
mesh-gui
```

(or `python -m meshcomparison.gui`). Select the GT and RM (STL, OBJ, PLY, OFF, GLB/GLTF), a new output folder, the pipelines and the LPIPS device (Auto prefers CUDA), optionally the **Input view**, and click **Run evaluation**. The 3D view shows the aligned meshes and heatmap; **Results** shows the geometric and perceptual summaries and the saved images.

Fixed parameters (`RunConfig`, `src/meshcomparison/gui/config.py`): ICP threshold `1e-4`, render `1600 × 1200`, elevation `25.264°`, geometric camera azimuth `-135°`, `100` perceptual views (images saved for views 1, 33, 66), camera margin `1.05`, radius factor `1.45`, 100 000 samples per mesh, τ = 1/2/5 %.

### Metric figures

```bash
python scripts/plot_metrics.py --run output [--uncertainty] [--perceptual-metrics lpips,psnr,ssim]
```

Writes to `output/figures/`: F(τ) curves, per-region metrics, per-view perceptual metrics with the mean and its 95 % bootstrap interval, and, with `--uncertainty`, the metric spread over seeds and sample counts.

### Robustness study

```bash
python scripts/robustness_study.py --gt data/samples/gt.stl --out output/robustness [--views 8] [--lpips]
```

Checks invariance to re-triangulation and sensitivity to noise, local bumps and missing surface, against a vertex-to-vertex baseline ([results](docs/results/robustness/README.md)). `python scripts/icp_study.py --gt data/samples/gt.stl --out output/icp` measures how far the ICP recovers known rotations ([results](docs/results/icp/README.md)).

## Outputs

| File (in the output folder) | Content |
| --- | --- |
| `metrics/metrics_geometry.csv` | One row per region: Chamfer, HD95, precision/recall/F-score per τ, AUC-F, normal consistency; run settings (files, pre/post-alignment MSE, ICP scale, seeds, input view, camera, heatmap scale, final transform) |
| `metrics/fscore_curve.csv` | F(τ), precision and recall per region, τ = 0.5–10 % |
| `metrics/per_view_metrics.csv` | LPIPS, PSNR, SSIM, camera and crop per view |
| `metrics/metrics_perceptual.csv` | min, p25, median, p75, max, mean of the finite per-view values |
| `metrics/run_metadata.csv` | Perceptual run settings and final transform |
| `aligned/rm_aligned.ply` | Aligned RM in GT units |
| `renders/`, `heatmaps/` | Orthographic renders, selected view pairs, heatmap image and coloured mesh |

## Limitations

- STL has no physical units; distances are in the GT's units.
- Metrics are Monte Carlo estimates over surface samples. With point-to-surface distances they do not drift with the sample count; at 10⁵ samples the seed spread is about 1 % for Chamfer and HD95 and ≤ 0.1 % for the scores (sample pair).
- The input view uses an orthographic camera and a z-up convention that must match the dataset.
- ICP is local: on the sample GT it recovers rotations up to about 45°–60° (scale error < 0.1 %) and fails beyond, leaving a plausible-looking Chamfer of 2.5–3.1 % of the diagonal. Bring each model's output into the GT frame (axis convention) before evaluating ([ICP study](docs/results/icp/README.md)).
- Validation so far uses synthetic cases and one sample pair; benchmark meshes (TripoSR, Stable Fast 3D, InstantMesh) and GPU LPIPS are still to be validated ([validation plan](docs/implementation/README.md)).

## Development

```bash
ruff check .
pytest
```

CI (`.github/workflows/ci.yml`) runs Ruff, pytest (pipelines in subprocesses at 320 × 240 px, 2 perceptual views on CPU) and an import check; it checks structure, not metric values, CUDA or the GUI window. Coding agents follow [AGENTS.md](AGENTS.md); see the [documentation index](docs/README.md) for architecture, tests and results.

## Troubleshooting

- **No offscreen OpenGL context:** on headless Linux install `libegl1 libgl1 libglu1-mesa libosmesa6` and set `PYOPENGL_PLATFORM=egl`.
- **`No module named 'PySide6'`:** `python -m pip install PySide6 pyvista pyvistaqt`.
- **CUDA not available:** LPIPS runs on CPU, more slowly.
- **`.fbx` files:** not supported; convert to STL, OBJ or PLY.

## License and credits

Fork of [ThiagoFigueiroRibeiro/MeshComparison](https://github.com/ThiagoFigueiroRibeiro/MeshComparison). The modifications in this fork are proprietary; see [LICENSE](LICENSE). Code derived from the original project remains the property of its author.
