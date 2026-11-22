---
id: REC-APP-REGISTRY-001
type: capability
target: REConsole, contesto runtime e registro locale
epistemic_state: derived
lifecycle_state: current
coverage: partial
---

# Percorsi runtime e registro dispositivi

## Scope

Descrive le API sorgente di `core/runtime.py` e `core/device_registry.py`.
Il contenuto di `devices.json` non è stato acquisito perché può contenere
identificatori locali.

## Affermazione

`RuntimeContext.from_file` deriva la directory base dal file principale e
costruisce percorsi per filtri e log. `SourceType` e `WifiMode` sono enum
dichiarati; non si attribuisce loro altro uso GUI. Il registro normalizza le
chiavi MAC con trim e maiuscolo, persiste JSON e offre `load`, `save`,
`add_device`, `get_device`, `update_device`, `is_ignored`. Un MAC assente
risulta non ignorato per default.

## Evidenza e provenienza

- `core/runtime.py`: enum e `RuntimeContext.from_file`.
- `core/device_registry.py`: `DEFAULT_DEVICE`, `_normalize_mac`,
  `_device_path` e funzioni pubbliche sopra elencate.
- `devices.json` esiste, ma non è stato letto; lo schema qui deriva dal
  codice, non dal contenuto operativo.
- `README.md` e `README_EN.md` lo descrivono come registro locale.

## Limiti e relazioni

- Validità e identità delle voci correnti non verificate.
- Non è stabilito un collegamento del registro al percorso di acquisizione
  ADB descritto in [REC-APP-LOGCAT-001](REC-APP-LOGCAT-001.md).
