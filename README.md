# Cadence

> Tell it what to do in plain English. It confirms the plan. Then it does it on your Android device.

**Cadence** is an open-source, provider-agnostic agentic UI-automation framework for Android. You describe a routine in natural language — *"log in, add an item to the cart, go to checkout, and stop before paying"* — Cadence turns that into a concrete plan, shows it to you for confirmation, and then drives the screen the way a person would: looking at it, deciding the next action, and performing it.

It works on **any app**, including apps with no accessibility tree (anything rendered to a raw graphics surface), because it perceives the screen *visually* rather than relying on UI metadata.

**What it's for:**

- **Mobile QA & test automation** — drive real apps through real flows on real devices, without brittle hard-coded selectors that break when a button moves.
- **Accessibility automation** — operate apps on behalf of users who can't tap through them manually.
- **Personal, single-account productivity** — automate *your own* repetitive routines on *your own* accounts, within each app's rules.

> ⚠️ **Android only.** iOS is intentionally unsupported — Apple does not expose an equivalent to ADB input injection or accessibility gesture dispatch to third parties, so this approach cannot work on iOS. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

> 🚫 **Out of scope by design.** Cadence is a **single-device, single-account** tool. It is not a multi-account / multi-device orchestration platform, and it will not ship account-farming or platform-detection-evasion features. See [docs/SAFETY.md](docs/SAFETY.md) for the line we hold and why.

> 🟡 **Cadence is a working name** — rename it freely; it only appears in headings.

---

## How it works in one picture

```
  ┌─────────────────────────────────────────────────────────────┐
  │  You: "run the checkout smoke test, stop before paying"       │
  └───────────────────────────────┬─────────────────────────────┘
                                   ▼
            ┌──────────────────────────────────────┐
            │  Plan + Confirm                       │
            │  "I'll: 1) open the app               │
            │         2) add item to cart           │
            │         3) go to checkout             │
            │         4) STOP (no payment).          │
            │   Proceed? [y/N]"                     │
            └──────────────────┬───────────────────┘
                               ▼  (you approve)
   ┌───────────────────────────────────────────────────────────┐
   │                     THE LOOP (per step)                     │
   │                                                             │
   │   screencap ──▶ settle? ──▶ LLM decides ──▶ humanize ──▶    │
   │       ▲                      (TAP x,y)       (jitter)       │
   │       │                                          │          │
   │       └────────── verify screen changed ◀── inject tap     │
   └───────────────────────────────────────────────────────────┘
```

The brain (which action to take) is a vision-capable LLM. The hands (actually tapping) are ADB / Shizuku / root on the device. Cadence is the glue, the state machine, and the safety/humanization layer around them.

---

## Quickstart

```bash
# 1. Prerequisites: Python 3.11–3.13, a USB cable, and adb installed.
#    Full setup (incl. Shizuku): docs/INSTALL.md
pipx install cadence-android

# 2. Plug your phone in, enable USB debugging, confirm it's visible:
adb devices

# 3. Bring your own key (Gemini is the default provider):
export GEMINI_API_KEY="your-key-here"

# 4. Copy the example config:
cp cadence.config.example.yaml cadence.config.yaml

# 5. Run a routine in plain English:
cadence run "open settings, turn on airplane mode, then turn it back off"

# ...or run a named routine from an app profile (see docs/PROFILES.md):
cadence run --profile my-app login_smoke_test
```

Cadence prints the plan it intends to follow and waits for your `y` before touching anything. Nothing happens without your confirmation, and you can run any routine with `--dry-run` to see the decisions without injecting a single tap.

---

## Bring Your Own Key (BYOK) — and bring your own *provider*

Cadence is **built Gemini-first but is provider-agnostic.** You hold the key; Cadence never proxies your calls through anyone's servers, so there's no shared bill and no central key to leak.

The default is **Google Gemini** (`gemini-3-flash-preview`) because it ships a built-in *Computer Use* capability that returns UI actions directly. But the provider layer is a thin adapter — switch models in two lines of config:

| Provider | Models | Mode | Notes |
|---|---|---|---|
| **Gemini** (default) | `gemini-3-flash-preview` | native computer-use | Recommended. Cheapest capable tier. |
| Gemini (vision) | `gemini-3.1-flash-lite` | scaffolded vision | Cheap classifier / fallback. |
| Anthropic | Claude (computer use) | native computer-use | Drop-in via adapter. |
| OpenAI | GPT computer-use models | native computer-use | Drop-in via adapter. |
| Local | Ollama / vision models | scaffolded vision | Fully offline, lower accuracy. |

Any vision-capable model works in *scaffolded* mode (Cadence supplies the action-prompt and parses coordinates); models with a native computer-use tool work in *native* mode. All adapters normalize to the same coordinate space, so the rest of Cadence doesn't care which you chose. See [docs/PROVIDERS.md](docs/PROVIDERS.md).

---

## What it costs you to run

Because of BYOK, **the project costs you nothing to run** — you pay only your own model usage, and light use can fit inside free tiers.

- Typical routine: **30–60 model steps**.
- Optimized cost: **~$0.06–0.25 per run** (~$2–7/month for a daily routine).
- Free-tier daily quotas can cover a light user at **$0**.

Cost levers built in: per-request thinking budget, screenshot downscaling, context caching of the static prompt, and a cheap classifier model for "what screen is this?" checks. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

---

## Documentation

| Doc | What's in it |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | Android setup: ADB, Shizuku, root — the friction walkthrough. |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | The config file, every option, and cost tuning. |
| [docs/PROVIDERS.md](docs/PROVIDERS.md) | The provider adapter interface; using Gemini and others. |
| [docs/TASKS.md](docs/TASKS.md) | Writing natural-language tasks; the confirm→execute flow. |
| [docs/PROFILES.md](docs/PROFILES.md) | The community app-profile format and how to author one. |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | The full system design and the loop internals. |
| [docs/HUMANIZATION.md](docs/HUMANIZATION.md) | Realistic input timing/movement, and the honest limits of it. |
| [docs/SAFETY.md](docs/SAFETY.md) | **Read this.** Scope, ToS, responsible use, what we won't build. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute — especially app profiles. |
| [ROADMAP.md](ROADMAP.md) | Where this is going. |

---

## Responsible use

Cadence is a general automation tool, which means it can be pointed at things it shouldn't be. The rules of the road:

- **Automate software you own or are authorized to automate.** QA on your team's app, your own accounts, accessibility tasks — all fine.
- **Automating online games and many social apps violates their Terms of Service.** If you do it anyway, the risk to that account is yours. Humanization lowers the odds of a fast automated flag; it does **not** make you safe and cannot defeat server-side behavioral analysis.
- **No mass / multi-account use.** Cadence is single-device, single-account by design. We don't build farming or evasion features, and PRs that add them will be declined.

See [docs/SAFETY.md](docs/SAFETY.md) for the full picture.

## License

[MIT](LICENSE). Contributions welcome under the same license.
