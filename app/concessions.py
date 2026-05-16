"""Pure calculation core for the concession method.

This module must stay independent from Qt.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import isclose, isfinite

from app.models import Alternative, ConcessionResult, ConcessionStep, Criterion, Direction


EPSILON = 1e-9


class ConcessionMethodError(ValueError):
    """Base controlled error for the calculation core."""


class ValidationError(ConcessionMethodError):
    """Input data failed validation."""


class EmptyAlternativesError(ConcessionMethodError):
    """A concession step removed all alternatives."""


def validate_input(alternatives: Sequence[Alternative], criteria: Sequence[Criterion]) -> None:
    """Validate decision data before running the concession method."""

    if len(alternatives) < 2:
        raise ValidationError("Количество альтернатив должно быть не меньше 2.")
    if len(criteria) < 2:
        raise ValidationError("Количество критериев должно быть не меньше 2.")

    _ensure_unique_names([alternative.name for alternative in alternatives], "альтернатив")
    _ensure_unique_names([criterion.name for criterion in criteria], "критериев")

    criterion_names = {criterion.name for criterion in criteria}
    for alternative in alternatives:
        if not alternative.name.strip():
            raise ValidationError("Название альтернативы не может быть пустым.")
        missing = criterion_names - alternative.values.keys()
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValidationError(
                f"Для альтернативы {alternative.name} не заданы значения: {missing_text}."
            )
        for criterion_name in criterion_names:
            value = alternative.values[criterion_name]
            if not _is_number(value):
                raise ValidationError(
                    f"Значение критерия {criterion_name} для альтернативы "
                    f"{alternative.name} должно быть числом."
                )

    priorities = [criterion.priority for criterion in criteria]
    expected_priorities = set(range(1, len(criteria) + 1))
    if set(priorities) != expected_priorities or len(priorities) != len(set(priorities)):
        raise ValidationError("Порядок важности критериев должен быть задан числами без повторов.")

    ordered_criteria = sorted(criteria, key=lambda criterion: criterion.priority)
    last_criterion = ordered_criteria[-1]
    for criterion in criteria:
        if not criterion.name.strip():
            raise ValidationError("Название критерия не может быть пустым.")
        if criterion.direction not in {"max", "min"}:
            raise ValidationError(
                f"Для критерия {criterion.name} направление должно быть max или min."
            )
        if criterion.concession_type not in {"absolute", "percent"}:
            raise ValidationError(
                f"Для критерия {criterion.name} тип уступки должен быть absolute или percent."
            )
        if criterion.concession is not None:
            if not _is_number(criterion.concession):
                raise ValidationError(f"Уступка критерия {criterion.name} должна быть числом.")
            if criterion.concession < 0:
                raise ValidationError(f"Уступка критерия {criterion.name} не может быть отрицательной.")
        if criterion != last_criterion and criterion.concession is None:
            raise ValidationError(f"Для критерия {criterion.name} должна быть задана уступка.")


def get_best_value(alternatives: Sequence[Alternative], criterion: Criterion) -> float:
    """Return the optimum criterion value for the given alternatives."""

    if not alternatives:
        raise EmptyAlternativesError("Множество допустимых альтернатив пусто.")

    values = [alternative.values[criterion.name] for alternative in alternatives]
    if criterion.direction == "max":
        return max(values)
    if criterion.direction == "min":
        return min(values)
    raise ValidationError(f"Неизвестное направление оптимизации: {criterion.direction}.")


def compare_by_direction(value: float, best_value: float, direction: Direction) -> bool:
    """Return whether value is as good as best_value for the direction."""

    if isclose(value, best_value, abs_tol=EPSILON):
        return True
    if direction == "max":
        return value > best_value
    if direction == "min":
        return value < best_value
    raise ValidationError(f"Неизвестное направление оптимизации: {direction}.")


def apply_concession(
    alternatives: Sequence[Alternative],
    criterion: Criterion,
    step_number: int,
) -> tuple[list[Alternative], ConcessionStep]:
    """Apply one concession step and return the filtered alternatives plus protocol."""

    if criterion.concession is None:
        raise ValidationError(f"Для критерия {criterion.name} должна быть задана уступка.")
    if criterion.concession < 0:
        raise ValidationError(f"Уступка критерия {criterion.name} не может быть отрицательной.")

    optimum = get_best_value(alternatives, criterion)
    boundary, applied_concession = _calculate_boundary(optimum, criterion)
    remaining: list[Alternative] = []
    excluded: list[Alternative] = []

    for alternative in alternatives:
        value = alternative.values[criterion.name]
        if _passes_boundary(value, boundary, criterion.direction):
            remaining.append(alternative)
        else:
            excluded.append(alternative)

    step = ConcessionStep(
        step_number=step_number,
        criterion=criterion.name,
        direction=criterion.direction,
        optimum_value=optimum,
        applied_concession=applied_concession,
        boundary_value=boundary,
        constraint_description=_build_constraint_description(
            criterion, optimum, applied_concession, boundary
        ),
        remaining_alternatives=[alternative.name for alternative in remaining],
        excluded_alternatives=[alternative.name for alternative in excluded],
    )

    if not remaining:
        raise EmptyAlternativesError(
            f"После применения уступки по критерию {criterion.name} не осталось альтернатив."
        )
    return remaining, step


def solve_concession_method(
    alternatives: Sequence[Alternative],
    criteria: Sequence[Criterion],
) -> ConcessionResult:
    """Solve a discrete multicriteria decision task by the concession method."""

    try:
        validate_input(alternatives, criteria)
        ordered_criteria = sorted(criteria, key=lambda criterion: criterion.priority)
        current = list(alternatives)
        steps: list[ConcessionStep] = []

        for step_number, criterion in enumerate(ordered_criteria[:-1], start=1):
            current, step = apply_concession(current, criterion, step_number)
            steps.append(step)

        last_criterion = ordered_criteria[-1]
        optimum = get_best_value(current, last_criterion)
        winners = [
            alternative
            for alternative in current
            if isclose(alternative.values[last_criterion.name], optimum, abs_tol=EPSILON)
        ]
        excluded_on_final = [alternative for alternative in current if alternative not in winners]
        steps.append(
            ConcessionStep(
                step_number=len(ordered_criteria),
                criterion=last_criterion.name,
                direction=last_criterion.direction,
                optimum_value=optimum,
                applied_concession=None,
                boundary_value=None,
                constraint_description=(
                    f"Последний критерий {last_criterion.name}: выбран оптимум "
                    f"{_format_number(optimum)} без применения уступки."
                ),
                remaining_alternatives=[alternative.name for alternative in winners],
                excluded_alternatives=[alternative.name for alternative in excluded_on_final],
            )
        )

        return ConcessionResult(
            winners=[alternative.name for alternative in winners],
            final_alternatives=[alternative.name for alternative in current],
            steps=steps,
            success=True,
        )
    except ConcessionMethodError as error:
        return ConcessionResult(success=False, error_message=str(error))


def _ensure_unique_names(names: Sequence[str], entity_name: str) -> None:
    stripped_names = [name.strip() for name in names]
    if any(not name for name in stripped_names):
        raise ValidationError(f"Названия {entity_name} не должны быть пустыми.")
    if len(stripped_names) != len(set(stripped_names)):
        raise ValidationError(f"Названия {entity_name} не должны повторяться.")


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _calculate_boundary(optimum: float, criterion: Criterion) -> tuple[float, float]:
    concession = criterion.concession
    if concession is None:
        raise ValidationError(f"Для критерия {criterion.name} должна быть задана уступка.")

    if criterion.concession_type == "absolute":
        applied_concession = concession
    elif criterion.concession_type == "percent":
        applied_concession = abs(optimum) * concession / 100
    else:
        raise ValidationError(
            f"Для критерия {criterion.name} тип уступки должен быть absolute или percent."
        )

    if criterion.direction == "max":
        return optimum - applied_concession, applied_concession
    if criterion.direction == "min":
        return optimum + applied_concession, applied_concession
    raise ValidationError(f"Неизвестное направление оптимизации: {criterion.direction}.")


def _passes_boundary(value: float, boundary: float, direction: Direction) -> bool:
    if direction == "max":
        return value >= boundary or isclose(value, boundary, abs_tol=EPSILON)
    if direction == "min":
        return value <= boundary or isclose(value, boundary, abs_tol=EPSILON)
    raise ValidationError(f"Неизвестное направление оптимизации: {direction}.")


def _build_constraint_description(
    criterion: Criterion,
    optimum: float,
    applied_concession: float,
    boundary: float,
) -> str:
    sign = ">=" if criterion.direction == "max" else "<="
    return (
        f"Критерий {criterion.name}: оптимум = {_format_number(optimum)}, "
        f"уступка = {_format_number(applied_concession)}, "
        f"ограничение: значение {sign} {_format_number(boundary)}."
    )


def _format_number(value: float) -> str:
    if isclose(value, round(value), abs_tol=EPSILON):
        return str(int(round(value)))
    return f"{value:.6g}"
