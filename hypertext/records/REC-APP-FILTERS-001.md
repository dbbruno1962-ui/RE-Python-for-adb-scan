---
id: REC-APP-FILTERS-001
type: capability
target: REConsole v1.03, filtri su logcat Android
epistemic_state: derived
lifecycle_state: current
coverage: partial
---

# Filtri runtime e catalogo pattern

## Scope

Descrive caricamento e applicazione dei pattern, non dimostra che una stringa
sia pubblicità, rumore o protocollo nel comportamento di un'app.

## Affermazione

`filters.txt` è letto come lista di sottostringhe attive. Il confronto è
case-insensitive. Le checkbox aggiornano la lista in memoria; il doppio clic
su un candidato lo appende a `filters.txt` se assente. Il loader del catalogo
include solo `AD_MEDIATION`, `AD_DOMAINS` e `AD_CLASSES_OR_MARKERS`, escludendo
la sezione diagnostica di rete. Il motore segnala candidati incontrati nella
sessione e conta parole con `SUSPECT_WORDS`; sono classificazioni euristiche.

## Evidenza e provenienza

- `core/filter_manager.py`: `load_filters`, `load_filter_candidates`,
  `append_filter`, `classify_noise`, `map_proto`.
- `log_console_v_1_03.py`: `LogcatThread.should_filter`, `detect_patterns`,
  `detect_protocol` e gestione GUI dei filtri.
- `filters.txt`: lista attiva locale.
- `filters_candidates.txt`: catalogo dichiarato per `com.yunyi.smartcamera`,
  versione 5.0.9_20260515; vieta promozione automatica. La fonte indicata è
  un percorso esterno non verificato in questo worktree.
- `classify_noise` non decide il filtro nel percorso logcat esaminato; la
  decisione dipende dalla lista attiva.

Derivazione statica, senza valutazione su log reali.

## Limiti e relazioni

- Le sottostringhe possono causare falsi positivi e rimuovere righe correlate
  dal clean; il raw logcat viene scritto prima.
- Gli esempi sono sintetici e non validano il catalogo.
- Non trasferire candidati ad altri target/versioni senza verifica.
- Relazione: [REC-APP-LOGCAT-001](REC-APP-LOGCAT-001.md).
