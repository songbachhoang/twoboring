"""Device backends — the 'hands'. v0.1 ships ADB; shizuku/root are on the roadmap."""

from __future__ import annotations

from .base import DeviceBackend


def build_backend(device_cfg) -> DeviceBackend:
    if device_cfg.backend == "adb":
        from .adb import AdbBackend
        return AdbBackend(serial=device_cfg.serial)
    raise NotImplementedError(
        f"backend {device_cfg.backend!r} is on the roadmap but not in v0.1 — "
        "use 'adb' (docs/INSTALL.md)"
    )
