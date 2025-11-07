from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("data/database/vitesses.db")
TABLE   = "vitesses"

def read_csv_any(path: Path) -> pd.DataFrame:
    """
    Lecture tolérante : détection automatique du séparateur et de l'encodage.
    """
    # try common encodings and delimiters explicitly to avoid pandas sniffing issues
    encodings = ("utf-8", "utf-8-sig", "latin1")
    seps = [';', ',', '\t', '|']

    last_exc: Exception | None = None
    for enc in encodings:
        for sep in seps:
            try:
                # use default engine (C) when separator is explicit; it's faster and supports low_memory
                return pd.read_csv(path, sep=sep, encoding=enc, low_memory=False)
            except Exception as exc:
                last_exc = exc
                # try next separator/encoding
                continue

    # As a last resort try pandas autodetect (may be slower)
    try:
        # fallback to python engine without low_memory when autodetecting
        return pd.read_csv(path, sep=None, engine="python", encoding="utf-8")
    except Exception as exc:
        last_exc = exc

    # Raise a more informative error
    msg = f"Impossible de lire {path}. Dernière erreur: {type(last_exc).__name__}: {last_exc}"
    raise RuntimeError(msg)

def ensure_table(conn: sqlite3.Connection, replace: bool = False):
    if replace:
        conn.execute(f"DROP TABLE IF EXISTS {TABLE};")
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE}(
            date TEXT,
            latitude REAL,
            longitude REAL,
            vitesse_mesuree REAL,
            limitation REAL
        );
    """)
    conn.commit()

def safe_to_sql(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    """
    Insert pandas -> SQLite avec un chunksize sûr
    pour éviter 'too many SQL variables'.
    """
    if df.empty:
        return 0
    ncols = df.shape[1] or 1
    chunksize = max(1, 900 // ncols)
    df.to_sql(TABLE, conn, if_exists="append", index=False,
              chunksize=chunksize, method="multi")
    return len(df)

def create_db_from_clean_csvs(csv_paths: list[str | Path],
                              db_path: str | Path = DB_PATH,
                              replace_table: bool = True) -> int:
    """
    Crée une base SQLite (vitesses.db) à partir de CSV déjà nettoyés.
    Chaque CSV doit contenir : date, position, vitesse_mesuree, limitation.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = OFF;")
        ensure_table(conn, replace=replace_table)

        for p in map(Path, csv_paths):
            if not p.exists():
                print(f"[WARN] Fichier introuvable : {p}")
                continue
            print(f"[INFO] Lecture de {p.name}")
            df = read_csv_any(p)
            print(f"   → {len(df):,} lignes lues")
            n = safe_to_sql(conn, df)
            print(f"   ✅ {n:,} lignes insérées dans {TABLE}")
            total += n

        conn.execute("PRAGMA synchronous = NORMAL;")
        check = pd.read_sql(f"SELECT COUNT(*) AS n FROM {TABLE};", conn)["n"].iloc[0]
        print(f"[OK] {check:,} lignes totales dans {db_path}")

    print(f"✅ Total inséré : {total:,}")
    return total

# --- Exécution directe ---
if __name__ == "__main__":
    CSVs = [
        "data/cleaned/vitesse_2021_cleaned.csv",
        "data/cleaned/vitesse_2023_cleaned.csv",
    ]
    create_db_from_clean_csvs(CSVs, db_path=DB_PATH, replace_table=True)
