"""Tests for built-in examples."""

import pytest

from app.concessions import solve_concession_method
from app.examples import DecisionExample, get_example_1, get_example_2, get_variant_22


@pytest.mark.parametrize(
    "example",
    [
        get_example_1(),
        get_example_2(),
        get_variant_22(),
    ],
)
def test_examples_are_non_empty_and_solvable(example: DecisionExample) -> None:
    result = solve_concession_method(example.alternatives, example.criteria)

    assert example.alternatives
    assert example.criteria
    assert result.success is True
    assert result.error_message is None
    assert result.winners == example.expected_winners


def test_variant_22_contains_assignment_data() -> None:
    example = get_variant_22()

    assert [alternative.name for alternative in example.alternatives] == [
        "В1",
        "В2",
        "В3",
        "В4",
        "В5",
        "В6",
        "В7",
    ]
    assert [criterion.name for criterion in example.criteria] == [
        "К1",
        "К2",
        "К3",
        "К4",
        "К5",
        "К6",
    ]
    assert [criterion.direction for criterion in example.criteria] == [
        "min",
        "min",
        "min",
        "max",
        "max",
        "min",
    ]
    assert example.alternatives[0].values == {
        "К1": 190,
        "К2": 40,
        "К3": 19,
        "К4": 5,
        "К5": 86,
        "К6": 15,
    }
