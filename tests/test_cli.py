# Tests that every command-line tool starts (help text) both as a script and as a package module.
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ("check_gt", "fetch_gso", "plot_metrics", "robustness_study", "icp_study")


@pytest.mark.parametrize("name", COMMANDS)
def test_script_and_module_show_help(name):
    for args in ([str(ROOT / "scripts" / f"{name}.py")], ["-m", f"meshcomparison.cli.{name}"]):
        result = subprocess.run([sys.executable, *args, "--help"], capture_output=True, text=True, timeout=120)
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout
