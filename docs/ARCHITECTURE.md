# Architecture

Cadence is three layers with a hard seam between each: a **device backend** (hands), a **provider** (brain), and the **core** (everything that makes them work together safely). The seams are the design — each layer is swappable without touching the others.

```
            ┌──────────────────────────────────────────────────┐
            │                      CORE                          │
            │                                                    │
   goal ───▶│  Planner ──▶ Confirm gate ──▶ State machine ──┐   │
            │                                    │            │   │
            │   ┌────────────────────────────────▼─────────┐ │   │
            │   │  per-step loop:                           │ │   │
            │   │  capture → settle → decide → humanize →   │ │   │
            │   │  inject → verify → log                    │ │   │
            │   └───────┬───────────────────────┬──────────┘ │   │
            └───────────┼───────────────────────┼────────────┘   │
                        ▼                        ▼                 
                 ┌─────────────┐         ┌──────────────┐         
                 │  PROVIDER   │         │   DEVICE      │         
                 │  (brain)    │         │   BACKEND     │         
                 │ Gemini/etc. │         │ adb/shizuku/  │         
                 │             │         │ root          │         
                 └─────────────┘         └──────────────┘         
```

## The per-step loop

Each step of a routine runs the same cycle:

1. **Capture** — grab the current screen (`adb exec-out screencap -p`), downscaled per `device.screenshot_scale`.
2. **Settle** — frame-diff against the previous capture until the screen stops changing, up to `settle_timeout_ms`. This is what handles variable-length animations and transitions *without* hard-coded sleeps. Acting on a mid-animation frame is a top cause of mis-taps.
3. **Classify (optional)** — a cheap model answers "is this a known/expected screen, an interstitial, or unknown?" If it's a known interstitial, the recovery branch dismisses it without spending the expensive model.
4. **Decide** — the provider receives the screenshot, the current goal, recent action history, and any profile hints, and returns a normalized `Decision` (see [PROVIDERS.md](PROVIDERS.md)).
5. **Humanize** — the raw action (e.g. `TAP 540,1200`) is perturbed: coordinate jitter inside the target, a sampled inter-action delay, a randomized touch duration, curved swipes (see [HUMANIZATION.md](HUMANIZATION.md)).
6. **Inject** — the device backend performs the action (`adb shell input tap`, Shizuku, or raw `/dev/input`).
7. **Verify** — re-capture and confirm the screen actually changed in the expected direction. If it didn't (missed tap, popup intercepted), re-decide rather than blindly firing the next step.
8. **Log** — append the screenshot, the action, and the model's one-line rationale to the run log.

## The recovery branch

The single biggest source of real-world failure is unexpected interstitials — event banners, rate-the-app prompts, "you've got mail" overlays. When `classify` reports an unknown screen, Cadence consults the profile's `interstitials` and asks the model to find and tap the non-destructive dismiss control ("Close", "Later"), then returns to the task. If it sees `stop_on_unknown_after` consecutive unrecognized screens, it aborts cleanly rather than flailing. This is deliberately conservative: stopping is always safe; guessing on an unknown screen is not.

## Coordinate normalization

Providers return coordinates in a normalized **0–1000** space on each axis, origin top-left. The core rescales to the device's real resolution (auto-detected via `adb shell wm size`, overridable in config) immediately before injection. Centralizing this means adapters never deal with device pixels and every provider behaves identically. Get this wrong and *every* tap lands in the wrong place — it's the first thing `cadence doctor` validates.

## The planner and confirm gate

The planner expands a freeform goal (or a profile task) into an ordered list of sub-goals and presents them for confirmation. The confirm gate is not cosmetic: it's the boundary between "the model proposed a plan" and "the device did something." Sensitive actions (payment, deletion, posting, permission/security changes) trigger an additional inline confirmation even mid-run, and there is intentionally no global "auto-approve everything" — see [TASKS.md](TASKS.md).

## Why this is single-device / single-account

Cadence's process model is one orchestrator ↔ one device ↔ one session. There is no fleet manager, no account pool, no per-device identity rotation, and no scheduler for coordinating many sessions. That's a deliberate boundary, not a missing feature: the multi-device/multi-account orchestration layer is precisely what turns automation into farming and manipulation infrastructure, and it's out of scope (see [SAFETY.md](SAFETY.md)). The core data structures assume a single session by design, so this isn't a switch someone flips later.

## Why iOS can't work

The whole approach rests on two capabilities Android grants and iOS does not, for third parties:

- **Programmatic screen capture** of arbitrary apps (Android: `screencap` / MediaProjection).
- **Synthetic input injection** into arbitrary apps (Android: `adb shell input`, AccessibilityService `dispatchGesture`, or root `/dev/input`).

iOS sandboxes both. There is no third-party equivalent of ADB input injection, no cross-app accessibility gesture dispatch you can drive externally, and no sanctioned way to feed synthetic touches into another app. Apple's automation surfaces (XCUITest, Shortcuts) are either confined to your own app under a test harness or deliberately can't do free-form cross-app control. So an iOS port isn't a porting effort — the primitives don't exist. Android only.

## Logging and reproducibility

Every run writes to `run.log_dir/<timestamp>/`: ordered screenshots, the action taken at each, the model's rationale, and timings. Because the run is non-deterministic (live app + model), the log is how you debug — you replay the screenshots to see exactly which screen confused the model and adjust the goal, the profile interstitials, or the pacing accordingly. `--dry-run` produces the same log with injection disabled, so you can validate a routine's *decisions* without it touching anything.
