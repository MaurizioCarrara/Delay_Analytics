# Flight Delays Toolkit

Pipeline ETL in Python per normalizzare dati operativi voli (TSV), calcolare ritardi/anticipi, applicare regole di business e produrre report Excel affidabili. Progettata con standard “industrial-grade” orientati a **automazione**, **qualità dati** e **manutenibilità**.

## Funzionalità principali

- Import TSV/tab-delimited con intestazioni complesse.
- Normalizzazione:
  - `A/D`: P→D; `TRANSPORT`: PASSENGERS/FREIGHTER; `FLT_TYPE`: SCHEDULE/EXTRA/STATE/FERRY/TECHNICAL.
  - `STD = STD_1 + STD_2`, `ATD` da sorgenti raw, `ATOT = data(ATD) + ora(ATOT)`.
- Calcoli:
  - `DLY_REAL` in minuti, `ADV_IN` (anticipo arrivo), `DLY_WO_HNDLG` (ritardo netto da codici handling), `%TURN_RATE_*`, `SURCHARGE`.
- Accoppiamento A-D per `ID` con gestione arrivi del mese precedente.
- Report Excel con evidenziazioni condizionali (openpyxl).
- Dataset demo di 150 righe per test con dati sintetici.

## Requisiti

- Python 3.10+
- `pandas`, `openpyxl`, `xlsxwriter`
