"""PySide6 GUI layer."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.concessions import solve_concession_method
from app.examples import DecisionExample, get_example_1, get_example_2, get_variant_22
from app.models import Alternative, ConcessionResult, Criterion


DATA_MIN_WIDTH = 560
CRITERIA_MIN_WIDTH = 560


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TPR Concession Method")
        self.resize(1180, 760)

        self.alternative_count_input = QSpinBox()
        self.alternative_count_input.setRange(2, 100)
        self.alternative_count_input.setValue(3)

        self.criteria_count_input = QSpinBox()
        self.criteria_count_input.setRange(2, 30)
        self.criteria_count_input.setValue(3)

        self.data_table = QTableWidget()
        self.criteria_table = QTableWidget()
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)

        self._build_ui()
        self.create_tables()

    def _build_ui(self) -> None:
        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        root_layout.addWidget(self._build_size_group())
        root_layout.addLayout(self._build_tables_layout(), stretch=1)
        root_layout.addWidget(self._build_buttons_group())
        root_layout.addWidget(self._build_result_group(), stretch=1)

        self.setCentralWidget(central)

    def _build_size_group(self) -> QGroupBox:
        group = QGroupBox("Размер задачи")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Количество альтернатив:"))
        layout.addWidget(self.alternative_count_input)
        layout.addWidget(QLabel("Количество критериев:"))
        layout.addWidget(self.criteria_count_input)

        create_button = QPushButton("Создать таблицу")
        create_button.clicked.connect(self.create_tables)
        layout.addWidget(create_button)
        layout.addStretch()

        return group

    def _build_tables_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(self._build_data_group(), stretch=3)
        layout.addWidget(self._build_criteria_group(), stretch=2)
        return layout

    def _build_data_group(self) -> QGroupBox:
        group = QGroupBox("Исходные данные")
        layout = QVBoxLayout(group)
        self.data_table.setMinimumWidth(DATA_MIN_WIDTH)
        self.data_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.data_table)
        return group

    def _build_criteria_group(self) -> QGroupBox:
        group = QGroupBox("Критерии")
        layout = QVBoxLayout(group)
        self.criteria_table.setMinimumWidth(CRITERIA_MIN_WIDTH)
        self.criteria_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.criteria_table)
        return group

    def _build_buttons_group(self) -> QGroupBox:
        group = QGroupBox("Управление")
        layout = QGridLayout(group)

        calculate_button = QPushButton("Рассчитать")
        calculate_button.clicked.connect(self.calculate)

        clear_button = QPushButton("Очистить")
        clear_button.clicked.connect(self.clear_tables)

        example_1_button = QPushButton("Заполнить пример 1")
        example_1_button.clicked.connect(lambda: self.load_example(get_example_1()))

        example_2_button = QPushButton("Заполнить пример 2")
        example_2_button.clicked.connect(lambda: self.load_example(get_example_2()))

        variant_22_button = QPushButton("Заполнить вариант 22")
        variant_22_button.clicked.connect(lambda: self.load_example(get_variant_22()))

        exit_button = QPushButton("Выход")
        exit_button.clicked.connect(self.close)

        buttons = [
            calculate_button,
            clear_button,
            example_1_button,
            example_2_button,
            variant_22_button,
            exit_button,
        ]
        for index, button in enumerate(buttons):
            layout.addWidget(button, index // 3, index % 3)

        return group

    def _build_result_group(self) -> QGroupBox:
        group = QGroupBox("Результат")
        layout = QVBoxLayout(group)
        self.result_output.setPlaceholderText("Здесь появится протокол расчёта.")
        layout.addWidget(self.result_output)
        return group

    def create_tables(self) -> None:
        alternative_count = self.alternative_count_input.value()
        criteria_count = self.criteria_count_input.value()
        criteria_names = [f"K{index}" for index in range(1, criteria_count + 1)]

        self._create_data_table(alternative_count, criteria_names)
        self._create_criteria_table(criteria_names)
        self.result_output.clear()

    def clear_tables(self) -> None:
        self.create_tables()

    def calculate(self) -> None:
        try:
            alternatives = self._read_alternatives()
            criteria = self._read_criteria()
        except ValueError as error:
            message = str(error)
            self._show_error(message)
            self.result_output.setPlainText(f"Расчёт не выполнен.\n\n{message}")
            return

        result = solve_concession_method(alternatives, criteria)
        if not result.success:
            message = result.error_message or "Не удалось выполнить расчёт."
            self._show_error(message)
            self.result_output.setPlainText(f"Расчёт не выполнен.\n\n{message}")
            return

        self.result_output.setPlainText(self._format_result(result))

    def load_example(self, example: DecisionExample) -> None:
        self.alternative_count_input.setValue(len(example.alternatives))
        self.criteria_count_input.setValue(len(example.criteria))

        criteria_names = [criterion.name for criterion in example.criteria]
        self._create_data_table(len(example.alternatives), criteria_names)
        self._create_criteria_table(criteria_names)

        for row, alternative in enumerate(example.alternatives):
            self._set_table_text(self.data_table, row, 0, alternative.name)
            for column, criterion_name in enumerate(criteria_names, start=1):
                value = alternative.values[criterion_name]
                self._set_table_text(self.data_table, row, column, self._format_number(value))

        for row, criterion in enumerate(example.criteria):
            self._set_table_text(self.criteria_table, row, 0, criterion.name)
            self._set_combo_value(self.criteria_table, row, 1, criterion.direction)
            self._set_table_text(self.criteria_table, row, 2, str(criterion.priority))
            self._set_combo_value(self.criteria_table, row, 3, criterion.concession_type)
            concession = "" if criterion.concession is None else self._format_number(criterion.concession)
            self._set_table_text(self.criteria_table, row, 4, concession)

        expected = ", ".join(example.expected_winners) if example.expected_winners else "не задан"
        self.result_output.setPlainText(
            f"{example.title}\n"
            f"Данные загружены. Ожидаемый результат для проверки: {expected}."
        )

    def _create_data_table(self, alternative_count: int, criteria_names: list[str]) -> None:
        self.data_table.clear()
        self.data_table.setRowCount(alternative_count)
        self.data_table.setColumnCount(len(criteria_names) + 1)
        self.data_table.setHorizontalHeaderLabels(["Альтернатива", *criteria_names])

        for row in range(alternative_count):
            self._set_table_text(self.data_table, row, 0, f"A{row + 1}")
            for column in range(1, len(criteria_names) + 1):
                self._set_table_text(self.data_table, row, column, "")

        self.data_table.resizeColumnsToContents()

    def _create_criteria_table(self, criteria_names: list[str]) -> None:
        self.criteria_table.clear()
        self.criteria_table.setRowCount(len(criteria_names))
        self.criteria_table.setColumnCount(5)
        self.criteria_table.setHorizontalHeaderLabels(
            ["Критерий", "Направление", "Порядок", "Тип уступки", "Уступка"]
        )

        for row, criterion_name in enumerate(criteria_names):
            self._set_table_text(self.criteria_table, row, 0, criterion_name)
            self.criteria_table.setCellWidget(row, 1, self._make_combo(["max", "min"]))
            self._set_table_text(self.criteria_table, row, 2, str(row + 1))
            self.criteria_table.setCellWidget(row, 3, self._make_combo(["absolute", "percent"]))
            concession = "" if row == len(criteria_names) - 1 else "0"
            self._set_table_text(self.criteria_table, row, 4, concession)

        self.criteria_table.resizeColumnsToContents()

    def _read_alternatives(self) -> list[Alternative]:
        criteria_names = [self._table_text(self.criteria_table, row, 0) for row in range(self.criteria_table.rowCount())]
        alternatives: list[Alternative] = []

        for row in range(self.data_table.rowCount()):
            alternative_name = self._table_text(self.data_table, row, 0)
            if not alternative_name:
                raise ValueError(f"Строка {row + 1}: у альтернативы не задано название.")

            values: dict[str, float] = {}
            for column, criterion_name in enumerate(criteria_names, start=1):
                raw_value = self._table_text(self.data_table, row, column)
                values[criterion_name] = self._parse_float(
                    raw_value,
                    f"Строка {row + 1}, критерий {criterion_name}",
                )
            alternatives.append(Alternative(alternative_name, values))

        return alternatives

    def _read_criteria(self) -> list[Criterion]:
        criteria: list[Criterion] = []

        for row in range(self.criteria_table.rowCount()):
            criterion_name = self._table_text(self.criteria_table, row, 0)
            if not criterion_name:
                raise ValueError(f"Строка критериев {row + 1}: не задано название критерия.")

            direction = self._combo_text(self.criteria_table, row, 1)
            concession_type = self._combo_text(self.criteria_table, row, 3)
            priority = self._parse_int(
                self._table_text(self.criteria_table, row, 2),
                f"Критерий {criterion_name}: порядок важности",
            )
            concession_text = self._table_text(self.criteria_table, row, 4)
            concession = (
                None
                if concession_text == ""
                else self._parse_float(concession_text, f"Критерий {criterion_name}: уступка")
            )

            criteria.append(
                Criterion(
                    name=criterion_name,
                    direction=direction,  # type: ignore[arg-type]
                    priority=priority,
                    concession=concession,
                    concession_type=concession_type,  # type: ignore[arg-type]
                )
            )

        return criteria

    def _format_result(self, result: ConcessionResult) -> str:
        lines = [
            "Результат расчёта методом уступок",
            "",
            f"Итоговая альтернатива: {', '.join(result.winners)}",
            f"Итоговое множество после уступок: {', '.join(result.final_alternatives)}",
            "",
            "Пошаговый протокол:",
        ]

        for step in result.steps:
            applied_concession = (
                "не применяется"
                if step.applied_concession is None
                else self._format_number(step.applied_concession)
            )
            boundary = (
                "не применяется"
                if step.boundary_value is None
                else self._format_number(step.boundary_value)
            )
            remaining = ", ".join(step.remaining_alternatives) or "нет"
            excluded = ", ".join(step.excluded_alternatives) or "нет"

            lines.extend(
                [
                    "",
                    f"Шаг {step.step_number}. Критерий {step.criterion} ({step.direction})",
                    f"Оптимальное значение: {self._format_number(step.optimum_value)}",
                    f"Уступка: {applied_concession}",
                    f"Граница: {boundary}",
                    f"Ограничение: {step.constraint_description}",
                    f"Остались: {remaining}",
                    f"Исключены: {excluded}",
                ]
            )

        lines.extend(["", "Исключённые альтернативы по шагам:"])
        for step in result.steps:
            excluded = ", ".join(step.excluded_alternatives) or "нет"
            lines.append(f"Шаг {step.step_number}, {step.criterion}: {excluded}")

        return "\n".join(lines)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Ошибка ввода", message)

    @staticmethod
    def _make_combo(values: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.addItems(values)
        combo.setEditable(False)
        return combo

    @staticmethod
    def _set_combo_value(table: QTableWidget, row: int, column: int, value: str) -> None:
        widget = table.cellWidget(row, column)
        if isinstance(widget, QComboBox):
            index = widget.findText(value)
            if index >= 0:
                widget.setCurrentIndex(index)

    @staticmethod
    def _set_table_text(table: QTableWidget, row: int, column: int, value: str) -> None:
        item = QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, column, item)

    @staticmethod
    def _table_text(table: QTableWidget, row: int, column: int) -> str:
        item = table.item(row, column)
        return "" if item is None else item.text().strip()

    @staticmethod
    def _combo_text(table: QTableWidget, row: int, column: int) -> str:
        widget = table.cellWidget(row, column)
        if isinstance(widget, QComboBox):
            return widget.currentText().strip()
        return ""

    @staticmethod
    def _parse_float(value: str, field_name: str) -> float:
        normalized = value.strip().replace(",", ".")
        if not normalized:
            raise ValueError(f"{field_name}: значение должно быть заполнено.")
        try:
            return float(normalized)
        except ValueError as error:
            raise ValueError(f"{field_name}: значение должно быть числом.") from error

    @staticmethod
    def _parse_int(value: str, field_name: str) -> int:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name}: значение должно быть заполнено.")
        try:
            return int(normalized)
        except ValueError as error:
            raise ValueError(f"{field_name}: значение должно быть целым числом.") from error

    @staticmethod
    def _format_number(value: float) -> str:
        return str(int(value)) if float(value).is_integer() else str(value)


def run_app() -> int:
    """Create and run the Qt application."""

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
