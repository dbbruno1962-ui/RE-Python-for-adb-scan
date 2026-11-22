#!/usr/bin/env bash
set -e

PKG="com.vidure.app"
OUT_DIR="./vidure_re_output"

# Rileva automaticamente adb (Linux nativo o adb.exe di Windows da WSL)
if command -v adb >/dev/null 2>&1; then
    ADB="adb"
elif command -v adb.exe >/dev/null 2>&1; then
    ADB="adb.exe"
elif [ -f "/mnt/e/platform-tools/adb.exe" ]; then
    ADB="/mnt/e/platform-tools/adb.exe"
else
    echo "Errore: adb non trovato nel PATH."
    exit 1
fi

echo "[*] Uso ADB: $ADB"
$ADB devices

mkdir -p "$OUT_DIR/apks" "$OUT_DIR/unpacked"
echo "[*] Estrazione pacchetti APK per $PKG..."

# Gestisce sia APK singolo che Split APK (base.apk + split_config.*)
APK_PATHS=$($ADB shell pm path "$PKG" | tr -d '\r' | sed 's/^package://')
if [ -z "$APK_PATHS" ]; then
    echo "Errore: pacchetto $PKG non trovato sul telefono."
    exit 1
fi

for remote_path in $APK_PATHS; do
    fname=$(basename "$remote_path")
    echo "    -> Pull $fname"
    $ADB pull "$remote_path" "$OUT_DIR/apks/$fname" >/dev/null
    unzip -qo "$OUT_DIR/apks/$fname" -d "$OUT_DIR/unpacked"
done

echo "[*] Estrazione stringhe da classes*.dex, librerie .so e asset..."
ALL_STRINGS="$OUT_DIR/all_strings.txt"
find "$OUT_DIR/unpacked" \( -name "*.dex" -o -name "*.so" -o -name "*.xml" -o -name "*.json" \) -exec strings -n 4 {} + | sort -u > "$ALL_STRINGS"

echo "[*] Filtraggio 1: Endpoint HTTP (/app/...)"
grep -E "^/app/[a-zA-Z0-9_/-]+" "$ALL_STRINGS" | sort -u > "$OUT_DIR/1_http_endpoints.txt"

echo "[*] Filtraggio 2: Comandi Wi-Fi, Client/STA, SSID e Telnet/Debug"
grep -iE "wifi|ssid|sta_mode|ap_mode|telnet|ftpd|debug|factory|wpa_supplicant|hostapd|setwifi|getwifi" "$ALL_STRINGS" | grep -E "^[a-zA-Z0-9_./:?=&-]{4,120}$" | sort -u > "$OUT_DIR/2_wifi_debug_strings.txt"

echo "[*] Filtraggio 3: Possibili nomi di file su scheda SD (.sh, .bin, .cfg, .ini, update, test)"
grep -iE "\.(sh|bin|img|fw|cfg|ini|txt|tar|gz)$" "$ALL_STRINGS" | grep -E "^[a-zA-Z0-9_./-]{4,80}$" | sort -u > "$OUT_DIR/3_sd_filenames.txt"

echo ""
echo "=========================================================="
echo " ANALISI COMPLETATA! File salvati in: $OUT_DIR/"
echo "=========================================================="
echo "--- Endpoint HTTP trovati ($(wc -l < "$OUT_DIR/1_http_endpoints.txt")) ---"
cat "$OUT_DIR/1_http_endpoints.txt"
echo ""
echo "--- Possibili file SD / Update / Script ($(wc -l < "$OUT_DIR/3_sd_filenames.txt")) ---"
head -n 40 "$OUT_DIR/3_sd_filenames.txt"
