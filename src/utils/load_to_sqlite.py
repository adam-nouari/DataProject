# -*- coding: utf-8 -*-
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
from astral import LocationInfo
from astral.sun import sun
import pytz

CLEANED_DIR = Path("data/cleaned")
DB_PATH     = Path("data/database/vitesses.db")

# ⬇️ UNIQUEMENT 2023
FILES = {
    "vitesse_2023_cleaned.csv": 2023,
}

TZ = pytz.timezone("Europe/Paris")
GRID_DECIMALS = 1       # 0.1° ~ 11 km → moins de clés éphémérides = plus rapide
CHUNKSIZE = 400_000

# ---------- utilitaires DB ----------
def drop_tables_if_exist(conn, names):
    for n in names:
        conn.execute(f"DROP TABLE IF EXISTS {n};")
    conn.commit()

def list_tables(conn):
    return pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;", conn)

def column_exists(conn, table, col):
    info = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
    return col in info["name"].tolist()

# ---------- étape 1 : importer le CSV 2023 -> vitesses ----------
def import_csvs_to_sqlite():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_data = []
    for file_name, annee in FILES.items():
        csv_path = CLEANED_DIR / file_name
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV introuvable: {csv_path}")
        print(f"[INFO] Lecture de {file_name}")
        df = pd.read_csv(csv_path, sep=";", dtype={"date": "string"})
        df["annee"] = annee
        df["date"] = (pd.to_datetime(df["date"], errors="coerce")
                        .dt.strftime("%Y-%m-%d %H:%M:%S"))
        mask_na = df["date"].isna()
        if mask_na.any():
            df.loc[mask_na, "date"] = df.loc[mask_na, "date"].astype("string")
        df["date"] = df["date"].str.replace("T", " ", regex=False)
        all_data.append(df)

    merged = pd.concat(all_data, ignore_index=True)
    merged["date"] = merged["date"].astype(str)

    with sqlite3.connect(DB_PATH) as conn:
        # Nettoyage d’anciennes tables si elles existent encore
        drop_tables_if_exist(conn, ["vitesses_avec_periode", "vitesses_old", "vitesses_final", "vitesses_preview"])
        merged.to_sql("vitesses", conn, if_exists="replace", index=False)
        print(f"[OK] Table 'vitesses' (2023) créée ({len(merged):,} lignes)")
        print("🗃️ Tables après import:\n", list_tables(conn))

# ---------- étape 2 : calcul/MAJ 'periode' dans vitesses ----------
def ensure_periode_column(conn):
    if not column_exists(conn, "vitesses", "periode"):
        conn.execute("ALTER TABLE vitesses ADD COLUMN periode TEXT;")
        conn.commit()
        print("[INFO] Colonne 'periode' ajoutée")

def localize_paris(series_naive: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series_naive, errors="coerce")
    try:
        return dt.dt.tz_localize(TZ, ambiguous="infer", nonexistent="shift_forward")
    except Exception:
        return dt.dt.tz_localize(TZ, ambiguous=False, nonexistent="shift_forward")

def compute_ephem_for_keys(keys_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for d, latr, lonr in keys_df.itertuples(index=False, name=None):
        try:
            loc = LocationInfo(latitude=latr, longitude=lonr, timezone=TZ.zone)
            s = sun(loc.observer, date=d, tzinfo=TZ)
            rows.append((d, latr, lonr, s["sunrise"], s["sunset"]))
        except Exception:
            rows.append((d, latr, lonr, pd.NaT, pd.NaT))
    return pd.DataFrame(rows, columns=["date_only","lat_round","lon_round","sunrise_local","sunset_local"])

def process_chunk_tag_periode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["datetime"]  = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["datetime", "position"]).copy()
    df["datetime"] = localize_paris(df["datetime"])
    df["date_only"] = df["datetime"].dt.date

    latlon = df["position"].str.split(expand=True)
    latlon.columns = ["lat", "lon"]
    df = pd.concat([df, latlon], axis=1)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat","lon"]).copy()

    df["lat_round"] = df["lat"].round(GRID_DECIMALS)
    df["lon_round"] = df["lon"].round(GRID_DECIMALS)

    keys = df[["date_only","lat_round","lon_round"]].drop_duplicates()
    ephem = compute_ephem_for_keys(keys)
    vm = df.merge(ephem, on=["date_only","lat_round","lon_round"], how="left")

    vm["periode"] = np.where(
        (vm["datetime"] >= vm["sunrise_local"]) & (vm["datetime"] <= vm["sunset_local"]),
        "jour", "nuit"
    )
    return vm[["rid","periode"]]

def tag_periode_inplace():
    with sqlite3.connect(DB_PATH) as conn:
        ensure_periode_column(conn)
        sql = "SELECT rowid AS rid, date, position FROM vitesses;"
        total = updated = 0
        for i, chunk in enumerate(pd.read_sql_query(sql, conn, chunksize=CHUNKSIZE)):
            n = len(chunk); total += n
            print(f"\n— Chunk #{i+1} — {n:,} lignes")
            vm = process_chunk_tag_periode(chunk)  # (rid, periode)
            pairs = [(p, rid) for rid, p in vm.itertuples(index=False, name=None)]
            conn.executemany("UPDATE vitesses SET periode=? WHERE rowid=?;", pairs)
            conn.commit()
            updated += len(pairs)
            print(f"   ✅ {len(pairs):,} lignes mises à jour")
        print(f"\n📦 Bilan MAJ : lus={total:,} / maj={updated:,}")

# ---------- main ----------
def main():
    print("🚀 DÉBUT (2023 uniquement)")
    import_csvs_to_sqlite()
    tag_periode_inplace()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_vitesses_date    ON vitesses(date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_vitesses_pos     ON vitesses(position);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_vitesses_periode ON vitesses(periode);")
        # on s’assure qu’il ne reste qu’UNE table métier
        drop_tables_if_exist(conn, ["vitesses_avec_periode", "vitesses_old", "vitesses_final", "vitesses_preview"])
        print("🗃️ Tables en fin de run:\n", list_tables(conn))
    print("✅ Terminé : table unique 'vitesses' (2023) avec 'periode'.")

if __name__ == "__main__":
    main()
