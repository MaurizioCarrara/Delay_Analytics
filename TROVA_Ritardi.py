import pandas as pd
import sys
import os
import CNA_rules

# Indici delle colonne da mantenere (partendo da 0) — ordine finale desiderato
COLUMNS_TO_KEEP_IDX = [26,10,14,12,27,16,62,7,8,2,3,1,28,41,30,19,23,20,24,63,42]

# Nuovi nomi (stesso ordine di COLUMNS_TO_KEEP_IDX)
NEW_COLUMN_NAMES = [
    'ID','A/D','TRANSPORT','FLT_TYPE','REG','MOD','MTOW','SEATS','STAND',
    'IATA','FLT_N','FROM','TO','STD_1','STD_2','DLY_1','DLY_1_t','DLY_2',
    'DLY_2_t','ATD','ATOT'
]

def _base_dir():
    # cartella in cui si trova l'eseguibile quando “freezato” con PyInstaller
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # cartella del file .py quando eseguito da sorgente
    return os.path.dirname(os.path.abspath(__file__))

def _validate_indices(header: list, idx_list: list):
    max_idx = len(header) - 1
    bad = [i for i in idx_list if i < 0 or i > max_idx]
    if bad:
        raise IndexError(
            f"Gli indici {bad} non esistono. Numero colonne trovate: {len(header)} (max indice {max_idx})."
        )

def load_txt_to_df(file_path: str, usecols_idx=None, new_names=None) -> pd.DataFrame:
    header_only = pd.read_csv(file_path, sep="\t", dtype=str, nrows=0, engine="python")
    original_cols = list(header_only.columns)
    idx_list = usecols_idx or []
    _validate_indices(original_cols, idx_list)

    selected_names_in_order = [original_cols[i] for i in idx_list]

    df = pd.read_csv(
        file_path,
        sep="\t",
        dtype=str,
        usecols=selected_names_in_order,
        engine="python",
        on_bad_lines="skip"
    )

    # forzo l’ordine desiderato, poi rinomino
    df = df[selected_names_in_order]

    if new_names:
        if len(new_names) != len(df.columns):
            raise ValueError(
                f"new_names ha {len(new_names)} elementi ma le colonne caricate sono {len(df.columns)}."
            )
        df.columns = new_names

    # ---- crea/normalizza STD e ordina (ascendente) ----
    if "STD" in df.columns:
        std_sort = pd.to_datetime(df["STD"], errors="coerce", dayfirst=True)
    elif {"STD_1", "STD_2"}.issubset(df.columns):
        std_sort = pd.to_datetime(
            df["STD_1"].astype(str) + " " + df["STD_2"].astype(str),
            errors="coerce", dayfirst=True
        )
        df["STD"] = std_sort
    else:
        return df

    df["_STD_SORT"] = std_sort
    df = df.sort_values("_STD_SORT", ascending=True).drop(columns=["_STD_SORT"]).reset_index(drop=True)

    return df

def ask_month() -> int:
    """Chiede un mese 1-12, valida e restituisce l'intero."""
    while True:
        raw = input("Inserisci il mese da analizzare (1-12): ").strip()
        if not raw.isdigit():
            print("Inserisci un numero da 1 a 12.")
            continue
        m = int(raw)
        if 1 <= m <= 12:
            return m
        print("Mese non valido. Inserisci un numero da 1 a 12.")

def _format_DLY_REAL(td: pd.Timedelta):
    """Ritorna i minuti totali (int) se td>0, altrimenti pd.NA."""
    if pd.isna(td):
        return pd.NA
    total_sec = td.total_seconds()
    if total_sec <= 0:
        return pd.NA
    return int(round(total_sec / 60))


if __name__ == "__main__":
    while True:
        print("Trascina qui il file .txt e premi Invio:")
        file_path = input().strip().strip('"')

        print("File acquisito correttamente!")

        try:
            month = ask_month()

            print("Analisi dati in corso...")

            df = load_txt_to_df(
                file_path,
                usecols_idx=COLUMNS_TO_KEEP_IDX,
                new_names=NEW_COLUMN_NAMES
            )

            # Crea STD (datetime) e pulisci ATD (datetime)
            df["STD"] = pd.to_datetime(
                df["STD_1"].astype(str) + " " + df["STD_2"].astype(str),
                errors="coerce",
                dayfirst=True
            )
            df["ATD"] = pd.to_datetime(df["ATD"].astype(str).str.strip(), errors="coerce", dayfirst=True)

            # Filtra per mese su STD (ignora NaT)
            # Normalizza A/D PRIMA del filtro (e rimuovi la stessa riga più sotto)
            df["A/D"] = df["A/D"].astype(str).str.strip().str.upper().replace({"P": "D"})

            # 1) Tieni SOLO le PARTENZE (D) del mese richiesto
            mask_dep = df["STD"].notna() & df["A/D"].eq("D") & (df["STD"].dt.month == month)
            df_dep = df[mask_dep].copy()

            # 2) Recupera gli ARRIVI (A) per gli stessi ID, anche se di mesi diversi
            ids = df_dep["ID"].dropna().unique()
            df_arr = df[df["A/D"].eq("A") & df["ID"].isin(ids)].copy()

            # 3) Ricompone il DF da passare alle funzioni
            df = pd.concat([df_dep, df_arr], ignore_index=True)


            if df.empty:
                print(f"\nNessun volo trovato per il mese {month:02d} nel file selezionato.")
                print("Riavvio del programma...\n")
                continue

            # Rimuovo STD_1 e STD_2
            df = df.drop(columns=["STD_1", "STD_2"])

            # Riposiziono STD e ATD subito dopo TO
            cols = list(df.columns)
            to_index = cols.index("TO")
            for col in ["STD", "ATD"]:
                if col in cols:
                    cols.remove(col)
            cols[to_index+1:to_index+1] = ["STD", "ATD"]
            df = df[cols]

            # ====== NORMALIZZAZIONI RICHIESTE (prima delle funzioni) ======

            # 1) A/D: tutte le P -> D (lasciando A invariato)
            df["A/D"] = df["A/D"].astype(str).str.strip().str.upper().replace({"P": "D"})

            # 2) TRANSPORT: mapping richiesto -> inglese
            tr_map = {
                "PASSEGGERI": "PASSENGERS",
                "SCALO TECNICO": "PASSENGERS",
                "VARI": "PASSENGERS",
                "CARGO": "FREIGHTER",
                "POSTALE": "FREIGHTER",
            }
            df["TRANSPORT"] = df["TRANSPORT"].astype(str).str.strip().str.upper().replace(tr_map)

            # 3) FLT_TYPE (ex VOLO): mapping richiesto -> inglese
            def _map_flt_type(x: str) -> str:
                s = str(x).strip().upper()
                if s == "LINEA":
                    return "SCHEDULE"
                if s == "BIS":
                    return "EXTRA"
                if s == "STATO":
                    return "STATE"
                if s in {"FERRY/POSIZIONAMENTO", "FERRY / POSIZIONAMENTO", "FERRY-POSIZIONAMENTO", "POSIZIONAMENTO", "FERRY"}:
                    return "FERRY"
                if s == "VOLO TECNICO":
                    return "TECHNICAL"
                return s
            df["FLT_TYPE"] = df["FLT_TYPE"].apply(_map_flt_type)

            # =============================================================

            # Calcolo DLY_REAL = ATD - STD in minuti (vuoto se <=0 o mancante)
            df["DLY_REAL"] = (df["ATD"] - df["STD"]).apply(_format_DLY_REAL)

            # Posiziono DLY_REAL subito dopo ATD
            cols = list(df.columns)
            if "DLY_REAL" in cols:
                cols.remove("DLY_REAL")
                atd_idx = cols.index("ATD")
                cols[atd_idx+1:atd_idx+1] = ["DLY_REAL"]
                df = df[cols]

            # Salvataggio Excel nella stessa cartella del .py
            script_dir = _base_dir()
            output_path = os.path.join(script_dir, "output.xlsx")
            df.to_excel(output_path, index=False)

            print(f"\nOUTPUT principale eseguito.\nFile Excel salvato in: {output_path}")

            # LANCIO FUNZIONI DOPO LE NORMALIZZAZIONI
            CNA_rules.delta(df)
            CNA_rules.etihad(df)
            CNA_rules.united(df)
            CNA_rules.arkia(df)
            CNA_rules.ritardo_generico(df, "3U",60, "FCO_Delays_SICHUAN.xlsx")
            CNA_rules.ritardo_generico(df, "CZ",120, "FCO_Delays_CHINA_SOUTHERN.xlsx")
            CNA_rules.ritardo_generico(df, "MU",120, "FCO_Delays_CHINA_EASTERN.xlsx")
            CNA_rules.anticipo_generico(df, "AR", 120, "FCO_Advance_AEROLINAS_ARGENTINAS.xlsx")
            CNA_rules.anticipo_generico(df, "CI", 60, "FCO_Advance_CHINA_AIRLINES.xlsx")
            
            break  # completato con successo

        except KeyboardInterrupt:
            print("\nInterrotto dall'utente.")
            sys.exit(0)
        except Exception as e:
            print(f"\nErrore: {e}")
            print("Riavvio del programma...\n")
