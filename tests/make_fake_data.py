"""Build small fake input files with the same layout as the real downloads,
so the pipeline can be tested without internet access."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(1)
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
data = root / "data"
(data / "csv").mkdir(parents=True, exist_ok=True)

GM = ["Bolton", "Bury", "Manchester", "Oldham", "Rochdale",
      "Salford", "Stockport", "Tameside", "Trafford", "Wigan"]
OTHER_METS = ["Leeds", "Liverpool", "Birmingham", "Newcastle upon Tyne", "Wirral", "Sefton",
              "St. Helens", "Knowsley", "Doncaster", "Barnsley", "Sheffield", "Rotherham",
              "Wakefield", "Bradford", "Kirklees", "Calderdale", "Sunderland", "Gateshead",
              "South Tyneside", "North Tyneside", "Dudley", "Sandwell", "Walsall", "Wolverhampton",
              "Coventry", "Solihull"]
MET_FORCE = {n: f for f, names in {
    "West Yorkshire": ["Leeds", "Wakefield", "Bradford", "Kirklees", "Calderdale"],
    "Merseyside": ["Liverpool", "Wirral", "Sefton", "St. Helens", "Knowsley"],
    "South Yorkshire": ["Doncaster", "Barnsley", "Sheffield", "Rotherham"],
    "Northumbria": ["Newcastle upon Tyne", "Sunderland", "Gateshead", "South Tyneside", "North Tyneside"],
    "West Midlands": ["Birmingham", "Dudley", "Sandwell", "Walsall", "Wolverhampton", "Coventry", "Solihull"],
}.items() for n in names}
DISTRICTS = [f"District {c}" for c in "ABCDEFGHIJKLMNOPQRST"]      # Lancashire, non-metropolitan
KENT = ["Kent Area 1", "Kent Area 2"]
GROUPS = ["Violence against the person", "Theft offences", "Public order offences",
          "Criminal damage and arson", "Drug offences", "Fraud offences"]
GROUP_SHARE = [0.42, 0.25, 0.11, 0.09, 0.05, 0.08]
YEARS = ["2020/21", "2021/22", "2022/23", "2023/24", "2024/25", "2025/26", "2026/27"]

areas = []   # (code, name, force, population, income_score)
for i, n in enumerate(GM, 1):
    areas.append((f"E08{i:06d}", n, "Greater Manchester", rng.integers(180, 590) * 1000, rng.uniform(0.15, 0.38)))
for i, n in enumerate(OTHER_METS, 11):
    areas.append((f"E08{i:06d}", n, MET_FORCE[n], rng.integers(150, 1100) * 1000, rng.uniform(0.18, 0.42)))
for i, n in enumerate(DISTRICTS, 1):
    areas.append((f"E07{i:06d}", n, "Lancashire", rng.integers(60, 150) * 1000, rng.uniform(0.08, 0.30)))
for i, n in enumerate(KENT, 50):
    areas.append((f"E07{i:06d}", n, "Kent", 120000, 0.15))

rows = []
for y_i, year in enumerate(YEARS):
    quarters = [1] if year == "2026/27" else [1, 2, 3, 4]
    for q in quarters:
        season = [1.05, 1.07, 0.97, 0.91][q - 1]
        trend = 1 - 0.03 * y_i
        missing = {"2025/26": [0.015, 0.023, 0.05, 0.155][q - 1], "2026/27": 0.84}.get(year, 0.004)
        gm_unassigned = 0
        for code, name, force, pop, inc in areas:
            rate = (40 + 180 * inc) / 4 * season * trend
            total = rng.poisson(rate * pop / 1000)
            if force == "Greater Manchester":
                moved = int(total * missing)
                gm_unassigned += moved
                total -= moved
            for g, s in zip(GROUPS, GROUP_SHARE):
                rows.append([year, q, force, name, f"{g} detail", g, g, "1", int(total * s)])
        for g, s in zip(GROUPS, GROUP_SHARE):
            rows.append([year, q, "Greater Manchester", "Unassigned Greater Manchester", f"{g} detail", g, g, "1",
                         int(gm_unassigned * s)])
            rows.append([year, q, "Greater Manchester", "Manchester Airport", f"{g} detail", g, g, "1", 80])
            rows.append([year, q, "Kent", "Unassigned Kent", f"{g} detail", g, g, "1", 3000])
            rows.append([year, q, "Gwent", "Newport", f"{g} detail", g, g, "1", 900])

cols = ["Financial Year", "Financial Quarter", "Police Force", "CSP Name", "Offence Description",
        "Offence Group", "Offence Subgroup", "Offence Code", "Offence Count"]
df = pd.DataFrame(rows, columns=cols)
for year in YEARS:
    df[df["Financial Year"] == year].to_csv(data / "csv" / f"prc_csp_tables-{year.replace('/', '_')}.csv", index=False)

pop_rows = []
for code, name, force, pop, inc in areas:
    if force == "Greater Manchester":
        for i, yr in enumerate(range(2020, 2026)):
            pop_rows.append([yr, name, code, int(pop * (1 + 0.01 * i))])
for i, yr in enumerate(range(2020, 2026)):
    pop_rows.append([yr, "England and Wales", "K04000001", int(59_400_000 * (1 + 0.009 * i))])
pd.DataFrame(pop_rows, columns=["DATE_NAME", "GEOGRAPHY_NAME", "GEOGRAPHY_CODE", "OBS_VALUE"]) \
    .to_csv(data / "population_gm.csv", index=False)

pd.DataFrame([[c, n, int(p * 1.04)] for c, n, f, p, _ in areas],
             columns=["code", "name", "population_2024"]).to_csv(data / "population_england_2024.csv", index=False)

iod = pd.DataFrame({
    "Local Authority District code (2024)": [a[0] for a in areas],
    "Local Authority District name (2024)": [a[1] for a in areas],
    "Income - Average rank ": rng.uniform(5000, 30000, len(areas)).round(2),
    "Income - Rank of average rank ": range(1, len(areas) + 1),
    "Income - Average score ": [round(a[4], 3) for a in areas],
    "Income - Rank of average score ": pd.Series([a[4] for a in areas]).rank(ascending=False).astype(int),
})
with pd.ExcelWriter(data / "iod2025_lad.xlsx") as xl:
    pd.DataFrame().to_excel(xl, sheet_name="Notes")
    iod.to_excel(xl, sheet_name="Income", index=False)
print(f"fake data written to {data}")
