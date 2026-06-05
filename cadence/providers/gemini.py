"""Gemini provider (BYOK).

v0.1 implements the **scaffolded-vision** path: a structured prompt asks the model
for a JSON action with normalized 0-1000 coordinates, which is parsed into a
Decision. This works with any vision-capable Gemini model. Wiring Gemini's native
Computer Use tool (lower prompt overhead, best grounding) is the next step — see
docs/PROVIDERS.md and ROADMAP.md.

The ``google-genai`` SDK is imported lazily, so the package imports fine without it;
install with ``pip install 'cadence-android[gemini]'``.
"""

from __future__ import annotations

import json
import re

from ..config import resolve_env
from ..types import ActionType, Decision
from .base import Provider

_PROMPT = """You are driving an Android phone by looking at the screen.
Goal for this step: {goal}
Recent actions: {history}
{hints}
Respond with ONLY a JSON object and nothing else:
{{"action": "TAP|SWIPE|TYPE|BACK|WAIT|DONE|UNKNOWN",
  "x": <int 0-1000>, "y": <int 0-1000>,
  "x2": <int 0-1000 or null>, "y2": <int 0-1000 or null>,
  "text": "<string for TYPE, else null>",
  "rationale": "<one short line>",
  "needs_confirmation": <true for a payment/delete/post/permission/account action>}}
Coordinates are normalized 0-1000 with the origin at the top-left.
Use DONE when the goal is already satisfied; UNKNOWN if the screen is unrecognizable."""


class GeminiProvider(Provider):
    name = "gemini"
    mode = "scaffolded"

    def __init__(self, provider_cfg):
        self.cfg = provider_cfg
        self.api_key = resolve_env(provider_cfg.api_key)
        self._client = None

    def _client_lazy(self):
        if self._client is None:
            try:
                from google import genai
            except ImportError as exc:
                raise RuntimeError(
                    "Gemini SDK missing — pip install 'cadence-android[gemini]'"
                ) from exc
            if not self.api_key:
                raise RuntimeError(
                    "no API key — set GEMINI_API_KEY "
                    "(config provider.api_key: env:GEMINI_API_KEY)"
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def decide(self, screenshot, goal, history, hints=None) -> Decision:
        client = self._client_lazy()
        prompt = _PROMPT.format(
            goal=goal,
            history=", ".join(history[-5:]) or "none",
            hints=f"App hints: {hints}" if hints else "",
        )
        resp = client.models.generate_content(
            model=self.cfg.model,
            contents=[
                {"inline_data": {"mime_type": "image/png", "data": screenshot}},
                prompt,
            ],
        )
        return parse_decision(getattr(resp, "text", "") or "")


def parse_decision(text: str) -> Decision:
    """Parse a model's JSON reply into a Decision, clamping coords to 0-1000."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return Decision(action=ActionType.UNKNOWN, rationale="unparseable model output")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return Decision(action=ActionType.UNKNOWN, rationale="invalid JSON from model")

    def clamp(v):
        if v is None:
            return None
        try:
            return max(0, min(1000, int(v)))
        except (TypeError, ValueError):
            return None

    try:
        action = ActionType(str(data.get("action", "UNKNOWN")).upper())
    except ValueError:
        action = ActionType.UNKNOWN

    return Decision(
        action=action,
        x=clamp(data.get("x")), y=clamp(data.get("y")),
        x2=clamp(data.get("x2")), y2=clamp(data.get("y2")),
        text=data.get("text"),
        rationale=str(data.get("rationale", ""))[:200],
        needs_confirmation=bool(data.get("needs_confirmation", False)),
    )
