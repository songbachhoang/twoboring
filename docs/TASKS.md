# Writing Tasks

Cadence's input is plain language. You describe *what you want to end up true*, not the taps to get there — the model figures out the taps by looking at the screen. This doc covers how to phrase tasks well, the confirm-before-execute flow, and how named profile tasks differ from freeform ones.

## The flow: describe → plan → confirm → execute

1. **You describe** a goal (or list of goals) in words.
2. **Cadence plans** — it expands your description into an ordered list of discrete steps, each with its own goal.
3. **Cadence confirms** — it prints the plan and waits for `y`. This is the safety gate; keep `run.confirm_before_execute: true`.
4. **Cadence executes** — one step at a time, verifying the screen changed as expected before advancing.

```
$ cadence run "open the app, go to my orders, and tell me my most recent order status"

Plan:
  1. Launch the app.
  2. Open the account / orders section.
  3. Open the most recent order.
  4. Read and report the order status. (read-only — no taps that change state)

Proceed? [y/N]
```

## How to phrase tasks well

**State the end condition, and the stop condition.** Especially for anything sensitive, say where to stop:

- Good: *"add the first item to the cart and go to checkout, but stop before entering any payment details."*
- Risky: *"buy the thing"* — leaves the model to decide where to stop on a money action.

**Be explicit about read-only vs. state-changing.** If you only want information, say so: *"don't tap anything that changes state — just read X and report it."* Cadence treats this as a constraint.

**Name the anchors you know.** If you know the screen names, use them: *"go to Settings → Network → Wi-Fi."* It gives the model grounding and reduces wrong turns.

**Don't over-specify coordinates or exact layouts.** The point of vision is robustness to layout changes. Telling it "tap the third icon from the left" backfires when the layout shifts; "open the search icon" survives it.

**One routine, several goals.** You can pass multiple goals; Cadence sequences them:

```bash
cadence run "1) open notifications and clear them all  2) go to home  3) open the calendar and read today's events"
```

## Sensitive actions always pause

Regardless of phrasing, Cadence pauses for an extra confirmation before irreversible or sensitive actions — submitting payment, deleting data, posting/publishing, changing account or security settings, accepting permissions. The provider can also raise `needs_confirmation` on its own when it's about to do something consequential. You approve in the terminal; the run continues. This mirrors the safety posture the underlying computer-use models already enforce.

If you want a fully unattended run, you must explicitly allow specific action classes — and Cadence will still refuse to auto-confirm payments and account/security changes. There is no "approve everything forever" switch by design.

## Named tasks from a profile

For routines you run often, define them once in an [app profile](PROFILES.md) and call them by name. A profile task is just a saved goal (plus optional hints), so this:

```bash
cadence run --profile my-app login_smoke_test checkout_smoke_test
```

is equivalent to typing out both goals as freeform text, but it's reusable, shareable, and benefits from the profile's known-screen and interstitial hints (which make execution more reliable). Use freeform for one-offs; promote anything you repeat into a profile task.

## A QA example

```yaml
# in profiles/my-app.yaml
tasks:
  checkout_smoke_test:
    label: "Checkout smoke test"
    goal: >
      From the home screen, search for a product, open the first result,
      add it to the cart, open the cart, and proceed to the checkout screen.
      STOP at the checkout screen. Do NOT enter payment details or place an order.
      Report whether each step succeeded.
```

```bash
cadence run --profile my-app checkout_smoke_test --dry-run   # see the decisions, inject nothing
cadence run --profile my-app checkout_smoke_test             # real run, with the stop built in
```

## A personal example (your own account, within the app's rules)

```yaml
tasks:
  morning_triage:
    label: "Morning triage"
    goal: >
      Open the email app, archive every newsletter in the inbox, and leave
      everything else untouched. Report how many you archived.
```

Reading logs after a run: every step's screenshot, action, and the model's one-line rationale are written to `run.log_dir`, so when a routine does something unexpected you can see exactly which screen confused it and why. That log is your main debugging tool — see [ARCHITECTURE.md](ARCHITECTURE.md).
