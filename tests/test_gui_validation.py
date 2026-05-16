"""Smoke tests for GUI input validation."""

from __future__ import annotations

import os
from collections.abc import Callable

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QTableWidgetItem  # noqa: E402

import app.gui as gui  # noqa: E402
from app.examples import get_example_1  # noqa: E402


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def capture_warnings(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    messages: list[str] = []

    def fake_warning(*args: object, **kwargs: object) -> int:
        if len(args) >= 3:
            messages.append(str(args[2]))
        return 0

    monkeypatch.setattr(gui.QMessageBox, "warning", fake_warning)
    return messages


def test_empty_numeric_cell_shows_human_error(
    qapp: QApplication,
    capture_warnings: list[str],
) -> None:
    window = gui.MainWindow()
    window.load_example(get_example_1())
    window.data_table.setItem(0, 1, QTableWidgetItem(""))

    window.calculate()

    assert capture_warnings
    assert "значение должно быть заполнено" in capture_warnings[0]
    assert "Расчёт не выполнен" in window.result_output.toPlainText()


def test_non_numeric_value_shows_human_error(
    qapp: QApplication,
    capture_warnings: list[str],
) -> None:
    window = gui.MainWindow()
    window.load_example(get_example_1())
    window.data_table.setItem(0, 1, QTableWidgetItem("abc"))

    window.calculate()

    assert capture_warnings
    assert "значение должно быть числом" in capture_warnings[0]
    assert "Расчёт не выполнен" in window.result_output.toPlainText()


def test_repeated_priority_shows_human_error(
    qapp: QApplication,
    capture_warnings: list[str],
) -> None:
    window = gui.MainWindow()
    window.load_example(get_example_1())
    window.criteria_table.setItem(1, 2, QTableWidgetItem("1"))

    window.calculate()

    assert capture_warnings
    assert "Порядок важности" in capture_warnings[0]
    assert "Расчёт не выполнен" in window.result_output.toPlainText()


def test_negative_concession_shows_human_error(
    qapp: QApplication,
    capture_warnings: list[str],
) -> None:
    window = gui.MainWindow()
    window.load_example(get_example_1())
    window.criteria_table.setItem(0, 4, QTableWidgetItem("-1"))

    window.calculate()

    assert capture_warnings
    assert "не может быть отрицательной" in capture_warnings[0]
    assert "Расчёт не выполнен" in window.result_output.toPlainText()


def test_missing_non_last_concession_shows_human_error(
    qapp: QApplication,
    capture_warnings: list[str],
) -> None:
    window = gui.MainWindow()
    window.load_example(get_example_1())
    window.criteria_table.setItem(0, 4, QTableWidgetItem(""))

    window.calculate()

    assert capture_warnings
    assert "должна быть задана уступка" in capture_warnings[0]
    assert "Расчёт не выполнен" in window.result_output.toPlainText()
