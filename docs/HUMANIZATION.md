# Humanization

Cadence perturbs its actions so they don't look like a robot hammering exact pixels at exact intervals. There are two honest reasons to do this, and one dishonest one it won't serve.

**The legitimate reasons:** (1) realistic input is *better testing* — apps behave differently under perfectly-regular synthetic input than under human-like input, and jittered timing surfaces race conditions that robotic timing hides; (2) it avoids stressing UIs in unnatural ways (e.g. tapping faster than any human could, which can trip rate limits and produce false test failures).

**What it is not:** a cloak that makes Terms-of-Service-violating automation safe. It isn't, and this doc is explicit about why. See [SAFETY.md](SAFETY.md).

## Tier 1 — gesture-level realism (what Cadence does)

These remove the obvious statistical signatures of synthetic input.

**Timing — log-normal, not uniform.** Human inter-action times cluster around a typical value with a long right tail (occasional longer pauses to read or hesitate). Uniform `random(0.5, 1.5)` delays are themselves a giveaway because real timing isn't uniform. Cadence samples delays from a log-normal (or gamma) distribution centered on `base_delay_ms`, so most actions come quickly and a few take noticeably longer.

**Tap coordinates — a Gaussian cloud inside the target.** Instead of the geometric center every time, Cadence samples a point from a 2D Gaussian centered on the target, σ ≈ ¼ of the target's half-width, clipped to the target bounds. Real taps scatter; a perfectly centered tap every time is abnormal.

**Tap duration — variable.** A real touch has a measurable down→up time (~60–150 ms), and it varies. Cadence randomizes within `tap_duration_ms`. Zero-duration or constant-duration taps are abnormal.

**Swipes — curved and eased.** Humans don't swipe in straight lines at constant velocity. Cadence generates the swipe path as a cubic Bézier with slightly randomized control points (a small perpendicular bow) and samples points along it with an ease-in/ease-out velocity profile. A linear, constant-speed swipe is one of the easiest synthetic signatures to spot.

**Occasional imperfection.** Flawlessness is itself anomalous. At `imperfection_rate`, Cadence will occasionally take a benign wrong turn and correct it, or pause as if reading. Off by default-ish (low rate); raise it for more human-like sessions, lower it for fast deterministic testing.

**Session rhythm.** `session_window_min` randomizes *when* a scheduled routine actually starts within a window, so a daily routine doesn't fire at the same wall-clock instant every day.

Configure all of this under `humanization:` in [CONFIGURATION.md](CONFIGURATION.md). For pure functional testing where you *want* determinism, run `--no-humanization`.

## Tier 2 — what humanization fundamentally cannot fix

This is the honest part, and it's why humanization is not a safety feature against a determined platform:

- **Injection-source fingerprinting.** A synthetic `MotionEvent` injected via ADB or an accessibility service carries provenance that differs from a real digitizer event — different flags, and none of the hardware-layer noise (pressure/size jitter, micro-timing irregularity) that a real capacitive sensor produces. No amount of timing or coordinate jitter changes *where in the stack the event was born*. Root `/dev/input` injection is closer to hardware but still distinguishable.
- **Automation-surface detection.** Apps can detect an enabled accessibility service, or ADB/debug state, and flag the session regardless of how human the taps look.
- **Environment anomalies.** A phone being driven while sitting motionless on a desk emits no accelerometer/gyro noise and no incidental touches — a held phone never does that. Unfixable from the input layer.
- **Server-side behavioral analysis.** This is the one that actually catches people and is completely invisible to client-side humanization. Platforms correlate behavior over *time*: flawless daily attendance, identical task sets, narrow time bands, month after month. Statistically perfect consistency is a stronger signal than any single session's input. The only mitigation is genuine irregularity — sometimes not running at all — which partly defeats the purpose of automation.

## The takeaway

Tier 1 moves you from "detectable by a trivial rule" to "detectable by effort," which is the right thing to do for honest testing realism and for not abusing UIs. It does **not** make you invisible, and against platforms that run Tier-2 detection (which is most of the big ones), humanization changes the odds, not the outcome. If a routine's only purpose is to evade detection at scale, humanization won't save it and Cadence isn't the tool for it.
