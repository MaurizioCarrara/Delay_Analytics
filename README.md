
# Documentazione – Ritardi

Questa guida descrive come usare l’app/script “Delay_Calculator”, come vengono calcolati **ritardi** e **anticipi**, quali **codici ritardo** sono considerati “handling” (e quindi esclusi dal calcolo “senza handling”), e quali file Excel vengono prodotti.

----------

## 1) Cosa fa il programma (in breve)

1.  Ti chiede di **trascinare** il file di input `.txt` o `.tsv` e premere Invio.

2.  Ti chiede il **mese (1–12)** da analizzare.
    
3.  Importa i dati, li **normalizza** (rinomina colonne in inglese, unifica date/ore in `STD` e `ATD`, ecc.), e applica alcune **regole di mapping**:
    
    -   `A/D`: tutte le `P` → `D` (le `A` restano `A`).
        
    -   `TRANSPORT`:  
        `PASSEGGERI`, `SCALO TECNICO`, `VARI` → `PASSENGERS`  
        `CARGO`, `POSTALE` → `FREIGHTER`
        
    -   `FLT_TYPE` (ex _VOLO_):  
        `LINEA` → `SCHEDULE`  
        `BIS` → `EXTRA`  
        `STATO` → `STATE`  
        `FERRY/POSIZIONAMENTO` (o varianti) → `FERRY`  
        `VOLO TECNICO` → `TECHNICAL`
        
4.  **Filtro mese (partenze):** tiene **solo le partenze (`A/D='D'`) con `STD` nel mese scelto**.  
    Per **gli arrivi** legati alle stesse partenze (stesso `ID`) **non c’è filtro di mese**: vengono inclusi anche se del mese precedente.
    
5.  Calcola i campi di interesse e genera **Excel** specifici (es. Delta, Etihad, United, Arkia, generici per IATA, anticipo generico).  
    I file vengono salvati **nella stessa cartella** del programma.
    

----------

## 2) Struttura delle colonne principali

-   `STD` – Orario **schedulato** (data+ora) della partenza.
    
-   `ATD` – Orario **effettivo** (data+ora) della partenza.
    
-   `STA` – Orario **schedulato** (data+ora) dell’arrivo.
    
-   `ATA` – Orario **effettivo** (data+ora) dell’arrivo.
    
-   `DLY_1`, `DLY_2` – **Codici ritardo** (IATA delay codes).
    
-   `DLY_1_t`, `DLY_2_t` – **Minuti** associati ai codici _DLY_1_ e _DLY_2_.
    
-   `DLY_REAL` – Ritardo reale della **partenza** in **minuti** (vedi §3).
    
-   `DLY_WO_HNDLG` – Ritardo “senza handling” in **minuti** (vedi §4).
    
-   `ADV_IN` – Anticipo in **minuti** dell’**arrivo** (vedi §5).
    

----------

## 3) Come calcoliamo i ritardi

### 3.1 Ritardo reale di partenza (`DLY_REAL`)

-   Formula:

	`DLY_REAL = max( minutes(ATD - STD), 0 )`
-   Unità: **minuti (interi)**.
    
-   Se `ATD ≤ STD` o uno dei due è mancante → `DLY_REAL` = vuoto/NaN.
    

----------

## 4) Ritardo “senza handling” (`DLY_WO_HNDLG`)

Alcuni **codici ritardo** appartengono all’**handling** e i relativi minuti **non vanno imputati** al vettore per le analisi “senza handling”.

**Lista codici handling usata dal programma:**
{12, 13, 15, 18, 31, 32, 33, 34, 35, 39, 52}

**Calcolo:**

1.  Si parte da `DLY_REAL`.
    
2.  Se `DLY_1` è in lista handling, **sottrai** `DLY_1_t`.
    
3.  Se `DLY_2` è in lista handling, **sottrai** `DLY_2_t`.
    
4.  Risultato **non scende sotto 0** (clip a 0).
    
5.  Esito in **minuti (interi)**.
    

> Se `DLY_WO_HNDLG = 0`, nei report generici viene comunque mantenuta la riga.

----------

## 5) Come calcoliamo gli anticipi in arrivo (`ADV_IN`)

`ADV_IN` misura di **quanto prima** è atterrato l’arrivo rispetto allo schedulato:

`ADV_IN   = max( minutes(STA - ATA), 0 )`

-   Unità: **minuti (interi)**.
    
-   Se l’arrivo è in ritardo o se dati mancanti → `ADV_IN = 0`.
    

----------

## 6) Logiche specifiche dei report

### 6.1 **Delta** – `Delays_DELTA.xlsx`

-   Filtra e **allinea** per `ID` gli **arrivi (A)** e le **partenze (D)** con `IATA='DL'`.
    
-   Calcola `DLY_REAL` sulla partenza.
    
-   **SURCHARGE**:
    
    -   `30%` se:
        
        -   `DLY_REAL > 180` **e**
            
        -   `07:00 ≤ ATD ≤ 21:00` **e**
            
        -   `FLT_TYPE_A != 'FERRY'` **e** `FLT_TYPE_D != 'FERRY'`
            
    -   `15%` se:
        
        -   `DLY_REAL > 180` **e**
            
        -   `07:00 ≤ ATD ≤ 21:00` **e**
            
        -   **almeno uno** tra `FLT_TYPE_A` o `FLT_TYPE_D` è `'FERRY'`
            
    -   altrimenti vuota.
        
-   **Evidenzia** in giallo le righe con `SURCHARGE` valorizzato.
    
-   Ordine righe: `STD` crescente (dal meno al più recente).
    

### 6.2 **Etihad** – `Delays_ETHIAD.xlsx`

-   **Partenze** con `IATA ∈ {EY, ETIHAD, ETHIAD}`.
    
-   Calcola/usa `DLY_REAL`.
    
-   **Evidenzia** intere righe se `DLY_REAL > 60`.
    
-   Ordine: `STD` crescente.
    

### 6.3 **United** – `Delays_UNITED.xlsx`

-   Allinea per `ID` **arrivo (A)** e **partenza (D)** con `IATA='UA'`.
    
-   Calcola `DLY_REAL`, `ADV_IN`, `DLY_WO_HNDLG`.
    
-   Calcola **%TURN_RATE_IN** da `ADV_IN` (soglie: `0%/15%/25%/50%/100%` per 0–60/61–120/121–180/181–240/>240).
    
-   Calcola **%_TURN_RATE_OUT** da `DLY_WO_HNDLG` con la stessa griglia.
    
-   **INFO_REQUIRED** = `"YES"` se la somma `DLY_1_t + DLY_2_t` è **diversa** da `DLY_REAL` (dove disponibile), altrimenti vuota.
    
-   Evidenzia le **celle** con `% > 0%` e le **celle** `DLY_1`/`DLY_2` che contengono codici handling.
    
-   Ordine: `STD` crescente.
    

### 6.4 **Arkia (IZ)** – `Delays_ARKIA.xlsx`

-   **Partenze** `IATA='IZ'`, join con arrivo.
    
-   Calcola `DLY_REAL`, `DLY_WO_HNDLG`.
    
-   **SURCHARGE** da `DLY_WO_HNDLG`:
    
    -   `20%` se `91–120`
        
    -   `30%` se `121–180`
        
    -   `45%` se `>180`
        
-   Evidenzia righe con `SURCHARGE` non vuota.
    
-   Ordine: `STD` crescente.
    

### 6.5 **Ritardo generico** 

-   **Partenze** per lo IATA indicato (es. `3U`, `CZ`, `MU`…), join con eventuale arrivo.
    
-   Calcola `DLY_REAL` e `DLY_WO_HNDLG`.
    
-   Ordine: `STD` crescente.
    
-   **Evidenzia** righe con `DLY_WO_HNDLG ≥ soglia_min`.
    
-   **Mantiene tutte le righe** anche se `DLY_WO_HNDLG = 0`.
    

### 6.6 **Anticipo generico** – `anticipo_generico(df, IATA, soglia_min, filename)`

-   **Arrivi** per lo IATA indicato (es. `AR`, `CI`…), join con eventuale partenza.
    
-   Calcola `ADV_IN`.
    
-   Ordine: `STA` crescente.
    
-   **Evidenzia** righe con `ADV_IN ≥ soglia_min`.
    

----------


## 7) Logica del filtro “per mese” (importante)

-   Il mese inserito (1–12) filtra **solo le PARTENZE (`A/D='D'`)** in base al **mese di `STD`**.
    
-   Gli **ARRIVI** collegati (stesso `ID`) vengono recuperati **anche se di altri mesi**.  
    Questo consente di analizzare i turni notturni o i casi in cui l’arrivo è alla fine del mese precedente e la partenza all’inizio del mese selezionato.
    

----------

## 8) Note e suggerimenti

-   Se i dati contengono stringhe “strane” per orari/date, il programma tenta la conversione con `dayfirst=True`. Le celle non convertibili restano vuote (NaT/NaN) e non partecipano al calcolo.
    
-   I report ordinano sempre **dal volo più “vecchio” al più “recente”** (crescente su `STD` o `STA`, a seconda del report).
    
-   Se una funzione specifica non trova righe pertinenti, **non crea file** e stampa un messaggio esplicativo.
    

