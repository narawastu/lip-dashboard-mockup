"""Compose a poster-style infographic from selected metrics.

Pure Pillow rendering, no browser dependency. Returns (png_bytes, pdf_bytes).
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

import theme as T
from data import generator as G, reference as R


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
    show_kpi_overall: bool = True
    show_kpi_effort: bool = True
    show_kpi_trust: bool = True
    show_kpi_loyalty: bool = True
    show_kpi_advokasi: bool = True
    show_kpi_total: bool = True
    show_kpi_resolution: bool = True
    show_hot_topics: bool = True
    show_trend: bool = True
    show_channels_donut: bool = True
    show_classification_donut: bool = True
    show_requestor_donut: bool = True
    show_sentiment: bool = True
    show_footer: bool = True
    theme_mode: str = "Navy"


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

    # 5-index satisfaction model — Top 2 Boxes %
    INDEX_DEF = [
        ("show_kpi_overall",  "Kepuasan Overall",  "t2b_overall",  NAVY),
        ("show_kpi_effort",   "Customer Effort",   "t2b_effort",   (15, 118, 110)),
        ("show_kpi_trust",    "Trust",             "t2b_trust",    NAVY_SOFT),
        ("show_kpi_loyalty",  "Loyalty",           "t2b_loyalty",  (124, 58, 237)),
        ("show_kpi_advokasi", "Advokasi",          "t2b_advokasi", GOLD),
    ]
    for flag, label, col, accent in INDEX_DEF:
        if not getattr(sel, flag, True):
            continue
        if col not in monthly.columns:
            continue
        now = monthly[col].iloc[-1]
        prev = monthly[col].iloc[-2]
        cards.append((label, f"{now:.1f}", "%", now - prev, accent))

    total = monthly["total"].iloc[-1]
    total_prev = monthly["total"].iloc[-2]
    avg_res = monthly["avg_resolution"].iloc[-1]
    res_prev = monthly["avg_resolution"].iloc[-2]

    if sel.show_kpi_total:
        delta = (total - total_prev) / max(total_prev, 1) * 100
        cards.append(("Total Permohonan", f"{total:,}", "tiket", delta, NAVY_DEEP))
    if sel.show_kpi_resolution:
        delta = (avg_res - res_prev) / max(res_prev, 0.1) * 100
        cards.append(("Waktu Penyelesaian", f"{avg_res:.2f}", "jam", -delta, RED))

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


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _draw_hot_topics(canvas, sel, tickets_recent, y_start):
    """Pure-Pillow horizontal bar chart."""
    draw = ImageDraw.Draw(canvas)
    y = _draw_section_title(draw, 64, y_start + 8, "7 Hot Topics", "Topik permohonan terbanyak bulan ini")
    box_w = W - 128
    box_h = 320
    box_x, box_y = 64, y
    _rounded_rect(draw, (box_x, box_y, box_x + box_w, box_y + box_h), 14, fill=SURFACE, outline=BORDER, width=1)

    topic_counts = tickets_recent[tickets_recent["topic"] != "Lainnya"]["topic"].value_counts().head(7)
    pcts = (topic_counts / max(len(tickets_recent), 1) * 100)
    items = list(zip(topic_counts.index.tolist(), pcts.values.tolist()))
    items.sort(key=lambda t: t[1], reverse=True)

    if not items:
        return y + box_h + 24

    # Layout: each row has a label on the left, bar on the right
    row_h = (box_h - 40) // len(items)
    label_w = 280
    bar_x = box_x + 24 + label_w
    bar_max_w = box_w - (24 + label_w) - 80  # leave 80px for the % label
    max_pct = max(p for _, p in items) or 1

    bar_color = NAVY
    for i, (label, pct) in enumerate(items):
        ry = box_y + 20 + i * row_h + (row_h - 22) // 2
        # Label
        _text(draw, (box_x + 24, ry + 11), label, _font(12), fill=INK, anchor="lm")
        # Bar
        bw = int((pct / max_pct) * bar_max_w)
        _rounded_rect(draw, (bar_x, ry, bar_x + bw, ry + 22), 4, fill=bar_color)
        # Value label
        _text(draw, (bar_x + bw + 8, ry + 11), f"{pct:.2f}%",
              _font(11, bold=True), fill=INK, anchor="lm")
    return y + box_h + 24


def _draw_trend(canvas, sel, monthly, y_start):
    """Pure-Pillow smoothed line chart with gradient fill."""
    draw = ImageDraw.Draw(canvas)
    y = _draw_section_title(draw, 64, y_start + 8, "Tren 12 Bulan", "Volume permohonan Jun 2025 → Mei 2026")
    box_w = W - 128
    box_h = 220
    box_x, box_y = 64, y
    _rounded_rect(draw, (box_x, box_y, box_x + box_w, box_y + box_h), 14, fill=SURFACE, outline=BORDER, width=1)

    df = monthly.copy()
    df["label"] = df["yearmonth"].apply(G.label_ym)
    values = df["total"].tolist()
    labels = df["label"].tolist()
    if not values:
        return y + box_h + 24

    # Plot area
    margin_l, margin_r, margin_t, margin_b = 64, 32, 24, 36
    plot_x0 = box_x + margin_l
    plot_y0 = box_y + margin_t
    plot_x1 = box_x + box_w - margin_r
    plot_y1 = box_y + box_h - margin_b
    plot_w = plot_x1 - plot_x0
    plot_h = plot_y1 - plot_y0

    vmin, vmax = min(values), max(values)
    span = max(vmax - vmin, 1)
    pad_v = span * 0.1
    y_lo, y_hi = vmin - pad_v, vmax + pad_v

    def to_xy(i, v):
        x = plot_x0 + (i / max(len(values) - 1, 1)) * plot_w
        py = plot_y1 - ((v - y_lo) / (y_hi - y_lo)) * plot_h
        return (x, py)

    # Gridlines + y-axis ticks (2 ticks: low and high band)
    grid_color = (228, 233, 242)
    for tick_v in (y_lo, (y_lo + y_hi) / 2, y_hi):
        _, ty = to_xy(0, tick_v)
        draw.line([(plot_x0, ty), (plot_x1, ty)], fill=grid_color, width=1)
        # tick label
        _text(draw, (plot_x0 - 8, ty), f"{int(tick_v):,}", _font(10), fill=MUTED, anchor="rm")

    # Fill polygon under the line
    points = [to_xy(i, v) for i, v in enumerate(values)]
    fill_poly = [(plot_x0, plot_y1)] + points + [(plot_x1, plot_y1)]
    fill_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    fl_draw = ImageDraw.Draw(fill_layer)
    fl_draw.polygon(fill_poly, fill=(*NAVY, 28))
    canvas.paste(fill_layer, (0, 0), fill_layer)

    # Line
    draw = ImageDraw.Draw(canvas)
    for a, b in zip(points, points[1:]):
        draw.line([a, b], fill=NAVY, width=3)

    # Endpoint dots
    for x, py in points:
        draw.ellipse((x - 3, py - 3, x + 3, py + 3), fill="white", outline=NAVY, width=2)

    # X-axis labels (every other one to avoid clutter)
    for i, lab in enumerate(labels):
        if i % 2 != 0 and i != len(labels) - 1:
            continue
        x, _ = to_xy(i, values[i])
        _text(draw, (x, plot_y1 + 16), lab, _font(10), fill=MUTED, anchor="mm")

    return y + box_h + 24


def _draw_donut(canvas, cx, cy, outer_r, inner_r, values, colors):
    """Draw a donut by drawing colored arcs as wedges + a white inner circle."""
    draw = ImageDraw.Draw(canvas)
    total = sum(values) or 1
    # Use anti-aliased composite by drawing on a 2x layer then downscaling
    scale = 2
    sx, sy = cx * scale, cy * scale
    sr_o, sr_i = outer_r * scale, inner_r * scale
    layer_size = (canvas.size[0] * scale, canvas.size[1] * scale)
    # Just draw on canvas directly at single resolution — Pillow's pieslice is decent enough
    angle = -90.0
    for v, col in zip(values, colors):
        if v <= 0:
            continue
        sweep = (v / total) * 360
        bbox = (cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r)
        draw.pieslice(bbox, angle, angle + sweep, fill=col, outline="white", width=1)
        angle += sweep
    # Inner circle to make it a donut
    draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r), fill="white")


def _draw_donut_row(canvas, sel, tickets_recent, y_start):
    """Pure-Pillow donut + legend for each composition card."""
    draw = ImageDraw.Draw(canvas)
    y = _draw_section_title(draw, 64, y_start + 8, "Komposisi Permohonan",
                            "Media komunikasi, klasifikasi, kategori pemohon")

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

        # Palette as RGB tuples
        palette_hex = palette or T.CAT_PALETTE
        colors = [_hex_to_rgb(c) for c in palette_hex[: len(labels)]]

        # Donut
        cx = x + card_w // 2
        cy = y + 60 + 110
        outer_r, inner_r = 90, 56
        _draw_donut(canvas, cx, cy, outer_r, inner_r, values, colors)
        draw = ImageDraw.Draw(canvas)

        # Inline percent labels for the largest 3 slices, written outside the donut
        total = sum(values) or 1
        angle = -90.0
        for v, col in zip(values, colors):
            if v <= 0:
                angle += 0
                continue
            sweep = (v / total) * 360
            mid_a = math.radians(angle + sweep / 2)
            pct = v / total * 100
            if pct >= 5:
                lx = cx + math.cos(mid_a) * (outer_r * 0.62)
                ly = cy + math.sin(mid_a) * (outer_r * 0.62)
                _text(draw, (lx, ly), f"{pct:.0f}%", _font(11, bold=True), fill="white", anchor="mm")
            angle += sweep

        # Legend below
        legend_y = y + card_h - 80
        cols_per_row = 2
        col_w = (card_w - 28) // cols_per_row
        for j, (lab, col) in enumerate(zip(labels, colors)):
            row = j // cols_per_row
            col_idx = j % cols_per_row
            lx = x + 14 + col_idx * col_w
            ly = legend_y + row * 18
            if ly + 14 > y + card_h - 4:
                break
            draw.rectangle((lx, ly + 4, lx + 8, ly + 12), fill=col)
            _text(draw, (lx + 14, ly + 8), str(lab)[:24], _font(10), fill=MUTED, anchor="lm")

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
