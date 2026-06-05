"""Configuration loading and validation (docs/CONFIGURATION.md).

Reads a single YAML file, merges it over typed defaults, validates enums/ranges,
and resolves ``env:VAR`` references for secrets. Every field has a sane default,
so a minimal config — or none at all — still produces a usable Config.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields

import yaml


def resolve_env(value):
    """Resolve an ``env:VAR`` reference to its environment value; pass others through."""
    if isinstance(value, str) and value.startswith("env:"):
        return os.environ.get(value[4:])
    return value


@dataclass
class DeviceConfig:
    serial: str = "auto"
    backend: str = "adb"
    screenshot_scale: float = 0.5
    resolution: str = "auto"


@dataclass
class ProviderConfig:
    name: str = "gemini"
    model: str = "gemini-3-flash-preview"
    api_key: str = "env:GEMINI_API_KEY"
    thinking: str = "low"
    max_output_tokens: int = 512
    endpoint: str | None = None        # local/ollama


@dataclass
class ClassifierConfig:
    enabled: bool = False
    name: str = "gemini"
    model: str = "gemini-3.1-flash-lite"
    api_key: str = "env:GEMINI_API_KEY"
    endpoint: str | None = None


@dataclass
class HumanizationConfig:
    enabled: bool = True
    timing: str = "lognormal"
    base_delay_ms: float = 800.0
    tap_jitter: bool = True
    tap_duration_ms: list = field(default_factory=lambda: [60, 150])
    swipe_curve: str = "bezier"
    imperfection_rate: float = 0.05
    session_window_min: int = 120


@dataclass
class RunConfig:
    confirm_before_execute: bool = True
    max_steps: int = 120
    stop_on_unknown_after: int = 3
    settle_timeout_ms: int = 4000
    post_tap_wait_ms: int = 700
    verify_screen_change: bool = True
    log_dir: str = "./runs"
    dry_run: bool = False


@dataclass
class CacheConfig:
    enabled: bool = True


@dataclass
class Config:
    device: DeviceConfig = field(default_factory=DeviceConfig)
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    humanization: HumanizationConfig = field(default_factory=HumanizationConfig)
    run: RunConfig = field(default_factory=RunConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        data = {}
        if path:
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        cfg = cls(
            device=_build(DeviceConfig, data.get("device")),
            provider=_build(ProviderConfig, data.get("provider")),
            classifier=_build(ClassifierConfig, data.get("classifier")),
            humanization=_build(HumanizationConfig, data.get("humanization")),
            run=_build(RunConfig, data.get("run")),
            cache=_build(CacheConfig, data.get("cache")),
        )
        cfg.validate()
        return cfg

    def validate(self) -> "Config":
        _check(self.device.backend, {"adb", "shizuku", "root"}, "device.backend")
        _check(self.provider.name, {"gemini", "anthropic", "openai", "ollama"}, "provider.name")
        _check(self.provider.thinking, {"off", "low", "high"}, "provider.thinking")
        _check(self.humanization.timing, {"lognormal", "gamma", "fixed"}, "humanization.timing")
        _check(self.humanization.swipe_curve, {"bezier", "linear"}, "humanization.swipe_curve")
        if not 0 < self.device.screenshot_scale <= 1:
            raise ValueError("device.screenshot_scale must be in (0, 1]")
        if self.run.max_steps <= 0:
            raise ValueError("run.max_steps must be positive")
        return self


def _build(klass, data):
    if not data:
        return klass()
    known = {f.name for f in fields(klass)}
    unknown = set(data) - known
    if unknown:
        raise ValueError(f"unknown {klass.__name__} key(s): {sorted(unknown)}")
    return klass(**{k: v for k, v in data.items() if k in known})


def _check(value, allowed, name):
    if value not in allowed:
        raise ValueError(f"{name} must be one of {sorted(allowed)}, got {value!r}")
