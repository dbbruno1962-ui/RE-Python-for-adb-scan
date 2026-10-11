import shutil
import subprocess
import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
ADB_FALLBACK_PATH = Path(r"E:\platform-tools\adb.exe")
ADB_WSL_FALLBACK_PATH = Path("/mnt/e/platform-tools/adb.exe")


def resolve_adb_path():
    candidates = []
    configured = os.environ.get("ADB_PATH")
    if configured:
        candidates.append(Path(configured))
    candidates.extend([
        PROJECT_DIR / "adb.exe",
        ADB_WSL_FALLBACK_PATH,
        ADB_FALLBACK_PATH,
        shutil.which("adb"),
        shutil.which("adb.exe"),
    ])
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def adb_command(cmd, timeout=20):
    adb_path = resolve_adb_path()
    if not adb_path:
        return False, "", "ADB non trovato. Metti adb.exe accanto allo script o nel PATH."

    try:
        result = subprocess.run(
            [adb_path] + cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "ADB timeout"
    except Exception as e:
        return False, "", str(e)


def get_connected_devices():
    ok, output, error = adb_command(["devices"], timeout=10)
    if not ok:
        return [], error or output or "Errore durante adb devices"

    devices = []
    problems = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        serial, state = parts[0], parts[1]
        if state == "device":
            devices.append(serial)
        else:
            problems.append(f"{serial}: {state}")

    if devices:
        return devices, ""
    if problems:
        return [], "Device non pronto: " + ", ".join(problems)
    return [], "Nessun device/emulatore rilevato"


def adb_restart():
    adb_path = resolve_adb_path()
    if not adb_path:
        return False, "ADB non trovato"

    try:
        subprocess.run([adb_path, "kill-server"], capture_output=True, text=True)
        subprocess.run([adb_path, "start-server"], capture_output=True, text=True)
        return True, "ADB riavviato"
    except Exception as e:
        return False, f"Errore nel riavvio di ADB: {e}"
