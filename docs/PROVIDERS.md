# Providers (BYOK)

Cadence separates *deciding what to do* (the provider) from *doing it* (the device backend). The provider is a thin adapter around a vision-capable model. Gemini is the default and best-supported; anything else is a config change.

## The contract

Every adapter implements one method:

```python
class Provider:
    def decide(self,
               screenshot: Image,          # current screen (already downscaled per config)
               goal: str,                  # the current step's goal, in natural language
               history: list[Action],      # recent actions taken this run
               hints: ProfileHints | None  # optional per-app hints (see PROFILES.md)
               ) -> Decision: ...
```

It returns a normalized `Decision`:

```python
Decision = {
  "action": "TAP" | "SWIPE" | "TYPE" | "BACK" | "WAIT" | "DONE" | "UNKNOWN",
  "x": int, "y": int,            # normalized 0–1000 (origin top-left)
  "x2": int, "y2": int,          # SWIPE endpoint, normalized 0–1000
  "text": str,                   # for TYPE
  "rationale": str,              # one line, for the run log
  "needs_confirmation": bool     # provider is asking the human before a sensitive action
}
```

**The coordinate contract is the whole point of the abstraction.** Every provider returns coordinates in a normalized 0–1000 space on each axis. Cadence rescales to the device's real resolution before injecting. This is also the classic bug source: a provider that returns raw pixels, or uses a different origin, will make every tap land in the wrong place. Adapters are responsible for normalizing into 0–1000 *before* returning.

## Two modes

**Native computer-use** — the model has a first-class UI-action tool and returns an action directly. Lowest prompt overhead, best grounding. Gemini (`gemini-3-flash-preview`), Anthropic computer-use, and OpenAI computer-use models run here.

**Scaffolded vision** — the model is a plain vision LLM with no action tool. Cadence supplies a structured prompt ("here is the screen and the goal; respond ONLY with JSON: action + normalized coordinates") and parses the JSON. Works with almost any vision model, including local ones, at lower accuracy. Used for the cheap classifier and for offline/local setups.

The adapter declares which mode it is; the rest of Cadence is identical either way.

## Configuring a provider

### Gemini (default)

```yaml
provider:
  name: gemini
  model: gemini-3-flash-preview   # the model with built-in Computer Use
  api_key: env:GEMINI_API_KEY
  thinking: low                   # off | low | high  (billed as output; keep low for menus)
```

Notes specific to Gemini:
- Computer Use is built into `gemini-3-flash-preview`; you do not add a separate tool.
- Not every Flash model supports Computer Use — notably the newest "Flash" tier may not. If you switch models and get capability errors, the model lacks the computer-use tool; either pick one that has it or set the adapter to scaffolded mode.
- `thinking` maps to Gemini's per-request thinking budget. `low` is plenty for UI navigation and meaningfully cheaper.

### Anthropic / OpenAI

```yaml
provider:
  name: anthropic        # or: openai
  model: <computer-use-capable model>
  api_key: env:ANTHROPIC_API_KEY    # or env:OPENAI_API_KEY
```

Both run in native computer-use mode. Their action schemas differ from Gemini's; the adapter maps them onto the normalized `Decision` above.

### Local (Ollama / self-hosted vision)

```yaml
provider:
  name: ollama
  model: <a vision model you've pulled>
  endpoint: http://localhost:11434
```

Runs in scaffolded mode, fully offline, no key, no per-token cost. Accuracy is lower and you'll lean harder on app profiles and recovery — but nothing leaves your machine.

## Mixing providers: the classifier

You can run a **cheap** model for "is this a normal expected screen / which known screen is this?" and reserve the **capable** model for actual action decisions. This is the biggest single cost lever for long routines.

```yaml
provider:                          # the expensive "brain"
  name: gemini
  model: gemini-3-flash-preview
classifier:                        # the cheap "eyes"
  enabled: true
  name: gemini
  model: gemini-3.1-flash-lite
```

The classifier and the brain can be different providers entirely (e.g. local classifier + cloud brain).

## Writing a new adapter

1. Subclass `Provider`, implement `decide(...)`, declare `mode = "native" | "scaffolded"`.
2. Normalize all coordinates to 0–1000 before returning.
3. Map the model's refusal/confirmation signals onto `needs_confirmation=True` rather than guessing.
4. Register it under a `name:` so config can select it.
5. Add a short section here and a row to the table in the README.

Keep adapters dumb: they translate, they don't make policy. The state machine, humanization, and safety rails live in the core, not in the adapter.

Next: [TASKS.md](TASKS.md) for how goals become a confirmed plan.
