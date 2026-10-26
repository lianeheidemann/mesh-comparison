# Recovery of known similarity transforms by the conditional ICP (unit and end-to-end through the pipeline).
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import trimesh

from meshcomparison.analysis.robustness import icp_recovery, normalized, similarity_transform

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"


@pytest.fixture(scope="module")
def asymmetric_box():
    # unequal extents and an offset from the origin: no symmetry that would make the rotation ambiguous
    box = normalized(trimesh.creation.box(extents=(1.0, 0.6, 0.3)))
    box.apply_translation([0.1, 0.05, 0.0])
    return box


def test_icp_recovers_rotation_translation_and_scale(asymmetric_box):
    applied = similarity_transform(15.0, axis=(0, 0, 1), scale=1.3, translation=(0.2, 0.0, 0.0))
    r = icp_recovery(asymmetric_box, applied, n_samples=20_000)
    assert r["alignment_triggered"]
    assert r["rotation_error_deg"] < 1.0
    assert abs(r["scale_error"]) < 0.01
    assert r["icp_scale"] == pytest.approx(1 / 1.3, rel=0.01)
    assert r["chamfer"] < 1e-3 and r["fscore_tau1pct"] > 0.99


def test_icp_is_not_triggered_for_the_identity(asymmetric_box):
    r = icp_recovery(asymmetric_box, np.eye(4), n_samples=20_000)
    assert not r["alignment_triggered"]
    assert r["rotation_error_deg"] == 0.0 and r["scale_error"] == pytest.approx(0.0, abs=1e-12)
    assert r["chamfer"] < 1e-6


def test_pipeline_aligns_a_known_transform(tmp_path):
    from meshcomparison.geometry.pipeline import run_pipeline

    gt = trimesh.load(SAMPLES / "gt.stl")
    rm = gt.copy()
    rm.apply_transform(similarity_transform(10.0, axis=(0, 0, 1), scale=0.8, translation=(0.3, -0.2, 0.1)))
    rm_path = tmp_path / "rm.stl"
    rm.export(rm_path)
    try:
        run_pipeline(str(SAMPLES / "gt.stl"), str(rm_path), str(tmp_path / "out"), width=96, height=72)
    except Exception as exc:  # no offscreen OpenGL available (headless machine)
        pytest.skip(f"offscreen rendering unavailable: {exc}")

    metrics = pd.read_csv(tmp_path / "out" / "metrics" / "metrics_geometry.csv").iloc[0]
    assert metrics["alignment_triggered"]
    assert metrics["icp_scale"] == pytest.approx(1 / 0.8, rel=0.01)
    assert metrics["chamfer_mean_normalized"] < 1e-3
    assert metrics["fscore_tau1pct"] > 0.99
