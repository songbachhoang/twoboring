# Configuration

Cadence reads a single YAML file, `cadence.config.yaml`, from the working directory (override with `--config path`). Start from `cadence.config.example.yaml` and change only what you need — every field has a sane default.

## The full config, annotated

```yaml
# ── Device & input ─────────────────────────────────────────────
device:
  serial: auto            # auto = first device from `adb devices`; or a specific serial
  backend: adb            # adb | shizuku | root   (see INSTALL.md)
  screenshot_scale: 0.5   # downscale screenshots before sending to the model.
                          # 0.5 ≈ halves image-input tokens; menus stay legible.
  resolution: auto        # auto-detected; override as "1080x2400" only if needed

# ── Primary provider (the "brain") ─────────────────────────────
provider:
  name: gemini                    # gemini | anthropic | openai | ollama  (see PROVIDERS.md)
  model: gemini-3-flash-preview   # the model that has built-in Computer Use
  api_key: env:GEMINI_API_KEY     # env:VAR reads from environment (never hard-code keys)
  thinking: low                   # off | low | high  — Gemini-only; ignored by other providers.
                                  # Menu navigation rarely needs more than `low`.
  max_output_tokens: 512

# ── Optional cheap classifier (the "is this the normal screen?" check) ──
# Used to decide *whether* to spend the expensive model. Big cost saver.
classifier:
  enabled: true
  name: gemini
  model: gemini-3.1-flash-lite
  api_key: env:GEMINI_API_KEY

# ── Humanization (see HUMANIZATION.md) ─────────────────────────
humanization:
  enabled: true
  timing: lognormal       # lognormal | gamma | fixed
  base_delay_ms: 800      # center of the inter-action delay distribution
  tap_jitter: true        # scatter taps inside the target instead of dead-center
  tap_duration_ms: [60, 150]   # randomized touch-down→up time
  swipe_curve: bezier     # bezier | linear  — bezier looks human
  imperfection_rate: 0.05 # chance of a deliberate wrong-then-correct tap
  session_window_min: 120 # randomize routine start within this many minutes

# ── Run behavior & safety rails ────────────────────────────────
run:
  confirm_before_execute: true   # ALWAYS show the plan and wait for `y`. Keep this true.
  max_steps: 120                 # hard cap on model steps per routine (cost + runaway guard)
  stop_on_unknown_after: 3       # N consecutive unrecognized screens → abort cleanly
  settle_timeout_ms: 4000        # max wait for the screen to stop animating
  post_tap_wait_ms: 700          # pause after each tap before re-capturing
  verify_screen_change: true     # confirm the screen actually changed before advancing
  log_dir: ./runs                # per-run screenshots + actions + model rationale
  dry_run: false                 # true = plan and log decisions but DON'T inject taps

# ── Context caching (cost) ─────────────────────────────────────
cache:
  enabled: true          # cache the static system prompt + tool defs (≈90% input savings on those)
```

## Cost tuning — the four levers that matter

Your bill is dominated by (a) how many steps a routine takes and (b) tokens per step. In rough order of impact:

1. **`provider.thinking: low` (or `off`).** Gemini bills thinking tokens as output at the higher output rate. Menu navigation is not a reasoning-heavy task — turning thinking down is usually your single biggest saving with no accuracy loss.
2. **`classifier.enabled: true`.** Run a cheap model (`gemini-3.1-flash-lite`) to answer "is this a normal expected screen?" and only invoke the expensive computer-use model when you actually need a decision. Skips spend on routine transitions.
3. **`device.screenshot_scale: 0.5`.** Image input is a per-step fixed cost; halving resolution roughly halves it. Drop to `0.4` if your menus are still legible to the model.
4. **`cache.enabled: true`.** Your system prompt and action-tool definitions are identical every step — cache them so they bill at ~10% after the first call.

A note on what *doesn't* help here: batch pricing (50% off) is for asynchronous jobs and is incompatible with a real-time perceive→act loop, so Cadence does not use it.

## Per-routine overrides

Any `run.*` field can be overridden on the command line for a one-off:

```bash
cadence run "do my dailies" --dry-run            # see the plan + decisions, inject nothing
cadence run "do my dailies" --max-steps 60
cadence run "do my dailies" --no-humanization    # faster, for debugging only
```

## Multiple profiles / phones

Keep separate config files per device or per game and select with `--config`:

```bash
cadence run --config configs/pixel.yaml --profile fc-mobile daily_checkin
```

Next: [PROVIDERS.md](PROVIDERS.md) for swapping the model, or [TASKS.md](TASKS.md) for writing routines.
