"""Settings for the whole pipeline. Change things here, not in the stage files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CSV_DIR = DATA / "csv"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
MODELS = ROOT / "models"

# ---- Sources (pinned to the versions used in the report) --------------------
# Home Office police recorded crime, Community Safety Partnership open data tables,
# year ending March 2021 to year ending June 2026 (release of 22 October 2026).
# gov.uk sometimes replaces files in place; the download step records a SHA-256
# checksum in data/manifest.json so you can tell if your copy differs.
CRIME_ODS_URL = ("https://assets.publishing.service.gov.uk/media/6a5f8ab4f869f6a53d0c898e/"
                 "prc-csp-mar2021-mar2026-tables-230726.ods")

# English Indices of Deprivation 2025, File 10 (local authority summaries), v2
IOD_URL = ("https://assets.publishing.service.gov.uk/media/6917412ebc34c86ce4e6e7fc/"
           "File_10_-_IoD2025_Local_Authority_District_Summaries__lower-tier__v2.xlsx")

# ONS mid-year population estimates via Nomis (dataset NM_2002_1)
NOMIS_URL = "https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1.data.csv"

# ---- Areas -------------------------------------------------------------------
FORCE = "Greater Manchester"
BOROUGHS = ["Bolton", "Bury", "Manchester", "Oldham", "Rochdale",
            "Salford", "Stockport", "Tameside", "Trafford", "Wigan"]
GM_CODES = [f"E08{n:06d}" for n in range(1, 11)]       # E08000001 Bolton ... E08000010 Wigan
EW_CODE = "K04000001"                                  # England and Wales
UNASSIGNED = "Unassigned Greater Manchester"
AIRPORT = "Manchester Airport"
FOCUS = "Wigan"
CONTROL = "Bolton"
AREAS = [FOCUS, CONTROL, "Greater Manchester", "England and Wales"]
WELSH_FORCES = ["Dyfed-Powys", "Gwent", "North Wales", "South Wales"]

# ---- Analysis rules ----------------------------------------------------------
POP_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]       # mid-year N matches financial year N/N+1
MAX_UNASSIGNED_PCT = 2.0          # a year is reliable for borough comparison below this
DEPRIVATION_MAX_UNASSIGNED = 5.0  # looser rule for the England-wide comparison
DEPRIVATION_YEAR = "2024/25"
CORE_CITIES = ["Manchester", "Birmingham", "Leeds", "Liverpool", "Newcastle upon Tyne"]

# Old district names in the crime file -> the council they merged into
MERGED = {
    "Aylesbury Vale": "Buckinghamshire", "Chiltern": "Buckinghamshire",
    "South Bucks": "Buckinghamshire", "Wycombe": "Buckinghamshire",
    "Corby": "North Northamptonshire", "East Northamptonshire": "North Northamptonshire",
    "Kettering": "North Northamptonshire", "Wellingborough": "North Northamptonshire",
    "Northampton": "West Northamptonshire",
    "Daventry and South Northamptonshire": "West Northamptonshire",
    "Suffolk Coastal": "East Suffolk", "Waveney": "East Suffolk",
}

# ---- Forecasting -------------------------------------------------------------
TRAIN_FROM = "2021/22"            # skips 2020/21 (Covid lockdowns, GMP under-recording)
BACKTEST_YEAR = "2024/25"
TARGET_YEAR = "2025/26"
CV_ORIGINS = range(10, 16)        # train on first n of 16 clean quarters, predict up to 4 ahead
WEIGHT_GRID_STEP = 0.05
FORECAST_TO = (2030, 4)           # last quarter to forecast: 2030/31 Q4
BAND_PCT = [3, 7, 11, 15, 19]     # yearly band: measured for years 1-2, then indicative

HW_DESIGNS = {
    "HW no trend, add season":  dict(trend=None,  damped_trend=False, seasonal="add"),
    "HW no trend, mult season": dict(trend=None,  damped_trend=False, seasonal="mul"),
    "HW trend, add season":     dict(trend="add", damped_trend=False, seasonal="add"),
    "HW damped, add season":    dict(trend="add", damped_trend=True,  seasonal="add"),
    "HW trend, mult season":    dict(trend="add", damped_trend=False, seasonal="mul"),
    "HW damped, mult season":   dict(trend="add", damped_trend=True,  seasonal="mul"),
}
# The two models combined in the ensemble
ENSEMBLE_PARTS = ("HW damped, mult season", "HW no trend, mult season")


def ensure_dirs():
    for d in [DATA, CSV_DIR, OUT, CHARTS, MODELS]:
        d.mkdir(parents=True, exist_ok=True)
