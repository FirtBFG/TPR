"""PySide6 GUI layer."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    """Main application window placeholder for stage 1."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TPR Concession Method")
        self.resize(1000, 700)
        self.setCentralWidget(QLabel("TPR Concession Method"))


def run_app() -> int:
    """Create and run the Qt application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
