---
id: REC-ZHENYI-GUIDE-001
type: unknown
target: dispositivo descritto come ZHENYI-E63C / SGK GK720X e app `com.vidure.app`; associazione non verificata
epistemic_state: unknown
lifecycle_state: proposed
coverage: partial
---

# Affermazioni non corroborate nella guida ZHENYI-E63C

## Scope

La guida riguarda un target separato da REConsole e dal flusso Yi. Non
riproduciamo credenziali, MAC, password o URL operativi contenuti nella guida.
Applicabilità al dispositivo attuale non stabilita.

## Affermazione o domanda

`vidure_re_output/zhenyi_camera_guida_completa.md` formula affermazioni su
hardware/firmware, servizi di rete, streaming RTSP, API HTTP, telemetria,
prove endpoint e avvio script SD; propone inoltre lavoro futuro su accesso
seriale. Sono **asserzioni della guida**: le fonti primarie consultate qui
non corroborano le misure runtime (porte, stream, risposte HTTP, firmware,
script SD). La guida attribuisce alcune conclusioni a prove, ma non fornisce
per ogni claim i log, i protocolli o le condizioni necessarie a riprodurle.

## Evidenza e provenienza

- `vidure_re_output/zhenyi_camera_guida_completa.md` (fonte narrativa).
- Materiale statico collegato con limiti in
  [REC-ZHENYI-APK-001](REC-ZHENYI-APK-001.md).
- `1_http_endpoints.txt` è un filtro rumoroso, non prova servizi HTTP attivi.
- Log e tar locali non letti; nessuna connessione o prova dispositivo eseguita.

## Limiti e relazioni

- Stato `unknown` per le affermazioni hardware/runtime finché manca la catena
  di prova. Nuove evidenze possono generare record atomici distinti.
- Non usare la guida da sola per comandi di scrittura/reset, modifiche rete,
  root o equivalenza tra versioni.
- Il file include segreti/identificatori operativi: riferirsi al percorso,
  senza copiarli nei record.
