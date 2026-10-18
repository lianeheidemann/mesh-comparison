from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

ACCENT = "#3d8bd9"

_DARK = {
    "window": "#23272e", "base": "#1b1e24", "alt": "#262a32", "text": "#e3e6ea",
    "muted": "#8d95a1", "button": "#2d323b", "border": "#3a404a",
}
_LIGHT = {
    "window": "#f3f4f6", "base": "#ffffff", "alt": "#f7f8fa", "text": "#1f2328",
    "muted": "#6a727d", "button": "#e8eaee", "border": "#cfd4db",
}


def apply_theme(app: QApplication, dark: bool):
    c = _DARK if dark else _LIGHT
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(c["window"]))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(c["text"]))
    pal.setColor(QPalette.ColorRole.Base, QColor(c["base"]))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(c["alt"]))
    pal.setColor(QPalette.ColorRole.Text, QColor(c["text"]))
    pal.setColor(QPalette.ColorRole.Button, QColor(c["button"]))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(c["text"]))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(c["base"]))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor(c["text"]))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(c["muted"]))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(c["muted"]))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(c["muted"]))
    app.setPalette(pal)

    app.setStyleSheet(f"""
        QGroupBox {{ border: 1px solid {c['border']}; border-radius: 6px; margin-top: 14px;
            padding: 10px 8px 8px 8px; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; font-weight: 600; }}
        QPushButton {{ border: 1px solid {c['border']}; border-radius: 5px; padding: 5px 12px;
            background: {c['button']}; }}
        QPushButton:hover {{ border-color: {ACCENT}; }}
        QPushButton:disabled {{ color: {c['muted']}; }}
        QPushButton#primary {{ background: {ACCENT}; color: white; border: none; font-weight: 600; padding: 8px 14px; }}
        QPushButton#primary:disabled {{ background: {c['border']}; color: {c['muted']}; }}
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit {{
            border: 1px solid {c['border']}; border-radius: 4px; padding: 3px 5px; background: {c['base']}; }}
        QTabWidget::pane {{ border: 1px solid {c['border']}; border-radius: 4px; }}
        QTabBar::tab {{ padding: 6px 14px; border: 1px solid transparent; }}
        QTabBar::tab:selected {{ border-bottom: 2px solid {ACCENT}; font-weight: 600; }}
        QProgressBar {{ border: 1px solid {c['border']}; border-radius: 4px; text-align: center; height: 16px; }}
        QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
        QLabel#hint {{ color: {c['muted']}; }}
        QLabel#warning {{ color: #d9822b; }}
        QHeaderView::section {{ background: {c['button']}; border: none; padding: 4px 8px; font-weight: 600; }}
    """)
