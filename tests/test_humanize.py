import random

from cadence.humanize import (
    HumanizeConfig,
    bezier_swipe,
    jitter_tap,
    sample_delay,
    sample_tap_duration,
)


def cfg(**kw):
    return HumanizeConfig(**kw)


def test_delay_is_deterministic_with_seed():
    a = sample_delay(cfg(), random.Random(42))
    b = sample_delay(cfg(), random.Random(42))
    assert a == b
    assert a > 0


def test_fixed_timing_returns_base():
    assert sample_delay(cfg(timing="fixed", base_delay_ms=800), random.Random(1)) == 800


def test_jitter_stays_within_target():
    rng = random.Random(7)
    for _ in range(500):
        x, y = jitter_tap(500, 500, 40, 40, cfg(), rng)
        assert 460 <= x <= 540
        assert 460 <= y <= 540


def test_jitter_disabled_returns_center():
    assert jitter_tap(500, 500, 40, 40, cfg(tap_jitter=False), random.Random(1)) == (500, 500)


def test_tap_duration_in_range():
    rng = random.Random(3)
    for _ in range(200):
        d = sample_tap_duration(cfg(tap_duration_ms=(60, 150)), rng)
        assert 60 <= d <= 150


def test_bezier_endpoints_and_count():
    pts = bezier_swipe(100, 200, 800, 900, cfg(), random.Random(5), n=24)
    assert len(pts) == 24
    assert pts[0] == (100, 200)
    assert abs(pts[-1][0] - 800) < 1e-6
    assert abs(pts[-1][1] - 900) < 1e-6


def test_linear_swipe_is_straight():
    pts = bezier_swipe(0, 0, 100, 100, cfg(swipe_curve="linear"), random.Random(1), n=10)
    for x, y in pts:
        assert abs(x - y) < 1e-9          # on the diagonal
