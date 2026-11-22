---
id: REC-ZHENYI-APK-001
type: evidence
target: Android app APK `com.vidure.app`; hardware target non provato staticamente
epistemic_state: derived
lifecycle_state: historical
coverage: partial
---

# Provenienza e limiti del corpus APK ZHENYI/SGK

## Scope

Mappa la pipeline di estrazione e gli artefatti testuali. Il package non prova
che APK/versione corrisponda all'app installata sul dispositivo della guida.
Firmware ed esecuzione non sono acquisiti qui.

## Affermazione

`analyze_vidure.sh` estrae via ADB i path APK, esegue pull/unzip e genera
`all_strings.txt` più tre filtri: endpoint, stringhe Wi-Fi/debug e nomi file.
Lo script non genera direttamente `api_mappate.txt`, `tabella_absapi.txt`,
`classi_chiave.txt`, `risultati_mirati.txt`, `risultati_re.txt` o la guida;
la provenienza puntuale di questi artefatti non è documentata nello script.

Gli APK e DEX locali supportano l'esistenza di materiale statico analizzabile.
`api_mappate.txt` espone stringhe attribuite a classi/API, non richieste HTTP
osservate né endpoint confermati nel firmware. `1_http_endpoints.txt` include
anche numerose classi/librerie precedute da `/app/`: è un filtro rumoroso,
non un inventario affidabile dei servizi del device.

## Evidenza e provenienza

- `analyze_vidure.sh`: `pm path`, pull/unzip, `strings -n 4 | sort -u` e
  successivi `grep`.
- `vidure_re_output/apks/`, `vidure_re_output/unpacked/`: APK split e output
  presenti; non hashati in questa sessione.
- `api_mappate.txt`, `tabella_absapi.txt`, `classi_chiave.txt`,
  `risultati_mirati.txt`, `risultati_re.txt` e tre risultati filtro: report
  preesistenti, provenienza parziale.
- `unpacked/AndroidManifest.xml` è binario; la stringa package è visibile,
  ma il manifest non è stato decodificato integralmente.

## Limiti e relazioni

- Non attribuire risultati ad un firmware o dispositivo senza collegare APK,
  device e osservazione runtime.
- Non è stata verificata ogni riga dei report voluminosi.
- Relazione: [REC-ZHENYI-GUIDE-001](REC-ZHENYI-GUIDE-001.md).
