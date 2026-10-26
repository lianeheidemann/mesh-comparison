# Runs the metric invariance and sensitivity study (ADR 0002) on one GT mesh and writes CSVs and figures.
"""Same as ``mesh-robustness-study``; see ``meshcomparison.cli.robustness_study``."""
import sys

from meshcomparison.cli.robustness_study import main

if __name__ == "__main__":
    sys.exit(main())
