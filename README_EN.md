# RE Console v1.03

[Italiano](README.md) | [English](README_EN.md)

Graphical tool for Android log acquisition and correlation through ADB, with
runtime filtering, a pattern catalog, and synchronized Wi-Fi snapshots.

## Requirements

- Python 3
- PySide6
- ADB available through one of the following methods:
  - the `ADB_PATH` environment variable;
  - `/mnt/e/platform-tools/adb.exe` in WSL;
  - `adb` or `adb.exe` in `PATH`;
  - `adb.exe` in the project directory.

Install dependencies:

```sh
python3 -m pip install -r requirements.txt
```

## Running the application

After installing the global launcher:

```sh
re-console
```

Or run it from the project directory:

```sh
./re-console
```

Configuration and log paths are resolved relative to the project directory,
so the launcher can be run from any location.

## ADB over Wi-Fi (Android 8.1 / ADB TCP/IP)

This uses the legacy ADB TCP/IP protocol on port `5555`; it is not the
`adb pair` flow used by newer Android versions. The initial step still needs a
USB cable and an authorized debugging connection on the phone.

With the phone connected by USB:

```sh
adb devices
adb -s <USB_SERIAL> tcpip 5555
adb -s <USB_SERIAL> shell ip -f inet addr show wlan0
```

Note the IPv4 address assigned to `wlan0`, unplug the USB cable, then connect
from a computer on the same LAN:

```sh
adb connect <PHONE_IP>:5555
adb devices
```

The device must show the `device` state. RE Console can then be used normally:
scan the apps and start capture. For example, `light_meter` messages produced
by a lux-meter app continue through the existing logcat pipeline; no dedicated
source is needed.

The current console runs `adb` without `-s <serial>`. Before launching it,
leave only one ADB target in the `device` state: after switching to Wi-Fi,
unplug USB. To reconnect after a network interruption:

```sh
adb connect <PHONE_IP>:5555
```

To return to USB, reconnect the cable and run:

```sh
adb -s <USB_SERIAL> usb
adb disconnect <PHONE_IP>:5555
```

ADB over TCP/IP does not encrypt or re-authenticate every connection on port
`5555`; enable it only on a trusted LAN and disable it when it is no longer
needed.

## Repository layout

- `log_console_v_1_03.py`: main application.
- `core/`: ADB, Wi-Fi, filters, device registry, and runtime management.
- `filters.txt`: active exclusion filters.
- `filters_candidates.txt`: catalog of candidate patterns.
- `devices.json`: local device registry.
- `logs/`: local capture output, excluded from version control.
- `examples/`: synthetic, sanitized examples of log formats.
- `notes/`: roadmap and project notes.

## Log privacy

Real captures can contain device identifiers, network addresses, application
metadata, and other operational data. For that reason, `logs/` is not tracked
by Git. The files under `examples/` are synthetic and do not originate from a
real capture.

## Roadmap

The historical roadmap and its later addenda are kept under `notes/`. The goal
remains a general console able to correlate ADB, Wi-Fi, Ethernet, and later
BLE on a common timeline.

By Bruno
