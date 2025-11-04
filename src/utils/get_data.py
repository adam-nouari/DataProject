from pathlib import Path
import requests
from tqdm import tqdm

RESOURCES = {
    "2021": "8b6cd190-3b66-43a8-b609-ce130019069f",  # CSV listé sur la page Data.gouv
    "2023": "52200d61-5e80-4a4e-999f-6e1c184fa122",  # CSV listé sur la page Data.gouv
}

BASE_URL = "https://www.data.gouv.fr/api/1/datasets/r/"
OUT_DIR = Path("data/raw")

def download(resource_id: str, out_path: Path) -> None:
    url = f"{BASE_URL}{resource_id}"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        with open(out_path, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc=out_path.name
        ) as bar:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

def main():
    for year, rid in RESOURCES.items():
        filename = f"vitesse_{year}.csv"
        out_path = OUT_DIR / filename
        print(f"[INFO] Téléchargement {year} -> {out_path}")
        download(rid, out_path)
    print("[OK] Fichiers téléchargés dans data/raw/")

if __name__ == "__main__":
    main()