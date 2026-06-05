# Safety, Scope & Responsible Use

Cadence is a general automation tool. General tools can be pointed at things they shouldn't be, so this document is explicit about the line the project holds, what's your risk to carry, and what we won't build. Read it before pointing Cadence at anything you don't own.

> This is not legal advice. It's the project's stance and a plain-language summary of the risks.

## The scope boundary: single device, single account

Cadence is designed and maintained as a **one orchestrator → one device → one account** tool. That boundary is intentional and structural (see [ARCHITECTURE.md](ARCHITECTURE.md)), not a feature we haven't gotten to yet.

**Explicitly out of scope — we will not build, and will decline PRs that add:**

- Multi-device / multi-account orchestration (fleets of phones, account pools, session schedulers across many identities).
- Identity-rotation, device-fingerprint spoofing, or proxy/IP rotation aimed at evading platform association of accounts.
- Detection-evasion features whose purpose is to defeat platform anti-automation at scale.
- Profiles whose primary purpose is mass Terms-of-Service violation (engagement farming, mass account creation, coordinated posting).

The reason is simple: that combination — many accounts + evasion + automation — is the infrastructure of coordinated inauthentic behavior (fake engagement, astroturfing, spam, and the device layer under romance/investment scams). It's a different product from "automate my own app/account," it's what platforms invest heavily to destroy, and it's not what this project is for. Keeping Cadence single-session keeps it a tool we can stand behind.

## What Cadence is for

- **Mobile QA & test automation** of apps you build or are authorized to test.
- **Accessibility automation** — operating apps for users who can't tap through them.
- **Personal, single-account productivity** — automating *your own* routines on *your own* accounts, within each app's rules.

## Terms of Service — your risk to carry

**Automating online games and many social/consumer apps violates their Terms of Service.** This includes the kind of "daily chores" automation that's a common first idea. Some specifics worth internalizing:

- **Games with anti-cheat (e.g. major EA titles) actively detect and ban automation**, and bans typically hit the *entire account* — including money spent and competitive progress.
- **Social platforms** treat automated account activity as a policy violation and may suspend accounts; some have pursued operators of automation/fake-engagement tooling directly.
- **Humanization does not make this safe.** As [HUMANIZATION.md](HUMANIZATION.md) explains in detail, gesture-level realism cannot defeat injection-source fingerprinting, automation-surface detection, or server-side behavioral analysis. It changes the odds of a fast automated flag; it does not change the outcome against a determined platform.

If you choose to automate something against its ToS anyway, **that risk is entirely yours.** Don't do it on accounts you can't afford to lose, and don't expect the project to help you evade detection.

## Things Cadence does to stay on the safe side

- **Confirm-before-execute is on by default.** Nothing happens without you approving the plan.
- **Sensitive actions pause for an extra confirmation** — payments, deletions, posting/publishing, permission grants, account/security changes — even mid-run. There is no global "auto-approve everything."
- **Recovery prefers stopping over guessing.** On repeated unknown screens, Cadence aborts cleanly.
- **`--dry-run`** lets you validate a routine's decisions without injecting anything.
- **BYOK, no proxy.** Your model calls go straight from your machine to your provider; the project never holds your key or sees your traffic.

## Privacy

- Cadence captures screenshots of whatever is on screen and sends them to your chosen model provider. **Don't run it on screens with secrets you don't want sent to that provider** (passwords, 2FA codes, private messages) — or use a local provider (see [PROVIDERS.md](PROVIDERS.md)) to keep everything on-device.
- Run logs contain screenshots. Treat `run.log_dir` as sensitive and don't commit it.
- Some screens set `FLAG_SECURE` and can't be captured at all; that's a feature, not a bug.

## If you're unsure whether a use is OK

A quick test: *Would you be comfortable describing this use, by name, to the platform you're automating?* If automating your own QA suite or your own inbox — yes, fine. If the honest description is "operating many accounts to fake activity" or "evading detection" — that's the out-of-scope side, and Cadence isn't the right tool.

Questions about whether a contribution crosses the line: open an issue before building it. We'd rather discuss scope early than reject a PR you spent a weekend on.
