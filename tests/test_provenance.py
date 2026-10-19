import sys

from meshcomparison.common.provenance import collect_provenance
from meshcomparison.perceptual.pipeline import resolve_save_views


def test_provenance_has_expected_keys():
    info = collect_provenance()
    assert {"project_version", "python_version", "torch_version", "torch_cuda_version",
            "timestamp_utc"} <= set(info)
    assert info["python_version"] == sys.version.split()[0]


def test_provenance_does_not_import_torch(monkeypatch):
    monkeypatch.delitem(sys.modules, "torch", raising=False)
    assert collect_provenance()["torch_cuda_version"] == "not loaded"
    assert "torch" not in sys.modules


def test_resolve_save_views_default_with_100_views():
    assert resolve_save_views((1, 33, 66), 100) == [1, 33, 66]


def test_resolve_save_views_falls_back_with_few_views():
    assert resolve_save_views((1, 33, 66), 9) == [1, 3, 6]
    assert resolve_save_views((1, 33, 66), 1) == [1]


def test_resolve_save_views_spreads_views_when_some_are_missing():
    assert resolve_save_views((1, 33, 66), 40) == [1, 13, 26]
