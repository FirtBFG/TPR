"""Built-in examples for manual filling and tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models import Alternative, Criterion


@dataclass(frozen=True)
class DecisionExample:
    """Complete task data that can be loaded into GUI or tests."""

    title: str
    alternatives: list[Alternative]
    criteria: list[Criterion]
    expected_winners: list[str] = field(default_factory=list)


def get_example_1() -> DecisionExample:
    """Return the first sample from the assignment."""

    return DecisionExample(
        title="Пример 1",
        alternatives=[
            Alternative("A1", {"K1": 100, "K2": 20, "K3": 8}),
            Alternative("A2", {"K1": 95, "K2": 10, "K3": 7}),
            Alternative("A3", {"K1": 80, "K2": 5, "K3": 10}),
        ],
        criteria=[
            Criterion("K1", "max", priority=1, concession=10),
            Criterion("K2", "min", priority=2, concession=10),
            Criterion("K3", "max", priority=3),
        ],
        expected_winners=["A1"],
    )


def get_example_2() -> DecisionExample:
    """Return the second sample from the assignment."""

    return DecisionExample(
        title="Пример 2",
        alternatives=[
            Alternative("A1", {"K1": 10, "K2": 100, "K3": 5}),
            Alternative("A2", {"K1": 12, "K2": 90, "K3": 5}),
            Alternative("A3", {"K1": 15, "K2": 60, "K3": 3}),
        ],
        criteria=[
            Criterion("K1", "min", priority=1, concession=3),
            Criterion("K2", "max", priority=2, concession=15),
            Criterion("K3", "max", priority=3),
        ],
        # According to the formal concession rule, A2 remains on K2:
        # 90 >= 100 - 15, so A1 and A2 are equivalent on the last criterion.
        expected_winners=["A1", "A2"],
    )


def get_variant_22() -> DecisionExample:
    """Return the dormitory-choice task data for variant 22."""

    criteria_names = ["К1", "К2", "К3", "К4", "К5", "К6"]
    raw_values = {
        "В1": [190, 40, 19, 5, 86, 15],
        "В2": [230, 66, 20, 1, 60, 25],
        "В3": [120, 10, 12, 3, 15, 20],
        "В4": [110, 60, 20, 4, 30, 10],
        "В5": [250, 50, 12, 0, 10, 30],
        "В6": [250, 33, 12, 4, 75, 20],
        "В7": [180, 20, 10, 3, 40, 10],
    }

    return DecisionExample(
        title="Вариант 22: выбор общежития",
        alternatives=[
            Alternative(name, dict(zip(criteria_names, values, strict=True)))
            for name, values in raw_values.items()
        ],
        criteria=[
            Criterion("К1", "min", priority=1, concession=80),
            Criterion("К2", "min", priority=2, concession=30),
            Criterion("К3", "min", priority=3, concession=5),
            Criterion("К4", "max", priority=4, concession=2),
            Criterion("К5", "max", priority=5, concession=50),
            Criterion("К6", "min", priority=6),
        ],
        expected_winners=["В7"],
    )
