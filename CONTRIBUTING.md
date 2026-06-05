# Contributing

Thanks for considering a contribution. The highest-value, lowest-friction contribution is an **app profile** — but adapters, recovery improvements, and docs are all welcome.

## Before anything: scope

Cadence is a **single-device, single-account** automation tool for QA, accessibility, and personal use. Contributions that push it toward multi-account orchestration, identity/fingerprint spoofing, or detection-evasion-at-scale will be declined — see [docs/SAFETY.md](docs/SAFETY.md). If you're unsure whether an idea fits, **open an issue first**; we'd rather talk scope before you spend a weekend.

## Ways to contribute

### 1. App profiles (start here)

Profiles teach Cadence about one app's quirks. They're small YAML files, take ~15 minutes for a first pass, and help everyone running that app. See [docs/PROFILES.md](docs/PROFILES.md) for the schema and the authoring walkthrough.

- Put the file in `profiles/<app-id>.yaml`.
- Cover the common path; mark gaps with `# TODO:` comments — partial profiles are useful.
- Use **non-destructive** dismiss actions in interstitials ("Later", "Close", never "Rate now"/"Buy"/"Delete").
- Don't submit profiles whose primary purpose is to violate an app's ToS at scale.

### 2. Provider adapters

Add support for a new model/provider by implementing the `Provider` interface (see [docs/PROVIDERS.md](docs/PROVIDERS.md)). Keep adapters thin: translate the model's output into the normalized `Decision`, normalize coordinates to 0–1000, and map confirmation/refusal signals honestly. Policy lives in the core, not the adapter.

### 3. Device backends

Improvements to the `adb` / `shizuku` / `root` backends — reliability, reconnect handling, input fidelity — are welcome.

### 4. Recovery & robustness

The recovery branch (handling unexpected interstitials) is where real-world reliability lives. Better generic dismissal heuristics, better settle-detection, better verify-screen-changed logic — all high impact.

### 5. Docs

If something tripped you up, fix the doc that should have prevented it.

## Development setup

```bash
git clone https://github.com/<your-handle>/cadence
cd cadence
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cadence doctor          # verify your device + provider are wired up
pytest                  # run the test suite
```

You'll need a connected Android device (or emulator) and a provider key for end-to-end testing. Unit tests for the core (state machine, coordinate rescaling, humanization samplers) run without a device.

## Pull request checklist

- [ ] Scope is consistent with [docs/SAFETY.md](docs/SAFETY.md).
- [ ] `pytest` passes; new logic has tests where practical.
- [ ] New provider/backend/profile has a short doc section and (for providers) a README table row.
- [ ] No secrets, keys, or `run.log_dir` screenshots committed.
- [ ] Coordinate-handling code keeps the normalized 0–1000 contract.

## Code of conduct

Be decent. Assume good faith. Keep discussion technical. Harassment or bad-faith participation isn't welcome.

## License

By contributing you agree your contribution is licensed under the project's [MIT License](LICENSE).
