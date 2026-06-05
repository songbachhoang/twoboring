# Roadmap

Directional, not a promise. Ordering reflects priority. Scope stays within the single-device / single-account boundary in [docs/SAFETY.md](docs/SAFETY.md).

## v0.1 — Walking skeleton
- [ ] ADB backend (USB): capture + tap + swipe + type.
- [ ] Gemini provider (native computer-use, `gemini-3-flash-preview`).
- [ ] Core loop: capture → settle → decide → inject → verify → log.
- [ ] Planner + confirm gate (the `y/N` before execution).
- [ ] Coordinate normalization (0–1000 → device pixels) + `cadence doctor`.
- [ ] `--dry-run`.

## v0.2 — Reliability
- [ ] Frame-diff settle detection (no hard-coded sleeps).
- [ ] Recovery branch + profile-driven interstitial handling.
- [ ] Cheap classifier model ("known screen / interstitial / unknown").
- [ ] Verify-screen-changed with re-decide on mismatch.
- [ ] Structured run logs (screenshots + actions + rationale).

## v0.3 — Usability & cost
- [ ] App-profile loader + schema validation; first community profiles.
- [ ] Humanization layer (log-normal timing, Gaussian tap cloud, Bézier swipes).
- [ ] Cost levers: thinking budget, screenshot scaling, context caching.
- [ ] `cadence run` ergonomics: multi-goal, profile task names.

## v0.4 — Provider breadth
- [ ] Anthropic + OpenAI computer-use adapters.
- [ ] Local/Ollama scaffolded-vision adapter (fully offline).
- [ ] Mixed provider/classifier configs.

## v0.5 — Backends & robustness
- [ ] Shizuku backend (no-root, no on-device a11y service).
- [ ] Root `/dev/input` backend (highest input fidelity).
- [ ] Wireless ADB stability + reconnect handling.

## Later / exploring
- [ ] QA-oriented assertions in tasks ("verify the cart shows 1 item").
- [ ] Replay: turn a successful run into a deterministic macro for fixed paths.
- [ ] A small profile registry/index so users can discover community profiles.
- [ ] Emulator-first CI for the core loop.
- [ ] On-device backend — standalone Android app (MediaProjection capture + AccessibilityService or root injection) so a routine can run without a tethered computer. A post-core option for the QA / accessibility / own-account use cases; a convenience, **not** stealth — an enabled accessibility service *raises* detectability (see [docs/HUMANIZATION.md](docs/HUMANIZATION.md)). Stays single-device / single-account.

## Explicitly NOT on the roadmap
- Multi-device / multi-account orchestration, account pools, session schedulers.
- Identity/fingerprint spoofing, proxy/IP rotation, anti-detection-at-scale.
- Anything whose primary purpose is mass Terms-of-Service violation.

See [docs/SAFETY.md](docs/SAFETY.md) for why these are out of scope.
