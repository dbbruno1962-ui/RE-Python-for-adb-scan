# log_console_v1_03.py
# Reverse Console v1.03

# New Features:
# - Runtime filter panel
# - Live filter enable/disable
# - Protocol tags
# - Highlight engine
# - Stats panel
# - Wireshark compatible timestamps
# - Event tagging
# - Search app filter
# - Better PID selection visibility
# - Cleaner RE workflow

# Requirements:
# pip install PySide6

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILTER_FILE = os.path.join(BASE_DIR, "filters.txt")
LOG_DIR = os.path.join(BASE_DIR, "logs")
ADB_FALLBACK_PATH = r"E:\platform-tools\adb.exe"

DEFAULT_FILTERS = [
    "Vlion", "mentamob", "advlion", "Vungle", "Pangle",
    "firebase", "analytics", "NebulaLog", "getaddrinfo", "gai_error",
]

SUSPECT_WORDS = [
    "ad", "analytics", "banner", "firebase", "menta", "vlion",
    "vungle", "campaign", "applovin",
]

PROTOCOL_PATTERNS = {
    "BLE": ["bluetooth", "blescan", "gatt", "btbind"],
    "PAIR": ["configwifi", "pair", "bind", "choicemodeactivity"],
    "TLS": ["443", "okhttp", "https", "tls"],
    "UDP": ["udp", "9377", "broadcast"],
    "TUTK": ["tutk", "iotc", "avapi"],
    "UI": ["activity", "fragment", "view", "layout"],
}

# ============================================
# SOURCE / WIFI RUNTIME CONTEXT
# Future multi-source RE architecture
# ============================================

class SourceType:
    ADB = "ADB"
    WIFI_CONNECTED = "WIFI_CONNECTED"
    WIFI_MONITOR = "WIFI_MONITOR"
    ETH = "ETH"


class WifiMode:
    DISABLED = 0
    CONNECTED = 1
    MONITOR = 2


class RuntimeContext:
    def __init__(self):

        # Current active source
        self.source_type = SourceType.ADB

        # WiFi runtime mode
        self.wifi_mode = WifiMode.DISABLED

        # Runtime flags
        self.capture_enabled = False
        self.has_ip = False
        self.monitor_capable = False

        # Runtime info
        self.interface_name = ""
        self.ssid = ""

        # Future timestamp sync support
        self.time_sync_enabled = False

        # Future Wireshark integration
        self.wireshark_active = False

    def set_wifi_connected(self, iface="", ssid=""):
        self.source_type = SourceType.WIFI_CONNECTED
        self.wifi_mode = WifiMode.CONNECTED
        self.capture_enabled = True
        self.has_ip = True
        self.interface_name = iface
        self.ssid = ssid

    def set_wifi_monitor(self, iface=""):
        self.source_type = SourceType.WIFI_MONITOR
        self.wifi_mode = WifiMode.MONITOR
        self.capture_enabled = True
        self.has_ip = False
        self.interface_name = iface

    def set_adb(self):
        self.source_type = SourceType.ADB

    def disable_wifi(self):
        self.wifi_mode = WifiMode.DISABLED
        self.capture_enabled = False
        self.has_ip = False
        self.interface_name = ""
        self.ssid = ""


# Global runtime context
RUNTIME_CONTEXT = RuntimeContext()

def ensure_filter_file():
    if not os.path.exists(FILTER_FILE):
        with open(FILTER_FILE, "w", encoding="utf-8") as f:
            for item in DEFAULT_FILTERS:
                f.write(item + "\n")


def load_filters():
    ensure_filter_file()
    result = []
    with open(FILTER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                result.append(line)
    return result


def append_filter(pattern):
    existing = load_filters()
    if pattern in existing:
        return
    with open(FILTER_FILE, "a", encoding="utf-8") as f:
        f.write(pattern + "\n")


def resolve_adb_path():
    candidates = [
        os.path.join(BASE_DIR, "adb.exe"),
        ADB_FALLBACK_PATH,
        shutil.which("adb"),
        shutil.which("adb.exe"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
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


class LogcatThread(QThread):
    new_line = Signal(str, str)
    status = Signal(str)
    pattern_found = Signal(str)
    stats_update = Signal(dict)

    def __init__(self, package_name, raw_path, clean_path, filters=None):
        super().__init__()
        self.package_name = package_name
        self.raw_path = raw_path
        self.clean_path = clean_path
        self.running = True
        self.process = None
        self.filters = filters if filters is not None else load_filters()
        self.pattern_counter = {}
        self.stats = {
            "lines": 0,
            "filtered": 0,
            "ble": 0,
            "pair": 0,
            "tls": 0,
            "udp": 0,
            "tutk": 0,
        }

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def update_filters(self, filters):
        self.filters = filters

    def should_filter(self, line):
        lower = line.lower()
        for item in self.filters:
            if item.lower() in lower:
                return True
        return False

    def detect_protocol(self, line):
        lower = line.lower()
        for proto, patterns in PROTOCOL_PATTERNS.items():
            for item in patterns:
                if item in lower:
                    return proto
        return "GEN"

    def detect_patterns(self, line):
        lower = line.lower()
        words = re.findall(r"[a-zA-Z0-9\.\-_]+", lower)
        for word in words:
            if len(word) < 6:
                continue
            for suspect in SUSPECT_WORDS:
                if suspect in word:
                    self.pattern_counter[word] = (
                        self.pattern_counter.get(word, 0) + 1
                    )
                    if self.pattern_counter[word] == 5:
                        self.pattern_found.emit(word)

    def get_pid(self):
        ok, output, error = adb_command([
            "shell",
            "pidof",
            self.package_name,
        ])
        if ok:
            return output
        return ""

    def run(self):
        adb_path = resolve_adb_path()
        if not adb_path:
            self.status.emit("ADB not found")
            return

        pid = self.get_pid()
        if not pid:
            self.status.emit("PID not found")
            return

        self.status.emit(f"PID: {pid}")

        cmd = [
            adb_path,
            "logcat",
            f"--pid={pid}",
        ]

        try:
            with open(self.raw_path, "w", encoding="utf-8") as raw_log, open(
                self.clean_path, "w", encoding="utf-8"
            ) as clean_log:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                )

                if not self.process.stdout:
                    self.status.emit("Logcat output not available")
                    return

                while self.running:
                    line = self.process.stdout.readline()
                    if not line:
                        break

                    line = line.rstrip()
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    proto = self.detect_protocol(line)
                    final = f"[{ts}] [{proto}] {line}"

                    self.stats["lines"] += 1
                    if proto == "BLE":
                        self.stats["ble"] += 1
                    elif proto == "PAIR":
                        self.stats["pair"] += 1
                    elif proto == "TLS":
                        self.stats["tls"] += 1
                    elif proto == "UDP":
                        self.stats["udp"] += 1
                    elif proto == "TUTK":
                        self.stats["tutk"] += 1

                    raw_log.write(final + "\n")
                    raw_log.flush()
                    self.detect_patterns(line)

                    if self.should_filter(line):
                        self.stats["filtered"] += 1
                        self.stats_update.emit(dict(self.stats))
                        continue

                    clean_log.write(final + "\n")
                    clean_log.flush()
                    self.new_line.emit(final, proto)
                    self.stats_update.emit(dict(self.stats))
        except Exception as e:
            self.status.emit(f"Logcat error: {e}")
            return

        self.status.emit("Stopped")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.packages = {}
        self.setWindowTitle("Yi Reverse Console v1.03")
        self.resize(1700, 950)
        self.init_ui()
        self.update_capture_buttons()

    def init_ui(self):
        root = QVBoxLayout()

        top = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search package...")
        self.scan_btn = QPushButton("SCAN APPS")
        self.start_btn = QPushButton("START")
        self.stop_btn = QPushButton("STOP")
        self.reload_btn = QPushButton("RELOAD FILTERS")
        self.restart_adb_btn = QPushButton("RESTART ADB")
        self.status_label = QLabel("Idle")

        top.addWidget(self.search_box)
        top.addWidget(self.scan_btn)
        top.addWidget(self.start_btn)
        top.addWidget(self.stop_btn)
        top.addWidget(self.reload_btn)
        top.addWidget(self.restart_adb_btn)
        top.addWidget(self.status_label)
        root.addLayout(top)

        center = QHBoxLayout()
        self.app_list = QListWidget()
        self.app_list.setMinimumWidth(260)
        center.addWidget(self.app_list, 1)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        center.addWidget(self.log_view, 5)

        right = QVBoxLayout()
        right.addWidget(QLabel("PATTERNS"))
        self.pattern_list = QListWidget()
        right.addWidget(self.pattern_list)
        right.addWidget(QLabel("ACTIVE FILTERS"))
        self.filter_list = QListWidget()
        right.addWidget(self.filter_list)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        right.addWidget(line)

        self.stats_label = QLabel(
            "LINES: 0\n"
            "FILTERED: 0\n"
            "BLE: 0\n"
            "PAIR: 0\n"
            "TLS: 0\n"
            "UDP: 0\n"
            "TUTK: 0"
        )
        right.addWidget(self.stats_label)
        center.addLayout(right, 1)
        root.addLayout(center)
        self.setLayout(root)

        self.populate_filter_panel()

        self.scan_btn.clicked.connect(self.scan_apps)
        self.start_btn.clicked.connect(self.start_capture)
        self.stop_btn.clicked.connect(self.stop_capture)
        self.reload_btn.clicked.connect(self.reload_filters)
        self.pattern_list.itemDoubleClicked.connect(self.add_pattern_to_filters)
        self.search_box.textChanged.connect(self.filter_app_list)
        self.filter_list.itemChanged.connect(self.apply_runtime_filters)
        self.restart_adb_btn.clicked.connect(self.handle_restart_adb)

    def update_capture_buttons(self):
        running = self.thread is not None
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)

    def handle_restart_adb(self):
        self.status_label.setText("Riavvio ADB in corso...")
        ok, message = adb_restart()
        self.status_label.setText(message)
        if not ok:
            QMessageBox.warning(self, "ADB", message)

    def populate_filter_panel(self):
        self.filter_list.blockSignals(True)
        self.filter_list.clear()
        for item in load_filters():
            check = QListWidgetItem(item)
            check.setFlags(check.flags() | Qt.ItemIsUserCheckable)
            check.setCheckState(Qt.Checked)
            self.filter_list.addItem(check)
        self.filter_list.blockSignals(False)
        self.apply_runtime_filters()

    def active_filters(self):
        filters = []
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            if item.checkState() == Qt.Checked:
                filters.append(item.text())
        return filters

    def apply_runtime_filters(self):
        if self.thread:
            self.thread.update_filters(self.active_filters())

    def filter_app_list(self, text):
        text = text.lower()
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            item.setHidden(text not in item.text().lower())

    def scan_apps(self):
        self.app_list.clear()
        self.packages.clear()
        self.status_label.setText("Scanning user apps...")

        devices, device_error = get_connected_devices()
        if not devices:
            self.status_label.setText(device_error)
            QMessageBox.warning(self, "ADB", device_error)
            return

        ok, output, error = adb_command([
            "shell",
            "pm",
            "list",
            "packages",
            "-3",
        ])
        if not ok:
            message = error or output or "Impossibile leggere le app utente"
            self.status_label.setText(message)
            QMessageBox.warning(self, "ADB", message)
            return

        packages = []
        for line in output.splitlines():
            line = line.strip()
            if not line.startswith("package:"):
                continue
            package = line.replace("package:", "").strip()
            packages.append(package)

        packages.sort()
        for package in packages:
            ok, pid, _ = adb_command([
                "shell",
                "pidof",
                package,
            ])
            if ok and pid:
                display = f"[RUN] {package}    [PID {pid}]"
            else:
                display = f"[OFF] {package}"

            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, package)
            if ok and pid:
                item.setBackground(QColor(20, 90, 60))
            self.app_list.addItem(item)

        self.status_label.setText(f"User apps found: {len(packages)} | Device: {devices[0]}")

    def start_capture(self):
        if self.thread:
            QMessageBox.warning(self, "Warning", "Already running")
            return

        selected = self.app_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Select app")
            return

        package = selected.data(Qt.UserRole)
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        raw_log = os.path.join(LOG_DIR, f"{timestamp}_raw.log")
        clean_log = os.path.join(LOG_DIR, f"{timestamp}_clean.log")

        self.log_view.clear()
        self.thread = LogcatThread(package, raw_log, clean_log, self.active_filters())
        self.thread.new_line.connect(self.append_log)
        self.thread.status.connect(self.update_status)
        self.thread.pattern_found.connect(self.add_pattern)
        self.thread.stats_update.connect(self.update_stats)
        self.thread.finished.connect(self.capture_finished)
        self.thread.start()
        self.update_capture_buttons()

    def stop_capture(self):
        if self.thread:
            self.status_label.setText("Stopping...")
            self.thread.stop()

    def capture_finished(self):
        self.thread = None
        self.update_capture_buttons()

    def append_log(self, line, proto):
        color = "#AAAAAA"
        if proto == "BLE":
            color = "#00BFFF"
        elif proto == "PAIR":
            color = "#228B22"
        elif proto == "TLS":
            color = "#FF4500"
        elif proto == "UDP":
            color = "#6A5ACD"
        elif proto == "TUTK":
            color = "#FF1493"
        elif proto == "UI":
            color = "#3333FF"

        self.log_view.append(f'<span style="color:{color}">{line}</span>')
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_view.setTextCursor(cursor)

    def update_status(self, text):
        self.status_label.setText(text)

    def update_stats(self, stats):
        self.stats_label.setText(
            f"LINES: {stats['lines']}\n"
            f"FILTERED: {stats['filtered']}\n"
            f"BLE: {stats['ble']}\n"
            f"PAIR: {stats['pair']}\n"
            f"TLS: {stats['tls']}\n"
            f"UDP: {stats['udp']}\n"
            f"TUTK: {stats['tutk']}"
        )

    def add_pattern(self, pattern):
        items = [
            self.pattern_list.item(i).text()
            for i in range(self.pattern_list.count())
        ]
        if pattern not in items:
            self.pattern_list.addItem(pattern)

    def add_pattern_to_filters(self, item):
        pattern = item.text()
        append_filter(pattern)
        self.populate_filter_panel()
        self.status_label.setText(f"Filter added: {pattern}")

    def reload_filters(self):
        self.populate_filter_panel()
        self.status_label.setText("Filters reloaded")

    def closeEvent(self, event):
        if self.thread:
            self.thread.stop()
            self.thread.wait(3000)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())