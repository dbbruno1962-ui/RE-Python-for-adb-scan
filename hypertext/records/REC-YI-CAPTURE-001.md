---
id: REC-YI-CAPTURE-001
type: capability
target: Yi .55 / Android app `com.yunyi.smartcamera` (target dichiarato)
epistemic_state: derived
lifecycle_state: current
coverage: partial
---

# Script di acquisizione Yi SD keysync

## Scope

Descrive staticamente `scripts/capture_yi_sd_logcat.sh` nello stato locale
letto il 2026-11-22. Git lo segnalava già modificato prima dell'assimilazione;
versione deployata e run non stabiliti.

## Affermazione

Lo script risolve ADB, crea una directory sessione sotto `logs/`, avvia il
server e attende un device; per default tenta `logcat -c` se
`CLEAR_LOGCAT=1`. Avvia logcat raw `threadtime` e una vista focus via regex.
Comandi interattivi aggiungono marker agli eventi e tentano di inviarli anche
come messaggi Android `CODXMARK`; consentono snapshot Wi-Fi, probe TCP su porte
e lettura PID. Il trap marca lo stop e termina logcat. Variabili d'ambiente
possono sovrascrivere alcuni target e percorsi.

## Evidenza e provenienza

- `scripts/capture_yi_sd_logcat.sh`: variabili `PACKAGE`, `CAMERA_IP`,
  `SESSION`, `OUT_DIR`, `CLEAR_LOGCAT`; funzioni `resolve_adb`, `mark`,
  `wifi_snapshot`, `camera_probe`, `pid_snapshot`, `cleanup` e loop comandi.
- `logs/sd_baseline/*/README_CAPTURE.txt`: target, output e sequenza manuale
  intesa; non prova che ogni marker o passaggio sia avvenuto.
- I log locali non sono stati letti né copiati.

Derivazione statica da script e README.

## Limiti e relazioni

- Il probe TCP non è handshake di protocollo né identifica da solo un servizio.
- Regex, risoluzione ADB e semantica dei marker non eseguite né validate qui.
- La modifica preesistente allo script è stata preservata.
- Target distinto dall'app REConsole e dalla camera ZHENYI/SGK.
