# RE Console v1.03

Tool grafico per acquisizione e correlazione di log Android via ADB, con
filtraggio runtime, catalogo pattern e snapshot Wi-Fi sincronizzati.

## Requisiti

- Python 3
- PySide6
- ADB disponibile tramite una delle seguenti modalita':
  - variabile `ADB_PATH`;
  - `/mnt/e/platform-tools/adb.exe` in WSL;
  - `adb` o `adb.exe` nel `PATH`;
  - `adb.exe` nella directory del progetto.

Installazione dipendenze:

```sh
python3 -m pip install -r requirements.txt
```

## Avvio

Dopo l'installazione del launcher globale:

```sh
re-console
```

Oppure dalla directory del progetto:

```sh
./re-console
```

I percorsi di configurazione e dei log sono risolti rispetto alla directory
del progetto, quindi il comando puo' essere lanciato da qualsiasi posizione.

## Struttura

- `log_console_v_1_03.py`: applicazione principale.
- `core/`: gestione ADB, Wi-Fi, filtri, dispositivi e runtime.
- `filters.txt`: filtri attivi.
- `filters_candidates.txt`: catalogo dei pattern candidati.
- `devices.json`: registro locale dei dispositivi.
- `logs/`: output locale delle catture, escluso dal controllo di versione.
- `examples/`: campioni sintetici e bonificati del formato dei log.
- `notes/`: roadmap e note di progetto.

## Privacy dei log

Le catture reali possono contenere identificatori di dispositivo, indirizzi di
rete, metadati di app e altri dati operativi. Per questo `logs/` non viene
versionata. I campioni in `examples/` sono sintetici e non provengono da una
cattura reale.

## Roadmap

La roadmap storica e i successivi addendum sono conservati in `notes/`.
L'obiettivo resta una console generale per correlare ADB, Wi-Fi, Ethernet e,
in seguito, BLE su una timeline comune.

By Bruno
