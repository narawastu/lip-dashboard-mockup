# Dashboard Mockup

Streamlit dashboard mockup for tracking stakeholder satisfaction and
experience metrics at a public-information service team. Synthetic
data; not connected to any real system.

Two satisfaction indices are tracked separately: one from direct
service touchpoints (email, phone, livechat, walk-in) and one from
public listening (social media, news). Includes an **infographic
export** feature: pick which metrics to include, preview the poster,
download as PNG or PDF.

Bahasa Indonesia UI by default.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Opens on http://localhost:8501.

## Tabs

1. **Ringkasan Eksekutif** — operational KPIs and headline indices.
2. **Experience** — gauge, score distribution, channel/topic drivers, SLA performance.
3. **Sentimen Publik** — sentiment trend, share of voice, top mentions.
4. **Ekspor Infografis** — compose, preview, and download a poster.
5. **Operasional & Drill-Down** — heatmap, resolution time distribution, backlog, regional spread, ticket table.

## Replacing demo data

Replace the two functions in `data/generator.py`:

- `generate_tickets()` → `pd.DataFrame` with columns:
  `timestamp, channel, topic, classification, requestor, status, province, resolution_h, sxi_score, date, yearmonth, sla_met, rejection_reason, requestor_id, is_repeat`
- `generate_social()` → `pd.DataFrame` with columns:
  `timestamp, platform, topic, sentiment, engagement, response_minutes, yearmonth, date`

Everything downstream is column-addressed Pandas, no other changes needed.

## Notes

- **Period**: hardcoded to "Mei 2026" in `data/reference.py:CURRENT_PERIOD_LABEL`.
- **Theme**: navy / gold / red palette in `theme.py`. Adjust to match the deploying organization's brand.
- **Kaleido**: requires `>=1.0.0` for static chart export (used by the infographic feature).
