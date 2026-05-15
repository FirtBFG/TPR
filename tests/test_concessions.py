"""Tests for the concession method calculation core."""

from app.concessions import solve_concession_method
from app.models import Alternative, Criterion


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
