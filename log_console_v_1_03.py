# log_console_v1_03.py
# Yi Reverse Console v1.03

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

from core.adb_manager import adb_command, adb_restart, get_connected_devices, resolve_adb_path
from core.filter_manager import (
    append_filter,
    load_filter_candidates,
    load_filters,
    map_proto,
)
from core.runtime import RuntimeContext
from core.wifi_manager import WifiLoggerThread

RUNTIME = RuntimeContext.from_file(__file__)
BASE_DIR = str(RUNTIME.base_dir)
FILTER_FILE = str(RUNTIME.filter_file)
CANDIDATE_FILE = os.path.join(BASE_DIR, "filters_candidates.txt")
LOG_DIR = str(RUNTIME.log_dir)

SUSPECT_WORDS = [
    "ad", "analytics", "banner", "firebase", "menta", "vlion",
    "vungle", "campaign", "applovin",
]


class LogcatThread(QThread):
    new_line = Signal(str, str)
    status = Signal(str)
    pattern_found = Signal(str)
    catalog_pattern_found = Signal(str)
    stats_update = Signal(dict)
    app_started = Signal(str)

    def __init__(self, package_name, raw_path, clean_path, filters=None):
        super().__init__()
        self.package_name = package_name
        self.raw_path = raw_path
        self.clean_path = clean_path
        self.running = True
        self.process = None
        self.filters = filters if filters is not None else load_filters(FILTER_FILE)
        self.filter_candidates = load_filter_candidates(CANDIDATE_FILE)
        self.catalog_seen = set()
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
        return map_proto(line)

    def detect_patterns(self, line):
        lower = line.lower()
        for candidate in self.filter_candidates:
            candidate_lower = candidate.lower()
            if len(candidate_lower) <= 4:
                match = re.search(
                    rf"(?<![a-z0-9]){re.escape(candidate_lower)}(?![a-z0-9])",
                    lower,
                )
            else:
                match = candidate_lower in lower
            if match and candidate_lower not in self.catalog_seen:
                self.catalog_seen.add(candidate_lower)
                self.catalog_pattern_found.emit(candidate)

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
        self.app_started.emit(f"package={self.package_name} pid={pid}")

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
        self.wifi_thread = None
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
        running = self.thread is not None or self.wifi_thread is not None
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
        for item in load_filters(FILTER_FILE):
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
        wifi_raw_log = os.path.join(LOG_DIR, f"{timestamp}_wifi_raw.log")
        wifi_clean_log = os.path.join(LOG_DIR, f"{timestamp}_wifi_clean.log")

        self.log_view.clear()
        self.thread = LogcatThread(package, raw_log, clean_log, self.active_filters())
        self.thread.new_line.connect(self.append_log)
        self.thread.status.connect(self.update_status)
        self.thread.pattern_found.connect(self.add_pattern)
        self.thread.catalog_pattern_found.connect(self.add_catalog_pattern)
        self.thread.stats_update.connect(self.update_stats)
        self.thread.finished.connect(self.capture_finished)
        self.wifi_thread = WifiLoggerThread(wifi_raw_log, wifi_clean_log)
        self.wifi_thread.new_line.connect(self.append_log)
        self.wifi_thread.status.connect(self.update_status)
        self.wifi_thread.finished.connect(self.wifi_capture_finished)
        self.thread.app_started.connect(self.wifi_thread.mark_app_start)
        self.wifi_thread.start()
        self.thread.start()
        self.update_capture_buttons()

    def stop_capture(self):
        if self.thread:
            self.status_label.setText("Stopping...")
            self.thread.stop()
        if self.wifi_thread:
            self.wifi_thread.stop()

    def capture_finished(self):
        self.thread = None
        self.update_capture_buttons()

    def wifi_capture_finished(self):
        self.wifi_thread = None
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
        elif proto == "WIFI":
            color = "#008B8B"

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
            item = QListWidgetItem(pattern)
            item.setData(Qt.UserRole, pattern)
            self.pattern_list.addItem(item)

    def add_catalog_pattern(self, pattern):
        for i in range(self.pattern_list.count()):
            item = self.pattern_list.item(i)
            if item.data(Qt.UserRole) == pattern:
                return

        item = QListWidgetItem(f"[CATALOG] {pattern}")
        item.setData(Qt.UserRole, pattern)
        item.setForeground(QColor("#FFB000"))
        item.setToolTip("Candidato catalogato: doppio clic per aggiungerlo a filters.txt")
        self.pattern_list.addItem(item)

    def add_pattern_to_filters(self, item):
        pattern = item.data(Qt.UserRole) or item.text()
        append_filter(FILTER_FILE, pattern)
        if self.thread:
            self.thread.update_filters(self.active_filters())
        item.setText('[ADDED] ' + pattern)
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
