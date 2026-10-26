import numpy as np
import pytest
import trimesh

from meshcomparison.common.alignment import initial_similarity_from_bboxes
from meshcomparison.common.distances import maybe_subsample, surface_distances, symmetric_surface_mse
from meshcomparison.common.sampling import sample_surface
from meshcomparison.common.transforms import apply_transform_points


@pytest.fixture
def cloud():
    rng = np.random.default_rng(0)
    return rng.random((200, 3))


def _unit_triangle():
    return trimesh.Trimesh([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], [[0, 1, 2]], process=False)


def test_surface_distance_to_face_edge_and_vertex():
    points = np.array([[0.2, 0.2, 0.5],    # above the face: closest point inside the triangle
                       [0.5, -0.3, 0.4],   # beside the edge y = 0: closest point on that edge
                       [-0.3, -0.4, 0.0]])  # beyond vertex (0, 0, 0)
    distances, normals = surface_distances(points, _unit_triangle())
    assert np.allclose(distances, [0.5, 0.5, 0.5], atol=1e-6)
    assert np.allclose(np.abs(normals[:, 2]), 1.0)


def test_symmetric_surface_mse_is_zero_for_the_same_surface_and_delta_squared_for_a_shift():
    box = trimesh.creation.box()
    a, b = sample_surface(box, 5000, 0), sample_surface(box, 5000, 1)
    assert symmetric_surface_mse(a, b, box, box) < 1e-12  # independent samples, same surface

    square = trimesh.Trimesh([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], [[0, 1, 2], [0, 2, 3]], process=False)
    shifted = square.copy()
    shifted.apply_translation([0.0, 0.0, 0.03])
    pa, pb = sample_surface(square, 2000, 0), sample_surface(shifted, 2000, 1)
    assert symmetric_surface_mse(pa, pb, square, shifted) == pytest.approx(0.03 ** 2, rel=1e-4)


def test_maybe_subsample_limits_size(cloud):
    assert len(maybe_subsample(cloud, max_points=50)) == 50
    assert maybe_subsample(cloud, max_points=1000) is cloud


def test_bbox_similarity_aligns_scaled_shifted_cloud(cloud):
    moved = cloud * 2.0 + np.array([1.0, -2.0, 3.0])
    T = initial_similarity_from_bboxes(moved, cloud)
    back = apply_transform_points(moved, T)
    assert np.allclose(back.min(axis=0), cloud.min(axis=0), atol=1e-6)
    assert np.allclose(back.max(axis=0), cloud.max(axis=0), atol=1e-6)
