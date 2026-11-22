---
id: REC-APP-WIFI-001
type: capability
target: REConsole v1.03 e Android interrogato via ADB shell
epistemic_state: derived
lifecycle_state: current
coverage: partial
---

# Snapshot Wi-Fi associati alla sessione

## Scope

Descrive `core/wifi_manager.py` e l'avvio GUI, non prova disponibilità o
correttezza delle informazioni su uno specifico firmware.

## Affermazione

All'avvio cattura la GUI crea raw e clean Wi-Fi e avvia `WifiLoggerThread`
insieme al thread logcat. Ogni ciclo (default 2 secondi) interroga via ADB
indirizzi `wlan0`, route e un sottoinsieme di `dumpsys wifi`. L'uscita
selezionata è scritta sia nel raw sia nel clean; i marker interni sono
scartati. Quando logcat notifica l'avvio dell'app, il logger registra
`[APP_START]` al ciclo successivo. Il logger non seleziona un seriale.

## Evidenza e provenienza

- `core/wifi_manager.py`: `snapshot`, `mark_app_start`, `run`.
- `log_console_v_1_03.py`: `MainWindow.start_capture` crea i file e collega
  `LogcatThread.app_started` a `mark_app_start`.
- `examples/wifi_snapshot.sample.txt`: esempio sintetico e redatto.
- `notes/Roadmap_addendum_2026-07-12.rtf`: requisiti storici. Il codice usa
  grep/tail per selezionare righe; il clean non realizza qui una deduplicazione
  dimostrata.

## Limiti e relazioni

- Query e tag dipendono dai comandi disponibili sul firmware, non testati.
- I timestamp sono generati separatamente da thread distinti e non provano
  correlazione causale o sincronizzazione precisa.
- Errori ADB sono registrati come testo; interpretazione downstream non
  stabilita.
- Relazione: [REC-APP-LOGCAT-001](REC-APP-LOGCAT-001.md).
