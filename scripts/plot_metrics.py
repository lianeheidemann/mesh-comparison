# Saves figures of the metrics of a finished run (F(tau), regions, perceptual per view, sampling spread).
"""Same as ``mesh-plot-metrics``; see ``meshcomparison.cli.plot_metrics``."""
import sys

from meshcomparison.cli.plot_metrics import main

if __name__ == "__main__":
    sys.exit(main())
