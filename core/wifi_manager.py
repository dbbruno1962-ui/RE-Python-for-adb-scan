from datetime import datetime
from threading import Lock

from PySide6.QtCore import QThread, Signal

from core.adb_manager import adb_command, resolve_adb_path


class WifiLoggerThread(QThread):
    """Collect a small, timestamped Wi-Fi snapshot through ADB."""

    new_line = Signal(str, str)
    status = Signal(str)

    def __init__(self, raw_path, clean_path, interval=2.0):
        super().__init__()
        self.raw_path = raw_path
        self.clean_path = clean_path
        self.interval = interval
        self.running = True
        self.marker_lock = Lock()
        self.pending_marker = None

    def stop(self):
        self.running = False

    def mark_app_start(self, message):
        with self.marker_lock:
            self.pending_marker = message

    def snapshot(self):
        script = (
            "printf '__ADDR__\\n'; ip -o addr show wlan0 2>/dev/null; "
            "printf '__ROUTE__\\n'; ip route 2>/dev/null; "
            "printf '__WIFI__\\n'; "
            "dumpsys wifi 2>/dev/null | "
            "grep -E 'SSID|BSSID|RSSI|mWifiState|NetworkInfo|frequency|CMD_ONESHOT_RSSI_POLL' | "
            "grep -v 'rec\\[' | tail -20"
        )
        ok, output, error = adb_command(["shell", "sh", "-c", script], timeout=10)
        if ok:
            return output
        return f"wifi command failed: {error or output}"

    def run(self):
        if not resolve_adb_path():
            self.status.emit("Wi-Fi logger: ADB not found")
            return

        try:
            with open(self.raw_path, "w", encoding="utf-8") as raw_log, open(
                self.clean_path, "w", encoding="utf-8"
            ) as clean_log:
                self.status.emit("Wi-Fi logger active")
                while self.running:
                    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    with self.marker_lock:
                        marker = self.pending_marker
                        self.pending_marker = None
                    if marker:
                        final = f"[{stamp}] [WIFI] [APP_START] {marker}"
                        raw_log.write(final + "\n")
                        clean_log.write(final + "\n")
                        self.new_line.emit(final, "WIFI")
                    output = self.snapshot()
                    for line in output.splitlines():
                        line = line.strip()
                        if not line or line.startswith("__"):
                            continue
                        final = f"[{stamp}] [WIFI] {line}"
                        raw_log.write(final + "\n")
                        clean_log.write(final + "\n")
                        self.new_line.emit(final, "WIFI")
                    raw_log.flush()
                    clean_log.flush()
                    self.msleep(int(self.interval * 1000))
        except Exception as exc:
            self.status.emit(f"Wi-Fi logger error: {exc}")
            return

        self.status.emit("Wi-Fi logger stopped")
