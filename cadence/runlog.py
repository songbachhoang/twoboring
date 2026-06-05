"""Structured run logs (docs/ARCHITECTURE.md).

Every run writes to ``<log_dir>/<timestamp>/``: ordered screenshots plus an
``events.jsonl`` of the action taken at each, the model's one-line rationale, and
whether it was injected. Because a run is non-deterministic, the log is how you
debug — replay the screenshots to see which screen confused the model.

Treat the log dir as sensitive: it contains screenshots (docs/SAFETY.md).
"""

from __future__ import annotations

import json
import os
from datetime import datetime


class RunLog:
    def __init__(self, base_dir: str):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.dir = os.path.join(base_dir, stamp)
        os.makedirs(self.dir, exist_ok=True)
        self._n = 0
        self._events = open(os.path.join(self.dir, "events.jsonl"), "a", encoding="utf-8")

    def step(self, screenshot: bytes, decision, injected: bool, extra=None):
        self._n += 1
        shot = f"{self._n:04d}.png"
        with open(os.path.join(self.dir, shot), "wb") as fh:
            fh.write(screenshot)
        record = {
            "n": self._n,
            "screenshot": shot,
            "action": decision.action.value,
            "x": decision.x, "y": decision.y,
            "x2": decision.x2, "y2": decision.y2,
            "text": decision.text,
            "rationale": decision.rationale,
            "injected": injected,
        }
        if extra:
            record.update(extra)
        self._events.write(json.dumps(record) + "\n")
        self._events.flush()

    def close(self):
        self._events.close()
