# ESG-to-Financial Decision Intelligence Dashboard

A Streamlit dashboard built from your five datasets (`esg.csv`, `financial.csv`,
`materiality.csv`, `reporting_quality.csv`, `risks.csv`, `targets.csv`) for
AVI, Tiger Brands, Astral Foods, RCL Foods and Libstar (FY2021–2025), following
the `Proposed_Dashboard.pdf` brief.

## Setup

```bash
cd esg_dashboard
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

This opens the dashboard at `http://localhost:8501`.

## Structure

```
esg_dashboard/
├── app.py              # the whole dashboard (7 pages, sidebar navigation)
├── requirements.txt
├── data/                # your six CSVs — replace with updated exports any time
│   ├── esg.csv
│   ├── financial.csv
│   ├── materiality.csv
│   ├── reporting_quality.csv
│   ├── risks.csv
│   └── targets.csv
└── README.md
```

## Pages

1. **Executive Overview** — company + year selector, financial and ESG KPI cards,
   sustainability targets and top risks for the selected company, with a
   source-traceability expander.
2. **Company Comparison** — bar charts comparing all five companies across
   financial, environmental, social and governance indicators for a chosen year.
   Companies with no disclosed value are listed separately rather than plotted as zero.
3. **ESG Performance Trends** — line chart of one indicator for one company across
   2021–2025, with year-on-year % change, 2021–2025 % change, and the disclosed
   target overlaid where one exists.
4. **ESG + Financial Performance** — scatter plot + OLS trendline of an ESG
   indicator against a financial indicator, Pearson correlation, and a
   correlation table across financial indicators. Only company-years with a
   disclosed value for both sides are used — no imputation.
5. **Sustainability Risks** — risk frequency by company, and the
   Risk → Operational Effect → Financial Effect pathway table, with a
   viewer for the underlying evidence text and its source page.
6. **Sustainability Targets & Progress** — a card per target with baseline,
   target and current values, a traffic-light status, and a summary chart.
   Targets with no calculable progress show "Progress cannot be calculated
   from disclosed information" rather than being marked as failed.
7. **Reporting Quality & Comparability** — average Reporting Quality Index
   (0–8) by company, its trend over time, a per-criterion breakdown, and the
   full indicator-level scoring table. Explicitly labelled as a disclosure-quality
   measure, not an ESG performance score.

## Data notes

- Missing values are **never** silently treated as zero. Where a chart has no
  disclosed value for a company/year, that company is either omitted (with a
  caption listing it) or the gap is left in the line chart (`connectgaps=False`).
- Codes used elsewhere in the underlying dataset: `0` = reported zero,
  `ND` = not disclosed, `NA` = not applicable, `NR` = not reported,
  `NC` = not comparable.
- To refresh with a new export, just overwrite the CSVs in `data/` — column
  names must stay the same (see each CSV's header row).

## Deploy on Render

This folder includes `render.yaml`, so Render can pick up the config automatically.

1. Push this whole project (or your full repo containing it) to GitHub/GitLab.
2. On [render.com](https://render.com) → **New +** → **Blueprint**, point it at the repo.
   Render reads `render.yaml` and pre-fills the service — just confirm and deploy.
3. No Blueprint? Use **New +** → **Web Service** instead and set manually:
   - **Root Directory**: `esg_dashboard` (if this sits inside a larger repo; leave blank if this folder *is* the repo root)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
4. First deploy on the free plan takes a few minutes; the service sleeps after 15 minutes idle and wakes on the next request (~30–60s cold start) — fine for a demo, upgrade the plan if you need it always warm for the panel.

## Extending it

- `materiality.csv` is loaded but not yet given its own page — Page 1 or a
  new Page 8 could show material issues by company/Six Capital if you want it added.
- Swap the Plotly charts for `st.altair_chart` if you prefer Altair.
- Deploy for free on [Streamlit Community Cloud](https://streamlit.io/cloud) by
  pushing this folder to a GitHub repo and pointing Streamlit Cloud at `app.py`.
