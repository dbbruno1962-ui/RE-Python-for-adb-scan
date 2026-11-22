# REConsole Hypertext — indice

Catalogo semantico delle aree del worktree. Questo indice è una mappa di
retrieval, non una fonte primaria. I record iniziali verificano soprattutto
comportamenti statici del codice e provenienza documentale; non attestano
esecuzioni runtime dei flussi descritti.

Istruzioni dell'agent Builder/Curator: [AGENT_BUILDER_CURATOR.md](AGENT_BUILDER_CURATOR.md).

| Area | Target | Fonti iniziali | Copertura semantica |
|---|---|---|---|
| Avvio, configurazione e pipeline ADB/logcat | Applicazione REConsole v1.03 | `README.md`, `README_EN.md`, `log_console_v_1_03.py`, `core/adb_manager.py`, esempi | [REC-APP-LOGCAT-001](records/REC-APP-LOGCAT-001.md) — parziale, analisi statica |
| Filtri runtime e catalogo pattern | Applicazione REConsole v1.03 | `core/filter_manager.py`, `filters.txt`, `filters_candidates.txt`, `log_console_v_1_03.py` | [REC-APP-FILTERS-001](records/REC-APP-FILTERS-001.md) — parziale; nessuna valutazione su log reali |
| Snapshot Wi-Fi correlati | Applicazione REConsole e dispositivo Android via ADB | `core/wifi_manager.py`, `log_console_v_1_03.py`, campione Wi-Fi, roadmap | [REC-APP-WIFI-001](records/REC-APP-WIFI-001.md) — parziale, codice e campione |
| Contesto runtime e registro locale | Applicazione REConsole | `core/runtime.py`, `core/device_registry.py`, `devices.json` (contenuto non acquisito) | [REC-APP-REGISTRY-001](records/REC-APP-REGISTRY-001.md) — parziale |
| Roadmap e documentazione del prodotto | Applicazione REConsole | `README.md`, `README_EN.md`, `notes/Roadmap*.rtf`, `requirements.txt` | [REC-APP-DOCS-001](records/REC-APP-DOCS-001.md) — parziale; roadmap come intenzione/documentazione |
| Acquisizione Yi .55 SD keysync | Dispositivo Yi / app Android `com.yunyi.smartcamera` | `scripts/capture_yi_sd_logcat.sh`, README_CAPTURE, log locali non letti | [REC-YI-CAPTURE-001](records/REC-YI-CAPTURE-001.md) — flusso statico; script locale modificato; runtime non verificato |
| Documentazione archivi Yi/Anyka | Target Yi IoT / Anyka secondo i README d'archivio | `logs/archives/README.md`, `logs/archives/SHA256SUMS`, archivi locali non aperti | [REC-YI-ARCHIVES-001](records/REC-YI-ARCHIVES-001.md) — inventario documentale parziale; contenuti non analizzati |
| Analisi statica APK ZHENYI/SGK | App `com.vidure.app`; dispositivo descritto nei documenti come ZHENYI/SGK | `analyze_vidure.sh`, APK, `unpacked/`, report testuali | [REC-ZHENYI-APK-001](records/REC-ZHENYI-APK-001.md) — provenienza parziale; script limitato a stringhe e tre filtri |
| Guida operativa ZHENYI-E63C / GK720X | Target asserito dalla guida; applicabilità/versione non indipendentemente confermate | `vidure_re_output/zhenyi_camera_guida_completa.md`, estratti APK | [REC-ZHENYI-GUIDE-001](records/REC-ZHENYI-GUIDE-001.md) — guida acquisita; affermazioni runtime non corroborate |

Per aggiungere un record, usare `templates/record.md`, assegnare un ID stabile,
delimitare il target e collegare direttamente le fonti. I log reali e i dati
operativi in `logs/` non sono stati copiati nei record. Leggere
`reports/status.md` per la cronologia di sessione; l'append di questa
assimilazione è registrato nella sessione 2026-11-22.
