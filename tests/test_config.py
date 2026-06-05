import pytest

from cadence.config import Config, resolve_env


def test_defaults():
    c = Config.load(None)
    assert c.device.backend == "adb"
    assert c.provider.name == "gemini"
    assert c.run.confirm_before_execute is True
    assert c.run.max_steps == 120


def test_example_config_parses():
    # The shipped example must always load (it is what users copy).
    c = Config.load("cadence.config.example.yaml")
    assert c.device.screenshot_scale == 0.5
    assert c.run.max_steps == 120
    assert c.humanization.timing == "lognormal"


def test_resolve_env(monkeypatch):
    monkeypatch.setenv("CADENCE_TEST_KEY", "secret")
    assert resolve_env("env:CADENCE_TEST_KEY") == "secret"
    assert resolve_env("literal") == "literal"
    assert resolve_env("env:CADENCE_DOES_NOT_EXIST") is None


def test_validation_rejects_bad_enum(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("provider:\n  thinking: ultra\n")
    with pytest.raises(ValueError):
        Config.load(str(p))


def test_unknown_key_rejected(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("device:\n  bogus: 1\n")
    with pytest.raises(ValueError):
        Config.load(str(p))
