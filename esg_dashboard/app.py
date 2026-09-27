"""
ESG-to-Financial Decision Intelligence Dashboard
APFA802 Major Project — Beyond the Report

Companies: AVI, Tiger Brands, Astral Foods, RCL Foods, Libstar Holdings
Reporting period: 2021-2025

Run with:
    pip install -r requirements.txt
    streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ESG-to-Financial Decision Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"

# ---------------------------------------------------------------------------
# THEME — ledger palette (functional colour: gold = financial, sage = natural
# capital, rust = risk only; amber / slate are the remaining company keys)
# ---------------------------------------------------------------------------
INK, PANEL, PANEL_ALT, HAIRLINE = "#0F1512", "#161D18", "#1D2620", "#2B362F"
PAPER, MUTE = "#EDEAE0", "#93A499"
GRAIN, SAGE, RUST, AMBER, SLATE = "#C9A227", "#7A9E85", "#C1553F", "#D98F4E", "#5C7A99"

COMPANY_COLORS = {
    "AVI Limited": GRAIN,
    "Tiger Brands Limited": RUST,
    "Astral Foods Limited": SAGE,
    "RCL Foods Limited": AMBER,
    "Libstar Holdings Limited": SLATE,
}

MISSING_CODES = {"0", "ND", "NA", "NR", "NC"}


def inject_css():
    css_path = ASSETS_DIR / "theme.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def style_fig(fig, height=420):
    """Apply the ledger palette to a plotly figure so every chart matches the page."""
    fig.update_layout(
        height=height,
        paper_bgcolor=INK,
        plot_bgcolor=INK,
        font=dict(family="Inter, sans-serif", color=PAPER, size=13),
        title_font=dict(family="Fraunces, serif", color=PAPER, size=18),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=PAPER)),
        margin=dict(t=50, l=10, r=10, b=10),
        hoverlabel=dict(bgcolor=PANEL_ALT, font=dict(color=PAPER, family="Inter")),
    )
    fig.update_xaxes(gridcolor=HAIRLINE, zerolinecolor=HAIRLINE, color=MUTE, linecolor=HAIRLINE)
    fig.update_yaxes(gridcolor=HAIRLINE, zerolinecolor=HAIRLINE, color=MUTE, linecolor=HAIRLINE)
    return fig


def hero(eyebrow, title, sub=""):
    st.markdown(
        f"""<div class="hero">
                <p class="hero-eyebrow">{eyebrow}</p>
                <p class="hero-title">{title}</p>
                <p class="hero-sub">{sub}</p>
            </div>""",
        unsafe_allow_html=True,
    )


def badge(text, kind):
    cls = {"achieved": "badge-achieved", "not-achieved": "badge-not-achieved",
           "progress": "badge-progress", "unknown": "badge-unknown"}.get(kind, "badge-unknown")
    return f'<span class="badge {cls}">{text}</span>'

# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    esg = pd.read_csv(DATA_DIR / "esg.csv")
    fin = pd.read_csv(DATA_DIR / "financial.csv")
    mat = pd.read_csv(DATA_DIR / "materiality.csv")
    rq = pd.read_csv(DATA_DIR / "reporting_quality.csv")
    risks = pd.read_csv(DATA_DIR / "risks.csv")
    targets = pd.read_csv(DATA_DIR / "targets.csv")

    # Coerce Year to numeric where possible (keep NaN for undated rows rather than 0)
    for df, col in [(esg, "Year"), (mat, "Year"), (rq, "Year"), (risks, "Year")]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    fin["Year"] = pd.to_numeric(fin["Year"], errors="coerce")

    return esg, fin, mat, rq, risks, targets


esg, fin, mat, rq, risks, targets = load_data()
inject_css()

ALL_COMPANIES = sorted(esg["Company"].dropna().unique().tolist())
ALL_YEARS = sorted(esg["Year"].dropna().unique().astype(int).tolist())


def color_for(company):
    return COMPANY_COLORS.get(company, "#7f7f7f")


def fmt_num(x, decimals=1):
    if pd.isna(x):
        return "N/D"
    return f"{x:,.{decimals}f}"


def missing_note():
    st.caption(
        "⚠️ Missing data is **not** treated as zero. Gaps in the disclosure record "
        "are shown as gaps in charts / as 'N/D' (not disclosed), never plotted as 0."
    )


# ---------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------------------
st.sidebar.markdown(
    """<div style="border-bottom:1px solid #2B362F; padding-bottom:14px; margin-bottom:10px;">
         <p style="font-family:'Fraunces',serif; font-size:1.5rem; font-weight:600;
                   color:#EDEAE0; margin:0; line-height:1.15;">
            Beyond the Report
         </p>
         <p style="color:#93A499; font-size:0.82rem; margin-top:4px;">
            ESG-to-Financial Decision Intelligence · FY2021–2025
         </p>
       </div>""",
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Go to page",
    [
        "1 · Executive Overview",
        "2 · Company Comparison",
        "3 · ESG Performance Trends",
        "4 · ESG + Financial Performance",
        "5 · Sustainability Risks",
        "6 · Sustainability Targets & Progress",
        "7 · Reporting Quality & Comparability",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown('<hr style="margin:18px 0 12px 0;">', unsafe_allow_html=True)
st.sidebar.markdown(
    '<p style="font-size:0.85rem; color:#93A499; line-height:1.5;">'
    "<em>Report → Data → Analysis → Insight → Decision</em><br><br>"
    "Converts integrated / sustainability / annual report disclosures into a "
    "structured, traceable dataset, linking ESG performance to financial outcomes."
    "</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown('<hr style="margin:12px 0;">', unsafe_allow_html=True)
chips = "".join(
    f'<span class="company-chip"><span class="company-dot" style="background:{c}"></span>{n.replace(" Limited","").replace(" Holdings","")}</span>'
    for n, c in COMPANY_COLORS.items()
)
st.sidebar.markdown(f'<div style="line-height:2.2;">{chips}</div>', unsafe_allow_html=True)

# ===========================================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ===========================================================================
if page.startswith("1"):
    hero("Page 1 · Landing page", "Executive Overview",
         "One company, one year — financial position, ESG position, targets and risks at a glance.")

    c1, c2 = st.columns([2, 1])
    company = c1.selectbox("Company", ALL_COMPANIES, key="p1_company")
    year = c2.selectbox("Year", ALL_YEARS, index=len(ALL_YEARS) - 1, key="p1_year")

    st.markdown("### Financial snapshot")
    f_row = fin[(fin.Company == company) & (fin.Year == year)]
    if f_row.empty:
        st.info("No financial data disclosed / matched for this company-year.")
    else:
        r = f_row.iloc[0]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Revenue (ZARm)", fmt_num(r.get("Revenue_ZARm")))
        k2.metric("EBITDA (ZARm)", fmt_num(r.get("EBITDA_ZARm")))
        k3.metric("Profit after tax (ZARm)", fmt_num(r.get("Profit After Tax_ZARm")))
        k4.metric("Operating margin (%)", fmt_num(r.get("Operating Margin")))
        k5, k6 = st.columns(2)
        yoy = r.get("Revenue YoY %")
        k5.metric("Revenue YoY %", fmt_num(yoy) if pd.notna(yoy) else "N/D",
                   delta=None if pd.isna(yoy) else f"{yoy:.1f}%")
        k6.metric("ROE (%)", fmt_num(r.get("ROE")))

    st.markdown("### ESG snapshot")

    def kpi_for(indicator):
        row = esg[(esg.Company == company) & (esg.Year == year) & (esg.Indicator == indicator)]
        if row.empty or pd.isna(row.iloc[0]["Value_Clean"]):
            return "N/D", ""
        v = row.iloc[0]
        return fmt_num(v["Value_Clean"], 2), (v["Unit"] if pd.notna(v["Unit"]) else "")

    esg_kpis = ["Water Consumption", "Energy Consumption", "Total GHG", "LTIR"]
    cols = st.columns(len(esg_kpis))
    for c, ind in zip(cols, esg_kpis):
        val, unit = kpi_for(ind)
        c.metric(ind, f"{val} {unit}".strip())

    missing_note()

    st.markdown("### Sustainability targets (selected company)")
    t_sub = targets[targets.Company == company]
    if t_sub.empty:
        st.info("No targets recorded for this company.")
    else:
        st.dataframe(
            t_sub[["Indicator", "Target", "Baseline_Year", "Baseline_Value",
                   "Target_Year", "Target_Value", "Current_Year", "Current_Value",
                   "Progress", "Status"]],
            use_container_width=True, hide_index=True,
        )

    st.markdown("### Major sustainability risks (selected company)")
    r_sub = risks[risks.Company == company]
    if r_sub.empty:
        st.info("No risks recorded for this company.")
    else:
        risk_counts = r_sub["Risk"].value_counts().reset_index()
        risk_counts.columns = ["Risk", "Mentions"]
        fig = px.bar(risk_counts.head(10), x="Mentions", y="Risk", orientation="h",
                     color_discrete_sequence=[RUST])
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(style_fig(fig, height=350), use_container_width=True)

    with st.expander("🔎 Source traceability — ESG records for this company/year"):
        trace = esg[(esg.Company == company) & (esg.Year == year)][
            ["Indicator", "Value_Clean", "Unit", "Source", "Page"]
        ]
        st.dataframe(trace, use_container_width=True, hide_index=True)

# ===========================================================================
# PAGE 2 — COMPANY COMPARISON
# ===========================================================================
elif page.startswith("2"):
    hero("Page 2 · Benchmarking", "Company Comparison",
         "AVI · Tiger Brands · Astral Foods · RCL Foods · Libstar, side by side.")

    companies_sel = st.multiselect("Companies", ALL_COMPANIES, default=ALL_COMPANIES, key="p2_companies")
    year_sel = st.selectbox("Year", ALL_YEARS, index=len(ALL_YEARS) - 1, key="p2_year")
    missing_note()

    tab_fin, tab_env, tab_soc, tab_gov = st.tabs(
        ["💰 Financial", "🌱 Environmental", "👥 Social", "🏛️ Governance"]
    )

    with tab_fin:
        f_sub = fin[(fin.Company.isin(companies_sel)) & (fin.Year == year_sel)]
        fin_indicators = ["Revenue_ZARm", "EBITDA_ZARm", "Operating Profit_ZARm",
                           "Profit After Tax_ZARm", "Operating Margin", "ROA", "ROE"]
        chosen = st.selectbox("Financial indicator", fin_indicators, key="p2_fin_ind")
        if f_sub.empty:
            st.info("No financial data for this selection.")
        else:
            fig = px.bar(f_sub, x="Company", y=chosen, color="Company",
                         color_discrete_map=COMPANY_COLORS, text_auto=".2s")
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig), use_container_width=True)
            st.dataframe(f_sub[["Company", "Year"] + fin_indicators], use_container_width=True, hide_index=True)

    def esg_comparison_tab(category, key_prefix):
        sub = esg[(esg.Company.isin(companies_sel)) & (esg.Year == year_sel) & (esg["ESG Category"] == category)]
        if sub.empty:
            st.info(f"No {category.lower()} data disclosed for this year/selection.")
            return
        indicators = sorted(sub["Indicator"].unique())
        ind = st.selectbox("Indicator", indicators, key=f"{key_prefix}_ind")
        d = sub[sub.Indicator == ind].dropna(subset=["Value_Clean"])
        if d.empty:
            st.warning("Indicator disclosed by name but no comparable value recorded (N/D).")
        else:
            fig = px.bar(d, x="Company", y="Value_Clean", color="Company",
                         color_discrete_map=COMPANY_COLORS,
                         labels={"Value_Clean": f"{ind} ({d['Unit'].dropna().iloc[0] if d['Unit'].notna().any() else ''})"})
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        missing_companies = set(companies_sel) - set(d.Company.unique())
        if missing_companies:
            st.caption(f"Not disclosed / no comparable value: {', '.join(sorted(missing_companies))}")
        st.dataframe(
            sub[sub.Indicator == ind][["Company", "Value_Clean", "Unit", "Disclosure Status", "Comparability", "Source", "Page"]],
            use_container_width=True, hide_index=True,
        )

    with tab_env:
        esg_comparison_tab("Environmental", "p2_env")
    with tab_soc:
        esg_comparison_tab("Social", "p2_soc")
    with tab_gov:
        esg_comparison_tab("Governance", "p2_gov")

# ===========================================================================
# PAGE 3 — ESG PERFORMANCE TRENDS
# ===========================================================================
elif page.startswith("3"):
    hero("Page 3 · Time series", "ESG Performance Trends",
         "2021 → 2025, one company and indicator at a time, with the disclosed target overlaid.")

    c1, c2 = st.columns(2)
    company = c1.selectbox("Company", ALL_COMPANIES, key="p3_company")
    company_esg = esg[esg.Company == company]
    indicators = sorted(company_esg["Indicator"].dropna().unique())
    indicator = c2.selectbox("ESG indicator", indicators, key="p3_indicator")

    series = company_esg[company_esg.Indicator == indicator].sort_values("Year")
    series_valid = series.dropna(subset=["Value_Clean"])

    missing_note()

    if series_valid.empty:
        st.warning("This indicator has no disclosed comparable values across the period.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=series_valid.Year, y=series_valid.Value_Clean, mode="lines+markers",
            name="Actual", line=dict(color=color_for(company), width=3),
            connectgaps=False,
        ))

        # overlay target if one exists for this company/indicator
        t_match = targets[(targets.Company == company) &
                           (targets.Indicator.str.contains(indicator.split()[0], case=False, na=False))]
        if not t_match.empty:
            trow = t_match.iloc[0]
            try:
                ty, tv = float(trow.Target_Year), float(trow.Target_Value)
                fig.add_trace(go.Scatter(x=[ty], y=[tv], mode="markers+text",
                                          marker=dict(color=GRAIN, size=14, symbol="star"),
                                          text=["Target"], textposition="top center", name="Target"))
            except (TypeError, ValueError):
                pass

        unit = series_valid.Unit.dropna().iloc[0] if series_valid.Unit.notna().any() else ""
        fig.update_layout(xaxis_title="Year", yaxis_title=f"{indicator} ({unit})", xaxis=dict(dtick=1))
        st.plotly_chart(style_fig(fig, height=450), use_container_width=True)

        # YoY and 2021-2025 change
        s = series_valid.set_index("Year")["Value_Clean"]
        yoy_tbl = s.pct_change().mul(100).round(1)
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Year-on-year change (%)**")
            st.dataframe(yoy_tbl.rename("YoY %").to_frame(), use_container_width=True)
        with colB:
            if len(s) >= 2:
                first_year, last_year = s.index.min(), s.index.max()
                pct_change = (s.loc[last_year] - s.loc[first_year]) / s.loc[first_year] * 100 if s.loc[first_year] != 0 else np.nan
                st.metric(f"{int(first_year)}–{int(last_year)} % change", fmt_num(pct_change) + "%")
            else:
                st.info("Not enough disclosed years to compute a period change.")

    with st.expander("🔎 Underlying records & source pages"):
        st.dataframe(
            series[["Year", "Value_Clean", "Unit", "Value_Status", "Disclosure Status", "Source", "Page"]],
            use_container_width=True, hide_index=True,
        )

# ===========================================================================
# PAGE 4 — ESG + FINANCIAL PERFORMANCE
# ===========================================================================
elif page.startswith("4"):
    hero("Page 4 · Association, not causation", "ESG + Financial Performance",
         "Where sustainability metrics and financial outcomes move together.")
    st.info(
        "📌 **Correlation does not prove causation.** This page identifies statistical "
        "relationships / associations between ESG and financial indicators. It does not "
        "claim that an ESG factor *caused* a financial result unless there is separate, "
        "sufficient evidence for that claim.",
        icon="📌",
    )

    esg_indicators = sorted(esg["Indicator"].dropna().unique())
    fin_indicators = ["Revenue_ZARm", "EBITDA_ZARm", "Operating Profit_ZARm",
                       "Profit After Tax_ZARm", "Operating Margin", "EBITDA Margin", "ROA", "ROE"]

    c1, c2, c3 = st.columns(3)
    esg_ind = c1.selectbox("ESG indicator (x-axis)", esg_indicators,
                            index=esg_indicators.index("Water Intensity") if "Water Intensity" in esg_indicators else 0)
    fin_ind = c2.selectbox("Financial indicator (y-axis)", fin_indicators,
                            index=fin_indicators.index("Operating Margin"))
    companies_sel = c3.multiselect("Companies", ALL_COMPANIES, default=ALL_COMPANIES, key="p4_companies")

    esg_sub = esg[(esg.Indicator == esg_ind) & (esg.Company.isin(companies_sel))][
        ["Company", "Year", "Value_Clean", "Unit"]
    ].rename(columns={"Value_Clean": "ESG_Value"})
    fin_sub = fin[fin.Company.isin(companies_sel)][["Company", "Year", fin_ind]]

    merged = pd.merge(esg_sub, fin_sub, on=["Company", "Year"], how="inner").dropna(subset=["ESG_Value", fin_ind])

    if merged.empty:
        st.warning("No overlapping company-years with disclosed values for both indicators — "
                    "no chart is shown, since missing data cannot be assumed or filled in.")
    else:
        fig = px.scatter(
            merged, x="ESG_Value", y=fin_ind, color="Company", trendline="ols",
            color_discrete_map=COMPANY_COLORS, hover_data=["Year"],
            labels={"ESG_Value": f"{esg_ind} ({merged.Unit.dropna().iloc[0] if merged.Unit.notna().any() else ''})"},
        )
        st.plotly_chart(style_fig(fig, height=480), use_container_width=True)

        if len(merged) >= 3:
            corr = merged["ESG_Value"].corr(merged[fin_ind])
            st.metric(f"Pearson correlation: {esg_ind} vs {fin_ind}", f"{corr:.2f}",
                       help="Based on pooled company-year observations with disclosed values only.")
        else:
            st.caption("Fewer than 3 paired observations — correlation not computed (insufficient disclosure).")

        with st.expander("Correlation table across all financial indicators"):
            rows = []
            for fi in fin_indicators:
                fs = fin[fin.Company.isin(companies_sel)][["Company", "Year", fi]]
                m = pd.merge(esg_sub, fs, on=["Company", "Year"], how="inner").dropna(subset=["ESG_Value", fi])
                if len(m) >= 3:
                    rows.append({"Financial indicator": fi, "n": len(m), "Correlation": round(m["ESG_Value"].corr(m[fi]), 2)})
                else:
                    rows.append({"Financial indicator": fi, "n": len(m), "Correlation": "Insufficient data"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("🔎 Matched observations used in this chart"):
        st.dataframe(merged, use_container_width=True, hide_index=True)

# ===========================================================================
# PAGE 5 — SUSTAINABILITY RISKS
# ===========================================================================
elif page.startswith("5"):
    hero("Page 5 · Risk pathway", "Sustainability Risks",
         "Risk → Operational Effect → Financial Effect.")

    c1, c2 = st.columns(2)
    companies_sel = c1.multiselect("Companies", ALL_COMPANIES, default=ALL_COMPANIES, key="p5_companies")
    all_risk_types = sorted(risks["Risk"].dropna().unique())
    risk_type = c2.selectbox("Risk", ["All"] + all_risk_types, key="p5_risk")

    r_sub = risks[risks.Company.isin(companies_sel)]
    if risk_type != "All":
        r_sub = r_sub[r_sub.Risk == risk_type]

    st.markdown("### Risk frequency by company")
    if r_sub.empty:
        st.info("No risk disclosures matched.")
    else:
        freq = r_sub.groupby(["Company", "Risk"]).size().reset_index(name="Mentions")
        fig = px.bar(freq, x="Risk", y="Mentions", color="Company", barmode="group",
                     color_discrete_map=COMPANY_COLORS)
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    st.markdown("### Risk pathway (Risk → Operational Effect → Financial Effect)")
    st.caption(
        "🔶 Distinguishes financial impact **reported by the company** from financial "
        "impact **inferred from the risk pathway**. The 'Financial Indicator' column shows "
        "the metric management or this analysis links the risk to — it is not itself a "
        "confirmed reported financial impact unless the evidence explicitly states one."
    )
    if not r_sub.empty:
        display_cols = ["Company", "Risk", "Operational Effect", "Financial Effect", "Financial Indicator", "Source", "Page"]
        st.dataframe(r_sub[display_cols].drop_duplicates(), use_container_width=True, hide_index=True, height=400)

        with st.expander("🔎 Supporting evidence text (verbatim excerpt from report)"):
            pick = st.selectbox("Choose a record to inspect",
                                 options=r_sub.index,
                                 format_func=lambda i: f"{r_sub.loc[i,'Company']} — {r_sub.loc[i,'Risk']} (p.{r_sub.loc[i,'Page']})")
            st.write(r_sub.loc[pick, "Evidence"])
            st.caption(f"Source: {r_sub.loc[pick, 'Source']}, page {r_sub.loc[pick, 'Page']}")

# ===========================================================================
# PAGE 6 — SUSTAINABILITY TARGETS & PROGRESS
# ===========================================================================
elif page.startswith("6"):
    hero("Page 6 · Targets ledger", "Sustainability Targets & Progress",
         "Baseline → target → current, against each company's own disclosed commitments.")

    companies_sel = st.multiselect("Companies", ALL_COMPANIES, default=ALL_COMPANIES, key="p6_companies")
    t_sub = targets[targets.Company.isin(companies_sel)].copy()

    st.caption(
        "Progress is only shown where it can be calculated from disclosed information. "
        "Missing information is **not** assumed to mean the target was missed."
    )

    def status_kind(status):
        if pd.isna(status):
            return "unknown", "Progress cannot be calculated from disclosed information"
        s = str(status).lower()
        if "achiev" in s and "not" not in s:
            return "achieved", "Achieved"
        if "not achiev" in s or "worsen" in s:
            return "not-achieved", "Not achieved"
        if s.startswith("nd") or "no target disclosed" in s:
            return "unknown", "Progress cannot be calculated from disclosed information"
        return "progress", str(status)

    if t_sub.empty:
        st.info("No targets available for the selected companies.")
    else:
        kinds = t_sub["Status"].apply(lambda s: status_kind(s)[0])
        t_sub["Status light"] = t_sub["Status"].apply(lambda s: status_kind(s)[1])
        for company in companies_sel:
            c_targets = t_sub[t_sub.Company == company]
            if c_targets.empty:
                continue
            st.markdown(
                f'<h3 style="display:flex; align-items:center; gap:8px;">'
                f'<span class="company-dot" style="background:{color_for(company)}; width:11px; height:11px; '
                f'border-radius:50%; display:inline-block;"></span>{company}</h3>',
                unsafe_allow_html=True,
            )
            for _, row in c_targets.iterrows():
                kind, label = status_kind(row.Status)
                row_class = {"achieved": "achieved", "not-achieved": "not-achieved", "progress": "progress"}.get(kind, "")
                st.markdown(
                    f"""<div class="target-row {row_class}">
                          <div style="display:flex; justify-content:space-between; align-items:baseline; gap:12px; flex-wrap:wrap;">
                            <div>
                              <strong style="font-size:1.02rem;">{row.Indicator}</strong>
                              <div style="color:{MUTE}; font-size:0.88rem; margin-top:2px;">{row.Target}</div>
                            </div>
                            {badge(label, kind)}
                          </div>
                          <div style="display:flex; gap:28px; margin-top:10px; flex-wrap:wrap;">
                            <div><div style="color:{MUTE}; font-size:0.78rem;">Baseline ({row.Baseline_Year})</div>
                                 <div style="font-family:'Fraunces',serif; font-size:1.2rem; color:{PAPER};">{row.Baseline_Value}</div></div>
                            <div><div style="color:{MUTE}; font-size:0.78rem;">Target ({row.Target_Year})</div>
                                 <div style="font-family:'Fraunces',serif; font-size:1.2rem; color:{GRAIN};">{row.Target_Value}</div></div>
                            <div><div style="color:{MUTE}; font-size:0.78rem;">Current ({row.Current_Year})</div>
                                 <div style="font-family:'Fraunces',serif; font-size:1.2rem; color:{PAPER};">{row.Current_Value}</div></div>
                            <div style="max-width:260px;"><div style="color:{MUTE}; font-size:0.78rem;">Progress</div>
                                 <div style="font-size:0.9rem; color:{PAPER};">{row.Progress}</div></div>
                          </div>
                          <div class="section-note" style="border-top:none; margin-top:8px; padding-top:0;">Source: {row.Source}, page {row.Page}</div>
                        </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("### Status summary across selected companies")
        summary = t_sub["Status light"].value_counts().reset_index()
        summary.columns = ["Status", "Count"]
        status_color_map = {"Achieved": SAGE, "Not achieved": RUST}
        fig = px.bar(summary, x="Status", y="Count", color="Status",
                     color_discrete_map=status_color_map,
                     color_discrete_sequence=[GRAIN, MUTE])
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig, height=350), use_container_width=True)

# ===========================================================================
# PAGE 7 — REPORTING QUALITY & COMPARABILITY
# ===========================================================================
elif page.startswith("7"):
    hero("Page 7 · Disclosure quality", "Reporting Quality & Comparability",
         "Not an ESG score — a measure of how usable each company's disclosures are.")
    st.info(
        "The **Reporting Quality Index** measures the quality and decision-usefulness of "
        "*disclosure* (out of 8: Disclosed, Definition clear, Unit clear, Consistent, "
        "Comparable, Assured, Target linked, Financial/operational linkage). "
        "It is **not** a measure of overall ESG/sustainability performance.",
        icon="📌",
    )

    c1, c2 = st.columns(2)
    companies_sel = c1.multiselect("Companies", ALL_COMPANIES, default=ALL_COMPANIES, key="p7_companies")
    years_sel = c2.multiselect("Years", ALL_YEARS, default=ALL_YEARS, key="p7_years")

    rq_sub = rq[(rq.Company.isin(companies_sel)) & (rq.Year.isin(years_sel))]

    if rq_sub.empty:
        st.info("No reporting-quality records for this selection.")
    else:
        st.markdown("### Average Reporting Quality Index by company (out of 8)")
        avg_by_company = rq_sub.groupby("Company")["Total Score"].mean().reset_index()
        fig = px.bar(avg_by_company, x="Company", y="Total Score", color="Company",
                     color_discrete_map=COMPANY_COLORS, range_y=[0, 8], text_auto=".2f")
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig, height=400), use_container_width=True)

        st.markdown("### Reporting Quality Index trend (2021–2025)")
        trend = rq_sub.groupby(["Company", "Year"])["Total Score"].mean().reset_index()
        fig2 = px.line(trend, x="Year", y="Total Score", color="Company", markers=True,
                        color_discrete_map=COMPANY_COLORS, range_y=[0, 8])
        fig2.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(style_fig(fig2, height=400), use_container_width=True)

        st.markdown("### Component breakdown (average score per criterion)")
        criteria = ["Disclosed", "Definition Clear", "Unit Clear", "Consistent",
                    "Comparable", "Assured", "Target Linked", "Financial Linked"]
        comp = rq_sub.groupby("Company")[criteria].mean().reset_index()
        comp_melt = comp.melt(id_vars="Company", var_name="Criterion", value_name="Avg score")
        fig3 = px.bar(comp_melt, x="Criterion", y="Avg score", color="Company", barmode="group",
                      color_discrete_map=COMPANY_COLORS, range_y=[0, 1])
        fig3.update_layout(xaxis_tickangle=-20)
        st.plotly_chart(style_fig(fig3, height=420), use_container_width=True)

        st.markdown("### Indicator-level detail")
        st.dataframe(
            rq_sub.sort_values(["Company", "Year", "Indicator"]),
            use_container_width=True, hide_index=True, height=350,
        )

st.sidebar.markdown('<hr style="margin:16px 0 8px 0;">', unsafe_allow_html=True)
st.sidebar.markdown(
    '<p style="font-size:0.75rem; color:#93A499;">APFA802 · Beyond the Report</p>',
    unsafe_allow_html=True,
)
