"""Brand theme: palette, fonts, and CSS injected into Streamlit."""

NAVY = "#002F6C"
NAVY_DEEP = "#001638"
NAVY_SOFT = "#1F4E91"
NAVY_GLOW = "#0A4A9E"
RED = "#E60012"
GOLD = "#C9A227"
GOLD_SOFT = "#E5C158"
INK = "#0B1220"
MUTED = "#4B5A75"
SUBTLE = "#8B98AE"
BORDER = "#E4E9F2"
BORDER_STRONG = "#CFD7E5"
SURFACE = "#FFFFFF"
BG = "#F2F4F9"
BG_ELEV = "#FFFFFF"
BG_TINT = "#EEF2F8"

POS = "#16A34A"
NEU = "#94A3B8"
NEG = "#DC2626"

# Categorical palette (channels, topics)
CAT_PALETTE = [
    "#002F6C",
    "#1F4E91",
    "#3D74C2",
    "#C9A227",
    "#E60012",
    "#0F766E",
    "#7C3AED",
    "#0891B2",
    "#65A30D",
    "#B45309",
]

PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, system-ui, -apple-system, sans-serif", color=INK, size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=8, r=8, t=8, b=8),
    colorway=CAT_PALETTE,
    xaxis=dict(gridcolor=BORDER, zeroline=False, linecolor=BORDER, tickcolor=BORDER),
    yaxis=dict(gridcolor=BORDER, zeroline=False, linecolor=BORDER, tickcolor=BORDER),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    hoverlabel=dict(
        bgcolor=SURFACE,
        bordercolor=BORDER,
        font=dict(family="Inter", color=INK, size=12),
    ),
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: {INK};
}}

.stApp {{
    background:
      radial-gradient(1200px 600px at 80% -20%, rgba(0, 47, 108, 0.06), transparent 60%),
      radial-gradient(900px 500px at -10% 110%, rgba(201, 162, 39, 0.05), transparent 60%),
      {BG};
    background-attachment: fixed;
}}

/* Hide default Streamlit chrome but keep sidebar toggle accessible */
#MainMenu {{visibility: hidden;}}
header[data-testid="stHeader"] {{
    background: transparent;
    height: 0;
}}
header[data-testid="stHeader"] > div:first-child {{
    background: transparent;
}}
/* Compact sidebar-expand button (only visible when sidebar is collapsed) */
button[data-testid="stExpandSidebarButton"] {{
    position: fixed !important;
    top: 16px !important;
    left: 16px !important;
    z-index: 9999 !important;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    background: {SURFACE} !important;
    color: {NAVY} !important;
    border: 1px solid {BORDER_STRONG} !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.10) !important;
    visibility: visible !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0 !important;
    overflow: hidden !important;
    transition: width 0.22s cubic-bezier(0.16, 1, 0.3, 1),
                background 0.18s ease,
                color 0.18s ease,
                box-shadow 0.18s ease !important;
}}
button[data-testid="stExpandSidebarButton"]:hover {{
    width: 130px !important;
    background: {NAVY} !important;
    color: white !important;
    box-shadow: 0 8px 22px rgba(0, 47, 108, 0.35) !important;
    gap: 8px !important;
    padding: 0 14px !important;
    justify-content: flex-start !important;
}}
button[data-testid="stExpandSidebarButton"] svg,
button[data-testid="stExpandSidebarButton"] span[data-testid="stIconMaterial"] {{
    width: 22px !important;
    height: 22px !important;
    font-size: 22px !important;
    flex: 0 0 auto !important;
    transition: color 0.18s ease, fill 0.18s ease !important;
}}
button[data-testid="stExpandSidebarButton"]:hover svg,
button[data-testid="stExpandSidebarButton"]:hover span[data-testid="stIconMaterial"] {{
    color: white !important;
    fill: white !important;
}}
button[data-testid="stExpandSidebarButton"]::after {{
    content: "Filter";
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    opacity: 0;
    width: 0;
    overflow: hidden;
    white-space: nowrap;
    transition: opacity 0.18s ease 0.05s, width 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}}
button[data-testid="stExpandSidebarButton"]:hover::after {{
    opacity: 1;
    width: auto;
}}
footer {{visibility: hidden;}}
.stDeployButton {{display: none !important;}}

/* Main block — leave room above hero for the floating Filter button */
.main .block-container {{
    padding-top: 60px;
    padding-bottom: 4rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1480px;
}}
.stMainBlockContainer {{
    padding-top: 60px !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 1rem;
}}

/* Multiselect chips: replace Streamlit's default red with brand navy */
section[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background-color: {NAVY} !important;
    border-color: {NAVY} !important;
    color: white !important;
    border-radius: 8px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="tag"] span,
section[data-testid="stSidebar"] [data-baseweb="tag"] svg {{
    color: white !important;
    fill: white !important;
}}
section[data-testid="stSidebar"] [data-baseweb="tag"]:hover {{
    background-color: {NAVY_DEEP} !important;
    border-color: {NAVY_DEEP} !important;
}}
/* The x button on each chip */
section[data-testid="stSidebar"] [data-baseweb="tag"] [role="button"] {{
    background-color: rgba(255,255,255,0.2) !important;
    border-radius: 4px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="tag"] [role="button"]:hover {{
    background-color: rgba(255,255,255,0.35) !important;
}}

/* Radio button selected state: navy outer circle, white inner dot */
section[data-testid="stSidebar"] label:has(input[type="radio"]:checked) > div:first-child {{
    background-color: {NAVY} !important;
    border-color: {NAVY} !important;
}}
section[data-testid="stSidebar"] label:has(input[type="radio"]:checked) > div:first-child > div {{
    background-color: white !important;
}}

/* Multiselect dropdown selected items in the popup also use navy */
[data-baseweb="popover"] [aria-selected="true"] {{
    background-color: rgba(0, 47, 108, 0.08) !important;
    color: {INK} !important;
}}

/* Multiselect input border on focus */
section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {{
    border-color: {BORDER} !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child:focus-within,
section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child[data-focus] {{
    border-color: {NAVY} !important;
    box-shadow: 0 0 0 2px rgba(0, 47, 108, 0.12) !important;
}}

/* Checkbox in export tab and elsewhere */
[data-testid="stCheckbox"] input:checked + div,
[data-baseweb="checkbox"] [aria-checked="true"] {{
    background-color: {NAVY} !important;
    border-color: {NAVY} !important;
}}

/* Native Streamlit bordered container → branded card.
   Streamlit 1.50+ applies border directly to the inner stVerticalBlock when border=True.
   Selector requires the title to be exactly 4 levels deep, so only the immediate card
   container matches, not ancestor blocks. */
[data-testid="stVerticalBlock"]:has(
    > [data-testid="stElementContainer"]
    > [data-testid="stMarkdown"]
    > [data-testid="stMarkdownContainer"]
    > .bi-card-title
) {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
}}
[data-testid="stVerticalBlock"]:has(
    > [data-testid="stElementContainer"]
    > [data-testid="stMarkdown"]
    > [data-testid="stMarkdownContainer"]
    > .bi-card-elev-tag
) {{
    border-radius: 14px !important;
    padding: 22px 24px !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05) !important;
}}
.bi-card-title {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {SUBTLE};
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid {BORDER};
}}
.bi-card-elev-tag {{ display: none; }}

/* Legacy bi-card (still used in places not yet migrated) — kept for compatibility */
.bi-card {{
    background: {SURFACE};
    border: 1px solid {BORDER_STRONG};
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow:
      0 1px 0 rgba(255,255,255,0.6) inset,
      0 1px 3px rgba(15, 23, 42, 0.04),
      0 12px 28px -20px rgba(15, 23, 42, 0.18);
}}
.bi-card-elev {{
    background: {SURFACE};
    border: 1px solid {BORDER_STRONG};
    border-radius: 16px;
    padding: 24px 26px;
    box-shadow:
      0 1px 0 rgba(255,255,255,0.6) inset,
      0 4px 10px rgba(15, 23, 42, 0.05),
      0 20px 40px -20px rgba(15, 23, 42, 0.20);
}}

/* KPI card */
.kpi {{
    position: relative;
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 20px 14px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 8px;
    min-height: 138px;
    transition: border-color 0.18s ease;
}}
.kpi:hover {{
    border-color: {BORDER_STRONG};
}}
.kpi-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {SUBTLE};
}}
.kpi-value {{
    font-size: 34px;
    font-weight: 800;
    color: {INK};
    line-height: 1;
    letter-spacing: -0.03em;
    font-variant-numeric: tabular-nums;
}}
.kpi-suffix {{
    font-size: 14px;
    font-weight: 600;
    color: {SUBTLE};
    margin-left: 6px;
    letter-spacing: 0;
}}
.kpi-delta {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 999px;
    letter-spacing: 0.02em;
}}
.kpi-delta.pos {{
    color: {POS};
    background: rgba(22, 163, 74, 0.1);
}}
.kpi-delta.neg {{
    color: {NEG};
    background: rgba(220, 38, 38, 0.1);
}}
.kpi-delta.neu {{
    color: {MUTED};
    background: {BG};
}}
.kpi-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}}
.kpi-spark {{
    width: 100%;
    height: 42px;
    margin-top: 2px;
}}

/* Hero header — distilled */
.bi-hero {{
    background: linear-gradient(120deg, {NAVY_DEEP} 0%, {NAVY} 60%, {NAVY_GLOW} 100%);
    border-radius: 16px;
    padding: 22px 28px;
    color: white;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    box-shadow: 0 12px 28px -20px rgba(0, 22, 56, 0.45);
}}
.bi-hero-left {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.bi-hero-logo {{
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: white;
    color: {NAVY};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 18px;
    letter-spacing: -0.03em;
}}
.bi-hero-eyebrow {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 2px;
}}
.bi-hero-title {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.2;
}}
.bi-hero-right {{
    display: flex;
    align-items: center;
}}
.bi-hero-period {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 999px;
    padding: 7px 14px 7px 12px;
    font-size: 13px;
    font-weight: 600;
    color: white;
}}
.bi-hero-live-dot {{
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: #34D399;
    box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.55);
    animation: bi-pulse 5s cubic-bezier(0.16, 1, 0.3, 1) infinite;
    flex: 0 0 auto;
}}
.bi-hero-period-sep {{
    opacity: 0.4;
    font-weight: 400;
}}
.bi-hero-period-live {{
    opacity: 0.7;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
@keyframes bi-pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.55); }}
    60% {{ box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }}
}}

/* Section heading */
.bi-section {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin: 32px 0 14px;
}}
.bi-section h2 {{
    font-size: 20px;
    font-weight: 700;
    color: {INK};
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
}}
.bi-section .bi-section-sub {{
    font-size: 13px;
    color: {MUTED};
    line-height: 1.4;
}}

/* Index panel (SXI / SSI on overview) */
.bi-index-panel {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    display: flex;
    align-items: stretch;
    gap: 28px;
}}
.bi-index-meta {{
    flex: 0 0 auto;
    min-width: 240px;
}}
.bi-index-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 4px 10px 4px 6px;
    border-radius: 999px;
    background: {BG_TINT};
    margin-bottom: 14px;
}}
.bi-index-badge-dot {{
    width: 14px;
    height: 14px;
    border-radius: 999px;
    flex: 0 0 auto;
}}
.bi-index-badge-dot.sxi {{ background: {NAVY}; }}
.bi-index-badge-dot.ssi {{ background: {GOLD}; }}
.bi-index-badge-tag {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {INK};
}}
.bi-index-value {{
    font-size: 52px;
    font-weight: 800;
    line-height: 1;
    color: {INK};
    letter-spacing: -0.04em;
    font-variant-numeric: tabular-nums;
}}
.bi-index-target {{
    display: inline-block;
    margin-top: 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: {MUTED};
    background: {BG_TINT};
    padding: 5px 11px;
    border-radius: 999px;
    text-transform: uppercase;
}}
.bi-index-spark {{
    flex: 1 1 auto;
    min-width: 0;
    display: flex;
    align-items: center;
}}

/* Pills */
.bi-pill {{
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    background: {BG};
    color: {MUTED};
    border: 1px solid {BORDER};
}}
.bi-pill.pos {{ color: {POS}; background: rgba(22,163,74,0.08); border-color: rgba(22,163,74,0.2); }}
.bi-pill.neg {{ color: {NEG}; background: rgba(220,38,38,0.08); border-color: rgba(220,38,38,0.2); }}
.bi-pill.neu {{ color: {MUTED}; }}

/* Tabs custom — pill bar */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: rgba(255,255,255,0.6);
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 6px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
    backdrop-filter: blur(6px);
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{
    display: none !important;
}}
.stTabs [data-baseweb="tab"] {{
    height: 40px;
    padding: 0 16px;
    background: transparent;
    border-radius: 10px;
    color: {MUTED};
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.01em;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {INK};
    background: rgba(0, 47, 108, 0.04);
}}
.stTabs [aria-selected="true"] {{
    color: white !important;
    background: linear-gradient(135deg, {NAVY} 0%, {NAVY_GLOW} 100%) !important;
    border-bottom: 0 !important;
    box-shadow: 0 4px 12px -4px rgba(0, 47, 108, 0.45);
}}

/* Buttons */
.stDownloadButton > button, .stButton > button {{
    border-radius: 10px;
    border: 1px solid {BORDER};
    background: {SURFACE};
    color: {INK};
    font-weight: 600;
    padding: 8px 16px;
    transition: all 0.15s ease;
}}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
    background: {NAVY};
    border-color: {NAVY};
    color: white;
}}
.stButton > button:hover {{
    border-color: {NAVY};
}}

/* Stat list — uses CSS grid so layout survives Streamlit's div wrapping */
.bi-stat-list {{
    display: grid;
    grid-template-columns: 1fr auto;
    column-gap: 16px;
    row-gap: 10px;
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid {BORDER};
}}
.bi-stat-list dt {{
    font-size: 12px;
    color: {MUTED};
    font-weight: 500;
    margin: 0;
    align-self: center;
}}
.bi-stat-list dd {{
    font-size: 15px;
    color: {INK};
    font-weight: 700;
    margin: 0;
    text-align: right;
    font-variant-numeric: tabular-nums;
}}

/* Top-mentions table */
.bi-mention {{
    padding: 12px 14px;
    border: 1px solid {BORDER};
    border-radius: 12px;
    margin-bottom: 8px;
    background: {SURFACE};
}}
.bi-mention-meta {{
    font-size: 12px;
    color: {MUTED};
    display: flex;
    gap: 10px;
    margin-bottom: 6px;
    align-items: center;
}}
.bi-mention-text {{
    font-size: 13px;
    color: {INK};
    line-height: 1.5;
}}

/* Infographic preview iframe */
.bi-poster-frame {{
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}}

/* Override Streamlit metric (used as fallback) */
[data-testid="stMetricValue"] {{
    font-size: 28px !important;
    font-weight: 700 !important;
    color: {INK} !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: {MUTED} !important;
}}
</style>
"""
