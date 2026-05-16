"""Tests for the concession method calculation core."""

import pytest

import app.concessions as concessions
from app.concessions import (
    EmptyAlternativesError,
    apply_concession,
    compare_by_direction,
    solve_concession_method,
)
from app.models import Alternative, Criterion


def names(alternatives: list[Alternative]) -> list[str]:
    return [alternative.name for alternative in alternatives]


def test_apply_concession_keeps_max_values_inside_absolute_concession() -> None:
    alternatives = [
        Alternative("A1", {"K": 10}),
        Alternative("A2", {"K": 8}),
        Alternative("A3", {"K": 7.9}),
    ]
    criterion = Criterion("K", "max", priority=1, concession=2)

    remaining, step = apply_concession(alternatives, criterion, step_number=1)

    assert names(remaining) == ["A1", "A2"]
    assert step.optimum_value == 10
    assert step.applied_concession == 2
    assert step.boundary_value == 8
    assert step.remaining_alternatives == ["A1", "A2"]
    assert step.excluded_alternatives == ["A3"]


def test_apply_concession_keeps_min_values_inside_absolute_concession() -> None:
    alternatives = [
        Alternative("A1", {"K": 10}),
        Alternative("A2", {"K": 12}),
        Alternative("A3", {"K": 13}),
    ]
    criterion = Criterion("K", "min", priority=1, concession=2)

    remaining, step = apply_concession(alternatives, criterion, step_number=1)

    assert names(remaining) == ["A1", "A2"]
    assert step.optimum_value == 10
    assert step.applied_concession == 2
    assert step.boundary_value == 12
    assert step.excluded_alternatives == ["A3"]


def test_apply_concession_converts_max_percent_concession_to_boundary() -> None:
    alternatives = [
        Alternative("A1", {"K": 200}),
        Alternative("A2", {"K": 180}),
        Alternative("A3", {"K": 179}),
    ]
    criterion = Criterion("K", "max", priority=1, concession=10, concession_type="percent")

    remaining, step = apply_concession(alternatives, criterion, step_number=1)

    assert names(remaining) == ["A1", "A2"]
    assert step.applied_concession == 20
    assert step.boundary_value == 180


def test_apply_concession_converts_min_percent_concession_to_boundary() -> None:
    alternatives = [
        Alternative("A1", {"K": 50}),
        Alternative("A2", {"K": 55}),
        Alternative("A3", {"K": 56}),
    ]
    criterion = Criterion("K", "min", priority=1, concession=10, concession_type="percent")

    remaining, step = apply_concession(alternatives, criterion, step_number=1)

    assert names(remaining) == ["A1", "A2"]
    assert step.applied_concession == 5
    assert step.boundary_value == 55


def test_apply_concession_empty_current_set_raises_controlled_error() -> None:
    criterion = Criterion("K", "max", priority=1, concession=1)

    with pytest.raises(EmptyAlternativesError):
        apply_concession([], criterion, step_number=1)


def test_example_1_returns_a1_and_full_step_history() -> None:
    alternatives = [
        Alternative("A1", {"K1": 100, "K2": 20, "K3": 8}),
        Alternative("A2", {"K1": 95, "K2": 10, "K3": 7}),
        Alternative("A3", {"K1": 80, "K2": 5, "K3": 10}),
    ]
    criteria = [
        Criterion("K1", "max", priority=1, concession=10),
        Criterion("K2", "min", priority=2, concession=10),
        Criterion("K3", "max", priority=3),
    ]

    result = solve_concession_method(alternatives, criteria)

    assert result.success is True
    assert result.error_message is None
    assert result.winners == ["A1"]
    assert result.final_alternatives == ["A1", "A2"]
    assert [step.criterion for step in result.steps] == ["K1", "K2", "K3"]
    assert result.steps[0].remaining_alternatives == ["A1", "A2"]
    assert result.steps[0].excluded_alternatives == ["A3"]


def test_full_method_returns_multiple_equal_winners() -> None:
    alternatives = [
        Alternative("A1", {"K1": 10, "K2": 5}),
        Alternative("A2", {"K1": 9, "K2": 5}),
        Alternative("A3", {"K1": 6, "K2": 9}),
    ]
    criteria = [
        Criterion("K1", "max", priority=1, concession=1),
        Criterion("K2", "max", priority=2),
    ]

    result = solve_concession_method(alternatives, criteria)

    assert result.success is True
    assert result.winners == ["A1", "A2"]
    assert result.final_alternatives == ["A1", "A2"]
    assert result.steps[-1].applied_concession is None
    assert result.steps[-1].excluded_alternatives == []


def test_solver_returns_controlled_error_when_concession_step_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    alternatives = [
        Alternative("A1", {"K1": 10, "K2": 1}),
        Alternative("A2", {"K1": 9, "K2": 2}),
    ]
    criteria = [
        Criterion("K1", "max", priority=1, concession=1),
        Criterion("K2", "max", priority=2),
    ]

    def fail_step(
        alternatives: list[Alternative],
        criterion: Criterion,
        step_number: int,
    ) -> tuple[list[Alternative], object]:
        raise EmptyAlternativesError("controlled empty set")

    monkeypatch.setattr(concessions, "apply_concession", fail_step)

    result = concessions.solve_concession_method(alternatives, criteria)

    assert result.success is False
    assert result.error_message == "controlled empty set"


def test_compare_by_direction_accepts_equal_values_with_tolerance() -> None:
    assert compare_by_direction(1.0 + 1e-10, 1.0, "max") is True
    assert compare_by_direction(1.0 - 1e-10, 1.0, "min") is True
