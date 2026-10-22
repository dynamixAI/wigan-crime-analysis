"""Stage 2: turn the Home Office sheets into small tidy tables."""
import pandas as pd

from . import config as C

COLS = ["Financial Year", "Financial Quarter", "Police Force",
        "CSP Name", "Offence Group", "Offence Count"]


def load_crime():
    files = sorted(C.CSV_DIR.glob("*-20*.csv"))        # one CSV per financial year
    if not files:
        raise SystemExit(f"No yearly CSVs in {C.CSV_DIR}. Run the download stage first.")
    df = pd.concat((pd.read_csv(f, usecols=COLS, dtype=str) for f in files), ignore_index=True)
    df.columns = ["year", "quarter", "force", "csp", "group", "count"]
    for c in ["year", "force", "csp", "group"]:
        df[c] = df[c].str.strip()
    df["quarter"] = pd.to_numeric(df["quarter"], errors="coerce").astype(int)
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0)
    # Fraud is mostly recorded by Action Fraud, not local police, so it is left out
    df = df[~df["group"].str.contains("fraud", case=False, na=False)]
    return df


def run():
    df = load_crime()
    print(f"  {len(df):,} offence rows after removing fraud")

    # Data quality checks reported in the methodology
    checks = {
        "rows": int(len(df)),
        "negative_rows": int((df["count"] < 0).sum()),
    }

    by_group = df.groupby(["year", "quarter", "force", "csp", "group"])["count"].sum().reset_index()
    by_group.to_csv(C.OUT / "crime_by_group.csv", index=False)

    # Quarterly table for Greater Manchester: one row per quarter, one column per area
    gm = by_group[(by_group["force"] == C.FORCE) & (by_group["year"] >= C.TRAIN_FROM)]
    q = gm.groupby(["year", "quarter", "csp"])["count"].sum().reset_index()
    q["period"] = q["year"] + " Q" + q["quarter"].astype(str)
    table = q.pivot(index="period", columns="csp", values="count").fillna(0).astype(int).sort_index()
    table.to_csv(C.OUT / "gm_quarterly.csv")

    clean_rows = [p for p in table.index if C.TRAIN_FROM <= p[:7] < C.TARGET_YEAR]
    clean = table.loc[clean_rows, C.BOROUGHS]
    checks["clean_borough_quarters"] = int(clean.size)
    checks["clean_borough_quarters_zero_or_negative"] = int((clean <= 0).sum().sum())
    pd.Series(checks).to_csv(C.OUT / "data_checks.csv", header=["value"])
    print(f"  quarterly table: {table.shape[0]} quarters x {table.shape[1]} areas")
