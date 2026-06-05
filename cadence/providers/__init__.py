"""Providers — the 'brain'. v0.1 ships Gemini; anthropic/openai/ollama are next."""

from __future__ import annotations

from .base import Provider


def build_provider(provider_cfg) -> Provider:
    if provider_cfg.name == "gemini":
        from .gemini import GeminiProvider
        return GeminiProvider(provider_cfg)
    raise NotImplementedError(
        f"provider {provider_cfg.name!r} is on the roadmap but not in v0.1 — "
        "use 'gemini' (docs/PROVIDERS.md)"
    )
