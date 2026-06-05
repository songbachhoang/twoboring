"""`cadence doctor` — validate the full pipeline before a real run (docs/INSTALL.md).

Checks (read-only; never injects): config parses, adb present, device reachable,
resolution detected, screencap works, provider key present. Fix anything it flags
before running a routine.
"""

from __future__ import annotations

import shutil

from .config import resolve_env


def run_doctor(config) -> int:
    checks = []

    def add(ok, label, detail=""):
        checks.append((bool(ok), label, detail))

    add(True, "config parses")

    has_adb = shutil.which("adb") is not None
    add(has_adb, "adb on PATH", "" if has_adb else "install Android platform-tools")

    from .backends import build_backend
    try:
        backend = build_backend(config.device)
        ok, detail = backend.available()
        add(ok, "device reachable", detail)
        if ok:
            try:
                w, h = backend.resolution()
                add(True, "resolution detected", f"{w}x{h}")
            except Exception as exc:
                add(False, "resolution detected", str(exc))
            try:
                png = backend.screencap()
                add(png[:4] == b"\x89PNG", "screencap works", f"{len(png)} bytes")
            except Exception as exc:
                add(False, "screencap works", str(exc))
    except Exception as exc:
        add(False, "device backend", str(exc))

    key = resolve_env(config.provider.api_key)
    add(bool(key), f"provider key ({config.provider.name})",
        "present" if key else f"missing: {config.provider.api_key}")

    print("cadence doctor\n")
    all_ok = True
    for ok, label, detail in checks:
        mark = "OK " if ok else "FAIL"
        line = f"  [{mark}] {label}"
        if detail:
            line += f"  — {detail}"
        print(line)
        all_ok = all_ok and ok
    print("\n" + ("All checks passed." if all_ok else "Some checks failed — fix the FAILs above."))
    return 0 if all_ok else 1
