# RE Console v1.03

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
