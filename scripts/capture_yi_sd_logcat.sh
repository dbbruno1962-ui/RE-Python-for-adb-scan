#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE="${PACKAGE:-com.yunyi.smartcamera}"
CAMERA_IP="${CAMERA_IP:-192.168.1.55}"
SESSION="${SESSION:-$(date +%Y-%m-%d_%H-%M-%S)_yi55_sd_keysync}"
OUT_DIR="${OUT_DIR:-$ROOT/logs/sd_baseline/$SESSION}"
CLEAR_LOGCAT="${CLEAR_LOGCAT:-1}"

resolve_adb() {
    if [ -n "${ADB_PATH:-}" ] && [ -e "$ADB_PATH" ]; then
        printf '%s\n' "$ADB_PATH"
        return 0
    fi
    if [ -e /mnt/e/platform-tools/adb.exe ]; then
        printf '%s\n' /mnt/e/platform-tools/adb.exe
        return 0
    fi
    if command -v adb >/dev/null 2>&1; then
        command -v adb
        return 0
    fi
    if command -v adb.exe >/dev/null 2>&1; then
        command -v adb.exe
        return 0
    fi
    return 1
}

ADB="$(resolve_adb)" || {
    echo "ADB not found. Set ADB_PATH or install platform-tools." >&2
    exit 1
}

mkdir -p "$OUT_DIR"
RAW_LOG="$OUT_DIR/logcat_raw.log"
FOCUS_LOG="$OUT_DIR/logcat_focus.log"
EVENTS_LOG="$OUT_DIR/events.txt"
WIFI_LOG="$OUT_DIR/wifi_snapshots.log"
CAMERA_LOG="$OUT_DIR/camera_probe.log"
META="$OUT_DIR/README_CAPTURE.txt"

FOCUS_RE='CODXMARK|TNPXGBC|AntsLog|P2PPlayer|receive avframe|mCurrentAntsCameraState|IPCAM|IOTYPE|TNP|PPPP|p2p|P2P|TUTK|avframe|video|audio|stream|resolution|quality|HD|FHD|relay|cloud|yunyi|Yi|camera|Camera|error|fail|timeout|offline|online|connect|disconnect|rate'

cat > "$META" <<EOF_META
Yi .55 SD keysync logcat capture

Session:
  $SESSION

Package:
  $PACKAGE

Camera:
  $CAMERA_IP

Outputs:
  raw logcat:      $RAW_LOG
  focused logcat:  $FOCUS_LOG
  event markers:   $EVENTS_LOG
  wifi snapshots:  $WIFI_LOG
  camera probes:   $CAMERA_LOG

Intended manual sequence:
  1. Start this script before opening Yi IoT.
  2. MARK BOOT_SD_ONLINE when camera is online with SD baseline.
  3. MARK APP_OPEN immediately before opening Yi IoT.
  4. MARK LIVE_OPEN immediately before entering live.
  5. MARK VLC_OPEN when opening VLC RTSP.
  6. MARK QUALITY_HD, QUALITY_FHD, QUALITY_AUTO on quality changes.
  7. MARK LIVE_CLOSE before closing live.
  8. MARK APP_CLOSE before killing/closing app.
  9. MARK VLC_CLOSE before stopping VLC.
  10. Stop capture after 20-30 seconds of idle.

Interactive commands while running:
  mark TEXT     add marker to logcat and events.txt
  wifi          take Android Wi-Fi snapshot
  cam           take camera FTP/telnet reachability probe
  pid           record current app pid
  quit          stop capture

EOF_META

echo "ADB=$ADB" | tee -a "$EVENTS_LOG"
"$ADB" start-server >/dev/null
"$ADB" wait-for-device
"$ADB" devices | tee -a "$EVENTS_LOG"

if [ "$CLEAR_LOGCAT" = "1" ]; then
    "$ADB" logcat -c || true
    echo "$(date +%F' '%T.%3N) CLEAR_LOGCAT=1" | tee -a "$EVENTS_LOG"
fi

mark() {
    local msg="$*"
    local ts
    ts="$(date +%F' '%T.%3N)"
    echo "$ts MARK $msg" | tee -a "$EVENTS_LOG"
    "$ADB" shell log -p i -t CODXMARK "$msg" >/dev/null 2>&1 || true
}

wifi_snapshot() {
    local ts
    ts="$(date +%F' '%T.%3N)"
    {
        echo "===== WIFI $ts ====="
        "$ADB" shell sh -c "ip -o addr show wlan0 2>/dev/null; ip route 2>/dev/null; dumpsys wifi 2>/dev/null | grep -E 'SSID|BSSID|RSSI|mWifiState|NetworkInfo|frequency|CMD_ONESHOT_RSSI_POLL' | grep -v 'rec\\[' | tail -40" || true
    } >> "$WIFI_LOG"
    echo "$ts WIFI_SNAPSHOT" | tee -a "$EVENTS_LOG"
}

camera_probe() {
    local ts
    ts="$(date +%F' '%T.%3N)"
    {
        echo "===== CAMERA $ts ====="
        (timeout 2 bash -lc "</dev/tcp/$CAMERA_IP/21" && echo "ftp=open") || echo "ftp=closed"
        (timeout 2 bash -lc "</dev/tcp/$CAMERA_IP/23" && echo "telnet=open") || echo "telnet=closed"
        (timeout 2 bash -lc "</dev/tcp/$CAMERA_IP/8554" && echo "rtsp=open") || echo "rtsp=closed"
    } >> "$CAMERA_LOG"
    echo "$ts CAMERA_PROBE" | tee -a "$EVENTS_LOG"
}

pid_snapshot() {
    local ts pid
    ts="$(date +%F' '%T.%3N)"
    pid="$("$ADB" shell pidof "$PACKAGE" 2>/dev/null | tr -d '\r' || true)"
    echo "$ts PID ${pid:-none}" | tee -a "$EVENTS_LOG"
}

cleanup() {
    set +e
    mark CAPTURE_STOP
    if [ -n "${LOGCAT_PID:-}" ]; then
        kill "$LOGCAT_PID" >/dev/null 2>&1
        wait "$LOGCAT_PID" >/dev/null 2>&1
    fi
    sync
    echo "Capture saved in $OUT_DIR"
}
trap cleanup EXIT INT TERM

mark CAPTURE_START
wifi_snapshot
camera_probe

(
    "$ADB" logcat -v threadtime 2>&1 |
        tee "$RAW_LOG" |
        grep --line-buffered -E -i "$FOCUS_RE" > "$FOCUS_LOG"
) &
LOGCAT_PID=$!

echo "Capture running."
echo "Output: $OUT_DIR"
echo "Commands: mark TEXT | wifi | cam | pid | quit"

while IFS= read -r line; do
    case "$line" in
        quit|q|exit)
            break
            ;;
        wifi)
            wifi_snapshot
            ;;
        cam)
            camera_probe
            ;;
        pid)
            pid_snapshot
            ;;
        mark\ *)
            mark "${line#mark }"
            ;;
        "")
            ;;
        *)
            echo "Unknown command. Use: mark TEXT | wifi | cam | pid | quit"
            ;;
    esac
done
