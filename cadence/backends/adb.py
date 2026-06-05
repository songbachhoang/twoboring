"""ADB backend: drive the device by shelling out to `adb` (docs/INSTALL.md).

Screenshots come out via ``exec-out screencap -p``; input goes in via
``input tap/swipe/text/keyevent``. ``input tap`` has no press duration, so a
zero-distance ``input swipe`` is used to realize a humanized touch-down -> up time.
"""

from __future__ import annotations

import re
import shutil
import subprocess

from .base import DeviceBackend


class AdbError(RuntimeError):
    pass


class AdbBackend(DeviceBackend):
    name = "adb"

    def __init__(self, serial: str = "auto"):
        self.serial = None if serial in (None, "auto", "") else serial

    def _cmd(self, args):
        prefix = ["adb"]
        if self.serial:
            prefix += ["-s", self.serial]
        return prefix + args

    def _run(self, args, binary=False):
        try:
            res = subprocess.run(self._cmd(args), capture_output=True, check=True)
        except FileNotFoundError as exc:
            raise AdbError(
                "`adb` not found on PATH — install Android platform-tools (docs/INSTALL.md)"
            ) from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.decode(errors="replace").strip()
            raise AdbError(f"adb {' '.join(args)} failed: {detail}") from exc
        return res.stdout if binary else res.stdout.decode(errors="replace")

    def screencap(self) -> bytes:
        return self._run(["exec-out", "screencap", "-p"], binary=True)

    def resolution(self) -> tuple[int, int]:
        out = self._run(["shell", "wm", "size"])
        # Prefer an Override size if present, else the Physical size.
        m = re.search(r"Override size:\s*(\d+)x(\d+)", out) or \
            re.search(r"Physical size:\s*(\d+)x(\d+)", out)
        if not m:
            raise AdbError(f"could not parse resolution from {out!r}")
        return int(m.group(1)), int(m.group(2))

    def tap(self, px, py, duration_ms=80):
        # Zero-distance swipe => a press with a controllable hold duration.
        self._run(["shell", "input", "swipe",
                   str(px), str(py), str(px), str(py), str(int(duration_ms))])

    def swipe(self, px1, py1, px2, py2, duration_ms=200):
        self._run(["shell", "input", "swipe",
                   str(px1), str(py1), str(px2), str(py2), str(int(duration_ms))])

    def type_text(self, text):
        self._run(["shell", "input", "text", _escape(text)])

    def back(self):
        self._run(["shell", "input", "keyevent", "KEYCODE_BACK"])

    def available(self) -> tuple[bool, str]:
        if shutil.which("adb") is None:
            return False, "`adb` not on PATH"
        out = self._run(["devices"])
        devices = [ln for ln in out.splitlines()[1:] if "\tdevice" in ln]
        if not devices:
            return False, "no authorized device in `adb devices`"
        return True, devices[0].split("\t")[0]


def _escape(text: str) -> str:
    # `adb shell input text` uses %s for spaces; this is a minimal escaper.
    # Rich unicode / IME input is a known v0.1 limitation (see ROADMAP.md).
    return text.replace(" ", "%s").replace("'", "")
