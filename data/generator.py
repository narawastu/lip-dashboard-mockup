"""Synthetic data generator. Calibrated against Jun 2025 BI benchmark, anchored to May 2026."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

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
    "2026-03": 12480,  # Q1 spike (echo of the benchmark Mar 2025 anomaly, smaller)
    "2026-04": 7240,
    "2026-05": 7024,
}


def _weighted_choice(rng: np.random.Generator, options, n: int):
    labels = [o[0] for o in options]
    weights = np.array([o[1] for o in options], dtype=float)
    weights /= weights.sum()
    return rng.choice(labels, size=n, p=weights)


@st.cache_data(show_spinner=False)
def generate_tickets() -> pd.DataFrame:
    """Generate ~85k tickets across Jun 2025 → May 2026."""
    rng = np.random.default_rng(RNG_SEED)
    rows = []

    for ym, total in MONTHLY_VOLUME.items():
        year, month = map(int, ym.split("-"))
        # Distribute across days with weekly seasonality
        if month == 12:
            next_month = pd.Timestamp(year=year + 1, month=1, day=1)
        else:
            next_month = pd.Timestamp(year=year, month=month + 1, day=1)
        first = pd.Timestamp(year=year, month=month, day=1)
        days = pd.date_range(first, next_month - timedelta(days=1), freq="D")

        # Weight: weekday > weekend
        day_weights = np.array([1.0 if d.dayofweek < 5 else 0.35 for d in days])
        day_weights /= day_weights.sum()
        per_day = (day_weights * total).round().astype(int)
        # Adjust drift to match exactly
        diff = total - per_day.sum()
        per_day[0] += diff

        for d, n in zip(days, per_day):
            if n <= 0:
                continue
            # Hour distribution: peak 09–11 and 13–15
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

            # Resolution time (hours): log-normal mean ~1.9
            res_h = rng.lognormal(mean=0.4, sigma=0.55, size=n)  # median ~1.5h, mean ~1.9h
            res_h = np.clip(res_h, 0.05, 36.0)

            # SXI score per ticket (1–5), weighted high to give ~95–96% (matches Jun 2025 benchmark)
            score = rng.choice([1, 2, 3, 4, 5], size=n, p=[0.001, 0.005, 0.02, 0.10, 0.874])

            for i in range(n):
                rows.append((
                    pd.Timestamp(year=d.year, month=d.month, day=d.day, hour=int(hours[i]), minute=int(mins[i])),
                    channels[i],
                    topics[i],
                    classes[i],
                    requestors[i],
                    statuses[i],
                    provinces[i],
                    float(res_h[i]),
                    int(score[i]),
                ))

    df = pd.DataFrame(rows, columns=[
        "timestamp", "channel", "topic", "classification", "requestor",
        "status", "province", "resolution_h", "sxi_score",
    ])
    df["date"] = df["timestamp"].dt.date
    df["yearmonth"] = df["timestamp"].dt.strftime("%Y-%m")
    df["sla_met"] = df["resolution_h"] <= 4.0  # 4h SLA target
    df["rejection_reason"] = np.where(
        df["status"] != "Dikabulkan",
        np.random.default_rng(RNG_SEED + 1).choice(R.REJECTION_REASONS, size=len(df)),
        "",
    )
    # Repeat-inquiry flag — fake requestor IDs, ~15% repeat
    rng2 = np.random.default_rng(RNG_SEED + 2)
    n_unique_req = int(len(df) * 0.85)
    df["requestor_id"] = rng2.integers(1, n_unique_req + 1, size=len(df))
    df["is_repeat"] = df.duplicated(subset=["requestor_id"], keep="first")
    return df


def _province_weights():
    # Java-heavy distribution
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


@st.cache_data(show_spinner=False)
def generate_social() -> pd.DataFrame:
    """~50k social mentions across 12 months."""
    rng = np.random.default_rng(RNG_SEED + 10)
    rows = []
    for ym in MONTHLY_VOLUME.keys():
        year, month = map(int, ym.split("-"))
        n = int(rng.integers(3500, 5200))  # ~50k total
        if ym == "2026-03":
            n = int(n * 1.6)  # echo the spike
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


@st.cache_data(show_spinner=False)
def monthly_summary(tickets: pd.DataFrame) -> pd.DataFrame:
    """Roll up monthly KPIs."""
    g = tickets.groupby("yearmonth").agg(
        total=("timestamp", "size"),
        avg_resolution=("resolution_h", "mean"),
        sla_pct=("sla_met", lambda s: 100 * s.mean()),
        sxi_score=("sxi_score", "mean"),
    ).reset_index()
    # Convert SXI 1–5 into a percentage (5 = 100%, calibrated to land near 95–96%)
    g["sxi_pct"] = ((g["sxi_score"] - 1) / 4 * 100).clip(0, 100)
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
    # SSI: % positif + 0.5 * netral (a common sentiment-index formula)
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


def filter_tickets(tickets: pd.DataFrame, channels=None, topics=None, requestors=None,
                   provinces=None, date_range=None) -> pd.DataFrame:
    df = tickets
    if channels:
        df = df[df["channel"].isin(channels)]
    if topics:
        df = df[df["topic"].isin(topics)]
    if requestors:
        df = df[df["requestor"].isin(requestors)]
    if provinces:
        df = df[df["province"].isin(provinces)]
    if date_range and len(date_range) == 2:
        start, end = date_range
        df = df[(df["timestamp"].dt.date >= start) & (df["timestamp"].dt.date <= end)]
    return df
