import os
from pathlib import Path
import sys

# Interface zoom: 0.8 = 20 % smaller than the system scale. Set QT_SCALE_FACTOR to override (1 = system scale).
DEFAULT_SCALE_FACTOR = "0.8"


def main(argv=None):
    os.environ.setdefault("QT_SCALE_FACTOR", DEFAULT_SCALE_FACTOR)
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from .main_window import MainWindow
    from .theme import apply_theme

    app = QApplication(sys.argv if argv is None else argv)
    app.setOrganizationName("MeshComparison")
    app.setApplicationName("Mesh Comparison")
    app.setWindowIcon(QIcon(str(Path(__file__).with_name("icon.ico"))))
    apply_theme(app, QSettings().value("dark", True, type=bool))

    window = MainWindow()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
