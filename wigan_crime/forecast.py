"""Stage 5: forecasting.

1. Single back-test: train 2021/22-2023/24, predict 2024/25 (three simple models)
2. Rolling-origin cross-validation of six Holt-Winters designs (data to March 2025 only)
3. Ensemble weight chosen on the same cross-validation
4. 2025/26 forecast (never shown 2025/26) checked against the complete GMP total
5. Two-year test at force level
6. Forward forecast to 2030/31, with the fitted models saved for reuse
"""
import json
import pickle
import warnings
from datetime import date

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from . import config as C
from .analysis import load_population

warnings.filterwarnings("ignore")


# ---- Models ------------------------------------------------------------------
def fit_hw(history, design):
    return ExponentialSmoothing(np.asarray(history, dtype=float), seasonal_periods=4,
                                initialization_method="estimated", **design).fit()


def hw_forecast(history, design, h):
    try:
        return np.asarray(fit_hw(history, design).forecast(h))
    except Exception:
        return np.full(h, np.nan)


def seasonal_naive(history, h):
    history = np.asarray(history, dtype=float)
    return np.resize(history[-4:], h)            # same quarter last year, repeated


def trend_season(history, h):
    # Straight-line trend plus one term per quarter (series must start in Q1)
    y = np.asarray(history, dtype=float)

    def design(t):
        return np.column_stack([t] + [(t % 4 == k).astype(float) for k in range(4)])

    beta, *_ = np.linalg.lstsq(design(np.arange(len(y))), y, rcond=None)
    return design(np.arange(len(y), len(y) + h)) @ beta


def ensemble(history, h, w):
    d, f = (hw_forecast(history, C.HW_DESIGNS[p], h) for p in C.ENSEMBLE_PARTS)
    return w * d + (1 - w) * f


def pct_errors(pred, actual):
    return (np.asarray(pred, dtype=float) / np.asarray(actual, dtype=float) - 1) * 100


def mape(pred, actual):
    return float(np.nanmean(np.abs(pct_errors(pred, actual))))


def hw_params(res):
    out = {}
    for k, v in res.params.items():
        if isinstance(v, np.ndarray):
            out[k] = [round(float(x), 6) for x in v]
        elif v is not None and not (isinstance(v, float) and np.isnan(v)):
            out[k] = round(float(v), 6) if not isinstance(v, bool) else v
    return out


# ---- Stage -------------------------------------------------------------------
def run():
    table = pd.read_csv(C.OUT / "gm_quarterly.csv", index_col="period")
    periods = list(table.index)

    def year_q(y):
        return [p for p in periods if p.startswith(y)]

    clean = [p for p in periods if C.TRAIN_FROM <= p[:7] < C.TARGET_YEAR]     # 16 quarters
    bt_test = year_q(C.BACKTEST_YEAR)
    bt_train = [p for p in clean if p < bt_test[0]]
    target = year_q(C.TARGET_YEAR)
    results = {"clean_quarters": [clean[0], clean[-1], len(clean)]}

    # 1. Single back-test
    rows = []
    for b in C.BOROUGHS:
        y, actual = table.loc[bt_train, b].values, table.loc[bt_test, b].values
        rows.append({"borough": b,
                     "Seasonal naive": mape(seasonal_naive(y, 4), actual),
                     "Trend + season": mape(trend_season(y, 4), actual),
                     "HW damped, add season": mape(hw_forecast(y, C.HW_DESIGNS["HW damped, add season"], 4), actual)})
    single = pd.DataFrame(rows).set_index("borough").round(1)
    single.loc["Average"] = single.mean().round(1)
    single.to_csv(C.OUT / "backtest_single.csv")

    # 2 and 3. Rolling-origin CV: every design, the baseline, and ensemble weights
    weights = np.round(np.arange(0, 1 + 1e-9, C.WEIGHT_GRID_STEP), 2)
    err = {b: {m: [] for m in ["Seasonal naive", *C.HW_DESIGNS]} for b in C.BOROUGHS}
    werr = {b: {w: [] for w in weights} for b in C.BOROUGHS}
    for b in C.BOROUGHS:
        y = table.loc[clean, b].values.astype(float)
        for n in C.CV_ORIGINS:
            h = min(4, len(y) - n)
            hist, actual = y[:n], y[n:n + h]
            preds = {"Seasonal naive": seasonal_naive(hist, h)}
            for name, design in C.HW_DESIGNS.items():
                preds[name] = hw_forecast(hist, design, h)
            for m, p in preds.items():
                err[b][m].extend(np.abs(pct_errors(p, actual)))
            d, f = (preds[p] for p in C.ENSEMBLE_PARTS)
            for w in weights:
                werr[b][w].extend(np.abs(pct_errors(w * d + (1 - w) * f, actual)))

    cv = pd.DataFrame({b: {m: np.nanmean(v) for m, v in err[b].items()} for b in C.BOROUGHS}).T
    cv_summary = pd.DataFrame({"average": cv.mean(), "median": cv.median(), "worst borough": cv.max(),
                               "boroughs won": cv.idxmin(axis=1).value_counts().reindex(cv.columns).fillna(0)}) \
        .sort_values("average")
    cv.round(1).to_csv(C.OUT / "cv_scores_by_borough.csv")
    cv_summary.round(2).to_csv(C.OUT / "cv_summary.csv")
    best = cv_summary.index[0] if cv_summary.index[0] != "Seasonal naive" else cv_summary.index[1]
    best_design = C.HW_DESIGNS[best]

    wcurve = pd.Series({w: np.mean([np.nanmean(werr[b][w]) for b in C.BOROUGHS]) for w in weights})
    wcurve.rename("average_error_pct").to_csv(C.OUT / "ensemble_weights.csv", index_label="weight_damped")
    weight = float(wcurve.idxmin())
    results.update({"best_single": best, "cv_best_average": round(float(cv_summary.loc[best, "average"]), 2),
                    "ensemble_weight_damped": weight, "ensemble_cv_error": round(float(wcurve.min()), 3),
                    "ensemble_cv_error_at_0.5": round(float(wcurve.loc[0.5]), 3)})

    # Single vs ensemble on the back-test year
    comp = []
    for b in C.BOROUGHS:
        y, actual = table.loc[bt_train, b].values, table.loc[bt_test, b].values
        for name, pred in [("Single", hw_forecast(y, best_design, 4)), ("Ensemble", ensemble(y, 4, weight))]:
            e = pct_errors(pred, actual)
            comp.append({"borough": b, "model": name, "error": np.abs(e).mean(), "bias": e.mean()})
    comp = pd.DataFrame(comp)
    comp.pivot(index="borough", columns="model", values="error").round(1).to_csv(C.OUT / "single_vs_ensemble_2024_25.csv")
    results["backtest_bias"] = comp.groupby("model")["bias"].mean().round(1).to_dict()

    # 4. 2025/26 forecast trained on clean quarters only
    train = clean
    fc_single = pd.DataFrame({b: hw_forecast(table.loc[train, b].values, best_design, 4) for b in C.BOROUGHS},
                             index=target).round()
    fc_ens = pd.DataFrame({b: ensemble(table.loc[train, b].values, 4, weight) for b in C.BOROUGHS},
                          index=target).round()
    fc_single.to_csv(C.OUT / "forecast_2025_26_quarterly.csv")
    fc_ens.to_csv(C.OUT / "forecast_2025_26_quarterly_ensemble.csv")
    test_models = {b: hw_params(fit_hw(table.loc[train, b].values, best_design)) for b in C.BOROUGHS}

    actual_total = table.loc[target].sum(axis=1) - table.loc[target, C.AIRPORT]
    recorded = table.loc[target, C.BOROUGHS].sum(axis=1)
    check = pd.DataFrame({"forecast_single": fc_single.sum(axis=1), "forecast_ensemble": fc_ens.sum(axis=1),
                          "actual_incl_unassigned": actual_total, "published_boroughs": recorded}).astype(int)
    check.loc["Year"] = check.sum()
    for c in ["forecast_single", "forecast_ensemble", "published_boroughs"]:
        check[f"{c}_error_%"] = pct_errors(check[c], check["actual_incl_unassigned"]).round(1)
    check.to_csv(C.OUT / "forecast_vs_actual_2025_26.csv")

    early = target[:2]
    q12 = pd.DataFrame({"single_%": pct_errors(fc_single.loc[early].sum(), table.loc[early, C.BOROUGHS].sum()),
                        "ensemble_%": pct_errors(fc_ens.loc[early].sum(), table.loc[early, C.BOROUGHS].sum())}).round(1)
    q12.to_csv(C.OUT / "forecast_q1_q2_boroughs.csv")
    results["q1_q2_mean_abs_error"] = q12.abs().mean().round(1).to_dict()

    pop = load_population().set_index(["area", "pop_year"])["population"]
    wpop = float(pop.loc[(C.FOCUS, int(C.TARGET_YEAR[:4]))])
    rec = table.loc[target, C.BOROUGHS].sum()
    prop = rec + table.loc[target, C.UNASSIGNED].sum() * rec / rec.sum()
    wig = {"recorded": rec[C.FOCUS], "single": fc_single[C.FOCUS].sum(),
           "ensemble": fc_ens[C.FOCUS].sum(), "proportional_estimate": prop[C.FOCUS]}
    results["wigan_2025_26"] = {k: {"crimes": round(float(v)), "rate": round(v / wpop * 1000, 1)} for k, v in wig.items()}

    # 5. Two-year test at force level: train to the year before the back-test year, predict 8 quarters
    total = table.drop(columns=[C.AIRPORT]).sum(axis=1)
    tr2 = [p for p in periods if C.TRAIN_FROM <= p[:7] < C.BACKTEST_YEAR]
    te2 = bt_test + target
    act2 = total.loc[te2].values
    two = {}
    for name, pred in [("single", hw_forecast(total.loc[tr2].values, best_design, 8)),
                       ("ensemble", ensemble(total.loc[tr2].values, 8, weight)),
                       ("seasonal_naive", seasonal_naive(total.loc[tr2].values, 8))]:
        e = pct_errors(pred, act2)
        two[name] = {"year1_error": round(float(np.abs(e[:4]).mean()), 1),
                     "year2_error": round(float(np.abs(e[4:]).mean()), 1),
                     "year1_bias": round(float(e[:4].mean()), 1), "year2_bias": round(float(e[4:].mean()), 1)}
    results["two_year_test"] = two

    # 6. Forward forecast from the complete force total, all quarters available
    y_all = total.values.astype(float)
    last = periods[-1]
    yy, qq = int(last[:4]), int(last[-1])
    future = []
    while (yy, qq) != C.FORECAST_TO:
        qq += 1
        if qq == 5:
            yy, qq = yy + 1, 1
        future.append(f"{yy}/{str(yy + 1)[2:]} Q{qq}")
    m_d = fit_hw(y_all, C.HW_DESIGNS[C.ENSEMBLE_PARTS[0]])
    m_f = fit_hw(y_all, C.HW_DESIGNS[C.ENSEMBLE_PARTS[1]])
    falling, flat = np.asarray(m_d.forecast(len(future))), np.asarray(m_f.forecast(len(future)))
    force_fc = weight * falling + (1 - weight) * flat

    shares = {}
    for y in sorted({p[:7] for p in clean}):
        rows = year_q(y)
        shares[y] = table.loc[rows, C.FOCUS].sum() / table.loc[rows, C.BOROUGHS].sum().sum()
    share = float(np.mean(list(shares.values())[-2:]))

    wp = pop.loc[C.FOCUS].sort_index()
    growth = float((wp.iloc[-1] / wp.iloc[0]) ** (1 / (len(wp) - 1)) - 1)

    fq = pd.DataFrame({"force_ensemble": force_fc, "force_falling": falling, "force_flat": flat}, index=future)
    for c in ["ensemble", "falling", "flat"]:
        fq[f"wigan_{c}"] = fq[f"force_{c}"] * share
    fq["year"] = [p[:7] for p in future]
    annual = fq.groupby("year").sum(numeric_only=True)
    known = [p for p in periods if p.startswith(future[0][:7])]
    if known:
        k = float(total.loc[known].sum())
        for c in ["ensemble", "falling", "flat"]:
            annual.loc[future[0][:7], f"force_{c}"] += k
            annual.loc[future[0][:7], f"wigan_{c}"] += k * share
    annual["wigan_population"] = [wp.iloc[-1] * (1 + growth) ** (int(y[:4]) - int(wp.index[-1])) for y in annual.index]
    band = np.array(C.BAND_PCT[:len(annual)]) / 100
    for c in ["ensemble", "falling", "flat"]:
        annual[f"rate_{c}"] = annual[f"wigan_{c}"] / annual["wigan_population"] * 1000
    annual["rate_low"] = annual["rate_ensemble"] * (1 - band)
    annual["rate_high"] = annual["rate_ensemble"] * (1 + band)
    annual["band_pct"] = band * 100
    annual["kind"] = ["forecast"] * 2 + ["scenario"] * (len(annual) - 2)
    stamp = date.today().isoformat()
    fq.round().to_csv(C.OUT / f"forecast_quarterly_issued_{stamp}.csv")
    annual.round(1).to_csv(C.OUT / "forward_forecast_annual.csv")
    annual.round(1).to_csv(C.OUT / f"forward_forecast_annual_issued_{stamp}.csv")

    # Save the fitted models and a model card so anyone can reuse or audit them
    with open(C.MODELS / "hw_damped_mult.pkl", "wb") as f:
        pickle.dump(m_d, f)
    with open(C.MODELS / "hw_no_trend_mult.pkl", "wb") as f:
        pickle.dump(m_f, f)
    card = {
        "issued": stamp,
        "target": "Greater Manchester Police recorded crime per quarter, all boroughs incl. unassigned, "
                  "excl. Manchester Airport and fraud",
        "training_quarters": [periods[0], periods[-1], len(periods)],
        "training_values": [int(v) for v in y_all],
        "ensemble": {"parts": list(C.ENSEMBLE_PARTS), "weight_damped": weight},
        "models": {C.ENSEMBLE_PARTS[0]: {"design": C.HW_DESIGNS[C.ENSEMBLE_PARTS[0]], "params": hw_params(m_d)},
                   C.ENSEMBLE_PARTS[1]: {"design": C.HW_DESIGNS[C.ENSEMBLE_PARTS[1]], "params": hw_params(m_f)}},
        "wigan_share": round(share, 5), "wigan_share_by_year": {k: round(float(v), 5) for k, v in shares.items()},
        "wigan_population_growth": round(growth, 5),
        "band_pct_by_year": C.BAND_PCT,
        "check_next": {"quarter": future[0], "forecast_force_total": round(float(force_fc[0]))},
        "test_models_2025_26": {"design": best, "params_by_borough": test_models},
    }
    (C.MODELS / "model_card.json").write_text(json.dumps(card, indent=2))

    results.update({"wigan_share": round(share, 4), "population_growth": round(growth, 4),
                    "next_check": card["check_next"]})
    (C.OUT / "forecast_results.json").write_text(json.dumps(results, indent=2, default=float))
    print(f"  best single model: {best}; ensemble weight {weight}; "
          f"2025/26 force error {check.loc['Year', 'forecast_single_error_%']}% (single)")
