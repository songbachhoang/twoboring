"""The per-step loop / state machine (docs/ARCHITECTURE.md).

Each step runs: capture -> settle -> decide -> (sensitive? confirm) -> humanize ->
inject -> verify -> log. Settle frame-diffs successive captures so we never act on a
mid-animation frame; verify re-captures to confirm the screen actually changed and
re-decides if it didn't. Recovery prefers stopping over guessing: after
``stop_on_unknown_after`` consecutive unknown screens it aborts cleanly.
"""

from __future__ import annotations

import io
import random
import time

from . import humanize as hz
from .geometry import to_pixels
from .safety import is_sensitive
from .types import ActionType


def _downscale(png: bytes, scale: float) -> bytes:
    if scale >= 0.999:
        return png
    from PIL import Image
    img = Image.open(io.BytesIO(png))
    w, h = img.size
    img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))))
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def _signature(png: bytes):
    """A tiny grayscale thumbnail used for cheap frame-diffing."""
    from PIL import Image
    img = Image.open(io.BytesIO(png)).convert("L").resize((32, 32))
    return list(img.getdata())


def frames_differ(a, b, threshold: float = 8.0) -> bool:
    if a is None or b is None:
        return True
    diff = sum(abs(p - q) for p, q in zip(a, b)) / len(a)
    return diff > threshold


class Engine:
    def __init__(self, config, provider, backend, runlog, *, seed=None, humanize_cfg=None):
        self.cfg = config
        self.provider = provider
        self.backend = backend
        self.runlog = runlog
        self.rng = random.Random(seed)
        self.hcfg = humanize_cfg

    def _settle(self) -> bytes:
        deadline = time.monotonic() + self.cfg.run.settle_timeout_ms / 1000.0
        shot = self.backend.screencap()
        sig = _signature(shot)
        while time.monotonic() < deadline:
            time.sleep(0.15)
            nxt = self.backend.screencap()
            nsig = _signature(nxt)
            if not frames_differ(sig, nsig):
                return nxt
            shot, sig = nxt, nsig
        return shot

    def run(self, steps, dry_run=False, assume_yes=False):
        budget = self.cfg.run.max_steps   # hard cap on model steps across the whole run
        results = []
        for step in steps:
            if budget <= 0:
                results.append((step, "max_steps"))
                continue
            status, used = self._run_step(step, dry_run, assume_yes, budget)
            budget -= used
            results.append((step, status))
            if status != "done":      # any non-done step (aborted/declined) stops the run
                break
        return results

    def _run_step(self, step, dry_run, assume_yes, budget):
        history: list[str] = []
        unknown = 0
        used = 0
        while used < budget:
            used += 1
            raw = self._settle()
            shot = _downscale(raw, self.cfg.device.screenshot_scale)
            decision = self.provider.decide(shot, step.goal, history, None)

            if decision.action == ActionType.DONE:
                self.runlog.step(raw, decision, injected=False, extra={"phase": "done"})
                return "done", used
            if decision.action == ActionType.UNKNOWN:
                unknown += 1
                self.runlog.step(raw, decision, injected=False, extra={"phase": "unknown"})
                if unknown >= self.cfg.run.stop_on_unknown_after:
                    return "aborted-unknown", used
                continue
            unknown = 0

            if is_sensitive(decision) and not dry_run:
                if not _confirm_sensitive(decision):
                    self.runlog.step(raw, decision, injected=False, extra={"phase": "declined"})
                    return "declined", used

            injected = False
            if not dry_run:
                self._inject(decision)
                injected = True
                time.sleep(self.cfg.run.post_tap_wait_ms / 1000.0)

            self.runlog.step(raw, decision, injected=injected)
            history.append(f"{decision.action.value}({decision.x},{decision.y}) {decision.rationale}")

            if injected and self.cfg.run.verify_screen_change:
                after = self.backend.screencap()
                if not frames_differ(_signature(raw), _signature(after)):
                    history.append("note: screen did not change after the last action")
        return "max_steps", used

    def _inject(self, decision):
        width, height = self.backend.resolution()
        if decision.action == ActionType.TAP:
            x, y = decision.x, decision.y
            if self.hcfg and self.hcfg.enabled:
                x, y = hz.jitter_tap(x, y, 40, 40, self.hcfg, self.rng)
            px, py = to_pixels(x, y, width, height)
            dur = hz.sample_tap_duration(self.hcfg, self.rng) if self.hcfg else 80
            self.backend.tap(px, py, dur)
        elif decision.action == ActionType.SWIPE:
            px1, py1 = to_pixels(decision.x, decision.y, width, height)
            px2, py2 = to_pixels(decision.x2, decision.y2, width, height)
            self.backend.swipe(px1, py1, px2, py2, 220)
        elif decision.action == ActionType.TYPE:
            self.backend.type_text(decision.text or "")
        elif decision.action == ActionType.BACK:
            self.backend.back()
        elif decision.action == ActionType.WAIT:
            time.sleep(0.8)


def _confirm_sensitive(decision) -> bool:
    print(f"\n  Sensitive action: {decision.action.value} — {decision.rationale}")
    try:
        return input("  Approve this action? [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False
