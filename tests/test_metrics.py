# Deterministic tests of the geometric metrics (sampling, CD, HD95, F-score, visibility regions).
import numpy as np
import pytest
import trimesh

from meshcomparison.analysis.robustness import vertex_baseline
from meshcomparison.common.sampling import sample_surface
from meshcomparison.geometry.metrics import compute_metrics, icp_scale, tau_key


def _square(z=0.0, size=1.0):
    vertices = np.array([[0, 0, z], [size, 0, z], [size, size, z], [0, size, z]], dtype=np.float64)
    return trimesh.Trimesh(vertices, [[0, 1, 2], [0, 2, 3]], process=False)


def test_sampling_is_reproducible_and_on_the_surface():
    mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    a = sample_surface(mesh, 2000, seed=3)
    b = sample_surface(mesh, 2000, seed=3)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, sample_surface(mesh, 2000, seed=4))
    # every sample lies on a face of the unit box: inside it, with one coordinate at +-0.5
    assert np.all(np.abs(a) <= 0.5 + 1e-12)
    assert np.allclose(np.max(np.abs(a), axis=1), 0.5)


def test_sampling_is_proportional_to_area():
    # two disjoint triangles with areas 1 and 3: expect 25 % / 75 % of the samples (binomial 4-sigma tolerance)
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 2, 0], [5, 0, 0], [8, 0, 0], [5, 2, 0]], dtype=np.float64)
    mesh = trimesh.Trimesh(vertices, [[0, 1, 2], [3, 4, 5]], process=False)
    n = 40_000
    points = sample_surface(mesh, n, seed=0)
    share = np.mean(points[:, 0] < 2.5)
    assert abs(share - 0.25) < 4 * np.sqrt(0.25 * 0.75 / n)


def test_sampling_rejects_meshes_without_area():
    with pytest.raises(ValueError):
        sample_surface(trimesh.Trimesh(np.zeros((3, 3)), [[0, 1, 2]], process=False), 10, seed=0)


def test_identical_samples_give_zero_error_and_full_fscore():
    points = sample_surface(trimesh.creation.box(), 5000, seed=0)
    m = compute_metrics(points, points.copy())["all"]
    assert m["chamfer_mean"] == 0.0 and m["hd95"] == 0.0
    assert all(m[f"fscore_{tau_key(t)}"] == 1.0 for t in (0.01, 0.02, 0.05))


def test_parallel_offset_gives_known_distances_and_fscore_step():
    # the RM is the GT moved by delta along z, sampled with the same seed: every nearest distance is exactly delta
    delta = 0.03
    gt = sample_surface(_square(), 4000, seed=0)
    rm = gt + np.array([0.0, 0.0, delta])
    m = compute_metrics(gt, rm, taus=(0.02, 0.05))["all"]
    assert m["chamfer_mean"] == pytest.approx(delta, abs=1e-12)
    assert m["hd95"] == pytest.approx(delta, abs=1e-12)
    assert m["fscore_tau2pct"] == 0.0  # tau < delta
    assert m["fscore_tau5pct"] == 1.0  # tau > delta


def test_single_point_offset():
    a = np.array([[0.0, 0.0, 0.0]])
    b = np.array([[3.0, 4.0, 0.0]])
    m = compute_metrics(a, b, taus=(1.0, 10.0))["all"]
    assert m["chamfer_mean"] == pytest.approx(5.0)
    assert m["hd95"] == pytest.approx(5.0)
    assert m["mse"] == pytest.approx(25.0)
    assert m["fscore_tau100pct"] == 0.0 and m["fscore_tau1000pct"] == 1.0


def test_hd95_ignores_a_few_outliers_unlike_hausdorff():
    gt = sample_surface(_square(), 2000, seed=0)
    rm = gt.copy()
    rm[:10] += np.array([0.0, 0.0, 0.5])  # 0.5 % of the RM samples far from the GT
    assert vertex_baseline(gt, rm)["vertex_hausdorff"] == pytest.approx(0.5, abs=1e-9)
    assert compute_metrics(gt, rm)["all"]["hd95"] == 0.0


def test_precision_and_recall_follow_their_directions():
    # the RM covers only half of the GT square: precision 1, recall ~0.5 at a small tolerance
    gt = sample_surface(_square(), 20_000, seed=0)
    rm = gt[gt[:, 0] < 0.5]
    m = compute_metrics(gt, rm, taus=(0.01,))["all"]
    assert m["precision_tau1pct"] == 1.0
    assert m["recall_tau1pct"] == pytest.approx(0.5, abs=0.02)


def test_regions_split_gt_by_mask_and_rm_by_nearest_gt():
    gt = np.array([[0.0, 0, 0], [1.0, 0, 0]])
    rm = np.array([[0.0, 0, 0.1], [1.0, 0, 0.3]])
    out = compute_metrics(gt, rm, taus=(0.2,), gt_visible=np.array([True, False]))
    assert out["visible"]["gt_fraction"] == 0.5
    assert out["visible"]["chamfer_mean"] == pytest.approx(0.1)
    assert out["hidden"]["chamfer_mean"] == pytest.approx(0.3)
    assert out["visible"]["fscore_tau20pct"] == 1.0 and out["hidden"]["fscore_tau20pct"] == 0.0


def test_empty_region_is_nan():
    gt = np.array([[0.0, 0, 0], [1.0, 0, 0]])
    out = compute_metrics(gt, gt.copy(), taus=(0.1,), gt_visible=np.array([True, True]))
    assert out["hidden"]["gt_fraction"] == 0.0
    assert np.isnan(out["hidden"]["chamfer_mean"]) and np.isnan(out["hidden"]["fscore_tau10pct"])


def test_icp_scale_of_a_similarity_transform():
    angle = np.deg2rad(30)
    rotation = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
    transform = np.eye(4)
    transform[:3, :3] = 1.7 * rotation
    transform[:3, 3] = [1, 2, 3]
    assert icp_scale(transform) == pytest.approx(1.7)
    assert icp_scale(np.eye(4)) == 1.0


def test_visibility_of_a_box_seen_from_above():
    pytest.importorskip("pyrender")
    from meshcomparison.geometry.visibility import gt_visibility

    box = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    top = np.array([[0.1, 0.2, 0.5], [-0.3, 0.1, 0.5]])
    bottom = np.array([[0.1, 0.2, -0.5], [-0.3, 0.1, -0.5]])
    try:
        visible = gt_visibility(box, np.vstack([top, bottom]), azimuth_deg=0.0, elevation_deg=89.0, resolution=256)
    except Exception as exc:  # no offscreen OpenGL available (headless machine)
        pytest.skip(f"offscreen rendering unavailable: {exc}")
    assert visible.tolist() == [True, True, False, False]


def test_point_to_surface_has_no_sampling_floor():
    # independent samples of the same mesh: zero error and full scores, unlike sample-to-sample distances
    box = trimesh.creation.box()
    gt_points, gt_normals = sample_surface(box, 5000, 0, return_normals=True)
    rm_points, rm_normals = sample_surface(box, 5000, 1, return_normals=True)
    nearest = compute_metrics(gt_points, rm_points)["all"]
    exact = compute_metrics(gt_points, rm_points, gt_normals=gt_normals, rm_normals=rm_normals,
                            gt_mesh=box, rm_mesh=box)["all"]
    assert nearest["chamfer_mean"] > 1e-3  # the floor of the sample-to-sample distance
    assert exact["chamfer_mean"] < 1e-7 and exact["hd95"] < 1e-6
    assert exact["fscore_tau1pct"] == 1.0 and exact["normal_consistency"] == pytest.approx(1.0, abs=1e-6)


def test_point_to_surface_offset_is_exact_with_independent_samples():
    delta = 0.03
    gt_mesh, rm_mesh = _square(), _square(z=delta)
    m = compute_metrics(sample_surface(gt_mesh, 3000, 0), sample_surface(rm_mesh, 3000, 1), taus=(0.02, 0.05),
                        gt_mesh=gt_mesh, rm_mesh=rm_mesh)["all"]
    assert m["chamfer_mean"] == pytest.approx(delta, abs=1e-6)
    assert m["hd95"] == pytest.approx(delta, abs=1e-6)
    assert m["fscore_tau2pct"] == 0.0 and m["fscore_tau5pct"] == 1.0


def test_point_to_surface_chamfer_does_not_depend_on_the_sample_count():
    # a 0.02 bump on a densified square: the estimate converges to the same value at 1e3 and 1e5 samples
    gt_mesh = trimesh.remesh.subdivide_to_size(*(_square().vertices, _square().faces), max_edge=0.02)
    gt_mesh = trimesh.Trimesh(*gt_mesh, process=False)
    vertices = np.asarray(gt_mesh.vertices).copy()
    vertices[:, 2] = 0.02 * np.exp(-np.sum((vertices[:, :2] - 0.5) ** 2, axis=1) / 0.02)
    rm_mesh = trimesh.Trimesh(vertices, gt_mesh.faces, process=False)
    values = []
    for n in (1_000, 100_000):
        m = compute_metrics(sample_surface(gt_mesh, n, 0), sample_surface(rm_mesh, n, 1),
                            gt_mesh=gt_mesh, rm_mesh=rm_mesh)["all"]
        values.append(m["chamfer_mean"])
    assert values[0] == pytest.approx(values[1], rel=0.05)  # Monte Carlo noise at 1e3 samples


def test_point_to_surface_normal_consistency_of_a_tilted_plane():
    # GT square in z = 0, RM square tilted by 30 degrees: every closest triangle has the other plane's normal
    angle = np.deg2rad(30.0)
    gt_mesh = _square()
    rm_mesh = _square()
    rotation = np.array([[1, 0, 0], [0, np.cos(angle), -np.sin(angle)], [0, np.sin(angle), np.cos(angle)]])
    rm_mesh.vertices = np.asarray(rm_mesh.vertices) @ rotation.T
    gt_points, gt_normals = sample_surface(gt_mesh, 4000, 0, return_normals=True)
    rm_points, rm_normals = sample_surface(rm_mesh, 4000, 1, return_normals=True)
    m = compute_metrics(gt_points, rm_points, gt_normals=gt_normals, rm_normals=rm_normals,
                        gt_mesh=gt_mesh, rm_mesh=rm_mesh)["all"]
    assert m["normal_consistency"] == pytest.approx(np.cos(angle), abs=1e-6)
