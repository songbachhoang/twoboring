from cadence.providers.gemini import parse_decision
from cadence.types import ActionType


def test_basic_tap():
    d = parse_decision('{"action":"TAP","x":500,"y":600,"rationale":"tap login"}')
    assert d.action is ActionType.TAP
    assert (d.x, d.y) == (500, 600)
    assert d.rationale == "tap login"


def test_coordinates_are_clamped_to_0_1000():
    d = parse_decision('{"action":"TAP","x":2000,"y":-5}')
    assert (d.x, d.y) == (1000, 0)


def test_null_coordinates_stay_none():
    d = parse_decision('{"action":"BACK","rationale":"go back"}')
    assert d.action is ActionType.BACK
    assert d.x is None and d.y is None


def test_json_embedded_in_prose_is_recovered():
    d = parse_decision('Sure! {"action":"DONE","rationale":"goal met"} hope that helps')
    assert d.action is ActionType.DONE


def test_unknown_action_falls_back():
    d = parse_decision('{"action":"WIGGLE","x":1,"y":1}')
    assert d.action is ActionType.UNKNOWN


def test_invalid_json_is_unknown():
    d = parse_decision("not json at all")
    assert d.action is ActionType.UNKNOWN
    assert d.rationale


def test_needs_confirmation_flag():
    d = parse_decision('{"action":"TAP","x":1,"y":1,"needs_confirmation":true}')
    assert d.needs_confirmation is True
