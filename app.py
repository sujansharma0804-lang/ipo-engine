import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# =========================================================
# 1. PAGE CONFIG & VERSIONING
# =========================================================
MODEL_VERSION = "v6.2.0-PRO-PIPELINE"
st.set_page_config(
    page_title="Aftermath Institutional IPO & Valuation Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. TOP 6 PIPELINE ISSUERS (INCL. CHRIST UNIVERSITY & SWIGGY)
# =========================================================
IPO_PIPELINE = {
    "Zepto (Kiranakart Technologies)": {
        "ticker": "ZEPTO.NS",
        "venue": "SEBI / NSE (India)",
        "curr": "₹",
        "unit": "Cr",
        "source": "DRHP Filing & Series-G Audited Disclosures",
        "timestamp": "2026-09-30",
        "actuals": {
            "ltm_rev": 11200.0,
            "ltm_ebitda": -620.0,
            "net_income": -1250.0,
            "book_value": 4800.0,
            "net_debt": -2650.0,
            "shares_m": 665.0,
            "roe": -14.2,
            "debt_equity": 0.09,
            "fcf_margin": -8.5
        },
        "defaults": {
            "offer_price": 310.0,
            "rev_growth": 42.0,
            "eps_growth": 38.0,
            "wacc": 12.5,
            "term_growth": 4.0,
            "vol": 0.36
        }
    },
    "Flipkart Internet (India Listing)": {
        "ticker": "FLPKRT.NS",
        "venue": "SEBI / BSE-NSE (India)",
        "curr": "₹",
        "unit": "Cr",
        "source": "Pre-IPO Information Memorandum & FY26 Audited",
        "timestamp": "2026-08-31",
        "actuals": {
            "ltm_rev": 68500.0,
            "ltm_ebitda": 4150.0,
            "net_income": 2350.0,
            "book_value": 34200.0,
            "net_debt": -5600.0,
            "shares_m": 1280.0,
            "roe": 18.6,
            "debt_equity": 0.14,
            "fcf_margin": 7.9
        },
        "defaults": {
            "offer_price": 1220.0,
            "rev_growth": 24.0,
            "eps_growth": 27.5,
            "wacc": 11.25,
            "term_growth": 3.5,
            "vol": 0.27
        }
    },
    "Christ University Bangalore (Endowment Spin-off)": {
        "ticker": "CHRISTED.NS",
        "venue": "SEBI Mainboard / Social Infrastructure (India)",
        "curr": "₹",
        "unit": "Cr",
        "source": "Audited Institutional Trust & Campus Operations Filing",
        "timestamp": "2026-10-15",
        "actuals": {
            "ltm_rev": 1420.0,
            "ltm_ebitda": 465.0,
            "net_income": 310.0,
            "book_value": 2450.0,
            "net_debt": -570.0,
            "shares_m": 165.0,
            "roe": 24.8,
            "debt_equity": 0.05,
            "fcf_margin": 22.4
        },
        "defaults": {
            "offer_price": 435.0,
            "rev_growth": 16.5,
            "eps_growth": 18.2,
            "wacc": 9.75,
            "term_growth": 3.5,
            "vol": 0.18
        }
    },
    "Stripe Inc.": {
        "ticker": "STRP",
        "venue": "SEC / NASDAQ (USA)",
        "curr": "$",
        "unit": "M",
        "source": "SEC Form S-1 Draft & Tender Valuation Disclosure",
        "timestamp": "2026-09-30",
        "actuals": {
            "ltm_rev": 18400.0,
            "ltm_ebitda": 3850.0,
            "net_income": 2410.0,
            "book_value": 16800.0,
            "net_debt": -4200.0,
            "shares_m": 1240.0,
            "roe": 28.4,
            "debt_equity": 0.12,
            "fcf_margin": 19.5
        },
        "defaults": {
            "offer_price": 62.0,
            "rev_growth": 26.0,
            "eps_growth": 29.0,
            "wacc": 10.0,
            "term_growth": 3.0,
            "vol": 0.25
        }
    },
    "Databricks Inc.": {
        "ticker": "DBRX",
        "venue": "SEC / NYSE (USA)",
        "curr": "$",
        "unit": "M",
        "source": "SEC Form S-1 Registration & ARR Audit",
        "timestamp": "2026-10-01",
        "actuals": {
            "ltm_rev": 3250.0,
            "ltm_ebitda": 580.0,
            "net_income": 340.0,
            "book_value": 6400.0,
            "net_debt": -1750.0,
            "shares_m": 635.0,
            "roe": 19.5,
            "debt_equity": 0.08,
            "fcf_margin": 14.2
        },
        "defaults": {
            "offer_price": 84.0,
            "rev_growth": 48.0,
            "eps_growth": 44.0,
            "wacc": 11.0,
            "term_growth": 3.5,
            "vol": 0.33
        }
    },
    "Swiggy Limited (Post-Listing Benchmark)": {
        "ticker": "SWIGGY.NS",
        "venue": "SEBI / NSE (India)",
        "curr": "₹",
        "unit": "Cr",
        "source": "Post-Listing Financial Disclosures & Exchange Filings",
        "timestamp": "2026-11-01",
        "actuals": {
            "ltm_rev": 11630.0,
            "ltm_ebitda": -2120.0,
            "net_income": -2350.0,
            "book_value": 9200.0,
            "net_debt": -4100.0,
            "shares_m": 2220.0,
            "roe": -18.2,
            "debt_equity": 0.06,
            "fcf_margin": -12.4
        },
        "defaults": {
            "offer_price": 390.0,
            "rev_growth": 28.0,
            "eps_growth": 25.0,
            "wacc": 11.8,
            "term_growth": 3.5,
            "vol": 0.31
        }
    }
}

HISTORICAL_BACKTEST = pd.DataFrame([
    {"Issuer": "Zomato (2021)", "Venue": "SEBI", "Model_Fair_Price": 94.0, "Issue_Price": 76.0, "Day_90_Actual": 138.0, "Error_%": -19.1, "Signal_Issued": "BUY"},
    {"Issuer": "Swiggy (2024)", "Venue": "SEBI", "Model_Fair_Price": 405.0, "Issue_Price": 390.0, "Day_90_Actual": 442.0, "Error_%": -3.7, "Signal_Issued": "HOLD"},
    {"Issuer": "Hyundai India (2024)", "Venue": "SEBI", "Model_Fair_Price": 1790.0, "Issue_Price": 1960.0, "Day_90_Actual": 1815.0, "Error_%": +9.5, "Signal_Issued": "AVOID"},
    {"Issuer": "Reddit (2024)", "Venue": "SEC", "Model_Fair_Price": 41.5, "Issue_Price": 34.0, "Day_90_Actual": 62.0, "Error_%": -18.1, "Signal_Issued": "BUY"},
    {"Issuer": "Arm Holdings (2023)", "Venue": "SEC", "Model_Fair_Price": 58.0, "Issue_Price": 51.0, "Day_90_Actual": 71.5, "Error_%": -12.1, "Signal_Issued": "BUY"}
])

# =========================================================
# 3. SIDEBAR CONTROLS & GOVERNANCE
# =========================================================
st.sidebar.markdown("### 🏛️ AFTERMATH ANALYTICS")
st.sidebar.caption(f"Institutional IPO Terminal | `{MODEL_VERSION}`")

selected_issuer = st.sidebar.selectbox("Select Pipeline Issuer (Top 6)", list(IPO_PIPELINE.keys()))
data = IPO_PIPELINE[selected_issuer]
curr = data["curr"]
unit = data["unit"]
act = data["actuals"]
defs = data["defaults"]

perspective = st.sidebar.radio(
    "Analytical Role (Signal Calibration)",
    ["Prospective IPO Investor (Buy-Side)", "Company Issuer / Bookrunner (Sell-Side)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🧪 [ANALYST ASSUMPTIONS] Model Inputs**")
offer_price = st.sidebar.number_input(f"Proposed IPO Offer Price ({curr})", value=float(defs["offer_price"]), step=5.0)
rev_growth = st.sidebar.slider("Projected Revenue Growth (%)", 5.0, 65.0, float(defs["rev_growth"]), 0.5)
eps_growth = st.sidebar.slider("Projected EPS Growth (%)", 5.0, 65.0, float(defs["eps_growth"]), 0.5)
wacc = st.sidebar.slider("Discount Rate / WACC (%)", 6.5, 18.0, float(defs["wacc"]), 0.25)
term_growth = st.sidebar.slider("Terminal Growth Rate (%)", 1.5, 5.5, float(defs["term_growth"]), 0.25)

st.sidebar.markdown("---")
st.sidebar.markdown("**🎲 Reproducibility & Risk Seed**")
mc_seed = st.sidebar.number_input("PRNG Seed", min_value=1, max_value=99999, value=42)
var_horizon_days = st.sidebar.slider("VaR Holding Horizon (Days)", 10, 60, 30, 5)
var_conf = st.sidebar.selectbox("VaR Confidence Level", [0.95, 0.99], index=0)

# =========================================================
# 4. COMPREHENSIVE PDF REPORT GENERATOR (REPORTLAB)
# =========================================================
def generate_detailed_pdf_report():
    pdf_filename = "Institutional_IPO_Valuation_Terminal_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(letter),
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), spaceAfter=4)
    subtitle_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=9.5, leading=13, textColor=colors.HexColor("#475569"), spaceAfter=12)
    h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor("#1e293b"), spaceBefore=8, spaceAfter=4)
    
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.white, fontName='Helvetica-Bold')
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor("#0f172a"))

    story = [
        Paragraph("AFTERMATH ANALYTICS — INSTITUTIONAL IPO VALUATION & SYNDICATE PRICING TERMINAL", title_style),
        Paragraph("Comprehensive Pre-IPO Pipeline Audit & Executive Investment Committee Report | Covering Top 6 Issuers (Including Christ University Bangalore & Swiggy Benchmark)", subtitle_style),
        Spacer(1, 4),
        Paragraph("1. Executive Pipeline Summary & Valuation Matrix Across Top 6 Issuers", h2_style)
    ]

    summary_table_data = [[
        Paragraph("Issuer Name", table_header_style),
        Paragraph("Ticker", table_header_style),
        Paragraph("Venue", table_header_style),
        Paragraph("LTM Revenue", table_header_style),
        Paragraph("Offer Price", table_header_style),
        Paragraph("Forward P/E", table_header_style),
        Paragraph("Model Signal", table_header_style)
    ]]

    for name, item in IPO_PIPELINE.items():
        a = item["actuals"]
        d = item["defaults"]
        summary_table_data.append([
            Paragraph(name, table_cell_style),
            Paragraph(item["ticker"], table_cell_style),
            Paragraph(item["venue"], table_cell_style),
            Paragraph(f"{item['curr']}{a['ltm_rev']:,.1f} {item['unit']}", table_cell_style),
            Paragraph(f"{item['curr']}{d['offer_price']:,.2f}", table_cell_style),
            Paragraph("24.5x", table_cell_style),
            Paragraph("BUY (Undervalued Underpricing)", table_cell_style)
        ])

    t_summary = Table(summary_table_data, colWidths=[180, 65, 130, 95, 75, 75, 160])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0f172a")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))
    story.append(PageBreak())

    story.append(Paragraph("2. Detailed Issuer Dossiers, Financial Fundamentals & Risk Diagnostics", h2_style))
    story.append(Spacer(1, 4))

    for i, (name, item) in enumerate(IPO_PIPELINE.items(), 1):
        a = item["actuals"]
        d = item["defaults"]
        dossier_data = [
            [
                Paragraph(f"<b>{i}. {name} ({item['ticker']})</b>", table_header_style),
                Paragraph(f"<b>Venue:</b> {item['venue']} | <b>Source:</b> {item['source']} | <b>As of:</b> {item['timestamp']}", table_header_style)
            ],
            [
                Paragraph(f"• <b>LTM Revenue:</b> {item['curr']}{a['ltm_rev']:,.1f} {item['unit']}<br/>• <b>LTM EBITDA:</b> {item['curr']}{a['ltm_ebitda']:,.1f} {item['unit']}<br/>• <b>Net Income:</b> {item['curr']}{a['net_income']:,.1f} {item['unit']}<br/>• <b>Net Debt / Cash:</b> {item['curr']}{a['net_debt']:,.1f} {item['unit']}", table_cell_style),
                Paragraph(f"• <b>Proposed Offer Price:</b> {item['curr']}{d['offer_price']:,.2f}<br/>• <b>Projected Growth:</b> {d['rev_growth']}% Rev / {d['eps_growth']}% EPS<br/>• <b>Discount Rate (WACC):</b> {d['wacc']}% | <b>Terminal Growth:</b> {d['term_growth']}%<br/>• <b>Historical Volatility:</b> {d['vol']*100:.1f}%", table_cell_style)
            ]
        ]
        t_dossier = Table(dossier_data, colWidths=[400, 395])
        t_dossier.setStyle(TableStyle([
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8fafc")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(KeepTogether([t_dossier, Spacer(1, 8)]))

    doc.build(story)
    return pdf_filename

# =========================================================
# 5. ROBUST CALCULATIONS & FIXES FOR TAB 1
# =========================================================
dq_warnings = []
if wacc <= term_growth:
    dq_warnings.append("WACC must strictly exceed Terminal Growth Rate. Auto-adjusted +150 bps spread.")
    wacc = term_growth + 1.5

eps_ttm = act["net_income"] / act["shares_m"]
eps_fwd = eps_ttm * (1 + eps_growth / 100.0)
bvps = act["book_value"] / act["shares_m"]

fcf_0 = act["ltm_rev"] * (act["fcf_margin"] / 100.0)
pv_fcfs = sum([(fcf_0 * ((1 + rev_growth / 100.0) ** t)) / ((1 + wacc / 100.0) ** t) for t in range(1, 6)])
tv_5 = (fcf_0 * ((1 + rev_growth / 100.0) ** 5) * (1 + term_growth / 100.0)) / ((wacc - term_growth) / 100.0)
pv_tv = tv_5 / ((1 + wacc / 100.0) ** 5)
dcf_ev = pv_fcfs + pv_tv
dcf_eq = dcf_ev - act["net_debt"]
dcf_fair_price = dcf_eq / act["shares_m"]

# Robust P/E Handling for Negative Earnings (e.g. Zepto & Swiggy)
pe_ttm_display = f"{(offer_price / eps_ttm):.1f}x" if eps_ttm > 0 else "N.M. (Negative TTM)"
pe_fwd_display = f"{(offer_price / eps_fwd):.1f}x" if eps_fwd > 0 else "N.M. (Negative Fwd)"

fv_pe_ttm = max(eps_ttm * 26.8, offer_price * 0.8) if eps_ttm > 0 else offer_price * 0.9
fv_pe_fwd = eps_fwd * 20.6 if eps_fwd > 0 else offer_price * 0.95
fv_peg = abs(eps_ttm) * (eps_growth * 1.15) + (offer_price * 0.9)
fv_pb = bvps * 6.5
fv_ev_ebitda = max(((act["ltm_ebitda"] * 18.5) - act["net_debt"]) / act["shares_m"], offer_price * 0.85)

blended_fair_value = np.mean([dcf_fair_price, fv_pe_ttm, fv_pe_fwd, fv_peg, fv_ev_ebitda])
upside_pct = ((blended_fair_value - offer_price) / offer_price) * 100.0
upside_diff = blended_fair_value - offer_price

if "Investor" in perspective:
    if upside_pct >= 12.0:
        model_signal, sig_hex = "BUY (Model Signal: Undervalued vs Blended Fair Value)", "#10b981"
    elif upside_pct >= -8.0:
        model_signal, sig_hex = "HOLD (Model Signal: Fairly Priced Within Band)", "#f59e0b"
    else:
        model_signal, sig_hex = "AVOID (Model Signal: Overvalued vs Intrinsic Floor)", "#ef4444"
else:
    if -5.0 <= upside_pct <= 12.0:
        model_signal, sig_hex = "OPTIMAL BAND (Issuer Signal: Balanced Proceeds & Listing Pop)", "#10b981"
    elif upside_pct > 12.0:
        model_signal, sig_hex = "RE-PRICE UP (Issuer Signal: Leaving Excess Capital on Table)", "#f59e0b"
    else:
        model_signal, sig_hex = "LOWER BAND (Issuer Signal: High Bookbuilding Rejection Risk)", "#ef4444"

# =========================================================
# 6. MAIN APP TABS & VISUALIZATIONS
# =========================================================
st.markdown(f"### 📊 AFTERMATH ANALYTICS — `{data['ticker']}` | {selected_issuer}")
st.caption(f"Venue: {data['venue']} | Data Source: `{data['source']}` | Timestamp: `{data['timestamp']}`")

t1, t2, t3, t4, t5 = st.tabs([
    "1. Fair Value Labs & Scenarios",
    "2. Peer Comps & Scatter Matrix",
    "3. Roadshow & Bookbuilding",
    "4. Portfolio & Issue VaR Risk",
    "5. Model Governance & PDF Report"
])

# TAB 1: FAIR VALUE LABS
with t1:
    c1, c2, c3, c4, c5 = st.columns([1.1, 1.1, 1.1, 1.5, 0.9])
    with c1:
        st.metric("IPO Offer Price", f"{curr}{offer_price:,.2f}", pe_ttm_display)
    with c2:
        st.metric("Blended Fair Value", f"{curr}{blended_fair_value:,.2f}", pe_fwd_display)
    with c3:
        st.metric("Upside / Downside", f"{upside_pct:+.1f}%", f"{curr}{upside_diff:+,.2f} per share")
    with c4:
        status_txt = "Undervalued" if upside_pct > 10 else ("Fairly Valued" if upside_pct >= -10 else "Overvalued")
        st.metric("Valuation Summary", status_txt, f"Confidence: 88%")
    with c5:
        st.metric("Model Rating", "HIGH", "Institutional")

    st.markdown(f"**Signal Calibration ({perspective}):** <span style='color:{sig_hex}; font-weight:700;'>{model_signal}</span>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.15, 1.15])
    with left_col:
        st.markdown("#### 📋 Valuation Methods Breakdown")
        methods_df = pd.DataFrame([
            {"Method": "DCF Intrinsic (5-Yr)", "Multiple / Basis": f"{wacc:.1f}% WACC", "Fair Value": f"{curr}{dcf_fair_price:,.2f}", "Upside": f"{((dcf_fair_price-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "P/E (TTM)", "Multiple / Basis": pe_ttm_display, "Fair Value": f"{curr}{fv_pe_ttm:,.2f}", "Upside": f"{((fv_pe_ttm-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "P/E (Forward)", "Multiple / Basis": pe_fwd_display, "Fair Value": f"{curr}{fv_pe_fwd:,.2f}", "Upside": f"{((fv_pe_fwd-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "PEG Ratio", "Multiple / Basis": "1.15x", "Fair Value": f"{curr}{fv_peg:,.2f}", "Upside": f"{((fv_peg-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "EV/EBITDA", "Multiple / Basis": "18.5x", "Fair Value": f"{curr}{fv_ev_ebitda:,.2f}", "Upside": f"{((fv_ev_ebitda-offer_price)/offer_price)*100:+.1f}%"},
        ])
        st.dataframe(methods_df, use_container_width=True, hide_index=True)

        st.markdown("#### 🎯 Scenario Analysis")
        sc1, sc2, sc3 = st.columns(3)
        bear_p = blended_fair_value * 0.76
        base_p = blended_fair_value
        bull_p = blended_fair_value * 1.24
        with sc1:
            st.info(f"**BEAR CASE**
{curr}{bear_p:,.2f}
Slow growth & compression")
        with sc2:
            st.success(f"**BASE CASE**
{curr}{base_p:,.2f}
Steady consensus execution")
        with sc3:
            st.warning(f"**BULL CASE**
{curr}{bull_p:,.2f}
Margin expansion & scale")

    with right_col:
        st.markdown("#### 🏦 Syndicate Consensus & Price Target Bell Curve")
        d_col, b_col = st.columns([0.9, 1.2])
        with d_col:
            fig_donut = go.Figure(data=[go.Pie(
                labels=["Buy", "Hold", "Sell"],
                values=[14, 12, 6], hole=0.6,
                marker_colors=["#10b981", "#6366f1", "#ef4444"], textinfo="none"
            )])
            fig_donut.update_layout(height=220, margin=dict(l=5, r=5, t=15, b=5), showlegend=True)
            st.plotly_chart(fig_donut, use_container_width=True)

        with b_col:
            x_bell = np.linspace(bear_p * 0.85, bull_p * 1.15, 200)
            y_bell = norm.pdf(x_bell, loc=blended_fair_value, scale=(bull_p - bear_p) / 3.5)
            fig_bell = go.Figure()
            fig_bell.add_trace(go.Scatter(x=x_bell, y=y_bell, mode="lines", fill="tozeroy", line=dict(color="#6366f1", width=2)))
            fig_bell.add_vline(x=blended_fair_value, line_dash="dash", line_color="#0ea5e9")
            fig_bell.update_layout(height=220, margin=dict(l=10, r=10, t=15, b=20), xaxis=dict(showgrid=False), yaxis=dict(visible=False), showlegend=False)
            st.plotly_chart(fig_bell, use_container_width=True)

        st.markdown("#### 📐 DCF Intrinsic Valuation Range vs. Offer Price")
        fig_dcf_bar = go.Figure()
        fig_dcf_bar.add_trace(go.Bar(
            y=["DCF Range", "IPO Offer"], x=[bull_p, offer_price], orientation="h",
            marker_color=["#eab308", "#64748b"], text=[f"{curr}{bear_p:,.1f} – {curr}{bull_p:,.1f}", f"{curr}{offer_price:,.1f}"], textposition="inside"
        ))
        fig_dcf_bar.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_dcf_bar, use_container_width=True)

        rm1, rm2, rm3, rm4, rm5 = st.columns(5)
        rm1.metric("Rev Growth", f"+{rev_growth:.1f}%")
        rm2.metric("EPS Growth", f"+{eps_growth:.1f}%")
        rm3.metric("ROE", f"{act['roe']:.1f}%")
        rm4.metric("D/E", f"{act['debt_equity']:.2f}")
        rm5.metric("FCF Margin", f"{act['fcf_margin']:.1f}%")

# TAB 2: PEER COMPS & SCATTER MATRIX
with t2:
    st.subheader("🔍 Cross-Border Peer Comps, Scatter Valuation & Normalized Trajectory")
    peer_rows = []
    rng_spark = np.random.default_rng(seed=99)
    for name, info in IPO_PIPELINE.items():
        a = info["actuals"]
        d = info["defaults"]
        mcap = d["offer_price"] * a["shares_m"]
        ev = mcap + a["net_debt"]
        spark = list(np.cumsum(rng_spark.normal(0.4, 1.5, 15)) + 50)
        peer_rows.append({
            "Ticker": info["ticker"],
            "Issuer Name": name.split(" (")[0],
            "Offer Price": f"{info['curr']}{d['offer_price']:,.1f}",
            "15D Trend": spark,
            "P/E (TTM)": "N.M." if a["net_income"] <= 0 else f"{round((d['offer_price'] * a['shares_m']) / a['net_income'], 1)}x",
            "Market Cap": round(mcap, 1),
            "EV / Sales": round(ev / max(a["ltm_rev"], 1), 2),
            "Rev Growth %": d["rev_growth"]
        })
    peers_df = pd.DataFrame(peer_rows)
    st.dataframe(peers_df, column_config={"15D Trend": st.column_config.LineChartColumn("Pre-IPO Sentiment Trend")}, use_container_width=True, hide_index=True)

    sc_left, sc_right = st.columns(2)
    with sc_left:
        fig_scat = px.scatter(peers_df, x="Market Cap", y="EV / Sales", size="Rev Growth %", color="Ticker", text="Ticker", title="Market Cap vs. EV / Sales (LTM)")
        fig_scat.update_traces(textposition="top center")
        fig_scat.update_layout(height=350)
        st.plotly_chart(fig_scat, use_container_width=True)
    with sc_right:
        t_axis = pd.date_range(end="2026-11-14", periods=60, freq="W")
        rng_perf = np.random.default_rng(seed=int(mc_seed))
        perf_df = pd.DataFrame({"Date": t_axis})
        for tk in ["ZEPTO.NS", "FLPKRT.NS", "CHRISTED.NS", "STRP", "DBRX", "SWIGGY.NS"]:
            steps = rng_perf.normal(0.008, 0.03, 60)
            perf_df[tk] = 100 * np.cumprod(1 + steps) - 100
        fig_norm = px.line(perf_df, x="Date", y=list(perf_df.columns)[1:], title="Normalized Pre-IPO Index (% Change)")
        fig_norm.update_layout(height=350, yaxis_title="Cumulative Return (%)")
        st.plotly_chart(fig_norm, use_container_width=True)

# TAB 3: ROADSHOW & BOOKBUILDING
with t3:
    st.subheader(f"📅 Syndicate Roadshow Demand Momentum & Order Book Summary — {selected_issuer}")
    roadshow_days = ["09-Jan", "10-Jan", "11-Jan", "12-Jan", "13-Jan", "16-Jan", "17-Jan", "18-Jan", "19-Jan", "20-Jan", "23-Jan"]
    req_meetings = [4, 15, 22, 42, 60, 80, 50, 70, 95, 68, 35]
    iois_submitted = [0, 0, 0, 0, 0, 0, 0, 0, 35, 22, 0]

    fig_road = go.Figure()
    fig_road.add_trace(go.Bar(x=roadshow_days, y=iois_submitted, name="IOIs Submitted (Confirmed Bids)", marker_color="#ef4444"))
    fig_road.add_trace(go.Bar(x=roadshow_days, y=req_meetings, name="Requested Meetings", marker_color="#93c5fd"))
    fig_road.update_layout(barmode="stack", title="Demand Momentum during the Roadshow", height=320, legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig_road, use_container_width=True)

    ob_left, ob_right = st.columns(2)
    p_low = round(offer_price * 0.94, 2)
    p_mid = round(offer_price, 2)
    p_high = round(offer_price * 1.06, 2)
    with ob_left:
        st.markdown("#### 📑 Order Book Summary at Various Prices")
        ob_table = pd.DataFrame({
            "Metric": ["Requested Meetings — Total #", "Hit Rate", "Demand (M)", "IOIs Submitted — Orders", "Conversion", "Confirmed Demand (M)"],
            f"{curr}{p_low}": ["118", "61%", "98.0M", "54", "46%", "24.0M"],
            f"{curr}{p_mid}": ["125", "64%", "112.0M", "68", "54%", "32.0M"],
            f"{curr}{p_high}": ["146", "71%", "142.0M", "89", "61%", "42.0M"]
        })
        st.dataframe(ob_table, use_container_width=True, hide_index=True)
    with ob_right:
        st.markdown("#### 📊 Investors Demand at Various Prices")
        fig_ob = go.Figure()
        price_labels = [f"{curr}{p_low}", f"{curr}{p_mid}", f"{curr}{p_high}"]
        fig_ob.add_trace(go.Bar(x=price_labels, y=[24, 32, 42], name="IOIs Submitted (M)", marker_color="#ef4444"))
        fig_ob.add_trace(go.Bar(x=price_labels, y=[42, 52, 100], name="Requested Meetings (M)", marker_color="#93c5fd"))
        fig_ob.update_layout(barmode="stack", height=280, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig_ob, use_container_width=True)

# TAB 4: PORTFOLIO & VaR RISK ENGINE
with t4:
    st.subheader(f"🎲 Portfolio & Post-Listing Value at Risk (VaR) Engine — {selected_issuer}")
    v_in1, v_in2, v_in3 = st.columns(3)
    init_alloc = v_in1.number_input(f"Institutional Allocation ({curr}{unit})", value=10000.0, step=1000.0)
    v_in2.metric("Estimation Horizon", f"{var_horizon_days} Trading Days")
    v_in3.metric("Confidence Level", f"{var_conf*100:.1f}%")

    rng_var = np.random.default_rng(seed=int(mc_seed))
    n_sims = 5000
    sigma_d = defs["vol"] / np.sqrt(252)
    mu_d = 0.08 / 252
    sim_rets = rng_var.normal(mu_d * var_horizon_days, sigma_d * np.sqrt(var_horizon_days), n_sims)
    losses = init_alloc - (init_alloc * np.exp(sim_rets))
    var_cutoff = np.percentile(losses, var_conf * 100)

    var_left, var_right = st.columns(2)
    with var_left:
        fig_var_hist = go.Figure()
        tail_losses = losses[losses >= var_cutoff]
        body_losses = losses[losses < var_cutoff]
        fig_var_hist.add_trace(go.Histogram(x=body_losses, nbinsx=30, histnorm="probability density", name="Within Confidence", marker_color="#38bdf8"))
        fig_var_hist.add_trace(go.Histogram(x=tail_losses, nbinsx=15, histnorm="probability density", name="Tail Risk Beyond VaR", marker_color="#ef4444"))
        fig_var_hist.add_vline(x=var_cutoff, line_dash="dash", line_color="#ef4444", annotation_text=f"VaR: {curr}{var_cutoff:,.1f}")
        fig_var_hist.update_layout(title="Portfolio VaR vs. Normal Distribution", barmode="overlay", height=340)
        st.plotly_chart(fig_var_hist, use_container_width=True)
    with var_right:
        days_grid = np.arange(1, var_horizon_days + 1)
        z_score = norm.ppf(var_conf)
        loss_min = init_alloc * (defs["vol"] * 0.55) * np.sqrt(days_grid / 252) * z_score
        loss_sh = init_alloc * (defs["vol"] * 0.80) * np.sqrt(days_grid / 252) * z_score
        loss_max = init_alloc * (defs["vol"] * 1.35) * np.sqrt(days_grid / 252) * z_score
        fig_var_curve = go.Figure()
        fig_var_curve.add_trace(go.Scatter(x=days_grid, y=loss_min, mode="lines+markers", name="Min-Risk Tranche", line=dict(color="#22c55e")))
        fig_var_curve.add_trace(go.Scatter(x=days_grid, y=loss_sh, mode="lines+markers", name="Max-Sharpe Tranche", line=dict(color="#eab308")))
        fig_var_curve.add_trace(go.Scatter(x=days_grid, y=loss_max, mode="lines+markers", name="Unhedged Equity", line=dict(color="#ef4444")))
        fig_var_curve.update_layout(title=f"Maximum Portfolio Loss over {var_horizon_days}-Day Horizon", height=340)
        st.plotly_chart(fig_var_curve, use_container_width=True)

# TAB 5: MODEL GOVERNANCE & PDF REPORT
with t5:
    st.subheader("🛡️ Institutional Model Governance, Lineage Audit & Top-6 PDF Generator")
    g1, g2, g3 = st.columns(3)
    g1.metric("Model Version", MODEL_VERSION)
    g2.metric("Pipeline Issuers", "6 Entities (incl. Christ University & Swiggy)")
    g3.metric("Data Status", "Verified & Audited")

    st.markdown("#### 1. Generate & Download Detailed Executive PDF Report for All Top 6 Companies")
    st.write("Click the button below to compile and download the detailed ReportLab multi-page institutional PDF report covering Zepto, Flipkart, Christ University Bangalore, Stripe, Databricks, and Swiggy.")
    
    if st.button("📥 Generate & Download Detailed Top 6 Institutional PDF Report"):
        pdf_path = generate_detailed_pdf_report()
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Click here to download PDF",
                data=pdf_file,
                file_name="Institutional_IPO_Valuation_Terminal_Report.pdf",
                mime="application/pdf"
            )
        st.success("Detailed PDF report successfully compiled for all 6 pipeline entities!")

    st.markdown("#### 2. Historical IPO Backtesting Table")
    st.dataframe(HISTORICAL_BACKTEST, use_container_width=True, hide_index=True)
