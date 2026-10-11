# RE Console v1.03

[Italiano](README.md) | [English](README_EN.md)

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

## ADB via Wi-Fi (Android 8.1 / ADB TCP/IP)

Questa procedura usa il protocollo ADB TCP/IP classico sulla porta `5555`; non
e' il comando `adb pair` delle versioni Android piu' recenti. Il primo
passaggio richiede ancora il cavo USB e l'autorizzazione di debug sul telefono.

Con il telefono collegato via USB:

```sh
adb devices
adb -s <SERIAL_USB> tcpip 5555
adb -s <SERIAL_USB> shell ip -f inet addr show wlan0
```

Annotare l'indirizzo IPv4 di `wlan0`, scollegare il cavo USB e, dal computer
sulla stessa LAN, collegarsi al telefono:

```sh
adb connect <IP_TELEFONO>:5555
adb devices
```

Lo stato deve risultare `device`; a quel punto RE Console si usa normalmente:
eseguire la scansione delle app e avviare la cattura. Per esempio, i messaggi
`light_meter` dell'app luxmeter continuano a passare attraverso la stessa
pipeline logcat, senza una sorgente dedicata.

La versione attuale della console invoca `adb` senza `-s <serial>`. Prima di
avviarla, lasciare quindi un solo target ADB nello stato `device`: dopo il
passaggio Wi-Fi, scollegare l'USB. Per riconnettere dopo una caduta di rete:

```sh
adb connect <IP_TELEFONO>:5555
```

Per tornare a USB, ricollegare il cavo e usare:

```sh
adb -s <SERIAL_USB> usb
adb disconnect <IP_TELEFONO>:5555
```

ADB su TCP/IP non cifra ne' autentica nuovamente ogni connessione sulla porta
`5555`: abilitarlo soltanto su una LAN fidata e disattivarlo quando non serve.

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
