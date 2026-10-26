# Downloads the selected Google Scanned Objects (data/gso/selection.csv) from Gazebo Fuel and writes their manifest.
"""Same as ``mesh-fetch-gso``; see ``meshcomparison.cli.fetch_gso``."""
import sys

from meshcomparison.cli.fetch_gso import main

if __name__ == "__main__":
    sys.exit(main())
