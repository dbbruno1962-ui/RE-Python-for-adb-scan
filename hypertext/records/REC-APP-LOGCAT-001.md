---
id: REC-APP-LOGCAT-001
type: capability
target: REConsole v1.03 (Python/PySide6); Android target via ADB
epistemic_state: derived
lifecycle_state: current
coverage: partial
---

# Pipeline ADB e acquisizione logcat per PID

## Scope

Descrive il flusso statico nell'albero corrente, non un run osservato né la
compatibilità con ogni versione Android/ADB.

## Affermazione

La GUI elenca pacchetti utente, mostra se `pidof` restituisce un PID e avvia
`adb logcat --pid=<pid>`. Per ogni riga aggiunge un timestamp locale e un tag
euristico. Scrive nel raw prima del filtro; le righe filtrate non sono scritte
nel clean né mostrate nella GUI. La scansione verifica almeno un device nello
stato ADB `device`, ma non seleziona poi un seriale; i README richiedono un
solo target pronto.

## Evidenza e provenienza

- `log_console_v_1_03.py`: `MainWindow.scan_apps`, `start_capture`,
  `LogcatThread.get_pid`, `LogcatThread.run`, `should_filter`.
- `core/adb_manager.py`: `resolve_adb_path`, `adb_command`,
  `get_connected_devices`, `adb_restart`.
- `core/runtime.py`: `RuntimeContext.from_file` localizza filtri e log.
- `README.md`, `README_EN.md`: requisiti, avvio, vincolo del singolo target e
  privacy dei log. Gli esempi raw/clean sono dichiarati sintetici.

Derivato da lettura statica; nessun device, processo ADB o GUI è stato avviato.

## Limiti e relazioni

- Il timestamp è locale, non prova sincronizzazione con Android.
- Compatibilità ADB, formati e codici di uscita non sono stati testati.
- Relazioni: [REC-APP-FILTERS-001](REC-APP-FILTERS-001.md),
  [REC-APP-WIFI-001](REC-APP-WIFI-001.md).
- Cronologia: `reports/status.md`, sessione 2026-11-22. Nessun log reale
  esaminato.
