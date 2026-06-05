"""Coordinate normalization between the provider's 0-1000 space and device pixels.

Providers return coordinates in a normalized 0-1000 range on each axis with the
origin at the top-left (docs/PROVIDERS.md). The core rescales to the device's real
resolution immediately before injection. Centralizing this is the whole point of the
provider abstraction: get it wrong and *every* tap lands in the wrong place — which
is why `cadence doctor` validates it first.
"""

from __future__ import annotations

NORM_MAX = 1000


def _clamp(value: int, lo: int, hi: int) -> int:
    return lo if value < lo else hi if value > hi else value


def to_pixels(x: float, y: float, width: int, height: int) -> tuple[int, int]:
    """Map normalized (0-1000) coordinates to on-screen device pixels."""
    px = round(x / NORM_MAX * width)
    py = round(y / NORM_MAX * height)
    return _clamp(px, 0, width - 1), _clamp(py, 0, height - 1)


def from_pixels(px: int, py: int, width: int, height: int) -> tuple[int, int]:
    """Inverse of :func:`to_pixels`: device pixels back to normalized 0-1000."""
    x = round(px / width * NORM_MAX)
    y = round(py / height * NORM_MAX)
    return _clamp(x, 0, NORM_MAX), _clamp(y, 0, NORM_MAX)


def parse_resolution(text: str) -> tuple[int, int]:
    """Parse ``'WIDTHxHEIGHT'`` (e.g. ``'1080x2400'``) to ``(width, height)``."""
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"bad resolution {text!r}, expected like '1080x2400'") from exc
