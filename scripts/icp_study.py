# Sweeps known rotations (with scale and translation) of a GT mesh and measures how well the ICP recovers them.
"""Same as ``mesh-icp-study``; see ``meshcomparison.cli.icp_study``."""
import sys

from meshcomparison.cli.icp_study import main

if __name__ == "__main__":
    sys.exit(main())
