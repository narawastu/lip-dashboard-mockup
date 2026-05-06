"""Compose a poster-style infographic from selected metrics.

Pillow is the canvas; Plotly + Kaleido renders individual charts to PNG bytes.
Returns (png_bytes, pdf_bytes).
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import theme as T
from data import generator as G, reference as R
from components import charts as C


W, H = 1080, 2000
NAVY = (0, 47, 108)
NAVY_DEEP = (0, 26, 71)
NAVY_SOFT = (31, 78, 145)
GOLD = (201, 162, 39)
RED = (230, 0, 18)
INK = (15, 23, 42)
MUTED = (71, 85, 105)
BORDER = (226, 232, 240)
SURFACE = (255, 255, 255)
BG = (246, 248, 251)
POS = (22, 163, 74)
NEG = (220, 38, 38)


@dataclass
class PosterSelection:
    title: str = "Laporan Layanan Informasi Publik"
    period: str = R.CURRENT_PERIOD_LABEL
    show_header: bool = True
    show_kpi_sxi: bool = True
    show_kpi_ssi: bool = True
    show_kpi_total: bool = True
    show_kpi_resolution: bool = True
    show_hot_topics: bool = True
    show_trend: bool = True
    show_channels_donut: bool = True
    show_classification_donut: bool = True
    show_requestor_donut: bool = True
    show_sentiment: bool = True
    show_footer: bool = True
    theme_mode: str = "Navy"  # Navy | Light | Dark


# --- Font loading ---------------------------------------------------------

def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Load Inter via system fonts; fallback to default if missing."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# --- Plotly → PNG helper --------------------------------------------------

def _fig_to_png(fig: go.Figure, width: int, height: int) -> Image.Image:
    """Render Plotly figure to PIL image via kaleido, resized to exact target dimensions."""
    fig.update_layout(width=width, height=height, paper_bgcolor="white", plot_bgcolor="white")
    img_bytes = fig.to_image(format="png", scale=2)
    img = Image.open(io.BytesIO(img_bytes))
    # Kaleido at scale=2 gives 2x image — resize back to target
    if img.size != (width, height):
        img = img.resize((width, height), Image.LANCZOS)
    return img.convert("RGB")


# --- Drawing primitives ---------------------------------------------------

def _rounded_rect(draw: ImageDraw.ImageDraw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def _text(draw: ImageDraw.ImageDraw, xy, text, font, fill=INK, anchor="la"):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def _gradient_band(width, height, top_color, bottom_color):
    """Vertical gradient band."""
    band = Image.new("RGB", (width, height), top_color)
    pixels = band.load()
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    return band


# --- Poster sections ------------------------------------------------------

def _draw_header(canvas: Image.Image, sel: PosterSelection) -> int:
    """Draw the navy gradient header. Returns y after header."""
    band_h = 240
    band = _gradient_band(W, band_h, NAVY_DEEP, NAVY_SOFT)
    canvas.paste(band, (0, 0))
    draw = ImageDraw.Draw(canvas)

    # Logo block
    logo_size = 72
    logo_x, logo_y = 64, 60
    _rounded_rect(draw, (logo_x, logo_y, logo_x + logo_size, logo_y + logo_size), 14, fill="white")
    _text(draw, (logo_x + logo_size // 2, logo_y + logo_size // 2 - 2), "BI",
          _font(34, bold=True), fill=NAVY, anchor="mm")

    # Title
    _text(draw, (logo_x + logo_size + 22, 70), "BANK INDONESIA",
          _font(15, bold=True), fill=(255, 255, 255, 200), anchor="la")
    _text(draw, (logo_x + logo_size + 22, 92), sel.title, _font(30, bold=True), fill="white", anchor="la")
    _text(draw, (logo_x + logo_size + 22, 138), f"Periode: {sel.period}",
          _font(18), fill=(220, 230, 245), anchor="la")

    # Period chip top right
    chip_text = sel.period.upper()
    chip_font = _font(15, bold=True)
    bbox = draw.textbbox((0, 0), chip_text, font=chip_font)
    chip_w = bbox[2] - bbox[0] + 36
    chip_h = 38
    chip_x = W - 64 - chip_w
    chip_y = 76
    _rounded_rect(draw, (chip_x, chip_y, chip_x + chip_w, chip_y + chip_h), 999,
                  fill=(255, 255, 255, 30), outline=(255, 255, 255), width=1)
    _text(draw, (chip_x + chip_w // 2, chip_y + chip_h // 2 - 1), chip_text,
          chip_font, fill="white", anchor="mm")

    # Subtitle strip
    _text(draw, (W // 2, 200), "Stakeholders Experience Index · Stakeholders Satisfaction Index",
          _font(15), fill=(200, 215, 235), anchor="mm")

    return band_h


def _draw_kpi_card(draw: ImageDraw.ImageDraw, x, y, w, h, label, value, suffix,
                   delta=None, accent=NAVY):
    _rounded_rect(draw, (x, y, x + w, y + h), 16, fill=SURFACE, outline=BORDER, width=1)
    # Accent bar
    _rounded_rect(draw, (x, y, x + 5, y + h), 16, fill=accent)
    # Label
    _text(draw, (x + 22, y + 22), label.upper(), _font(11, bold=True), fill=MUTED, anchor="la")
    # Value
    _text(draw, (x + 22, y + 50), value, _font(40, bold=True), fill=INK, anchor="la")
    # Suffix
    if suffix:
        # Position suffix after value
        val_bbox = draw.textbbox((x + 22, y + 50), value, font=_font(40, bold=True), anchor="la")
        _text(draw, (val_bbox[2] + 6, y + 64), suffix, _font(18), fill=MUTED, anchor="la")
    # Delta
    if delta is not None:
        delta_color = POS if delta >= 0 else NEG
        arrow = "▲" if delta >= 0 else "▼"
        _text(draw, (x + 22, y + h - 28), f"{arrow} {delta:+.1f}% vs bulan lalu",
              _font(13, bold=True), fill=delta_color, anchor="la")


def _draw_kpi_grid(canvas: Image.Image, sel: PosterSelection, monthly: pd.DataFrame,
                   monthly_social: pd.DataFrame, y_start: int) -> int:
    draw = ImageDraw.Draw(canvas)
    cards = []
    sxi_now = monthly["sxi_pct"].iloc[-1]
    ssi_now = monthly_social["ssi_pct"].iloc[-1]
    total = monthly["total"].iloc[-1]
    avg_res = monthly["avg_resolution"].iloc[-1]

    sxi_prev = monthly["sxi_pct"].iloc[-2]
    ssi_prev = monthly_social["ssi_pct"].iloc[-2]
    total_prev = monthly["total"].iloc[-2]
    res_prev = monthly["avg_resolution"].iloc[-2]

    if sel.show_kpi_sxi:
        cards.append(("SXI · Experience Index", f"{sxi_now:.2f}", "%",
                      sxi_now - sxi_prev, NAVY))
    if sel.show_kpi_ssi:
        cards.append(("SSI · Satisfaction Index", f"{ssi_now:.2f}", "%",
                      ssi_now - ssi_prev, GOLD))
    if sel.show_kpi_total:
        delta = (total - total_prev) / max(total_prev, 1) * 100
        cards.append(("Total Permohonan", f"{total:,}", "tiket", delta, NAVY_SOFT))
    if sel.show_kpi_resolution:
        delta = (avg_res - res_prev) / max(res_prev, 0.1) * 100
        cards.append(("Waktu Penyelesaian", f"{avg_res:.2f}", "jam", -delta, NAVY_DEEP))

    if not cards:
        return y_start

    # 2 per row
    pad = 24
    card_w = (W - 64 * 2 - pad) // 2
    card_h = 152
    x0 = 64
    for i, (lbl, val, suf, delta, accent) in enumerate(cards):
        row, col = divmod(i, 2)
        x = x0 + col * (card_w + pad)
        y = y_start + row * (card_h + pad)
        _draw_kpi_card(draw, x, y, card_w, card_h, lbl, val, suf, delta, accent)
    rows = (len(cards) + 1) // 2
    return y_start + rows * (card_h + pad)


def _draw_section_title(draw: ImageDraw.ImageDraw, x, y, title, sub=None) -> int:
    _text(draw, (x, y), title, _font(20, bold=True), fill=INK, anchor="la")
    if sub:
        _text(draw, (x, y + 28), sub, _font(13), fill=MUTED, anchor="la")
        return y + 56
    return y + 32


def _draw_hot_topics(canvas, sel, tickets_recent, y_start):
    draw = ImageDraw.Draw(canvas)
    y = _draw_section_title(draw, 64, y_start + 8, "7 Hot Topics", "Topik permohonan terbanyak bulan ini")
    box_w = W - 128
    box_h = 320
    _rounded_rect(draw, (64, y, 64 + box_w, y + box_h), 14, fill=SURFACE, outline=BORDER, width=1)

    topic_counts = tickets_recent[tickets_recent["topic"] != "Lainnya"]["topic"].value_counts().head(7)
    pcts = (topic_counts / max(len(tickets_recent), 1) * 100)

    fig = C.hbar(topic_counts.index.tolist(), pcts.values.tolist(),
                 height=box_h - 24, value_suffix="%")
    fig.update_layout(margin=dict(l=8, r=80, t=8, b=8))
    chart = _fig_to_png(fig, box_w - 24, box_h - 24)
    canvas.paste(chart, (76, y + 12))
    return y + box_h + 24


def _draw_trend(canvas, sel, monthly, y_start):
    draw = ImageDraw.Draw(canvas)
    y = _draw_section_title(draw, 64, y_start + 8, "Tren 12 Bulan", "Volume permohonan Jun 2025 → Mei 2026")
    box_w = W - 128
    box_h = 220
    _rounded_rect(draw, (64, y, 64 + box_w, y + box_h), 14, fill=SURFACE, outline=BORDER, width=1)

    df = monthly.copy()
    df["label"] = df["yearmonth"].apply(G.label_ym)
    fig = C.line_trend(df, "label", "total", height=box_h - 24)
    fig.update_layout(margin=dict(l=40, r=20, t=10, b=30))
    chart = _fig_to_png(fig, box_w - 24, box_h - 24)
    canvas.paste(chart, (76, y + 12))
    return y + box_h + 24


def _draw_donut_row(canvas, sel, tickets_recent, y_start):
    draw = ImageDraw.Draw(canvas)
    y = _draw_section_title(draw, 64, y_start + 8, "Komposisi Permohonan",
                            "Media komunikasi · klasifikasi · kategori pemohon")

    donuts = []
    if sel.show_channels_donut:
        ch = tickets_recent["channel"].value_counts().reindex([c[0] for c in R.CHANNELS], fill_value=0)
        donuts.append(("Media Komunikasi", ch.index.tolist(), ch.values.tolist(), None))
    if sel.show_classification_donut:
        cl = tickets_recent["classification"].value_counts().reindex([c[0] for c in R.CLASSIFICATIONS], fill_value=0)
        donuts.append(("Klasifikasi Informasi", cl.index.tolist(), cl.values.tolist(),
                       [T.NAVY, T.NAVY_SOFT, T.GOLD, T.RED]))
    if sel.show_requestor_donut:
        rq = tickets_recent["requestor"].value_counts().reindex([r[0] for r in R.REQUESTORS], fill_value=0)
        donuts.append(("Kategori Pemohon", rq.index.tolist(), rq.values.tolist(), None))

    if not donuts:
        return y

    n = len(donuts)
    pad = 16
    card_w = (W - 128 - pad * (n - 1)) // n
    card_h = 360
    for i, (title, labels, values, palette) in enumerate(donuts):
        x = 64 + i * (card_w + pad)
        _rounded_rect(draw, (x, y, x + card_w, y + card_h), 14, fill=SURFACE, outline=BORDER, width=1)
        _text(draw, (x + card_w // 2, y + 22), title, _font(13, bold=True), fill=MUTED, anchor="mm")
        # Use insidetext for percentages, legend for labels — avoids cropping
        colors = (palette or T.CAT_PALETTE)[: len(labels)]
        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.55, sort=False,
            marker=dict(colors=colors, line=dict(color="white", width=1.5)),
            textposition="inside", textinfo="percent",
            insidetextorientation="horizontal",
            textfont=dict(size=11, color="white", family="Inter"),
        ))
        fig.update_layout(
            font=dict(family="Inter", size=10, color="#0F172A"),
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(l=8, r=8, t=8, b=8),
            showlegend=True,
            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center",
                        font=dict(size=9), itemsizing="constant"),
        )
        chart = _fig_to_png(fig, card_w - 16, card_h - 50)
        canvas.paste(chart, (x + 8, y + 40))
    return y + card_h + 24


def _draw_sentiment(canvas, sel, monthly_social, y_start):
    draw = ImageDraw.Draw(canvas)
    y = _draw_section_title(draw, 64, y_start + 8, "Sentimen Sosial Bulan Ini", "Distribusi sentimen mention publik")

    last = monthly_social.iloc[-1]
    pos = last["positif_pct"]
    neu = last["netral_pct"]
    neg = last["negatif_pct"]

    box_w = W - 128
    box_h = 100
    _rounded_rect(draw, (64, y, 64 + box_w, y + box_h), 14, fill=SURFACE, outline=BORDER, width=1)

    # Stacked horizontal bar
    bar_x, bar_y = 88, y + 30
    bar_w, bar_h = box_w - 48, 28
    pos_w = int(bar_w * pos / 100)
    neu_w = int(bar_w * neu / 100)
    neg_w = bar_w - pos_w - neu_w

    _rounded_rect(draw, (bar_x, bar_y, bar_x + pos_w, bar_y + bar_h), 6, fill=POS)
    draw.rectangle((bar_x + pos_w, bar_y, bar_x + pos_w + neu_w, bar_y + bar_h), fill=(148, 163, 184))
    _rounded_rect(draw, (bar_x + pos_w + neu_w, bar_y, bar_x + bar_w, bar_y + bar_h), 6, fill=NEG)

    if pos_w > 60:
        _text(draw, (bar_x + pos_w // 2, bar_y + bar_h // 2), f"Positif {pos:.1f}%",
              _font(13, bold=True), fill="white", anchor="mm")
    if neu_w > 60:
        _text(draw, (bar_x + pos_w + neu_w // 2, bar_y + bar_h // 2), f"Netral {neu:.1f}%",
              _font(13, bold=True), fill="white", anchor="mm")
    if neg_w > 60:
        _text(draw, (bar_x + pos_w + neu_w + neg_w // 2, bar_y + bar_h // 2), f"Negatif {neg:.1f}%",
              _font(13, bold=True), fill="white", anchor="mm")

    _text(draw, (88, y + 78), f"Total mention: {int(last['total']):,} · Rata-rata respons: {last['avg_response_min']:.1f} mnt",
          _font(12), fill=MUTED, anchor="la")
    return y + box_h + 16


def _draw_footer(canvas, sel, y_start):
    draw = ImageDraw.Draw(canvas)
    y = y_start + 4
    # Divider
    draw.line([(64, y), (W - 64, y)], fill=BORDER, width=1)
    y += 16
    _text(draw, (64, y), "Sumber data: Sistem Layanan Informasi Publik Bank Indonesia · Pemantauan Media Sosial",
          _font(11), fill=MUTED, anchor="la")
    _text(draw, (64, y + 18), "Dicetak otomatis dari Dashboard Stakeholders Experience & Satisfaction Index",
          _font(11), fill=MUTED, anchor="la")
    _text(draw, (W - 64, y + 9), "bi.go.id · @bank_indonesia",
          _font(11, bold=True), fill=NAVY, anchor="ra")


# --- Main entrypoint ------------------------------------------------------

def render_poster(tickets: pd.DataFrame, social: pd.DataFrame,
                  selection: PosterSelection) -> tuple[bytes, bytes]:
    """Return (png_bytes, pdf_bytes)."""
    # Background
    canvas = Image.new("RGB", (W, H), BG)

    # Recent month scope
    tickets_recent = tickets[tickets["yearmonth"] == "2026-05"]
    monthly = G.monthly_summary(tickets)
    monthly_social = G.monthly_social_summary(social)

    y = 0
    if selection.show_header:
        y = _draw_header(canvas, selection)
    else:
        y = 32

    # KPI grid
    y = _draw_kpi_grid(canvas, selection, monthly, monthly_social, y + 28)

    # Hot topics
    if selection.show_hot_topics:
        y = _draw_hot_topics(canvas, selection, tickets_recent, y)

    # Trend
    if selection.show_trend:
        y = _draw_trend(canvas, selection, monthly, y)

    # Donut row
    if selection.show_channels_donut or selection.show_classification_donut or selection.show_requestor_donut:
        y = _draw_donut_row(canvas, selection, tickets_recent, y)

    # Sentiment
    if selection.show_sentiment:
        y = _draw_sentiment(canvas, selection, monthly_social, y)

    # Footer — anchored to remaining y (or H-80 if there's space)
    if selection.show_footer:
        footer_y = max(y + 8, H - 80)
        _draw_footer(canvas, selection, footer_y)

    # Export
    png_buf = io.BytesIO()
    canvas.save(png_buf, format="PNG", optimize=True)
    png_buf.seek(0)

    pdf_buf = io.BytesIO()
    canvas.save(pdf_buf, format="PDF", resolution=150.0)
    pdf_buf.seek(0)

    return png_buf.getvalue(), pdf_buf.getvalue()
