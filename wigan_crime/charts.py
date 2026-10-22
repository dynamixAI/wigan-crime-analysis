"""Stage 6: report charts (PNG, 200 dpi)."""
import json
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from . import config as C

COLOURS = {"Wigan": "#2a78d6", "Bolton": "#eb6834",
           "Greater Manchester": "#1baf7a", "England and Wales": "#eda100"}
EW_TEXT = "#8a6100"        # darker yellow for readable text
FORECAST = "#6250d6"
GREY = "#b8b7b1"
TEXT = "#0b0b0b"
TEXT_SOFT = "#52514e"
SURFACE = "#fcfcfb"
GRID = "#e4e3df"
SOURCE = ("Source: Home Office police recorded crime by Community Safety Partnership; "
          "ONS mid-year population estimates. Excludes fraud. Analysis: Pius Ajamma")


def setup(figsize=(10, 6)):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID,
                         "axes.labelcolor": TEXT_SOFT, "xtick.color": TEXT_SOFT, "ytick.color": TEXT_SOFT,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=figsize, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def titles(fig, title, subtitle):
    # Shrink the title until it fits the width, so it never gets cut off
    size = 16
    t = fig.text(0.06, 0.95, title, fontsize=size, fontweight="bold", color=TEXT, ha="left")
    fig.canvas.draw()
    while t.get_window_extent().x1 > fig.bbox.width * 0.97 and size > 11:
        size -= 0.5
        t.set_fontsize(size)
        fig.canvas.draw()
    fig.text(0.06, 0.905, subtitle, fontsize=11, color=TEXT_SOFT, ha="left")


def footer(fig, note=""):
    fig.text(0.06, 0.02, (note + "\n" if note else "") + SOURCE, fontsize=8, color=TEXT_SOFT,
             ha="left", va="bottom")


def save(fig, name):
    fig.savefig(C.CHARTS / name, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)


def estimate_rates():
    files = sorted(C.OUT.glob("gm_ranking_estimate_*.csv"))
    return pd.read_csv(files[-1]).set_index("area")["rate_per_1000"] if files else pd.Series(dtype=float)


def chart1_trend():
    rates = pd.read_csv(C.OUT / "annual_rates.csv", index_col="area")
    est = estimate_rates()
    summary = json.loads((C.OUT / "analysis_summary.json").read_text())
    years = list(rates.columns)
    x = list(range(len(years)))
    last = len(years) - 1
    estimated = years[-1] in summary["unreliable_years"]

    fig, ax = setup()
    fig.subplots_adjust(left=0.08, right=0.76, top=0.84, bottom=0.17)
    ax.axvspan(-0.4, 2.4, color="#f0efec", zorder=0)
    ax.text(1, 61.5, "GMP recording improving\nafter 2020 inspection", ha="center", va="bottom",
            fontsize=9, color=TEXT_SOFT)
    for area, colour in COLOURS.items():
        v = rates.loc[area].tolist()
        if estimated and area in (C.FOCUS, C.CONTROL):
            ax.plot(x[:last], v[:last], color=colour, linewidth=2.2, marker="o", markersize=6, label=area)
            ax.plot([x[last - 1], x[last]], [v[last - 1], est[area]], color=colour, linewidth=2.2, linestyle="--")
            ax.plot(x[last], est[area], marker="o", markersize=8, markerfacecolor="white",
                    markeredgecolor=colour, markeredgewidth=2)
            end = est[area]
        else:
            ax.plot(x, v, color=colour, linewidth=2.2, marker="o", markersize=6, label=area)
            end = v[-1]
        ax.text(x[last] + 0.15, end, f"{area}  {end:.1f}", va="center", fontsize=10, fontweight="bold",
                color=EW_TEXT if area == "England and Wales" else colour, clip_on=False)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_xlim(-0.4, last + 0.4)
    ax.set_ylim(60, 135)
    ax.set_ylabel("Crimes per 1,000 residents")
    ax.legend(loc="upper right", frameon=False, fontsize=9, ncol=2)
    titles(fig, "Wigan's crime rate has fallen since 2021/22 and stays below Greater Manchester",
           f"Recorded crimes per 1,000 residents, {years[0]} to {years[-1]}")
    footer(fig, "Dashed lines and hollow markers: 2025/26 estimates for Wigan and Bolton "
                "(crimes with no borough recorded were shared out by borough share).")
    save(fig, "01_trend.png")


def chart2_ranking():
    summary = json.loads((C.OUT / "analysis_summary.json").read_text())
    year = summary["latest_reliable"]
    rank = pd.read_csv(C.OUT / "gm_ranking.csv").sort_values("rate_per_1000").reset_index(drop=True)
    rates = pd.read_csv(C.OUT / "annual_rates.csv", index_col="area")
    gm_avg, ew_avg = rates.loc["Greater Manchester", year], rates.loc["England and Wales", year]

    fig, ax = setup(figsize=(10, 6.5))
    fig.subplots_adjust(left=0.16, right=0.93, top=0.82, bottom=0.14)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.barh(rank["area"], rank["rate_per_1000"], height=0.65, zorder=2,
            color=[COLOURS["Wigan"] if a == C.FOCUS else GREY for a in rank["area"]])
    for value, label, colour, align, nudge in [(ew_avg, "England and Wales", EW_TEXT, "right", -1.5),
                                               (gm_avg, "Greater Manchester", COLOURS["Greater Manchester"], "left", 1.5)]:
        ax.axvline(value, color=colour, linewidth=1.5, linestyle="--", zorder=3)
        ax.text(value + nudge, len(rank) - 0.35, f"{label} {value:.1f}", ha=align, va="bottom",
                fontsize=9, color=colour, fontweight="bold")
    for i, row in rank.iterrows():
        w = row["area"] == C.FOCUS
        ax.text(row["rate_per_1000"] + 1.5, i, f"{row['rate_per_1000']:.1f}", va="center", fontsize=10,
                color=TEXT if w else TEXT_SOFT, fontweight="bold" if w else "normal", zorder=4,
                bbox=dict(boxstyle="round,pad=0.15", facecolor=SURFACE, edgecolor="none"))
    for tick in ax.get_yticklabels():
        if tick.get_text() == C.FOCUS:
            tick.set_color(COLOURS["Wigan"])
            tick.set_fontweight("bold")
    ax.set_xlim(0, rank["rate_per_1000"].max() * 1.12)
    ax.set_xlabel("Crimes per 1,000 residents")
    ax.tick_params(axis="y", length=0)
    pos = rank.index[rank["area"] == C.FOCUS][0] + 1
    ordinal = {1: "lowest", 2: "2nd lowest", 3: "3rd lowest"}.get(pos, f"{pos}th lowest")
    titles(fig, f"Wigan has the {ordinal} crime rate of Greater Manchester's 10 boroughs",
           f"Recorded crimes per 1,000 residents, {year} (latest year with reliable borough figures)")
    footer(fig)
    save(fig, "02_gm_ranking.png")


def chart3_offences():
    g = pd.read_csv(C.OUT / "offence_groups.csv", index_col="group")
    g["diff"] = (g[C.FOCUS] / g["England and Wales"] - 1) * 100
    g = g.sort_values("diff")
    y = list(range(len(g)))
    fig, ax = setup(figsize=(10, 7))
    fig.subplots_adjust(left=0.24, right=0.95, top=0.83, bottom=0.19)
    ax.grid(False)
    ax.barh(y, g["diff"], height=0.6, zorder=2,
            color=[COLOURS["Wigan"] if d > 0 else "#9ec5f4" for d in g["diff"]])
    ax.axvline(0, color=TEXT_SOFT, linewidth=1, zorder=3)
    for i, (_, r) in enumerate(g.iterrows()):
        d = r["diff"]
        pct = "same" if abs(d) < 0.5 else f"{d:+.0f}%"
        ax.text(d + (2 if d >= 0 else -2), i, f"{pct} · {r[C.FOCUS]:.1f} vs {r['England and Wales']:.1f}",
                va="center", ha="left" if d >= 0 else "right", fontsize=10, color=TEXT)
    ax.set_yticks(y)
    ax.set_yticklabels(["\n".join(textwrap.wrap(n, 24)) for n in g.index], fontsize=10)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(-75, 105)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.text(-3, -1.1, "← Lower in Wigan", ha="right", va="center", fontsize=10, color=TEXT_SOFT, fontweight="bold")
    ax.text(3, -1.1, "Higher in Wigan →", ha="left", va="center", fontsize=10, color=TEXT_SOFT, fontweight="bold")
    ax.set_ylim(-1.5, len(g) - 0.5)
    year = json.loads((C.OUT / "analysis_summary.json").read_text())["latest_reliable"]
    titles(fig, "Wigan: more violence and public order offences, less theft",
           f"Wigan compared with England and Wales, {year}. Labels: % difference · "
           "Wigan rate vs national rate (per 1,000)")
    footer(fig, "Violence and public order offences are the most sensitive to how thoroughly police record crime, "
                "so differences between forces partly reflect recording practice.")
    save(fig, "03_offence_types.png")


def chart4_deprivation():
    met = pd.read_csv(C.OUT / "metropolitan_comparison.csv")
    fig, ax = setup(figsize=(10, 7))
    fig.subplots_adjust(left=0.09, right=0.95, top=0.83, bottom=0.17)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    xs = np.array([met["income_pct"].min() - 1, met["income_pct"].max() + 1])
    slope, intercept = np.polyfit(met["income_pct"], met["expected"], 1)
    ax.plot(xs, intercept + slope * xs, color=TEXT_SOFT, linewidth=1.5, linestyle="--", zorder=1)
    lx = xs[0] + 0.2
    ax.text(lx, intercept + slope * lx + 6, "Expected for its\nlevel of deprivation", ha="left", va="bottom",
            fontsize=9, color=TEXT_SOFT)
    groups = [(met[met["force"] != C.FORCE], GREY, 60),
              (met[(met["force"] == C.FORCE) & (met["name"] != C.FOCUS)], COLOURS["Greater Manchester"], 70),
              (met[met["name"] == C.FOCUS], COLOURS["Wigan"], 180)]
    for data, colour, size in groups:
        ax.scatter(data["income_pct"], data["rate_per_1000"], s=size, color=colour, edgecolor=SURFACE,
                   linewidth=1.5, zorder=3)
    labels = {"Manchester": (-8, 0, "right"), "Leeds": (8, 0, "left"), "Doncaster": (8, 0, "left"),
              "Wirral": (8, 0, "left"), "Knowsley": (8, 0, "left"), "Bolton": (8, 0, "left"),
              "Sefton": (8, -2, "left"), "St. Helens": (8, -2, "left"), "Trafford": (8, 0, "left"),
              "Birmingham": (-8, 0, "right")}
    for name, (dx, dy, ha) in labels.items():
        row = met[met["name"] == name]
        if not row.empty:
            r = row.iloc[0]
            ax.annotate(name, (r["income_pct"], r["rate_per_1000"]), xytext=(dx, dy), textcoords="offset points",
                        ha=ha, va="center", fontsize=9, color=TEXT_SOFT)
    w = met[met["name"] == C.FOCUS].iloc[0]
    ax.annotate(f"Wigan  {w['rate_per_1000']:.1f}\n{w['vs_expected_%']:+.0f}% vs expected, "
                f"{int(w['rank'])}th of {len(met)}", (w["income_pct"], w["rate_per_1000"]), xytext=(-14, 26),
                textcoords="offset points", ha="right", va="bottom", fontsize=10, color=COLOURS["Wigan"],
                fontweight="bold", arrowprops=dict(arrowstyle="-", color=COLOURS["Wigan"], linewidth=1))
    ax.set_xlabel("Income deprivation (% of residents on low incomes)")
    ax.set_ylabel("Crimes per 1,000 residents")
    ax.legend(handles=[
        Line2D([], [], marker="o", linestyle="", markersize=10, color=COLOURS["Wigan"], label="Wigan"),
        Line2D([], [], marker="o", linestyle="", markersize=8, color=COLOURS["Greater Manchester"],
               label="Other Greater Manchester boroughs"),
        Line2D([], [], marker="o", linestyle="", markersize=8, color=GREY, label="Other metropolitan boroughs"),
    ], loc="upper left", frameon=False, fontsize=9)
    titles(fig, "Wigan's crime is close to what its deprivation predicts",
           f"England's {len(met)} metropolitan boroughs, {C.DEPRIVATION_YEAR}. "
           "Dots above the line have more crime than expected")
    footer(fig, "Deprivation: English Indices of Deprivation 2025, income domain.\n"
                "Expected line fitted without the five core cities (Manchester, Birmingham, Leeds, Liverpool, Newcastle).")
    save(fig, "04_deprivation.png")


def chart5a_test():
    table = pd.read_csv(C.OUT / "gm_quarterly.csv", index_col="period")
    table = table[table.index < f"{int(C.TARGET_YEAR[:4]) + 1}/"]
    actual = table.drop(columns=[C.AIRPORT]).sum(axis=1) / 1000
    published = table[C.BOROUGHS].sum(axis=1) / 1000
    fc = pd.read_csv(C.OUT / "forecast_2025_26_quarterly.csv", index_col=0).sum(axis=1) / 1000
    periods = list(table.index)
    x = {p: i for i, p in enumerate(periods)}
    test = list(fc.index)

    fig, ax = setup(figsize=(11, 6.5))
    fig.subplots_adjust(left=0.08, right=0.95, top=0.83, bottom=0.2)
    ax.axvspan(-0.5, x[test[0]] - 0.5, color="#f0efec", zorder=0)
    ax.text((x[test[0]] - 1) / 2, 98.5, "Model trained on these quarters only", ha="center", va="top",
            fontsize=9, color=TEXT_SOFT)
    ax.text((x[test[0]] + x[test[-1]]) / 2, 98.5, "Predicted without\nseeing this data", ha="center", va="top",
            fontsize=9, color=TEXT_SOFT)
    ax.plot([x[p] for p in periods], actual, color=COLOURS["Greater Manchester"], linewidth=2.4,
            marker="o", markersize=5, zorder=3)
    ax.plot([x[p] for p in test], published.loc[test], color=GREY, linewidth=2, linestyle="--",
            marker="o", markersize=5, zorder=2)
    ax.plot([x[p] for p in test], fc, color=FORECAST, linewidth=2.2, linestyle="--", marker="D",
            markersize=6, zorder=4)
    q4 = test[-1]
    ax.annotate(f"Jan–Mar {int(C.TARGET_YEAR[:4]) + 1}\nActual      {actual[q4]:.1f}k\n"
                f"Forecast   {fc[q4]:.1f}k\nPublished {published[q4]:.1f}k",
                xy=(x[q4], actual[q4] + 0.6), xytext=(x[q4] - 0.3, 92), ha="right", va="top", fontsize=9,
                color=TEXT, bbox=dict(boxstyle="round,pad=0.4", facecolor=SURFACE, edgecolor=GRID),
                arrowprops=dict(arrowstyle="-", color=TEXT_SOFT, linewidth=0.8))
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels([f"Q1\n{p[:7]}" if p.endswith("Q1") else p[-2:] for p in periods], fontsize=8)
    ax.set_xlim(-0.5, len(periods) - 0.5)
    ax.set_ylim(58, 100)
    ax.set_ylabel("Crimes per quarter (thousands)")
    ax.legend(handles=[
        Line2D([], [], color=COLOURS["Greater Manchester"], linewidth=2.4, marker="o", label="Actual GMP total (complete)"),
        Line2D([], [], color=FORECAST, linewidth=2.2, linestyle="--", marker="D", label="Forecast (data to March 2025 only)"),
        Line2D([], [], color=GREY, linewidth=2, linestyle="--", marker="o",
               label="Published borough figures (missing unassigned crimes)"),
    ], loc="lower left", frameon=False, fontsize=9)
    ye = (fc.sum() / actual.loc[test].sum() - 1) * 100
    pe = (published.loc[test].sum() / actual.loc[test].sum() - 1) * 100
    titles(fig, f"A model that never saw {C.TARGET_YEAR} was closer than the published figures",
           f"GMP borough crime by quarter. {C.TARGET_YEAR} forecast error {ye:+.1f}%, "
           f"published borough figures {pe:+.1f}%")
    footer(fig, "Forecast: Holt-Winters (damped trend, multiplicative seasonality) trained on 2021/22–2024/25. "
                "Actual total includes crimes with no borough recorded; excludes Manchester Airport.")
    save(fig, "05a_forecast_test.png")


def chart5b_forward():
    rates = pd.read_csv(C.OUT / "annual_rates.csv", index_col="area")
    est = estimate_rates()
    fc = pd.read_csv(C.OUT / "forward_forecast_annual.csv", index_col="year")
    hist_years = [y for y in rates.columns if C.TRAIN_FROM <= y < C.TARGET_YEAR]
    history = rates.loc[C.FOCUS, hist_years]
    est_year = C.TARGET_YEAR
    start = est.get(C.FOCUS, rates.loc[C.FOCUS, est_year])
    fut = list(fc.index)
    years = hist_years + [est_year] + fut
    x = {y: i for i, y in enumerate(years)}
    fx = [x[y] for y in fut]
    blue = COLOURS["Wigan"]

    fig, ax = setup(figsize=(11, 6.5))
    fig.subplots_adjust(left=0.08, right=0.84, top=0.83, bottom=0.17)
    ax.fill_between([x[est_year]] + fx, [start] + list(fc["rate_low"]), [start] + list(fc["rate_high"]),
                    color="#cde2fb", zorder=1, linewidth=0)
    for col, label in [("rate_flat", "If it levels off"), ("rate_falling", "If the fall continues")]:
        ax.plot([x[est_year]] + fx, [start] + list(fc[col]), color=GREY, linewidth=1.2, linestyle=":", zorder=2)
        ax.text(fx[-1] + 0.15, fc[col].iloc[-1], label, va="center", fontsize=9, color=TEXT_SOFT)
    ax.plot([x[y] for y in hist_years], history, color=blue, linewidth=2.4, marker="o", markersize=6, zorder=3)
    ax.plot([x[hist_years[-1]], x[est_year]], [history.iloc[-1], start], color=blue, linewidth=2.2,
            linestyle="--", zorder=3)
    ax.plot(x[est_year], start, marker="o", markersize=8, markerfacecolor="white", markeredgecolor=blue,
            markeredgewidth=2, zorder=4)
    ax.plot([x[est_year]] + fx, [start] + list(fc["rate_ensemble"]), color=blue, linewidth=2.2,
            linestyle="--", marker="o", markersize=5, markerfacecolor=SURFACE, zorder=3)
    for y in fut[:2]:
        r = fc.loc[y]
        ax.annotate(f"{r['rate_ensemble']:.1f}\n({r['rate_low']:.0f}–{r['rate_high']:.0f})", (x[y], r["rate_high"]),
                    xytext=(0, 6), textcoords="offset points", ha="center", va="bottom", fontsize=9, color=blue)
    ax.text(fx[-1] + 0.15, fc["rate_ensemble"].iloc[-1], f"Wigan {fc['rate_ensemble'].iloc[-1]:.1f}",
            va="center", fontsize=10, color=blue, fontweight="bold")
    top = 122
    ax.axvline(fx[0] - 0.5, color=GRID, linewidth=1, zorder=0)
    ax.axvline(fx[2] - 0.5, color=GRID, linewidth=1, zorder=0)
    for xpos, label in [((x[hist_years[0]] + x[est_year]) / 2, "Actual"), ((fx[0] + fx[1]) / 2, "Forecast"),
                        ((fx[2] + fx[-1]) / 2, "Scenarios (indicative)")]:
        ax.text(xpos, top, label, ha="center", fontsize=10, color=TEXT_SOFT, fontweight="bold")
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, fontsize=9)
    ax.set_xlim(-0.4, len(years) - 0.6)
    ax.set_ylim(60, 125)
    ax.set_ylabel("Crimes per 1,000 residents")
    card = json.loads((C.MODELS / "model_card.json").read_text())
    w = card["ensemble"]["weight_damped"]
    titles(fig, "Wigan's crime rate is expected to ease slowly",
           f"Recorded crimes per 1,000 residents: actual, {est_year} estimate, and forecast to {fut[-1]}")
    footer(fig, f"Forecast: {w:.0%}/{1 - w:.0%} ensemble of Holt-Winters damped-trend and no-trend models, GMP total × "
                f"Wigan's {card['wigan_share'] * 100:.1f}% share. Band: ±3% and ±7% (measured)\nfor years 1–2, then "
                f"widening ~4 points a year (indicative). Assumes Wigan's population grows "
                f"{card['wigan_population_growth'] * 100:.2f}% a year.")
    save(fig, "05b_forward.png")


def chart6_unassigned():
    share = pd.read_csv(C.OUT / "unassigned_share.csv", index_col="year")
    table = pd.read_csv(C.OUT / "gm_quarterly.csv", index_col="period")
    # Whole years before the problem began, then quarter by quarter from the target year
    years = [y for y in share.index if y < C.TARGET_YEAR]
    qs = [p for p in table.index if p >= C.TARGET_YEAR]
    labels = years + [f"{p[-2:]}\n{p[:7]}" for p in qs]
    vals = list(share.loc[years, "unassigned_pct"]) + \
        list((table.loc[qs, C.UNASSIGNED] / table.loc[qs].sum(axis=1) * 100).round(1))

    fig, ax = setup(figsize=(10, 6))
    fig.subplots_adjust(left=0.08, right=0.95, top=0.83, bottom=0.2)
    colours = [GREY] * len(years) + ["#e34948"] * len(qs)
    bars = ax.bar(range(len(vals)), vals, color=colours, width=0.65, zorder=2)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}%", ha="center", va="bottom", fontsize=9,
                color=TEXT)
    ax.axvline(len(years) - 0.5, color=GRID, linewidth=1)
    ax.text((len(years) - 1) / 2, 92, "By year", ha="center", fontsize=10, color=TEXT_SOFT, fontweight="bold")
    ax.text(len(years) + (len(qs) - 1) / 2, 92, "By quarter", ha="center", fontsize=10, color=TEXT_SOFT,
            fontweight="bold")
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of GMP crimes with no borough recorded")
    titles(fig, f"GMP crimes with no borough recorded rose from under 1% to {vals[-1]:.0f}% in a year",
           "Share of Greater Manchester Police recorded crime listed as 'Unassigned Greater Manchester'")
    footer(fig, "Total crime is unaffected, but borough figures from late 2025 are understated. "
                "The release notes do not mention this for Greater Manchester.")
    save(fig, "06_unassigned.png")


def run():
    C.CHARTS.mkdir(parents=True, exist_ok=True)
    for f in [chart1_trend, chart2_ranking, chart3_offences, chart4_deprivation,
              chart5a_test, chart5b_forward, chart6_unassigned]:
        f()
    print(f"  charts saved to {C.CHARTS}")
