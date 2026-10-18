from meshcomparison.gui.config import ProgressTracker, RunConfig, build_commands, validate


def _cfg(tmp_path, **kw):
    gt = tmp_path / "gt.stl"
    rm = tmp_path / "rm.stl"
    gt.write_text("x")
    rm.write_text("x")
    return RunConfig(gt=str(gt), rm=str(rm), out=str(tmp_path / "out"), **kw)


def test_validate_accepts_existing_files(tmp_path):
    assert validate(_cfg(tmp_path)) == []


def test_validate_rejects_fbx_and_missing(tmp_path):
    cfg = _cfg(tmp_path)
    cfg.gt = str(tmp_path / "model.fbx")
    cfg.rm = str(tmp_path / "missing.stl")
    errors = validate(cfg)
    assert any("FBX" in e for e in errors)
    assert any("not found" in e for e in errors)


def test_validate_requires_a_pipeline(tmp_path):
    assert validate(_cfg(tmp_path, run_geometry=False, run_perceptual=False))


def test_build_commands_order_and_device(tmp_path):
    python, commands = build_commands(_cfg(tmp_path, device="cuda"), python="py")
    assert python == "py"
    assert [c.name for c in commands] == ["Geometric", "Perceptual"]
    assert "meshcomparison.geometry" in commands[0].args
    assert "--azimuth" in commands[0].args and "--device" not in commands[0].args
    assert commands[1].args[commands[1].args.index("--device") + 1] == "cuda"


def test_progress_tracker_two_commands():
    t = ProgressTracker(2)
    t.start_command(0)
    t.feed("[1/7] Loading meshes...")
    assert t.fraction == 0.0
    t.feed("[5/7] Computing final metrics...")
    assert abs(t.fraction - (4 / 7) / 2) < 1e-9
    t.finish_command()
    assert abs(t.fraction - 0.5) < 1e-9
    t.start_command(1)
    t.feed("[6/8] Rendering 100 views and computing metrics...")
    t.feed("    View 050/100 | az=  1.00 | LPIPS=0.1")
    assert abs(t.fraction - (0.5 + (5.5 / 8) / 2)) < 1e-9
