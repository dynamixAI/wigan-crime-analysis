"""Stage 1: download the public data and record exactly what was downloaded."""
import hashlib
import json
import shutil
import subprocess
from datetime import date
from io import StringIO

import pandas as pd
import requests

from . import config as C

CRIME_ODS = C.DATA / "prc_csp_tables.ods"
IOD_XLSX = C.DATA / "iod2025_lad.xlsx"
POP_GM = C.DATA / "population_gm.csv"
POP_ENG = C.DATA / "population_england_2024.csv"
MANIFEST = C.DATA / "manifest.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url, path):
    print(f"  downloading {path.name}")
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    path.write_bytes(r.content)


def convert_ods_to_csv():
    # LibreOffice is far faster than pandas for a 50 MB ODS. The -1 at the end of the
    # filter string writes every sheet to its own CSV.
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise SystemExit("LibreOffice not found. Install it (e.g. sudo apt install libreoffice-calc).")
    for old in C.CSV_DIR.glob("*.csv"):
        old.unlink()
    print("  converting ODS to CSV with LibreOffice (a few minutes)")
    subprocess.run([
        soffice, "--headless", "--convert-to",
        "csv:Text - txt - csv (StarCalc):44,34,76,1,,0,false,true,false,false,false,-1",
        "--outdir", str(C.CSV_DIR), str(CRIME_ODS),
    ], check=True, capture_output=True)


def nomis(codes, years):
    rows = []
    for i in range(0, len(codes), 100):          # batches keep the URL short
        params = {
            "geography": ",".join(codes[i:i + 100]),
            "date": ",".join(str(y) for y in years),
            "gender": "0", "c_age": "200", "measures": "20100",
            "select": "date_name,geography_name,geography_code,obs_value",
        }
        r = requests.get(C.NOMIS_URL, params=params, timeout=120)
        r.raise_for_status()
        rows.append(pd.read_csv(StringIO(r.text)))
    return pd.concat(rows, ignore_index=True)


def run():
    C.ensure_dirs()
    fetch(C.CRIME_ODS_URL, CRIME_ODS)
    convert_ods_to_csv()
    fetch(C.IOD_URL, IOD_XLSX)

    print("  population: Greater Manchester boroughs and England and Wales")
    nomis(C.GM_CODES + [C.EW_CODE], C.POP_YEARS).to_csv(POP_GM, index=False)

    print("  population: all English local authorities, mid-2024")
    codes = pd.read_excel(IOD_XLSX, sheet_name="Income").iloc[:, 0].dropna().tolist()
    eng = nomis(codes, [2024])[["GEOGRAPHY_CODE", "GEOGRAPHY_NAME", "OBS_VALUE"]]
    eng.columns = ["code", "name", "population_2024"]
    eng.to_csv(POP_ENG, index=False)

    manifest = {
        "downloaded": date.today().isoformat(),
        "files": {
            p.name: {"sha256": sha256(p), "bytes": p.stat().st_size}
            for p in [CRIME_ODS, IOD_XLSX, POP_GM, POP_ENG]
        },
        "sources": {"crime": C.CRIME_ODS_URL, "deprivation": C.IOD_URL, "population": C.NOMIS_URL},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"  manifest written to {MANIFEST}")
