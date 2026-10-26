# Checks candidate ground-truth meshes (and, optionally, their manifest) and writes a report before a benchmark.
"""Same as ``mesh-check-gt``; see ``meshcomparison.cli.check_gt``."""
import sys

from meshcomparison.cli.check_gt import main

if __name__ == "__main__":
    sys.exit(main())
