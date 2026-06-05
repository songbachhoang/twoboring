# Installation & Device Setup (Android)

This is the part that determines whether Cadence is pleasant or painful to use, so it's written to be followed step by step. There are three ways to give Cadence "hands" on your device. Pick one based on how much friction you'll tolerate versus how robust and undetectable you need the input to be.

| Backend | Root needed? | Setup friction | Input quality | Detectability |
|---|---|---|---|---|
| **ADB** (USB or wireless) | No | Low | Good | Higher (ADB/debug state is visible) |
| **Shizuku** | No (one-time ADB activation) | Medium | Good, no on-device a11y service | Medium |
| **Root** (`/dev/input`) | Yes | High | Best (hardware-layer touches) | Lowest |

**Recommended starting point: ADB over USB.** Prove your routine works first, then move to Shizuku or root only if you need it. See [SAFETY.md](SAFETY.md) for why the backend choice affects detection.

---

## 0. Common prerequisites

On your **computer** (the orchestrator runs here):

- **Python 3.11–3.13** (3.14 is not yet supported by some dependencies).
- **Android Platform Tools** (provides `adb`):
  - macOS: `brew install android-platform-tools`
  - Linux: `sudo apt install adb` (or your distro equivalent)
  - Windows: download Platform Tools from Google and add to `PATH`.
- Verify: `adb version` prints a version.

Then install Cadence:

```bash
pipx install cadence-android      # recommended (isolated)
# or
pip install cadence-android
```

On your **phone**:

1. Enable **Developer Options**: Settings → About phone → tap *Build number* seven times.
2. Settings → System → Developer options → enable **USB debugging**.

---

## 1. Backend A — ADB over USB (start here)

1. Connect the phone to the computer with a cable.
2. On the phone, accept the **"Allow USB debugging?"** prompt (check *Always allow from this computer*).
3. Confirm the device is visible:

   ```bash
   adb devices
   # List of devices attached
   # 1A2B3C4D5E    device
   ```

4. Smoke-test capture and input manually:

   ```bash
   adb exec-out screencap -p > /tmp/screen.png   # should produce a real screenshot
   adb shell input tap 540 1200                  # should tap the middle-ish of the screen
   ```

If both work, you're done. Set `device.backend: adb` in your config.

### ADB over Wi-Fi (optional, no cable)

```bash
adb tcpip 5555
adb connect <phone-ip>:5555
```

Wireless is convenient for an unattended setup but adds latency per screenshot and is less stable. Use USB while developing a routine.

---

## 2. Backend B — Shizuku (no root, better than raw ADB)

Shizuku lets ordinary apps perform ADB-level operations after a **one-time activation**, without keeping a cable attached and without an on-device accessibility service that games can detect.

1. Install **Shizuku** on the phone (from its official source / Play Store).
2. Start the Shizuku service. On Android 11+ you can start it wirelessly via the phone's built-in wireless debugging; otherwise start it once from a computer:

   ```bash
   adb shell sh /storage/emulated/0/Android/data/moe.shizuku.privileged.api/start.sh
   ```

   (Shizuku's own in-app instructions are authoritative and version-specific — follow those.)
3. Grant Cadence's helper Shizuku permission when prompted.
4. Set `device.backend: shizuku` in your config.

> Note: Shizuku's activation does **not** survive a reboot on non-rooted devices — you re-run the activation step after each restart. On rooted devices it can auto-start.

---

## 3. Backend C — Root (`/dev/input`, best input fidelity)

Only if your device is rooted and you understand the tradeoffs. Root lets Cadence write raw kernel input events to the touchscreen device node, which are the closest thing to a real finger at the hardware level.

1. Grant Cadence root via your superuser manager (Magisk, etc.) when prompted.
2. Cadence auto-detects the touchscreen event device (e.g. `/dev/input/event3`); you can override it in config if detection is wrong.
3. Set `device.backend: root` in your config.

Root produces the most convincing input but is the most invasive setup and is overkill for most personal routines.

---

## 4. Verify the full pipeline

Once a backend is configured, run the built-in doctor:

```bash
cadence doctor
```

It checks: device reachable, screenshot works, input injection works, provider key present and valid, and config parses. Fix anything it flags before running a real routine.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `adb devices` shows `unauthorized` | USB-debug prompt not accepted | Re-plug, accept the prompt on the phone. |
| Screenshot is solid black | App blocks capture (secure flag) | Some apps/screens set `FLAG_SECURE`; capture won't work there. |
| Taps land in the wrong place | Coordinate rescale wrong | Confirm `device` resolution autodetect; see CONFIGURATION.md. |
| Works then drops mid-run (Wi-Fi) | Wireless ADB instability | Use USB, or increase reconnect retries in config. |
| Shizuku stopped after reboot | Expected on non-root | Re-run the activation step. |

Next: [CONFIGURATION.md](CONFIGURATION.md) to tune the run and your costs.
