# Tests of normal consistency, the F(tau) curve and the invariance/sensitivity study helpers.
import numpy as np
import pytest
import trimesh

from meshcomparison.analysis.robustness import (
    geometric_metrics, half_subdivided, local_bump, normal_noise, normalized, permute_vertices, remove_region,
    subdivide,
)
from meshcomparison.common.sampling import sample_surface
from meshcomparison.geometry.metrics import compute_metrics, fscore_auc, fscore_curve, normal_consistency

N = 20_000  # samples per mesh in these tests (the pipeline uses 100 000)


def _square(angle_deg=0.0):
    """Unit square in the xy plane, optionally rotated about the x axis through its centre line."""
    vertices = np.array([[0, -0.5, 0], [1, -0.5, 0], [1, 0.5, 0], [0, 0.5, 0]], dtype=np.float64)
    a = np.deg2rad(angle_deg)
    rotation = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    return trimesh.Trimesh(vertices @ rotation.T, [[0, 1, 2], [0, 2, 3]], process=False)


@pytest.fixture(scope="module")
def box():
    return normalized(trimesh.creation.box(extents=(1.0, 0.6, 0.4)))


def test_sample_normals_are_unit_face_normals_and_do_not_change_points():
    mesh = trimesh.creation.box()
    points, normals = sample_surface(mesh, 1000, seed=5, return_normals=True)
    assert np.array_equal(points, sample_surface(mesh, 1000, seed=5))
    assert np.allclose(np.linalg.norm(normals, axis=1), 1.0)
    # box face normals are the axis whose coordinate is at +-0.5
    axis = np.argmax(np.abs(points), axis=1)
    assert np.allclose(np.abs(normals[np.arange(1000), axis]), 1.0)


def test_normal_consistency_of_tilted_plane_is_cosine():
    for angle in (0.0, 30.0, 60.0):
        gt_points, gt_normals = sample_surface(_square(), N, 0, return_normals=True)
        rm_points, rm_normals = sample_surface(_square(angle), N, 1, return_normals=True)
        m = compute_metrics(gt_points, rm_points, gt_normals=gt_normals, rm_normals=rm_normals)["all"]
        assert m["normal_consistency"] == pytest.approx(np.cos(np.deg2rad(angle)), abs=1e-9)


def test_normal_consistency_ignores_orientation_and_needs_normals():
    n = np.array([[0.0, 0.0, 1.0]])
    assert normal_consistency(n, -n, n, -n) == 1.0
    points = np.zeros((1, 3))
    assert np.isnan(compute_metrics(points, points)["all"]["normal_consistency"])


def test_fscore_curve_is_monotonic_and_auc_bounded():
    rng = np.random.default_rng(0)
    d_gt2rm, d_rm2gt = rng.exponential(0.02, 500), rng.exponential(0.03, 400)
    taus, precision, recall, fscore = fscore_curve(d_gt2rm, d_rm2gt)
    assert np.all(np.diff(precision) >= 0) and np.all(np.diff(recall) >= 0) and np.all(np.diff(fscore) >= 0)
    assert 0.0 < fscore_auc(taus, fscore) < 1.0
    assert fscore_auc(taus, np.ones_like(taus)) == pytest.approx(1.0)
    assert fscore_auc(taus, np.zeros_like(taus)) == 0.0


def test_vertex_permutation_changes_no_metric(box):
    dense = subdivide(box, 2)
    reference = geometric_metrics(dense, dense, n_samples=N)
    permuted = geometric_metrics(dense, permute_vertices(dense, seed=3), n_samples=N)
    assert permuted == reference  # same faces in the same order: identical samples, exactly equal values


def test_retriangulation_moves_vertex_baseline_but_not_surface_metrics(box):
    # same surface, uneven vertex density: the vertex baseline grows, the point-to-surface metrics stay exact
    uneven = geometric_metrics(box, half_subdivided(box, 2), n_samples=N)
    assert geometric_metrics(box, box, n_samples=N)["vertex_chamfer"] == 0.0
    assert uneven["vertex_chamfer"] > 0.02
    assert uneven["chamfer"] < 1e-6 and uneven["hd95"] < 1e-6  # float32 round-off of the closest-point query
    assert uneven["fscore_tau1pct"] == 1.0 and uneven["fscore_auc"] == pytest.approx(1.0)
    assert uneven["normal_consistency"] == pytest.approx(1.0, abs=1e-6)


def test_perturbations_degrade_surface_metrics_monotonically(box):
    dense = subdivide(box, 3)
    noise = [geometric_metrics(dense, normal_noise(dense, s), n_samples=N)["chamfer"] for s in (0, 0.005, 0.02)]
    assert noise[0] < noise[1] < noise[2]
    bump = [geometric_metrics(dense, local_bump(dense, a), n_samples=N)["hd95"] for a in (0, 0.05, 0.1)]
    assert bump[0] <= bump[1] <= bump[2]


def test_removed_region_lowers_recall_not_precision(box):
    dense = subdivide(box, 3)
    gt_points = sample_surface(dense, N, 0)
    rm = remove_region(dense, 0.2)
    assert rm.area == pytest.approx(0.8 * dense.area, rel=0.05)
    m = compute_metrics(gt_points, sample_surface(rm, N, 1), taus=(0.01,), gt_mesh=dense, rm_mesh=rm)["all"]
    assert m["precision_tau1pct"] == 1.0  # what is left lies on the GT surface
    assert m["recall_tau1pct"] == pytest.approx(0.8, abs=0.02)  # 20 % of the area is missing (+ a 1 % rim)
