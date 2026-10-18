import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("open3d")
pytest.importorskip("pyrender")

from mesh_eval_pipeline import (
    apply_transform_points,
    compute_metrics,
    initial_similarity_from_bboxes,
    maybe_subsample,
    symmetric_mse,
)


@pytest.fixture
def cloud():
    rng = np.random.default_rng(0)
    return rng.random((200, 3))


def test_identical_clouds_have_zero_error(cloud):
    m = compute_metrics(cloud, cloud.copy())
    assert m["chamfer_mean"] == pytest.approx(0.0)
    assert m["hausdorff"] == pytest.approx(0.0)
    assert m["rmse"] == pytest.approx(0.0)
    assert symmetric_mse(cloud, cloud.copy()) == pytest.approx(0.0)


def test_single_point_offset():
    a = np.array([[0.0, 0.0, 0.0]])
    b = np.array([[3.0, 4.0, 0.0]])
    m = compute_metrics(a, b)
    assert m["chamfer_mean"] == pytest.approx(5.0)
    assert m["hausdorff"] == pytest.approx(5.0)
    assert m["rmse"] == pytest.approx(5.0)


def test_maybe_subsample_limits_size(cloud):
    assert len(maybe_subsample(cloud, max_points=50)) == 50
    assert maybe_subsample(cloud, max_points=1000) is cloud


def test_bbox_similarity_aligns_scaled_shifted_cloud(cloud):
    moved = cloud * 2.0 + np.array([1.0, -2.0, 3.0])
    T = initial_similarity_from_bboxes(moved, cloud)
    back = apply_transform_points(moved, T)
    assert np.allclose(back.min(axis=0), cloud.min(axis=0), atol=1e-6)
    assert np.allclose(back.max(axis=0), cloud.max(axis=0), atol=1e-6)
