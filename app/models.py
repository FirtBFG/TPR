"""Domain models for the concession method."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Direction = Literal["max", "min"]
ConcessionType = Literal["absolute", "percent"]


@dataclass(frozen=True)
class Criterion:
    """Decision criterion configuration."""

    name: str
    direction: Direction
    priority: int
    concession: float | None = None
    concession_type: ConcessionType = "absolute"


@dataclass(frozen=True)
class Alternative:
    """Decision alternative with values by criterion name."""

    name: str
    values: dict[str, float]


@dataclass(frozen=True)
class ConcessionStep:
    """One step of the concession method protocol."""

    step_number: int
    criterion: str
    direction: Direction
    optimum_value: float
    applied_concession: float | None
    boundary_value: float | None
    constraint_description: str
    remaining_alternatives: list[str] = field(default_factory=list)
    excluded_alternatives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConcessionResult:
    """Result returned by the calculation core."""

    winners: list[str] = field(default_factory=list)
    final_alternatives: list[str] = field(default_factory=list)
    steps: list[ConcessionStep] = field(default_factory=list)
    success: bool = True
    error_message: str | None = None
