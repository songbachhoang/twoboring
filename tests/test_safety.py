from cadence.safety import is_sensitive
from cadence.types import ActionType, Decision


def d(**kw):
    kw.setdefault("action", ActionType.TAP)
    return Decision(**kw)


def test_payment_rationale_is_sensitive():
    assert is_sensitive(d(rationale="tap the Pay button to complete checkout")) is True


def test_delete_rationale_is_sensitive():
    assert is_sensitive(d(rationale="confirm delete of the account")) is True


def test_benign_rationale_is_not_sensitive():
    assert is_sensitive(d(rationale="open the navigation menu")) is False


def test_provider_raised_flag_is_honored():
    assert is_sensitive(d(rationale="anything", needs_confirmation=True)) is True
