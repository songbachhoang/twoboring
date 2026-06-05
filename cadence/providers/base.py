"""The provider interface: decide the next action from a screenshot + goal.

Adapters are dumb: they translate the model's output into the normalized Decision,
normalize coordinates to 0-1000, and map confirmation/refusal signals honestly.
Policy (the state machine, humanization, safety rails) lives in the core.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import Decision


class Provider(ABC):
    name = "base"
    mode = "scaffolded"        # "native" | "scaffolded"

    @abstractmethod
    def decide(self, screenshot: bytes, goal: str, history: list, hints=None) -> Decision:
        ...
