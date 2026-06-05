"""Sensitive-action detection for the inline confirmation gate (docs/TASKS.md).

Sensitive actions pause for an extra confirmation even mid-run — payments,
deletions, posting/publishing, permission grants, account/security changes. The
provider can also raise ``needs_confirmation`` itself. There is no global
"auto-approve everything" switch by design.
"""

from __future__ import annotations

from .types import Decision

_SENSITIVE_WORDS = (
    "pay", "payment", "buy", "purchase", "order", "checkout",
    "delete", "remove", "erase",
    "post", "publish", "submit", "send",
    "permission", "allow", "grant",
    "password", "sign out", "log out", "logout", "account", "security",
)


def is_sensitive(decision: Decision) -> bool:
    """True if the decision should trigger an inline confirmation."""
    if decision.needs_confirmation:
        return True
    blob = f"{decision.rationale} {decision.text or ''}".lower()
    return any(word in blob for word in _SENSITIVE_WORDS)
