"""Validates the Gemini request is built on the real SDK surface — offline.

Skipped unless the `gemini` extra is installed. Constructs the client, the
generation config, and the image Part without making any network call, so SDK
breaking changes (the part previously written from memory) get caught by CI.
"""

import pytest

pytest.importorskip("google.genai")

from cadence.config import ProviderConfig
from cadence.providers.gemini import GeminiProvider


def test_provider_builds_request_offline(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-not-used-no-network")
    p = GeminiProvider(ProviderConfig(api_key="env:GEMINI_API_KEY", thinking="off"))

    p._client_lazy()                       # constructs Client (no network) + loads types
    cfg = p._gen_config()                  # builds GenerateContentConfig from our fields
    assert cfg.max_output_tokens == 512
    assert cfg.response_mime_type == "application/json"
    assert cfg.thinking_config is not None and cfg.thinking_config.thinking_budget == 0

    # the screenshot payload shape we previously guessed wrong:
    part = p._types.Part.from_bytes(data=b"\x89PNG", mime_type="image/png")
    assert type(part).__name__ == "Part"
