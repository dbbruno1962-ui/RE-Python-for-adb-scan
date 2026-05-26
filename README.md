# Yi Reverse Console v1.03

Un tool grafico per analisi avanzate di log Android via ADB, con filtro runtime, tagging protocollo, e salvataggio automatico.

## Requisiti

- Python 3.8+
- adb.exe nella stessa cartella
- PySide6 (`pip install -r requirements.txt`)

## Uso

1. Avvia un emulatore Android o collega un dispositivo
2. Avvia questo script
3. Clicca "SCAN APPS", seleziona un'app e poi "START"

## File
- `log_console_v_1_03.py`: applicazione principale
- `filters.txt`: filtri attivi (modificabile anche a runtime)
- `logs/`: log raw e puliti

## ROADMAP
![Roadmap finale](roadmap.png)

*Bruno*
