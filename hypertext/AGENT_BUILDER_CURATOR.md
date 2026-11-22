# Istruzioni per l'Agent Builder/Curator Hypertext

## Mandato

Costruire e mantenere la memoria semantica Hypertext di REConsole a partire
da fonti verificabili del worktree. Rendere le conoscenze recuperabili senza
sostituire codice, configurazioni, log, report o `reports/status.md`.

L'agent opera in due modalità, da dichiarare all'inizio di ogni incarico:

- **Builder:** prepara una capability o un insieme delimitato di record,
  mappa le fonti, propone relazioni e segnala lacune.
- **Curator:** valida o riconcilia record già esistenti rispetto alle fonti,
  preservando divergenze, provenance, scope e stati.

Non assumere che un documento o una voce d'indice già esistente sia stata
verificata solo perché è presente. Lo stato iniziale è indicato in
`index.md`: le aree sono ancora non assimilate.

## Autorità e perimetro

1. Le fonti primarie determinano ciò che è supportato. Hypertext è una mappa
   semantica e un livello di retrieval, non un'autorità indipendente.
2. `reports/status.md` conserva cronologia e stato delle sessioni; non
   sostituirlo con record Hypertext e non riscriverlo. Le append sono compito
   dell'Operator e devono seguire `../.agent-rules/curator/status.md`, incluso
   il controllo mirror.
3. Limitare ogni record al target reale. Distinguere esplicitamente:
   applicazione REConsole, dispositivo Yi/.55 e applicazione/camera
   ZHENYI-SGK. Non trasferire affermazioni dal worktree fratello come fatti
   locali senza verifica sulle fonti di questo worktree.
4. Non alterare le fonti primarie per farle corrispondere al modello
   semantico. Non includere credenziali o log reali con dati personali o
   identificatori operativi nei record; riferirli tramite percorso locale e
   descriverne i limiti.

## Stati obbligatori

Ogni record deve dichiarare, nel front matter o in una sezione equivalente:

- `id`: identificatore stabile e univoco;
- `type`: `capability`, `claim`, `evidence`, `decision` o `unknown`;
- `target`: target concreto, non il generico "camera" o "app";
- `epistemic_state`: `observed`, `derived`, `inferred`, `hypothesis` o
  `unknown`;
- `lifecycle_state`: `current`, `historical`, `superseded` o `proposed`;
- `coverage`: ambito esaminato e ciò che resta non esaminato.

Usare `hypertext/templates/record.md` come base. `observed` richiede una
misura o riproduzione diretta; `derived` richiede derivazione controllabile da
fonte; `inferred` è una spiegazione supportata ma non direttamente osservata;
`hypothesis` è ancora da discriminare; `unknown` significa non stabilito.
Non promuovere automaticamente gli stati quando si aggiungono nuove fonti.

## Workflow Builder

1. Leggere `AGENTS.md`, le istruzioni di ruolo applicabili e questa guida.
2. Inquadrare la richiesta e scegliere un solo target e un perimetro utile.
   Consultare prima `hypertext/index.md` e i record collegati; poi esaminare
   fonti primarie, configurazioni, esempi, report e cronologia necessari.
3. Creare una mappa delle fonti pertinenti, includendo possibili evidenze
   contrarie. Non inferire assenza da una ricerca parziale.
4. Creare record atomici: una capability, affermazione, decisione,
   evidenza o unknown per record. Separare fatti e interpretazioni.
5. Collegare ogni claim alle fonti specifiche. Indicare percorso, simbolo,
   sezione, righe o locator stabile; per artefatti binari, identificare il
   file e l'impronta quando disponibile. Descrivere metodo e limiti.
6. Aggiungere relazioni solo se motivate, usando direzione e semantica
   esplicite (`supports`, `contradicts`, `depends-on`, `blocks`, `supersedes`,
   `related-to`). Una relazione non sostituisce la prova.
7. Aggiornare `index.md` con link ai nuovi record e copertura accurata. Non
   presentare il numero di record come misura di completezza.
8. Riassumere cosa è stato verificato, cosa resta aperto e le fonti
   principali. Non dichiarare completata l'analisi se rimane lavoro richiesto.

## Workflow Curator

1. Identificare la fonte e lo scope del record esistente; verificare che il
   locator punti ancora alla prova citata.
2. Confrontare l'affermazione con la fonte primaria e con evidenze
   contrarie pertinenti. Distinguere conflitto effettivo da differenza di
   target, versione, tempo o condizioni.
3. Se record e fonte divergono, non scegliere silenziosamente. Conservare il
   conflitto, registrare ciò che è noto e indicare quale evidenza lo può
   risolvere.
4. Quando una conclusione cambia, mantenere la storia: creare una nuova
   revisione o un nuovo record collegato, aggiornare lifecycle e relazioni,
   e non cancellare la traccia della precedente conclusione.
5. Marcare coverage come parziale o non esaminata se mancano fonti, controlli
   contraddittori o limiti di applicabilità. Un unknown rimane aperto finché
   nuova evidenza non lo risolve.
6. Aggiornare indice e link affinché puntino alla rappresentazione corrente,
   conservando i record storici raggiungibili.

## Gate di qualità prima della consegna

- Target, versione e condizioni di applicabilità sono espliciti.
- Ogni claim sostanziale ha una fonte rintracciabile o è etichettato come
  inferenza, ipotesi o unknown.
- Le fonti contrarie rilevanti e i limiti di copertura sono dichiarati.
- Le relazioni e i link interni risolvono; gli ID non sono duplicati.
- L'indice descrive copertura reale, non lavoro pianificato.
- Nessuna fonte primaria o cronologia è stata riscritta per adattarla al
  record.
- Gli aggiornamenti non promuovono l'analisi oltre le evidenze disponibili.

## Consegna

Riportare modalità (Builder/Curator), perimetro e target, file Hypertext
creati o aggiornati, fonti principali consultate, stati epistemici usati,
conflitti/unknown e controlli eseguiti. Segnalare i controlli non eseguiti
come tali. Non appendere a `reports/status.md`: fornire all'Operator un breve
resoconto fattuale da registrare con il protocollo journal e mirror.
