# Acceptance tests T-01–T-07 and T-10 from docs/harness/CONTRATOS-CIENTIFICOS.md, with known expected values.
"""Scientific-contract tests (CC-01–CC-06, CC-09).

These tests check the documented behaviour of the current implementation against values derived by hand or
from controlled transformations. They do not compare against the original repository (T-09) and do not
cover rendering or LPIPS/SSIM equivalence (T-08).

Tolerances: meshes written to STL are stored as float32, so a round trip through a file perturbs coordinates by
about 1e-7 of the mesh size. After normalisation by the GT diagonal this bounds squared distances by ~1e-14;
``POST_ICP_MSE_TOL = 1e-10`` leaves margin for Open3D's iterative solution while staying six orders of magnitude
below the default ICP threshold (1e-4).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import trimesh

from meshcomparison.common.distances import symmetric_mse
from meshcomparison.common.io import load_mesh
from meshcomparison.common.prepare import prepare_meshes
from meshcomparison.geometry.heatmap import colorize_gt_heatmap
from meshcomparison.geometry.metrics import compute_metrics

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"
GT = SAMPLES / "gt.stl"
THRESHOLD = 1e-4  # default normalized MSE threshold (CC-04)
POST_ICP_MSE_TOL = 1e-10


def _moved_gt(tmp_path, name, transform):
    """Write a copy of the sample GT after ``transform(mesh)`` and return its path."""
    mesh = trimesh.load(GT, process=False)
    transform(mesh)
    path = tmp_path / f"{name}.stl"
    mesh.export(path)
    return path


def _prepare(rm_path, threshold=THRESHOLD):
    return prepare_meshes(str(GT), str(rm_path), threshold, 7)


def _similarity_scale(transform):
    return float(np.cbrt(np.linalg.det(transform[:3, :3])))


# --- T-01: GT = RM -------------------------------------------------------------------------------------------


def test_t01_identical_meshes_give_zero_metrics_without_icp():
    prepared = _prepare(GT)
    metrics = compute_metrics(prepared.gt.vertices, prepared.rm_aligned.vertices)

    assert prepared.pre_mse_norm == 0.0
    assert not prepared.alignment_triggered
    assert np.array_equal(prepared.final_transform, np.eye(4))
    for key in ("mse", "chamfer_mean", "hausdorff", "rmse"):
        assert metrics[key] == 0.0, key


def test_t01_geometry_pipeline_writes_zero_metrics_for_identical_meshes(tmp_path):
    pytest.importorskip("pyrender")
    from meshcomparison.geometry.pipeline import run_pipeline

    run_pipeline(str(GT), str(GT), str(tmp_path), width=160, height=120)
    row = pd.read_csv(tmp_path / "metrics" / "metrics_geometry.csv").iloc[0]

    assert not bool(row["alignment_triggered"])
    for column in ("pre_alignment_mse_normalized", "post_alignment_mse_normalized", "mean_chamfer_normalized",
                   "symmetric_hausdorff_normalized", "symmetric_rmse_normalized", "mean_chamfer_gt_units"):
        assert row[column] == 0.0, column
    transform = np.array([row[f"final_transform_{r}{c}"] for r in range(3) for c in range(4)]).reshape(3, 4)
    assert np.array_equal(transform, np.eye(4)[:3])


# --- CC-02: one GT-diagonal scale for both meshes, and unit conversions in the CSV ---------------------------


def test_cc02_both_meshes_use_the_gt_diagonal(tmp_path):
    rm_path = _moved_gt(tmp_path, "scaled", lambda m: m.apply_scale(2.0))
    gt_raw, rm_raw = load_mesh(str(GT)), load_mesh(str(rm_path))
    prepared = _prepare(rm_path)

    diag = np.linalg.norm(gt_raw.bounds[1] - gt_raw.bounds[0])
    assert prepared.gt_diag_raw == pytest.approx(diag, rel=1e-12)
    assert prepared.internal_scale == pytest.approx(1.0 / diag, rel=1e-12)
    # the RM keeps its relative size: twice the GT diagonal after normalisation
    rm_diag_norm = np.linalg.norm(rm_raw.bounds[1] - rm_raw.bounds[0]) / diag
    assert rm_diag_norm == pytest.approx(2.0, rel=1e-6)
    assert prepared.pre_mse_norm == pytest.approx(symmetric_mse(gt_raw.vertices / diag, rm_raw.vertices / diag),
                                                  rel=1e-12)


def test_cc02_csv_gt_units_are_normalized_values_times_the_diagonal(tmp_path):
    pytest.importorskip("pyrender")
    from meshcomparison.geometry.pipeline import run_pipeline

    run_pipeline(str(GT), str(SAMPLES / "mod.stl"), str(tmp_path), width=160, height=120)
    row = pd.read_csv(tmp_path / "metrics" / "metrics_geometry.csv").iloc[0]
    diag = row["gt_bbox_diagonal_original_units"]

    for name in ("mean_chamfer", "symmetric_hausdorff", "symmetric_rmse"):
        assert row[f"{name}_gt_units"] == pytest.approx(row[f"{name}_normalized"] * diag, rel=1e-12), name
    for stage in ("pre", "post"):
        assert row[f"{stage}_alignment_mse_gt_units_sq"] == pytest.approx(
            row[f"{stage}_alignment_mse_normalized"] * diag ** 2, rel=1e-12), stage
    assert row["symmetric_rmse_normalized"] ** 2 == pytest.approx(row["post_alignment_mse_normalized"], rel=1e-9)


# --- CC-04: ICP trigger is strictly greater than the threshold ------------------------------------------------


def test_cc04_icp_is_not_triggered_when_mse_equals_the_threshold(tmp_path):
    rm_path = _moved_gt(tmp_path, "shifted", lambda m: m.apply_translation([0.005 * m.scale, 0, 0]))
    pre = _prepare(rm_path).pre_mse_norm
    assert 0.0 < pre < THRESHOLD

    at_threshold = _prepare(rm_path, threshold=pre)
    assert not at_threshold.alignment_triggered
    assert np.array_equal(at_threshold.final_transform, np.eye(4))

    below_threshold = _prepare(rm_path, threshold=np.nextafter(pre, 0.0))
    assert below_threshold.alignment_triggered


# --- T-02: known rigid motion ---------------------------------------------------------------------------------


def test_t02_rigid_motion_is_undone_and_pre_alignment_error_is_kept(tmp_path):
    def move(mesh):
        mesh.apply_transform(trimesh.transformations.rotation_matrix(0.3, [0, 0, 1]))
        mesh.apply_translation([0.4 * mesh.scale, 0, 0])

    rm_path = _moved_gt(tmp_path, "rigid", move)
    prepared = _prepare(rm_path)
    metrics = compute_metrics(prepared.gt.vertices, prepared.rm_aligned.vertices)

    assert prepared.alignment_triggered and prepared.pre_mse_norm > THRESHOLD
    assert metrics["mse"] < POST_ICP_MSE_TOL
    assert _similarity_scale(prepared.final_transform) == pytest.approx(1.0, abs=1e-6)

    # final_transform is expressed in the normalized space and maps the normalized RM onto the aligned RM
    rm_norm = load_mesh(str(rm_path)).vertices * prepared.internal_scale
    mapped = trimesh.transform_points(rm_norm, prepared.final_transform)
    assert np.allclose(mapped, prepared.rm_aligned.vertices, atol=1e-12)


# --- T-03: different scale ------------------------------------------------------------------------------------


@pytest.mark.parametrize("factor", [1.5, 0.8])
def test_t03_scale_error_is_visible_before_icp_and_absorbed_by_similarity_icp(tmp_path, factor):
    rm_path = _moved_gt(tmp_path, f"scale_{factor}", lambda m: m.apply_scale(factor))
    prepared = _prepare(rm_path)
    metrics = compute_metrics(prepared.gt.vertices, prepared.rm_aligned.vertices)

    assert prepared.alignment_triggered and prepared.pre_mse_norm > THRESHOLD
    # uniform scaling in the ICP recovers the inverse factor, so post-alignment metrics hide the scale error
    assert _similarity_scale(prepared.final_transform) == pytest.approx(1.0 / factor, rel=1e-6)
    assert metrics["mse"] < POST_ICP_MSE_TOL


# --- T-04: vertex order ---------------------------------------------------------------------------------------


def test_t04_metrics_do_not_depend_on_vertex_order():
    rng = np.random.default_rng(4)
    gt = rng.random((300, 3))
    rm = gt + rng.normal(scale=0.01, size=gt.shape)
    reference = compute_metrics(gt, rm)
    permuted = compute_metrics(gt[rng.permutation(len(gt))], rm[rng.permutation(len(rm))])

    for key in ("mse", "chamfer_mean", "hausdorff", "rmse"):
        assert permuted[key] == pytest.approx(reference[key], rel=1e-12), key


# --- T-05: density and missing parts --------------------------------------------------------------------------


def _grid(step):
    axis = np.arange(0.0, 2.0 + step / 2, step)
    xs, ys = np.meshgrid(axis, axis)
    return np.column_stack([xs.ravel(), ys.ravel(), np.zeros(xs.size)])


def test_t05_denser_sampling_of_the_same_plane_changes_the_vertex_metrics():
    gt, rm = _grid(1.0), _grid(0.5)  # 3 x 3 and 5 x 5 vertices on the same square
    metrics = compute_metrics(gt, rm)

    # every GT vertex is also an RM vertex; the 16 extra RM vertices sit 0.5 or sqrt(0.5) from the GT
    assert np.all(metrics["d_gt2rm"] == 0.0)
    expected_rm2gt = (12 * 0.5 + 4 * np.sqrt(0.5)) / 25
    assert np.mean(metrics["d_rm2gt"]) == pytest.approx(expected_rm2gt, rel=1e-12)
    assert metrics["chamfer_mean"] == pytest.approx(0.5 * expected_rm2gt, rel=1e-12)
    assert metrics["hausdorff"] == pytest.approx(np.sqrt(0.5), rel=1e-12)


def test_t05_missing_region_only_shows_in_the_gt_to_rm_direction():
    gt = _grid(0.5)
    rm = gt[gt[:, 0] <= 1.0]  # the RM lacks the half x > 1
    metrics = compute_metrics(gt, rm)

    assert np.all(metrics["d_rm2gt"] == 0.0)
    missing = gt[:, 0] > 1.0
    assert np.all(metrics["d_gt2rm"][~missing] == 0.0)
    assert np.allclose(metrics["d_gt2rm"][missing], gt[missing, 0] - 1.0)
    assert metrics["hausdorff"] == pytest.approx(1.0)


# --- T-06: localized deformation and the directional heatmap ---------------------------------------------------


def test_t06_local_bump_is_confined_to_the_gt_heatmap_region():
    gt = trimesh.creation.icosphere(subdivisions=3)
    cap = gt.vertices[:, 2] > 0.9
    rm = gt.copy()
    rm.vertices[cap] *= 1.1
    metrics = compute_metrics(gt.vertices, rm.vertices)
    d_gt2rm = metrics["d_gt2rm"]

    assert np.all(d_gt2rm[~cap] == 0.0)
    assert np.all(d_gt2rm[cap] > 0.0)

    heat_mesh, norm, cmap = colorize_gt_heatmap(gt, d_gt2rm)
    assert len(heat_mesh.vertices) == len(gt.vertices)  # colours live on the GT, not on the RM
    assert norm.vmax == pytest.approx(max(np.percentile(d_gt2rm, 95), 1e-12))
    expected = (cmap(norm(d_gt2rm)) * 255).astype(np.uint8)
    assert np.array_equal(heat_mesh.visual.vertex_colors, expected)
    # undeformed vertices get the low end of the palette
    assert np.array_equal(heat_mesh.visual.vertex_colors[~cap][0], (np.array(cmap(0.0)) * 255).astype(np.uint8))


# --- T-07: legacy PSNR ----------------------------------------------------------------------------------------


def test_t07_legacy_psnr_divides_the_rgb_sum_by_the_pixel_count():
    pytest.importorskip("skimage")
    from meshcomparison.perceptual.image_metrics import masked_psnr

    gt = np.full((10, 10, 3), 0.5, dtype=np.float32)
    rm = gt + np.float32(0.1)
    mask = np.zeros((10, 10), dtype=bool)
    mask[2:6, 2:7] = True
    rm[~mask] = 0.0  # errors outside the mask must not count

    legacy = masked_psnr(gt, rm, mask)
    assert legacy == pytest.approx(10 * np.log10(1 / (3 * 0.1 ** 2)), abs=1e-4)
    # differs from the conventional per-channel mean by 10*log10(3) dB
    assert 10 * np.log10(1 / 0.1 ** 2) - legacy == pytest.approx(10 * np.log10(3), abs=1e-4)

    single_channel = gt.copy()
    single_channel[..., 0] += np.float32(0.1)
    assert masked_psnr(gt, single_channel, mask) == pytest.approx(20.0, abs=1e-4)


# --- T-10: invalid inputs fail visibly -------------------------------------------------------------------------


def test_t10_fbx_is_rejected(tmp_path):
    path = tmp_path / "model.fbx"
    path.write_bytes(b"")
    with pytest.raises(ValueError, match="FBX"):
        load_mesh(str(path))


def test_t10_missing_file_raises(tmp_path):
    with pytest.raises(RuntimeError, match="Could not load mesh file"):
        load_mesh(str(tmp_path / "missing.stl"))


def test_t10_degenerate_gt_stops_before_any_metric(tmp_path):
    path = tmp_path / "point.stl"
    trimesh.Trimesh(vertices=[[1.0, 1.0, 1.0]] * 3, faces=[[0, 1, 2]], process=False).export(path)
    with pytest.raises(ValueError, match="diagonal is too small"):
        prepare_meshes(str(path), str(GT), THRESHOLD, 7)


def test_t10_empty_union_mask_raises():
    pytest.importorskip("skimage")
    from meshcomparison.perceptual.image_metrics import crop_to_union_mask

    img = np.zeros((8, 8, 3), dtype=np.float32)
    empty = np.zeros((8, 8), dtype=bool)
    with pytest.raises(ValueError, match="Union mask is empty"):
        crop_to_union_mask(img, img, empty, empty)
