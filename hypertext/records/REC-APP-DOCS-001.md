---
id: REC-APP-DOCS-001
type: decision
target: REConsole project documentation and roadmap
epistemic_state: derived
lifecycle_state: historical
coverage: partial
---

# Documentazione di prodotto, campioni e roadmap

## Scope

Separa requisiti/intenzioni dal comportamento del codice; la roadmap non è
prova di implementazione o test completato.

## Affermazione o decisione documentata

I README italiano e inglese descrivono REConsole v1.03, dipendenza PySide6,
risoluzione ADB prevista, avvio, uso ADB TCP/IP legacy e privacy dei log.
Gli esempi dichiarati sintetici mostrano righe logcat raw/clean e snapshot
Wi-Fi. `requirements.txt` elenca PySide6.

La roadmap RTF e l'addendum 2026-07-12 registrano requisiti e asserzioni di
avanzamento a quelle date. L'addendum richiede query Wi-Fi selezionate e
correlazione temporale. Sono documenti storici, non prove di esecuzione; lo
stato implementativo va verificato nel codice.

## Evidenza e provenienza

- `README.md`, `README_EN.md`, `requirements.txt`.
- `examples/logcat_raw.sample.txt`, `examples/logcat_clean.sample.txt`,
  `examples/wifi_snapshot.sample.txt`; i README li dichiarano sintetici.
- `notes/Roadmap.rtf` (metadati: 2026-06-15) e
  `notes/Roadmap_addendum_2026-07-12.rtf`.
- Confronto selettivo con codice ADB, filtri e Wi-Fi; non con prove runtime.

## Limiti e relazioni

- Il testo della roadmap principale è stato consultato parzialmente; dettagli
  storici incompleti.
- Procedura README non ripetuta. Vedi
  [REC-APP-LOGCAT-001](REC-APP-LOGCAT-001.md) e
  [REC-APP-WIFI-001](REC-APP-WIFI-001.md).
- Archivi Yi separati in [REC-YI-ARCHIVES-001](REC-YI-ARCHIVES-001.md).
