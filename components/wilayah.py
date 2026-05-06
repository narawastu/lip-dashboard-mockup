"""Wilayah Koordinasi helpers: trend-pattern classification + per-wilayah aggregation."""

from __future__ import annotations

import pandas as pd
import numpy as np

from data import generator as G
from data import reference as R


def wilayah_summary(tickets: pd.DataFrame, score_col: str = "score_overall") -> pd.DataFrame:
    """Top-2-Box per wilayah for a given score column."""
    rows = []
    for w in R.WILAYAH_NAMES:
        sub = tickets[tickets["wilayah"] == w]
        rows.append({
            "wilayah": w,
            "responden": len(sub),
            "t2b": G.top2box(sub[score_col]) if len(sub) else float("nan"),
        })
    return pd.DataFrame(rows)


def monthly_per_wilayah(tickets: pd.DataFrame, score_col: str = "score_overall") -> pd.DataFrame:
    """Wide DataFrame: rows = yearmonth, columns = wilayah, values = top-2-box %."""
    df = tickets.copy()
    out = (
        df.groupby(["yearmonth", "wilayah"])[score_col]
        .apply(lambda s: 100 * (s >= 4).mean())
        .reset_index(name="t2b")
    )
    pivot = out.pivot(index="yearmonth", columns="wilayah", values="t2b")
    return pivot.reindex(columns=R.WILAYAH_NAMES)


PATTERN_LABELS = {
    "naik_terus":   ("Naik Terus", "↗", "Tren naik konsisten dalam {n} bulan terakhir"),
    "naik_turun":   ("Naik → Turun", "↗→↘", "Naik di awal periode, turun di akhir"),
    "turun_naik":   ("Turun → Naik", "↘→↗", "Turun di awal periode, naik di akhir"),
    "turun_terus":  ("Turun Terus", "↘", "Tren turun konsisten dalam {n} bulan terakhir"),
    "datar":        ("Stabil", "→", "Tidak ada perubahan signifikan"),
}


def classify_trend_pattern(series: pd.Series, threshold_pp: float = 0.3) -> str:
    """Classify a recent trend into one of the 5 patterns.
    `series` should be the last N (typically 3) values for one wilayah."""
    vals = series.dropna().tolist()
    if len(vals) < 3:
        return "datar"
    # Compare deltas: vals[1] - vals[0], vals[2] - vals[1]
    d1 = vals[1] - vals[0]
    d2 = vals[2] - vals[1]
    up1 = d1 > threshold_pp
    up2 = d2 > threshold_pp
    down1 = d1 < -threshold_pp
    down2 = d2 < -threshold_pp
    if up1 and up2:
        return "naik_terus"
    if down1 and down2:
        return "turun_terus"
    if up1 and down2:
        return "naik_turun"
    if down1 and up2:
        return "turun_naik"
    return "datar"


def categorize_wilayah_trends(tickets: pd.DataFrame, score_col: str = "score_overall",
                              window: int = 3) -> dict:
    """Return {pattern_key: [wilayah_name, ...]} grouping each wilayah by its recent trend."""
    pivot = monthly_per_wilayah(tickets, score_col).tail(window)
    buckets = {k: [] for k in PATTERN_LABELS}
    for w in pivot.columns:
        pattern = classify_trend_pattern(pivot[w])
        buckets[pattern].append((w, pivot[w].tolist(), pivot[w].iloc[-1] if not pivot[w].empty else float("nan")))
    return buckets
