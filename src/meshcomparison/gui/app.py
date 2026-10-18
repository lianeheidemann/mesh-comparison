import sys


def main(argv=None):
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication

    from .main_window import MainWindow
    from .theme import apply_theme

    app = QApplication(sys.argv if argv is None else argv)
    app.setOrganizationName("MeshComparison")
    app.setApplicationName("Mesh Comparison")
    apply_theme(app, QSettings().value("dark", True, type=bool))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
