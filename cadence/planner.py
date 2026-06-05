"""Planner + confirm gate (docs/TASKS.md).

The planner expands a freeform goal into an ordered list of steps and the confirm
gate prints them and waits for `y` — the boundary between "the model proposed a
plan" and "the device did something".

v0.1 uses a lightweight heuristic split (numbered lists, 'then', sentences). A
model-driven planner is a later enhancement; the seam is here so swapping it in
touches nothing else.
"""

from __future__ import annotations

import re

from .types import Step

_READONLY_HINTS = (
    "read-only", "read only", "don't change", "do not change",
    "just read", "report", "tell me", "don't tap anything that changes",
)
_SPLIT = re.compile(r"(?:\b\d\)\s*)|(?:\bthen\b)|(?:;)|(?:\.\s+)", re.IGNORECASE)


def plan(goal: str) -> list[Step]:
    parts = [p.strip(" .,") for p in _SPLIT.split(goal) if p and p.strip(" .,")]
    if not parts:
        parts = [goal.strip()]
    steps = []
    for part in parts:
        read_only = any(h in part.lower() for h in _READONLY_HINTS)
        steps.append(Step(goal=part, read_only=read_only))
    return steps


def render_plan(steps) -> str:
    lines = ["Plan:"]
    for i, step in enumerate(steps, 1):
        tag = "   (read-only)" if step.read_only else ""
        lines.append(f"  {i}. {step.goal}{tag}")
    return "\n".join(lines)


def confirm(steps, assume_yes: bool = False) -> bool:
    print(render_plan(steps))
    if assume_yes:
        print("\nProceed? [y/N] y   (--yes)")
        return True
    try:
        return input("\nProceed? [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False
