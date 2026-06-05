"""The device backend interface: capture the screen and inject input on one device."""

from __future__ import annotations

from abc import ABC, abstractmethod


class DeviceBackend(ABC):
    name = "base"

    @abstractmethod
    def screencap(self) -> bytes:
        """Return the current screen as PNG bytes."""

    @abstractmethod
    def resolution(self) -> tuple[int, int]:
        """Return the real screen resolution as (width, height) in pixels."""

    @abstractmethod
    def tap(self, px: int, py: int, duration_ms: float = 80) -> None:
        ...

    @abstractmethod
    def swipe(self, px1: int, py1: int, px2: int, py2: int, duration_ms: float = 200) -> None:
        ...

    @abstractmethod
    def type_text(self, text: str) -> None:
        ...

    @abstractmethod
    def back(self) -> None:
        ...

    def available(self) -> tuple[bool, str]:
        """Cheap reachability probe for ``cadence doctor``: (reachable, detail)."""
        return True, ""
