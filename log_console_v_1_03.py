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

# adb.exe must stay in the SAME folder.

import os
import re
import sys
import time
import subprocess
from datetime import datetime

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QListWidget,
    QMessageBox,
    QListWidgetItem,
    QLineEdit,
    QCheckBox,
    QFrame,
)

FILTER_FILE = "filters.txt"
LOG_DIR = "logs"

DEFAULT_FILTERS = [
    "Vlion", "mentamob", "advlion", "Vungle", "Pangle",
    "firebase", "analytics", "NebulaLog", "getaddrinfo", "gai_error"
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

def adb_command(cmd):
    try:
        full = ["./adb.exe"] + cmd
        result = subprocess.check_output(
            full,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        return result.strip()
    except Exception:
        return ""

class LogcatThread(QThread):
    new_line = Signal(str, str)
    status = Signal(str)
    pattern_found = Signal(str)
    stats_update = Signal(dict)

    def __init__(self, package_name, raw_path, clean_path):
        super().__init__()
        self.package_name = package_name
        self.raw_path = raw_path
        self.clean_path = clean_path
        self.running = True
        self.process = None
        self.filters = load_filters()
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
            self.process.kill()

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
        result = adb_command([
            "shell",
            "pidof",
            self.package_name
        ])
        return result

    def run(self):
        pid = self.get_pid()
        if not pid:
            self.status.emit("PID not found")
            return

        self.status.emit(f"PID: {pid}")

        raw_log = open(self.raw_path, "w", encoding="utf-8")
        clean_log = open(self.clean_path, "w", encoding="utf-8")

        cmd = [
            "./adb.exe",
            "logcat",
            f"--pid={pid}"
        ]

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

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
                self.stats_update.emit(self.stats)
                continue
            clean_log.write(final + "\n")
            clean_log.flush()
            self.new_line.emit(final, proto)
            self.stats_update.emit(self.stats)

        raw_log.close()
        clean_log.close()
        self.status.emit("Stopped")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.packages = {}
        self.setWindowTitle("Yi Reverse Console v1.03")
        self.resize(1700, 950)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        # TOP BAR
        top = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search package...")
        self.scan_btn = QPushButton("SCAN APPS")
        self.start_btn = QPushButton("START")
        self.stop_btn = QPushButton("STOP")
        self.reload_btn = QPushButton("RELOAD FILTERS")
        self.status_label = QLabel("Idle")
        top.addWidget(self.search_box)
        top.addWidget(self.scan_btn)
        top.addWidget(self.start_btn)
        top.addWidget(self.stop_btn)
        top.addWidget(self.reload_btn)
        top.addWidget(self.status_label)
        root.addLayout(top)

        # CENTER
        center = QHBoxLayout()
        # APP LIST
        self.app_list = QListWidget()
        self.app_list.setMinimumWidth(260)
        center.addWidget(self.app_list, 1)
        # LOG VIEW
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        center.addWidget(self.log_view, 5)
        # RIGHT PANEL
        right = QVBoxLayout()
        right.addWidget(QLabel("PATTERNS"))
        self.pattern_list = QListWidget()
        right.addWidget(self.pattern_list)
        right.addWidget(QLabel("ACTIVE FILTERS"))
        self.filter_list = QListWidget()
        right.addWidget(self.filter_list)

        # STATS
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

        # LOAD FILTERS
        self.populate_filter_panel()

        # SIGNALS
        self.scan_btn.clicked.connect(self.scan_apps)
        self.start_btn.clicked.connect(self.start_capture)
        self.stop_btn.clicked.connect(self.stop_capture)
        self.reload_btn.clicked.connect(self.reload_filters)
        self.pattern_list.itemDoubleClicked.connect(self.add_pattern_to_filters)
        self.search_box.textChanged.connect(self.filter_app_list)

    def populate_filter_panel(self):
        self.filter_list.clear()
        for item in load_filters():
            check = QListWidgetItem(item)
            check.setFlags(check.flags() | Qt.ItemIsUserCheckable)
            check.setCheckState(Qt.Checked)
            self.filter_list.addItem(check)

    def filter_app_list(self, text):
        text = text.lower()
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            item.setHidden(text not in item.text().lower())

    def scan_apps(self):
        self.app_list.clear()
        self.packages.clear()
        self.status_label.setText("Scanning user apps...")
        output = adb_command([
            "shell",
            "pm",
            "list",
            "packages",
            "-3"
        ])
        packages = []
        for line in output.splitlines():
            line = line.strip()
            if not line.startswith("package:"):
                continue
            package = line.replace("package:", "").strip()
            packages.append(package)
        packages.sort()
        for package in packages:
            pid = adb_command([
                "shell",
                "pidof",
                package
            ])
            if pid:
                display = f"🟢 {package}    [PID {pid}]"
            else:
                display = f"⚪ {package}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, package)
            if pid:
                item.setBackground(QColor(20, 90, 60))
            self.app_list.addItem(item)
        self.status_label.setText(f"User apps found: {len(packages)}")

    def start_capture(self):
        if self.thread:
            QMessageBox.warning(
                self,
                "Warning",
                "Already running"
            )
            return
        selected = self.app_list.currentItem()
        if not selected:
            QMessageBox.warning(
                self,
                "Warning",
                "Select app"
            )
            return
        package = selected.data(Qt.UserRole)
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        raw_log = os.path.join(LOG_DIR, f"{timestamp}_raw.log")
        clean_log = os.path.join(LOG_DIR, f"{timestamp}_clean.log")
        self.log_view.clear()
        self.thread = LogcatThread(package, raw_log, clean_log)
        self.thread.new_line.connect(self.append_log)
        self.thread.status.connect(self.update_status)
        self.thread.pattern_found.connect(self.add_pattern)
        self.thread.stats_update.connect(self.update_stats)
        self.thread.finished.connect(self.capture_finished)
        self.thread.start()

    def stop_capture(self):
        if self.thread:
            self.thread.stop()

    def capture_finished(self):
        self.thread = None

    def append_log(self, line, proto):
        # Nuova palette a contrasto alto
        color = "#AAAAAA"  # default: grigio chiaro

        if proto == "BLE":
            color = "#00BFFF"   # DeepSkyBlue
        elif proto == "PAIR":
            color = "#228B22"   # ForestGreen
        elif proto == "TLS":
            color = "#FF4500"   # OrangeRed
        elif proto == "UDP":
            color = "#6A5ACD"   # SlateBlue
        elif proto == "TUTK":
            color = "#FF1493"   # DeepPink
        elif proto == "UI":
            color = "#3333FF"   # strong blue

        self.log_view.append(
            f'<span style="color:{color}">{line}</span>'
        )
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
