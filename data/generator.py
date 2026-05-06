"""Synthetic data generator. Calibrated against Jun 2025 BI benchmark, anchored to May 2026.

v2: 5-dimension satisfaction model (Overall, Effort, Trust, Loyalty, Advokasi),
wilayah koordinasi, demografi (usia, jenis kelamin), comparison-period helpers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, date

from data import reference as R

RNG_SEED = 42

# Monthly volumes Jun 2025 → May 2026 (12 months); Jun 2025 = 7024 (matches benchmark)
MONTHLY_VOLUME = {
    "2025-06": 7024,
    "2025-07": 7320,
    "2025-08": 6890,
    "2025-09": 7150,
    "2025-10": 7480,
    "2025-11": 6710,
    "2025-12": 6420,
    "2026-01": 7080,
    "2026-02": 7860,
    "2026-03": 12480,
    "2026-04": 7240,
    "2026-05": 7024,
}

# Target top-2-box % per index — calibrated to research-director mockup
T2B_TARGETS = {
    "score_overall":  86.0,
    "score_effort":   78.0,
    "score_trust":    88.0,
    "score_loyalty":  82.0,
    "score_advokasi": 76.0,
}

INDEX_KEYS = ["overall", "effort", "trust", "loyalty", "advokasi"]
SCORE_COLS = [f"score_{k}" for k in INDEX_KEYS]
T2B_COLS = [f"t2b_{k}" for k in INDEX_KEYS]


def _likert_dist_for_t2b(t2b_target_pct: float) -> list[float]:
    """Return a 1..5 distribution that yields the requested top-2-box (4+5) percentage.
    Lower scores get small but realistic mass."""
    t2b = t2b_target_pct / 100.0
    rest = 1.0 - t2b
    # Distribute rest across [1, 2, 3] with most weight on 3 (netral)
    p1 = rest * 0.10
    p2 = rest * 0.22
    p3 = rest * 0.68
    # Within top-2-box: 5★ gets ~70% of the t2b mass, 4★ gets ~30%
    p5 = t2b * 0.70
    p4 = t2b * 0.30
    return [p1, p2, p3, p4, p5]


def _weighted_choice(rng: np.random.Generator, options, n: int):
    labels = [o[0] for o in options]
    weights = np.array([o[1] for o in options], dtype=float)
    weights /= weights.sum()
    return rng.choice(labels, size=n, p=weights)


def _province_weights():
    base = {
        "DKI Jakarta": 0.22, "Jawa Barat": 0.13, "Jawa Tengah": 0.10, "Jawa Timur": 0.11,
        "Banten": 0.05, "DI Yogyakarta": 0.03, "Bali": 0.03,
        "Sumatera Utara": 0.05, "Sumatera Barat": 0.02, "Sumatera Selatan": 0.025,
        "Riau": 0.018, "Lampung": 0.015, "Kalimantan Timur": 0.022, "Kalimantan Selatan": 0.014,
        "Kalimantan Barat": 0.012, "Sulawesi Selatan": 0.025, "Sulawesi Utara": 0.012,
        "Sulawesi Tengah": 0.008, "Aceh": 0.012, "Kepulauan Riau": 0.012,
        "Nusa Tenggara Barat": 0.012, "Nusa Tenggara Timur": 0.008,
        "Papua": 0.008, "Maluku": 0.005, "Bengkulu": 0.005, "Jambi": 0.008,
    }
    w = np.array([base[p] for p in R.PROVINCES])
    return w / w.sum()


def _age_weights_for_channel(channel: str) -> list[float]:
    """Digital channels skew younger; walk-in/visitor center skew older."""
    base = np.array([w for _, w in R.AGE_BRACKETS], dtype=float)
    if channel in ("Livechat", "Media Sosial"):
        bias = np.array([1.6, 1.4, 0.7, 0.5])
    elif channel in ("Visitor Center",):
        bias = np.array([0.5, 0.8, 1.3, 1.6])
    elif channel in ("Telepon",):
        bias = np.array([0.7, 1.0, 1.2, 1.3])
    else:
        bias = np.array([1.0, 1.0, 1.0, 1.0])
    w = base * bias
    return list(w / w.sum())


@st.cache_data(show_spinner=False)
def generate_tickets() -> pd.DataFrame:
    """Generate ~85k tickets across Jun 2025 → May 2026."""
    rng = np.random.default_rng(RNG_SEED)
    rows = []

    # Per-index distributions, computed once
    score_dists = {col: _likert_dist_for_t2b(t) for col, t in T2B_TARGETS.items()}

    for ym, total in MONTHLY_VOLUME.items():
        year, month = map(int, ym.split("-"))
        if month == 12:
            next_month = pd.Timestamp(year=year + 1, month=1, day=1)
        else:
            next_month = pd.Timestamp(year=year, month=month + 1, day=1)
        first = pd.Timestamp(year=year, month=month, day=1)
        days = pd.date_range(first, next_month - timedelta(days=1), freq="D")

        day_weights = np.array([1.0 if d.dayofweek < 5 else 0.35 for d in days])
        day_weights /= day_weights.sum()
        per_day = (day_weights * total).round().astype(int)
        per_day[0] += total - per_day.sum()

        for d, n in zip(days, per_day):
            if n <= 0:
                continue
            hours = rng.choice(
                np.arange(7, 19),
                size=n,
                p=np.array([0.04, 0.07, 0.13, 0.14, 0.11, 0.08, 0.10, 0.11, 0.09, 0.07, 0.04, 0.02]),
            )
            mins = rng.integers(0, 60, size=n)
            channels = _weighted_choice(rng, R.CHANNELS, n)
            topics = _weighted_choice(rng, R.TOPICS, n)
            classes = _weighted_choice(rng, R.CLASSIFICATIONS, n)
            requestors = _weighted_choice(rng, R.REQUESTORS, n)
            statuses = _weighted_choice(rng, R.STATUSES, n)
            provinces = rng.choice(R.PROVINCES, size=n, p=_province_weights())
            genders = _weighted_choice(rng, R.GENDERS, n)
            res_h = np.clip(rng.lognormal(mean=0.4, sigma=0.55, size=n), 0.05, 36.0)

            # Age depends on channel
            ages = np.array([
                rng.choice([a for a, _ in R.AGE_BRACKETS], p=_age_weights_for_channel(c))
                for c in channels
            ])

            # Five satisfaction scores per ticket — independent draws, calibrated to t2b targets
            scores = {
                col: rng.choice([1, 2, 3, 4, 5], size=n, p=dist)
                for col, dist in score_dists.items()
            }

            for i in range(n):
                rows.append((
                    pd.Timestamp(year=d.year, month=d.month, day=d.day, hour=int(hours[i]), minute=int(mins[i])),
                    channels[i], topics[i], classes[i], requestors[i],
                    statuses[i], provinces[i], float(res_h[i]),
                    int(scores["score_overall"][i]),
                    int(scores["score_effort"][i]),
                    int(scores["score_trust"][i]),
                    int(scores["score_loyalty"][i]),
                    int(scores["score_advokasi"][i]),
                    str(ages[i]), genders[i],
                ))

    df = pd.DataFrame(rows, columns=[
        "timestamp", "channel", "topic", "classification", "requestor",
        "status", "province", "resolution_h",
        "score_overall", "score_effort", "score_trust", "score_loyalty", "score_advokasi",
        "usia", "jenis_kelamin",
    ])
    df["wilayah"] = df["province"].map(R.PROVINCE_TO_WILAYAH)
    df["date"] = df["timestamp"].dt.date
    df["yearmonth"] = df["timestamp"].dt.strftime("%Y-%m")
    df["sla_met"] = df["resolution_h"] <= 4.0
    df["rejection_reason"] = np.where(
        df["status"] != "Dikabulkan",
        np.random.default_rng(RNG_SEED + 1).choice(R.REJECTION_REASONS, size=len(df)),
        "",
    )
    rng2 = np.random.default_rng(RNG_SEED + 2)
    n_unique_req = int(len(df) * 0.85)
    df["requestor_id"] = rng2.integers(1, n_unique_req + 1, size=len(df))
    df["is_repeat"] = df.duplicated(subset=["requestor_id"], keep="first")
    # Backwards-compat alias
    df["sxi_score"] = df["score_overall"]
    return df


@st.cache_data(show_spinner=False)
def generate_social() -> pd.DataFrame:
    """~50k social mentions across 12 months."""
    rng = np.random.default_rng(RNG_SEED + 10)
    rows = []
    for ym in MONTHLY_VOLUME.keys():
        year, month = map(int, ym.split("-"))
        n = int(rng.integers(3500, 5200))
        if ym == "2026-03":
            n = int(n * 1.6)
        first = pd.Timestamp(year=year, month=month, day=1)
        days_in = (pd.Timestamp(year=year, month=month % 12 + 1 if month < 12 else 1,
                                day=1) - first).days if month < 12 else 31
        if month == 12:
            days_in = 31

        for _ in range(n):
            day_offset = rng.integers(0, days_in)
            ts = first + timedelta(days=int(day_offset), hours=int(rng.integers(0, 24)))
            platform = rng.choice([p[0] for p in R.PLATFORMS], p=[p[1] for p in R.PLATFORMS])
            topic = rng.choice([t[0] for t in R.TOPICS], p=_norm([t[1] for t in R.TOPICS]))
            sentiment = rng.choice(
                list(R.SENTIMENT_DIST.keys()),
                p=list(R.SENTIMENT_DIST.values()),
            )
            engagement = int(rng.lognormal(mean=3.5, sigma=1.2))
            response_minutes = float(rng.lognormal(mean=3.5, sigma=0.8))
            rows.append((ts, platform, topic, sentiment, engagement, response_minutes))

    df = pd.DataFrame(rows, columns=[
        "timestamp", "platform", "topic", "sentiment", "engagement", "response_minutes",
    ])
    df["yearmonth"] = df["timestamp"].dt.strftime("%Y-%m")
    df["date"] = df["timestamp"].dt.date
    return df


def _norm(arr):
    a = np.array(arr, dtype=float)
    return a / a.sum()


# --- Top-2-Box and Likert helpers --------------------------------------

def top2box(scores) -> float:
    """Return % of scores ≥ 4 (Sangat Puas + Puas)."""
    s = pd.Series(scores)
    if len(s) == 0:
        return float("nan")
    return 100.0 * (s >= 4).mean()


def likert_distribution(scores) -> dict:
    """Return % at each Likert level. Keys: 'Sangat Puas', 'Puas', 'Netral', 'Tidak Puas', 'Sangat Tidak Puas'."""
    s = pd.Series(scores)
    total = max(len(s), 1)
    return {
        "Sangat Puas":       100.0 * (s == 5).sum() / total,
        "Puas":              100.0 * (s == 4).sum() / total,
        "Netral":            100.0 * (s == 3).sum() / total,
        "Tidak Puas":        100.0 * (s == 2).sum() / total,
        "Sangat Tidak Puas": 100.0 * (s == 1).sum() / total,
    }


# --- Monthly aggregations -----------------------------------------------

@st.cache_data(show_spinner=False)
def monthly_summary(tickets: pd.DataFrame) -> pd.DataFrame:
    """Roll up monthly KPIs. Adds Top-2-Box % per index."""
    g = tickets.groupby("yearmonth").agg(
        total=("timestamp", "size"),
        avg_resolution=("resolution_h", "mean"),
        sla_pct=("sla_met", lambda s: 100 * s.mean()),
    ).reset_index()
    # Top-2-Box per index
    for col in SCORE_COLS:
        t2b_col = "t2b_" + col.replace("score_", "")
        g[t2b_col] = (
            tickets.groupby("yearmonth")[col]
            .apply(lambda s: 100 * (s >= 4).mean())
            .reindex(g["yearmonth"])
            .values
        )
    # Backwards-compat aliases
    g["sxi_pct"] = g["t2b_overall"]
    g["sxi_score"] = (
        tickets.groupby("yearmonth")["score_overall"].mean().reindex(g["yearmonth"]).values
    )
    return g


@st.cache_data(show_spinner=False)
def monthly_social_summary(social: pd.DataFrame) -> pd.DataFrame:
    g = social.groupby("yearmonth").agg(
        total=("timestamp", "size"),
        avg_response_min=("response_minutes", "mean"),
    ).reset_index()
    sentiment_pivot = social.groupby(["yearmonth", "sentiment"]).size().unstack(fill_value=0)
    row_total = sentiment_pivot.sum(axis=1)
    sentiment_pivot["positif_pct"] = 100 * sentiment_pivot.get("Positif", 0) / row_total
    sentiment_pivot["netral_pct"] = 100 * sentiment_pivot.get("Netral", 0) / row_total
    sentiment_pivot["negatif_pct"] = 100 * sentiment_pivot.get("Negatif", 0) / row_total
    sentiment_pivot["ssi_pct"] = (
        sentiment_pivot["positif_pct"] + 0.5 * sentiment_pivot["netral_pct"]
    ).clip(0, 100)
    out = g.merge(
        sentiment_pivot[["positif_pct", "netral_pct", "negatif_pct", "ssi_pct"]].reset_index(),
        on="yearmonth",
    )
    return out


def label_ym(ym: str) -> str:
    year, month = ym.split("-")
    return f"{R.MONTH_ID[int(month) - 1]} {year[2:]}"


# --- Filtering -----------------------------------------------------------

def filter_tickets(tickets: pd.DataFrame, channels=None, topics=None, requestors=None,
                   provinces=None, wilayah=None, usia=None, gender=None,
                   date_range=None) -> pd.DataFrame:
    df = tickets
    if channels:
        df = df[df["channel"].isin(channels)]
    if topics:
        df = df[df["topic"].isin(topics)]
    if requestors:
        df = df[df["requestor"].isin(requestors)]
    if provinces:
        df = df[df["province"].isin(provinces)]
    if wilayah:
        df = df[df["wilayah"].isin(wilayah)]
    if usia:
        df = df[df["usia"].isin(usia)]
    if gender:
        df = df[df["jenis_kelamin"].isin(gender)]
    if date_range and len(date_range) == 2:
        start, end = date_range
        df = df[(df["timestamp"].dt.date >= start) & (df["timestamp"].dt.date <= end)]
    return df


# --- Comparison-period helpers ------------------------------------------

def _ymd_to_date(d) -> date:
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    return d


def previous_period(date_range: tuple) -> tuple:
    """Return the date range immediately preceding the given one, same length."""
    start, end = _ymd_to_date(date_range[0]), _ymd_to_date(date_range[1])
    span = (end - start).days + 1
    return (start - timedelta(days=span), start - timedelta(days=1))


def same_period_prior_year(date_range: tuple) -> tuple:
    """Return the same date range one year earlier."""
    start, end = _ymd_to_date(date_range[0]), _ymd_to_date(date_range[1])
    try:
        prev_start = date(start.year - 1, start.month, start.day)
        prev_end = date(end.year - 1, end.month, end.day)
    except ValueError:
        prev_start = start - timedelta(days=365)
        prev_end = end - timedelta(days=365)
    return (prev_start, prev_end)


def t2b_for_range(tickets: pd.DataFrame, date_range: tuple, score_col: str) -> float:
    """Top-2-Box % for the given date range (inclusive)."""
    if not date_range or len(date_range) != 2:
        return float("nan")
    start, end = _ymd_to_date(date_range[0]), _ymd_to_date(date_range[1])
    df = tickets[(tickets["timestamp"].dt.date >= start) & (tickets["timestamp"].dt.date <= end)]
    if len(df) == 0:
        return float("nan")
    return top2box(df[score_col])
