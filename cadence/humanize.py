"""Gesture-level humanization (docs/HUMANIZATION.md).

These perturbations remove the obvious statistical signatures of synthetic input,
for honest testing realism and to avoid stressing UIs in unnatural ways. They do
NOT defeat Tier-2 (injection-source fingerprinting, automation-surface detection,
server-side behavioral analysis) — the docs say so plainly and that is not a goal.

Every sampler takes an explicit ``random.Random`` so runs are reproducible in tests
and a seed can pin a session.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class HumanizeConfig:
    enabled: bool = True
    timing: str = "lognormal"          # lognormal | gamma | fixed
    base_delay_ms: float = 800.0
    tap_jitter: bool = True
    tap_duration_ms: tuple = (60, 150)
    swipe_curve: str = "bezier"        # bezier | linear
    imperfection_rate: float = 0.05


def sample_delay(cfg: HumanizeConfig, rng: random.Random) -> float:
    """Inter-action delay in ms, sampled from the configured distribution.

    Human inter-action times cluster around a typical value with a long right tail;
    uniform delays are themselves a giveaway. Lognormal/gamma reproduce that shape.
    """
    base = cfg.base_delay_ms
    if not cfg.enabled or cfg.timing == "fixed":
        return base
    if cfg.timing == "gamma":
        # mean = k * theta = base; shape k=2 gives a right-skewed tail.
        return max(0.0, rng.gammavariate(2.0, base / 2.0))
    # lognormal: median = exp(mu) = base  ->  mu = ln(base)
    return max(0.0, rng.lognormvariate(math.log(base), 0.5))


def jitter_tap(
    x: float, y: float, half_w: float, half_h: float,
    cfg: HumanizeConfig, rng: random.Random,
) -> tuple[float, float]:
    """Sample a tap point from a Gaussian cloud inside the target, clipped to it.

    sigma ~= 1/4 of the target half-width; a perfectly centered tap every time is
    abnormal. Coordinates here are in the same units the caller passes (normalized).
    """
    if not cfg.enabled or not cfg.tap_jitter:
        return x, y
    sx = rng.gauss(x, half_w / 4.0)
    sy = rng.gauss(y, half_h / 4.0)
    sx = min(x + half_w, max(x - half_w, sx))
    sy = min(y + half_h, max(y - half_h, sy))
    return sx, sy


def sample_tap_duration(cfg: HumanizeConfig, rng: random.Random) -> float:
    """A touch-down -> up time in ms. Zero/constant durations are abnormal."""
    lo, hi = cfg.tap_duration_ms
    if not cfg.enabled:
        return float(lo)
    return rng.uniform(lo, hi)


def bezier_swipe(
    x1: float, y1: float, x2: float, y2: float,
    cfg: HumanizeConfig, rng: random.Random, n: int = 24,
) -> list[tuple[float, float]]:
    """Sample ``n`` points along the swipe path with an ease-in/ease-out profile.

    With ``swipe_curve == 'bezier'`` the path is a cubic Bezier whose control points
    sit along the line with a small randomized perpendicular bow, so the swipe curves
    instead of tracing the straight, constant-velocity line that is trivial to detect.
    """
    if n < 2:
        n = 2
    if not cfg.enabled or cfg.swipe_curve == "linear":
        return [
            (
                _ease(i / (n - 1)) * (x2 - x1) + x1,
                _ease(i / (n - 1)) * (y2 - y1) + y1,
            )
            for i in range(n)
        ]
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    px, py = -dy / length, dx / length          # unit perpendicular
    bow = rng.uniform(-0.12, 0.12) * length
    c1 = (x1 + dx * 0.33 + px * bow, y1 + dy * 0.33 + py * bow)
    c2 = (x1 + dx * 0.66 + px * bow, y1 + dy * 0.66 + py * bow)
    pts = []
    for i in range(n):
        t = _ease(i / (n - 1))
        mt = 1 - t
        bx = mt ** 3 * x1 + 3 * mt ** 2 * t * c1[0] + 3 * mt * t ** 2 * c2[0] + t ** 3 * x2
        by = mt ** 3 * y1 + 3 * mt ** 2 * t * c1[1] + 3 * mt * t ** 2 * c2[1] + t ** 3 * y2
        pts.append((bx, by))
    return pts


def _ease(t: float) -> float:
    """Smoothstep ease-in/ease-out velocity profile on [0, 1]."""
    return t * t * (3 - 2 * t)
