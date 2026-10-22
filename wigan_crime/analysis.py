"""Stage 3: crime rates, Greater Manchester ranking, offence types and the
unassigned-crime check."""
import json

import pandas as pd

from . import config as C
from .download import POP_GM


def load_population():
    p = pd.read_csv(POP_GM).rename(columns=str.upper)
    p = p.rename(columns={"DATE_NAME": "pop_year", "GEOGRAPHY_NAME": "area", "OBS_VALUE": "population"})
    p = p[["pop_year", "area", "population"]]
    gm = (p[p["area"].isin(C.BOROUGHS)].groupby("pop_year")["population"]
          .sum().reset_index().assign(area="Greater Manchester"))
    return pd.concat([p, gm], ignore_index=True)


def by_area(df, extra=()):
    keys = ["year", *extra]
    parts = {
        C.FOCUS: df[df["csp"] == C.FOCUS],
        C.CONTROL: df[df["csp"] == C.CONTROL],
        "Greater Manchester": df[df["force"] == C.FORCE],     # whole force, incl. unassigned
        "England and Wales": df,
    }
    out = []
    for name, part in parts.items():
        t = part.groupby(keys)["count"].sum().reset_index()
        t["area"] = name
        out.append(t)
    return pd.concat(out, ignore_index=True)


def add_rate(t, pop):
    t = t.copy()
    t["pop_year"] = t["year"].str[:4].astype(int)
    t = t.merge(pop, on=["area", "pop_year"], how="left")
    t["rate_per_1000"] = (t["count"] / t["population"] * 1000).round(1)
    return t


def unassigned_share(df):
    gm = df[df["force"] == C.FORCE]
    total = gm.groupby("year")["count"].sum()
    un = gm[gm["csp"] == C.UNASSIGNED].groupby("year")["count"].sum().reindex(total.index).fillna(0)
    return pd.DataFrame({"gm_total": total.astype(int), "unassigned": un.astype(int),
                         "unassigned_pct": (un / total * 100).round(1)})


def borough_table(df, year, pop, share_out_unassigned=False):
    gm = df[(df["force"] == C.FORCE) & (df["year"] == year)]
    by_csp = gm.groupby("csp")["count"].sum()
    recorded = by_csp.reindex(C.BOROUGHS).fillna(0)
    count = recorded
    if share_out_unassigned:
        # Share unassigned crimes out in proportion to each borough's recorded crime
        count = (recorded + by_csp.get(C.UNASSIGNED, 0) * recorded / recorded.sum()).round()
    t = pd.DataFrame({"area": C.BOROUGHS, "recorded": recorded.values,
                      "count": count.values, "year": year})
    t = add_rate(t, pop).sort_values("rate_per_1000", ascending=False)
    t["rank"] = range(1, len(t) + 1)
    return t


def run():
    df = pd.read_csv(C.OUT / "crime_by_group.csv")
    pop = load_population()

    share = unassigned_share(df)
    share.to_csv(C.OUT / "unassigned_share.csv")

    quarters = df.groupby("year")["quarter"].nunique()
    full_years = sorted(quarters[quarters == 4].index)
    reliable = [y for y in full_years if share.loc[y, "unassigned_pct"] <= C.MAX_UNASSIGNED_PCT]
    unreliable = [y for y in full_years if y not in reliable]
    latest = reliable[-1]

    # Annual rates per 1,000
    annual = df[df["year"].isin(full_years)]
    rates = add_rate(by_area(annual), pop)
    rates["reliable"] = rates["year"].isin(reliable)
    rates.to_csv(C.OUT / "annual_rates_long.csv", index=False)
    rates.pivot(index="area", columns="year", values="rate_per_1000").loc[C.AREAS] \
        .to_csv(C.OUT / "annual_rates.csv")

    # Greater Manchester ranking, latest reliable year
    rank = borough_table(df, latest, pop)
    rank[["rank", "area", "count", "population", "rate_per_1000"]].to_csv(
        C.OUT / "gm_ranking.csv", index=False)

    # Offence groups, latest reliable year
    groups = add_rate(by_area(df[df["year"] == latest], ["group"]), pop)
    groups.to_csv(C.OUT / "offence_groups_long.csv", index=False)
    g = groups.pivot(index="group", columns="area", values="rate_per_1000")[C.AREAS]
    g["Wigan vs E&W"] = (g[C.FOCUS] / g["England and Wales"]).round(2)
    g.sort_values(C.FOCUS, ascending=False).to_csv(C.OUT / "offence_groups.csv")

    # Estimates for unreliable full years (unassigned crimes shared out)
    for year in unreliable:
        est = borough_table(df, year, pop, share_out_unassigned=True)
        est[["rank", "area", "recorded", "count", "population", "rate_per_1000"]].to_csv(
            C.OUT / f"gm_ranking_estimate_{year.replace('/', '_')}.csv", index=False)

    summary = {"full_years": full_years, "reliable_years": reliable,
               "unreliable_years": unreliable, "latest_reliable": latest}
    (C.OUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"  reliable years: {reliable[0]} to {latest}; estimated: {unreliable or 'none'}")
