# App Profiles

An **app profile** is a small YAML file that teaches Cadence about one app: its package name, the named routines you run on it, the popups it tends to throw, and how fast its screens settle. Profiles are optional — Cadence runs on freeform goals with no profile — but they make execution far more reliable, and they're the unit of community contribution.

The engine is app-agnostic; a profile is just knowledge *about* an app. A profile for a game and a profile for a banking app's QA suite have the same shape.

## Why profiles matter

The core loop perceives screens visually, so it works on an unknown app. What it can't know on its own is an app's *quirks*: that this app shows an event popup with the close button top-right, that its reward screens need a "tap to continue," that a particular transition takes two seconds to animate. Encoding those once, in a profile, turns "usually works" into "reliably works." This is exactly the knowledge that doesn't generalize across apps and therefore has to be captured per app — which is why profiles are community-contributed.

## Schema

```yaml
profile:
  id: my-app                         # unique slug, used on the CLI
  name: "My App"                     # human-readable
  package: com.example.myapp         # Android package (adb shell pm list packages)

# Named routines you can call: `cadence run --profile my-app <task_id>`
tasks:
  login_smoke_test:
    label: "Login smoke test"
    goal: >
      From the launcher, open the app, sign in with the saved credentials,
      and confirm the home screen loads. Report success or the failure point.
  checkout_smoke_test:
    label: "Checkout smoke test"
    goal: >
      Search a product, open the first result, add to cart, open cart,
      go to the checkout screen, then STOP. Do not enter payment or place an order.

# Popups/overlays the app throws that aren't part of any task.
# Cadence consults these when it hits an unrecognized screen (the recovery branch).
interstitials:
  - name: "event popup"
    looks_like: "A promotional banner overlay with a close (X) button, usually top-right."
    dismiss: "Tap the close/X button."
  - name: "rate-the-app prompt"
    looks_like: "A modal asking the user to rate the app, with 'Later' or 'No thanks'."
    dismiss: "Tap 'Later' or 'No thanks' — never 'Rate now'."
  - name: "reward / confirmation reveal"
    looks_like: "A full-screen animation prompting 'tap to continue'."
    dismiss: "Tap the center of the screen to advance until a normal menu returns."

# Pacing hints — tune to the app's animation speed.
pacing:
  settle_timeout_ms: 4000     # max wait for the screen to stop changing
  post_action_wait_ms: 700    # pause after each action before re-capturing

# Optional: named screen anchors the model can be told to expect, improving grounding.
anchors:
  home: "The main home screen with the bottom navigation bar."
  cart: "The cart screen listing items with a 'Checkout' button."
```

## Authoring a profile in ~15 minutes

1. **Get the package name:** `adb shell pm list packages | grep -i <app>`.
2. **Run the routine once with `--dry-run`** and watch the logged screenshots. Note every popup that appeared and every screen that confused the model.
3. **Write `interstitials`** for each popup you saw, describing what it looks like and how to dismiss it safely (always the *non-destructive* option — "Later", "Close", never "Rate now"/"Buy"/"Delete").
4. **Write your `tasks`** as end-state goals with explicit stop conditions for anything sensitive (see [TASKS.md](TASKS.md)).
5. **Tune `pacing`** if the app animates slowly (raise `settle_timeout_ms`) or fast (lower the waits to go quicker).
6. **Test with `--dry-run` again**, then a real run. Iterate.

## Reliability is a long tail (and that's fine)

A profile that works on a clean run is an afternoon. A profile that survives *every* popup, A/B layout, and seasonal event the app throws is weeks of incidental hardening — you discover each new quirk by hitting it. This is expected. Ship a profile that handles the common path, mark known gaps in a `# TODO:` comment, and let the community fill the tail. A partial profile is genuinely useful; don't wait for perfect.

## Contributing profiles

Profiles live in `profiles/` and are the easiest, highest-value contribution. See [CONTRIBUTING.md](../CONTRIBUTING.md). One rule up front: **don't contribute profiles whose primary purpose is to violate an app's Terms of Service at scale** (see [SAFETY.md](SAFETY.md)). QA suites, accessibility routines, and personal single-account chores are welcome.

A complete starter profile ships at [`profiles/example.yaml`](../profiles/example.yaml).
