"""Core value types shared across the engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionType(str, Enum):
    TAP = "TAP"
    SWIPE = "SWIPE"
    TYPE = "TYPE"
    BACK = "BACK"
    WAIT = "WAIT"
    DONE = "DONE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Decision:
    """A normalized action from a provider.

    Coordinates are in the normalized 0-1000 space on each axis, origin top-left
    (see docs/PROVIDERS.md). The core rescales to device pixels before injection.
    """

    action: ActionType
    x: int | None = None
    y: int | None = None
    x2: int | None = None
    y2: int | None = None
    text: str | None = None
    rationale: str = ""
    needs_confirmation: bool = False


@dataclass
class Step:
    """One sub-goal in a plan."""

    goal: str
    read_only: bool = False
