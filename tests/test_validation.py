"""Tests for calculation-core input validation."""

from __future__ import annotations

from math import inf, nan

import pytest

from app.concessions import ValidationError, validate_input
from app.models import Alternative, Criterion


def valid_alternatives() -> list[Alternative]:
    return [
        Alternative("A1", {"K1": 10, "K2": 5}),
        Alternative("A2", {"K1": 8, "K2": 6}),
    ]


def valid_criteria() -> list[Criterion]:
    return [
        Criterion("K1", "max", priority=1, concession=1),
        Criterion("K2", "min", priority=2),
    ]


def test_valid_data_passes_validation() -> None:
    validate_input(valid_alternatives(), valid_criteria())


def test_less_than_two_alternatives_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_input(valid_alternatives()[:1], valid_criteria())


def test_less_than_two_criteria_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), valid_criteria()[:1])


def test_empty_alternative_name_is_rejected() -> None:
    alternatives = [
        Alternative("", {"K1": 10, "K2": 5}),
        Alternative("A2", {"K1": 8, "K2": 6}),
    ]

    with pytest.raises(ValidationError):
        validate_input(alternatives, valid_criteria())


def test_duplicate_alternative_names_are_rejected() -> None:
    alternatives = [
        Alternative("A1", {"K1": 10, "K2": 5}),
        Alternative("A1", {"K1": 8, "K2": 6}),
    ]

    with pytest.raises(ValidationError):
        validate_input(alternatives, valid_criteria())


def test_empty_criterion_name_is_rejected() -> None:
    criteria = [
        Criterion("", "max", priority=1, concession=1),
        Criterion("K2", "min", priority=2),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


def test_duplicate_criterion_names_are_rejected() -> None:
    criteria = [
        Criterion("K1", "max", priority=1, concession=1),
        Criterion("K1", "min", priority=2),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


def test_missing_alternative_value_is_rejected() -> None:
    alternatives = [
        Alternative("A1", {"K1": 10}),
        Alternative("A2", {"K1": 8, "K2": 6}),
    ]

    with pytest.raises(ValidationError):
        validate_input(alternatives, valid_criteria())


@pytest.mark.parametrize("bad_value", ["10", None, True, nan, inf])
def test_nonnumeric_or_nonfinite_alternative_value_is_rejected(bad_value: object) -> None:
    alternatives = [
        Alternative("A1", {"K1": bad_value, "K2": 5}),  # type: ignore[dict-item]
        Alternative("A2", {"K1": 8, "K2": 6}),
    ]

    with pytest.raises(ValidationError):
        validate_input(alternatives, valid_criteria())


def test_unknown_direction_is_rejected() -> None:
    criteria = [
        Criterion("K1", "up", priority=1, concession=1),  # type: ignore[arg-type]
        Criterion("K2", "min", priority=2),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


def test_unknown_concession_type_is_rejected() -> None:
    criteria = [
        Criterion("K1", "max", priority=1, concession=1, concession_type="ratio"),  # type: ignore[arg-type]
        Criterion("K2", "min", priority=2),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


def test_repeated_priority_is_rejected() -> None:
    criteria = [
        Criterion("K1", "max", priority=1, concession=1),
        Criterion("K2", "min", priority=1),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


def test_incomplete_priority_sequence_is_rejected() -> None:
    criteria = [
        Criterion("K1", "max", priority=1, concession=1),
        Criterion("K2", "min", priority=3),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


@pytest.mark.parametrize("bad_concession", [-1, "1", True, nan, inf])
def test_negative_nonnumeric_or_nonfinite_concession_is_rejected(
    bad_concession: object,
) -> None:
    criteria = [
        Criterion("K1", "max", priority=1, concession=bad_concession),  # type: ignore[arg-type]
        Criterion("K2", "min", priority=2),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


def test_missing_concession_for_non_last_criterion_is_rejected() -> None:
    criteria = [
        Criterion("K1", "max", priority=1),
        Criterion("K2", "min", priority=2),
    ]

    with pytest.raises(ValidationError):
        validate_input(valid_alternatives(), criteria)


def test_empty_concession_for_last_criterion_is_allowed() -> None:
    criteria = [
        Criterion("K1", "max", priority=1, concession=1),
        Criterion("K2", "min", priority=2, concession=None),
    ]

    validate_input(valid_alternatives(), criteria)
