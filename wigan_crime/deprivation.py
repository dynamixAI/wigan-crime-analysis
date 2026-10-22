"""Stage 4: is Wigan's crime higher than its deprivation predicts?

Uses the income domain of the English Indices of Deprivation 2025, not the
overall index, because the overall index contains a crime domain (circular)."""
import json
import re

import numpy as np
import pandas as pd
import statsmodels.api as sm

from . import config as C
from .download import IOD_XLSX, POP_ENG


def norm(name):
    # Make names comparable across files: lower case, '&' -> 'and',
    # drop 'City of' / 'County of', drop punctuation
    n = str(name).lower().replace("&", "and")
    n = re.sub(r",?\s*(city|county) of\b", "", n)
    n = re.sub(r"^(city|county) of\s+", "", n)
    return re.sub(r"[^a-z0-9]", "", n)


def build_areas():
    df = pd.read_csv(C.OUT / "crime_by_group.csv")
    df = df[(df["year"] == C.DEPRIVATION_YEAR) & ~df["force"].isin(C.WELSH_FORCES)]
    by_csp = df.groupby(["force", "csp"])["count"].sum().reset_index()
    by_csp["unassigned"] = by_csp["csp"].str.lower().str.startswith("unassigned")

    force_tot = by_csp.groupby("force")["count"].sum()
    force_assigned = by_csp[~by_csp["unassigned"]].groupby("force")["count"].sum()
    un_pct = ((1 - force_assigned / force_tot) * 100).round(1)
    excluded = un_pct[un_pct > C.DEPRIVATION_MAX_UNASSIGNED]

    areas = by_csp[~by_csp["unassigned"] & ~by_csp["force"].isin(excluded.index)].copy()
    # Share unassigned crime out within each force, in proportion to each area's count
    areas = areas.merge((force_tot / force_assigned).rename("scale"), left_on="force", right_index=True)
    areas["count"] = (areas["count"] * areas["scale"]).round()
    areas["area"] = areas["csp"].replace(C.MERGED)
    areas = areas.groupby(["force", "area"])["count"].sum().reset_index()
    areas["key"] = areas["area"].map(norm)

    imd = pd.read_excel(IOD_XLSX, sheet_name="Income").rename(columns=lambda c: str(c).strip())
    imd = imd.rename(columns={
        "Local Authority District code (2024)": "code",
        "Local Authority District name (2024)": "name",
        "Income - Average score": "income_score",
        "Income - Rank of average score": "income_rank",
    })[["code", "name", "income_score", "income_rank"]]
    pop = pd.read_csv(POP_ENG)[["code", "population_2024"]]
    lad = imd.merge(pop, on="code", how="left")
    lad["key"] = lad["name"].map(norm)

    merged = lad.merge(areas[["key", "force", "count"]], on="key", how="inner").drop(columns="key")
    merged["rate_per_1000"] = (merged["count"] / merged["population_2024"] * 1000).round(1)
    merged = merged[~merged["name"].isin(["City of London", "Isles of Scilly"])].copy()
    merged["income_pct"] = merged["income_score"] * 100
    merged.to_csv(C.OUT / "england_areas_analysis.csv", index=False)
    return merged, excluded, len(lad)


def expected_line(data):
    model = sm.OLS(data["rate_per_1000"], sm.add_constant(data["income_pct"])).fit()
    return model


def gap(model, df, name):
    row = df[df["name"] == name].iloc[0]
    expected = model.params.iloc[0] + model.params.iloc[1] * row["income_pct"]
    return expected, (row["rate_per_1000"] / expected - 1) * 100


def run():
    df, excluded, n_lad = build_areas()
    w = df[df["name"] == C.FOCUS].iloc[0]
    eng_rate = df["count"].sum() / df["population_2024"].sum() * 1000
    results = {"areas_analysed": int(len(df)), "areas_in_index": n_lad,
               "forces_excluded": excluded.to_dict(), "england_rate": round(eng_rate, 1),
               "wigan_rate": float(w["rate_per_1000"]), "wigan_income_pct": round(float(w["income_pct"]), 1)}

    # A: all areas. B: without the 10 highest-rate areas (city centres inflate per-resident rates)
    m_a = expected_line(df)
    top10 = df.nlargest(10, "rate_per_1000")["name"].tolist()
    m_b = expected_line(df[~df["name"].isin(top10)])
    for label, m in [("all_areas", m_a), ("without_top10", m_b)]:
        exp, g = gap(m, df, C.FOCUS)
        resid = df["rate_per_1000"] - m.predict(sm.add_constant(df["income_pct"]))
        results[label] = {"slope": round(float(m.params.iloc[1]), 2), "r2": round(float(m.rsquared), 2),
                          "wigan_expected": round(float(exp), 1), "wigan_gap_pct": round(float(g), 1),
                          "pct_areas_below_wigan": round(float((resid < w["rate_per_1000"] - exp).mean() * 100))}
    results["top10_removed"] = top10

    # Peers: the 15 areas closest to Wigan on income deprivation
    others = df[df["name"] != C.FOCUS].copy()
    others["distance"] = (others["income_pct"] - w["income_pct"]).abs()
    peers = others.nsmallest(15, "distance").sort_values("rate_per_1000", ascending=False)
    peers[["name", "force", "income_pct", "rate_per_1000"]].round(1).to_csv(C.OUT / "wigan_peers.csv", index=False)
    results["peer_median"] = round(float(peers["rate_per_1000"].median()), 1)

    # Force effects: median gap from line B for each force
    df["expected_b"] = m_b.predict(sm.add_constant(df["income_pct"]))
    df["vs_expected_b"] = (df["rate_per_1000"] / df["expected_b"] - 1) * 100
    df.groupby("force")["vs_expected_b"].median().round(1).sort_values(ascending=False) \
        .to_csv(C.OUT / "force_effects.csv")
    df[df["force"] == C.FORCE][["name", "income_pct", "rate_per_1000", "expected_b", "vs_expected_b"]] \
        .round(1).sort_values("vs_expected_b", ascending=False).to_csv(C.OUT / "gm_vs_expected.csv", index=False)

    # Like with like: the 36 metropolitan boroughs (codes starting E08), line without core cities
    met = df[df["code"].str.startswith("E08")].copy()
    m_met = expected_line(met[~met["name"].isin(C.CORE_CITIES)])
    met["expected"] = m_met.predict(sm.add_constant(met["income_pct"])).round(1)
    met["vs_expected_%"] = ((met["rate_per_1000"] / met["expected"] - 1) * 100).round(1)
    met = met.sort_values("vs_expected_%", ascending=False)
    met["rank"] = range(1, len(met) + 1)
    met.to_csv(C.OUT / "metropolitan_comparison.csv", index=False)
    wm = met[met["name"] == C.FOCUS].iloc[0]
    results["metropolitan"] = {"n": int(len(met)), "r2": round(float(m_met.rsquared), 2),
                               "slope": round(float(m_met.params.iloc[1]), 2),
                               "wigan_expected": float(wm["expected"]), "wigan_gap_pct": float(wm["vs_expected_%"]),
                               "wigan_rank": int(wm["rank"]),
                               "median_rate": round(float(met["rate_per_1000"].median()), 1)}

    (C.OUT / "deprivation_results.json").write_text(json.dumps(results, indent=2, default=float))
    print(f"  {results['areas_analysed']} areas; Wigan vs expected: all {results['all_areas']['wigan_gap_pct']:+}%, "
          f"metropolitan {results['metropolitan']['wigan_gap_pct']:+}% "
          f"(rank {results['metropolitan']['wigan_rank']} of {results['metropolitan']['n']})")
