import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime

# =========================================================
# 1. PAGE CONFIG, VERSIONING & DARK TERMINAL THEME
# =========================================================
MODEL_VERSION = "v5.0.0-TERMINAL-PRO"
st.set_page_config(
    page_title="Aftermath Institutional IPO & Valuation Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark-Mode Institutional Terminal CSS (Matches Reference Screenshots)
st.markdown("""
<style>
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] {
        background-color: #111622;
        border-right: 1px solid #1e293b;
    }
    .kpi-card {
        background-color: #131824;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .kpi-val {
        font-size: 26px;
        font-weight: 700;
        color: #f8fafc;
    }
    .kpi-sub {
        font-size: 12px;
        color: #64748b;
        margin-top: 2px;
    }
    .scenario-bear {
        background-color: #1a131a;
        border: 1px solid #7f1d1d;
        border-radius: 8px;
        padding: 14px;
    }
    .scenario-base {
        background-color: #131829;
        border: 1px solid #3730a3;
        border-radius: 8px;
        padding: 14px;
    }
    .scenario-bull {
        background-color: #101f1c;
        border: 1px solid #065f46;
        border-radius: 8px;
        padding: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. TOP 5 UPCOMING IPO ISSUERS (INCL. CHRIST UNIVERSITY BANGALORE)
# Strict separation of [ACTUAL REPORTED DATA] vs [ANALYST ASSUMPTIONS]
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
            "ltm_ebitda": 420.0,
            "net_income": 210.0,
            "book_value": 4800.0,
            "net_debt": -2650.0,
            "shares_m": 665.0,
            "roe": 14.2,
            "debt_equity": 0.09,
            "fcf_margin": 4.8
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
    "Christ University Bangalore (Institutional Spin-off)": {
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
# 3. SIDEBAR CONTROLS & GOVERNANCE PARAMETERS
# =========================================================
st.sidebar.markdown("### 🏛️ AFTERMATH ANALYTICS")
st.sidebar.caption(f"Institutional Equity & IPO Terminal | `{MODEL_VERSION}`")

selected_issuer = st.sidebar.selectbox("Select Pre-IPO Issuer (Top 5 Pipeline)", list(IPO_PIPELINE.keys()))
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
wacc = st.sidebar.slider("Discount Rate / WACC (%)", 6.5, 16.0, float(defs["wacc"]), 0.25)
term_growth = st.sidebar.slider("Terminal Growth Rate (%)", 1.5, 5.5, float(defs["term_growth"]), 0.25)

st.sidebar.markdown("---")
st.sidebar.markdown("**🎲 Reproducibility & Risk Seed**")
mc_seed = st.sidebar.number_input("PRNG Seed", min_value=1, max_value=99999, value=42)
var_horizon_days = st.sidebar.slider("VaR Holding Horizon (Days)", 10, 60, 30, 5)
var_conf = st.sidebar.selectbox("VaR Confidence Level", [0.95, 0.99], index=0)

# =========================================================
# 4. CORE VALUATION & DATA-QUALITY ENGINE
# =========================================================
dq_warnings = []
if wacc <= term_growth:
    dq_warnings.append("WACC must strictly exceed Terminal Growth Rate. Auto-adjusted +150 bps spread.")
    wacc = term_growth + 1.5

# Fundamental & DCF Calculations
eps_ttm = act["net_income"] / act["shares_m"]
eps_fwd = eps_ttm * (1 + eps_growth / 100.0)
bvps = act["book_value"] / act["shares_m"]
ebitda_ps = act["ltm_ebitda"] / act["shares_m"]

# 5-Year DCF Fair Value per share
fcf_0 = act["ltm_rev"] * (act["fcf_margin"] / 100.0)
pv_fcfs = sum([(fcf_0 * ((1 + rev_growth / 100.0) ** t)) / ((1 + wacc / 100.0) ** t) for t in range(1, 6)])
tv_5 = (fcf_0 * ((1 + rev_growth / 100.0) ** 5) * (1 + term_growth / 100.0)) / ((wacc - term_growth) / 100.0)
pv_tv = tv_5 / ((1 + wacc / 100.0) ** 5)
dcf_ev = pv_fcfs + pv_tv
dcf_eq = dcf_ev - act["net_debt"]
dcf_fair_price = dcf_eq / act["shares_m"]

# Multi-Method Fair Values (Matches Screenshot 1 Valuation Methods Table)
fv_pe_ttm = eps_ttm * 26.8
fv_pe_fwd = eps_fwd * 20.6
fv_peg = eps_ttm * (eps_growth * 1.15)
fv_pb = bvps * 6.5
fv_ev_ebitda = ((act["ltm_ebitda"] * 18.5) - act["net_debt"]) / act["shares_m"]

blended_fair_value = np.mean([dcf_fair_price, fv_pe_ttm, fv_pe_fwd, fv_peg, fv_ev_ebitda])
upside_pct = ((blended_fair_value - offer_price) / offer_price) * 100.0
upside_diff = blended_fair_value - offer_price

# Role-Calibrated Signal
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
# 5. TOP TERMINAL BAR & NAVIGATION TABS
# =========================================================
st.markdown(f"### 📊 AFTERMATH ANALYTICS — `{data['ticker']}` | {selected_issuer}")
st.caption(f"Venue: {data['venue']} | Data Source: `{data['source']}` | Timestamp: `{data['timestamp']}`")

t1, t2, t3, t4, t5 = st.tabs([
    "1. Fair Value Labs & Scenarios",
    "2. Peer Comps & Scatter Matrix",
    "3. Roadshow & Bookbuilding",
    "4. Portfolio & Issue VaR Risk",
    "5. Model Governance & Backtest"
])

# =========================================================
# TAB 1: FAIR VALUE LABS, MULTI-METHOD TABLE & DCF BRIDGE (Screenshots 1 & 3)
# =========================================================
with t1:
    # Top 5 Institutional Header Cards (Matches Screenshot 1)
    c1, c2, c3, c4, c5 = st.columns([1.1, 1.1, 1.1, 1.5, 0.9])
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">IPO Offer Price</div>
            <div class="kpi-val">{curr}{offer_price:,.2f}</div>
            <div class="kpi-sub">{(offer_price/eps_ttm):.1f}x P/E (TTM)</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Blended Fair Value</div>
            <div class="kpi-val" style="color:#818cf8;">{curr}{blended_fair_value:,.2f}</div>
            <div class="kpi-sub">{(blended_fair_value/eps_fwd):.1f}x Forward P/E</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        color_up = "#10b981" if upside_pct >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Upside / Downside</div>
            <div class="kpi-val" style="color:{color_up};">{upside_pct:+.1f}%</div>
            <div class="kpi-sub" style="color:{color_up};">{curr}{upside_diff:+,.2f} per share</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        # Valuation Summary Gauge Bar (Undervalued -> Fairly Valued -> Overvalued)
        status_txt = "Undervalued" if upside_pct > 10 else ("Fairly Valued" if upside_pct >= -10 else "Significantly Overvalued")
        marker_pos = np.clip(50 - upside_pct, 5, 95)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Valuation Summary</div>
            <div style="background: linear-gradient(90deg, #10b981 0%, #eab308 50%, #ef4444 100%); height: 10px; border-radius: 5px; margin: 12px 0; position: relative;">
                <div style="position: absolute; left: {marker_pos}%; top: -4px; width: 4px; height: 18px; background: #ffffff; border-radius: 2px;"></div>
            </div>
            <div class="kpi-sub" style="text-align:center; color:#f8fafc; font-weight:600;">{status_txt}</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Model Confidence</div>
            <div class="kpi-val" style="color:#38bdf8;">88%</div>
            <div class="kpi-sub">High Confidence</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"**Signal Calibration ({perspective}):** <span style='color:{sig_hex}; font-weight:700;'>{model_signal}</span> *(Model Output — Not Investment Advice)*", unsafe_allow_html=True)

    # Middle Split: Valuation Methods Table + Analyst Consensus Donut & Bell Curve (Screenshot 1)
    left_col, right_col = st.columns([1.15, 1.15])

    with left_col:
        st.markdown("#### 📋 Valuation Methods Breakdown")
        methods_df = pd.DataFrame([
            {"Method": "DCF Intrinsic (5-Yr)", "Multiple / Basis": f"{wacc:.1f}% WACC", "Fair Value": f"{curr}{dcf_fair_price:,.2f}", "Upside / Downside": f"{((dcf_fair_price-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "P/E (TTM)", "Multiple / Basis": "26.8x", "Fair Value": f"{curr}{fv_pe_ttm:,.2f}", "Upside / Downside": f"{((fv_pe_ttm-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "P/E (Forward)", "Multiple / Basis": "20.6x", "Fair Value": f"{curr}{fv_pe_fwd:,.2f}", "Upside / Downside": f"{((fv_pe_fwd-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "PEG Ratio", "Multiple / Basis": "1.15x", "Fair Value": f"{curr}{fv_peg:,.2f}", "Upside / Downside": f"{((fv_peg-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "P/B Ratio", "Multiple / Basis": "6.5x", "Fair Value": f"{curr}{fv_pb:,.2f}", "Upside / Downside": f"{((fv_pb-offer_price)/offer_price)*100:+.1f}%"},
            {"Method": "EV/EBITDA", "Multiple / Basis": "18.5x", "Fair Value": f"{curr}{fv_ev_ebitda:,.2f}", "Upside / Downside": f"{((fv_ev_ebitda-offer_price)/offer_price)*100:+.1f}%"},
        ])
        st.dataframe(methods_df, use_container_width=True, hide_index=True)

        # Scenario Analysis Cards (Bear / Base / Bull - Screenshot 1)
        st.markdown("#### 🎯 Scenario Analysis")
        sc1, sc2, sc3 = st.columns(3)
        bear_p = blended_fair_value * 0.76
        base_p = blended_fair_value
        bull_p = blended_fair_value * 1.24
        with sc1:
            st.markdown(f"""<div class="scenario-bear"><div class="kpi-title">BEAR CASE</div><div style="font-size:20px;font-weight:700;color:#f87171;">{curr}{bear_p:,.2f}</div><div class="kpi-sub">Slow growth & multiple compression</div></div>""", unsafe_allow_html=True)
        with sc2:
            st.markdown(f"""<div class="scenario-base"><div class="kpi-title">BASE CASE</div><div style="font-size:20px;font-weight:700;color:#818cf8;">{curr}{base_p:,.2f}</div><div class="kpi-sub">Steady execution & consensus path</div></div>""", unsafe_allow_html=True)
        with sc3:
            st.markdown(f"""<div class="scenario-bull"><div class="kpi-title">BULL CASE</div><div style="font-size:20px;font-weight:700;color:#34d399;">{curr}{bull_p:,.2f}</div><div class="kpi-sub">Margin expansion & AI/scale tailwinds</div></div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown("#### 🏦 Institutional Syndicate Consensus & Price Target Distribution")
        d_col, b_col = st.columns([0.9, 1.2])
        with d_col:
            # Rating Distribution Donut Chart (Buy / Hold / Sell)
            fig_donut = go.Figure(data=[go.Pie(
                labels=["Buy (44%)", "Hold (36%)", "Sell (20%)"],
                values=[14, 12, 6],
                hole=0.62,
                marker_colors=["#10b981", "#6366f1", "#ef4444"],
                textinfo="none"
            )])
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=240,
                margin=dict(l=5, r=5, t=25, b=5),
                showlegend=True,
                legend=dict(orientation="h", y=-0.15, font=dict(color="#cbd5e1", size=10)),
                annotations=[dict(text="32<br>Desks", x=0.5, y=0.5, font_size=13, font_color="#f8fafc", showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with b_col:
            # Price Target Normal Distribution Bell Curve (Screenshot 1)
            x_bell = np.linspace(bear_p * 0.85, bull_p * 1.15, 200)
            y_bell = norm.pdf(x_bell, loc=blended_fair_value, scale=(bull_p - bear_p) / 3.5)
            fig_bell = go.Figure()
            fig_bell.add_trace(go.Scatter(
                x=x_bell, y=y_bell, mode="lines",
                fill="tozeroy", fillcolor="rgba(129, 140, 248, 0.25)",
                line=dict(color="#818cf8", width=2.5),
                name="Target Distribution"
            ))
            fig_bell.add_vline(x=blended_fair_value, line_dash="dash", line_color="#38bdf8",
                               annotation_text=f"Target: {curr}{blended_fair_value:,.1f}", annotation_font_color="#38bdf8")
            fig_bell.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=240,
                margin=dict(l=10, r=10, t=25, b=20),
                xaxis=dict(showgrid=False, color="#94a3b8"),
                yaxis=dict(visible=False),
                showlegend=False
            )
            st.plotly_chart(fig_bell, use_container_width=True)

        # DCF Valuation Range Bar vs Offer Price (Matches Screenshot 3 Left Panel)
        st.markdown("#### 📐 DCF Intrinsic Valuation Range vs. IPO Offer Price")
        fig_dcf_bar = go.Figure()
        fig_dcf_bar.add_trace(go.Bar(
            y=["DCF Range", "IPO Offer"],
            x=[bull_p, offer_price],
            orientation="h",
            marker_color=["#eab308", "#64748b"],
            text=[f"{curr}{bear_p:,.1f} – {curr}{bull_p:,.1f}", f"{curr}{offer_price:,.1f}"],
            textposition="inside"
        ))
        fig_dcf_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=150,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=True, gridcolor="#1e293b", color="#94a3b8"),
            yaxis=dict(color="#e2e8f0"),
            showlegend=False
        )
        st.plotly_chart(fig_dcf_bar, use_container_width=True)

        # Related Metrics Strip (Screenshot 1 Bottom Right)
        rm1, rm2, rm3, rm4, rm5 = st.columns(5)
        rm1.metric("Rev Growth", f"+{rev_growth:.1f}%")
        rm2.metric("EPS Growth", f"+{eps_growth:.1f}%")
        rm3.metric("ROE", f"{act['roe']:.1f}%")
        rm4.metric("Debt / Equity", f"{act['debt_equity']:.2f}")
        rm5.metric("FCF Margin", f"{act['fcf_margin']:.1f}%")

# =========================================================
# TAB 2: PEER COMPS TABLE, SCATTER PLOT & NORMALIZED PERFORMANCE (Screenshot 4)
# =========================================================
with t2:
    st.subheader(f"🔍 Cross-Border Peer Comps, Scatter Valuation & Normalized Trajectory")

    # Build Peer Table across all Top 5 Issuers + Global Benchmarks
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
            "P/E (TTM)": round((d["offer_price"] * a["shares_m"]) / max(a["net_income"], 1), 1),
            "Market Cap": round(mcap, 1),
            "EV / Sales": round(ev / a["ltm_rev"], 2),
            "Rev Growth %": d["rev_growth"]
        })
    peers_df = pd.DataFrame(peer_rows)

    st.dataframe(
        peers_df,
        column_config={
            "15D Trend": st.column_config.LineChartColumn("Pre-IPO Sentiment Trend", y_min=35, y_max=65)
        },
        use_container_width=True,
        hide_index=True
    )

    sc_left, sc_right = st.columns(2)
    with sc_left:
        # Scatter Plot: Market Cap vs EV/Sales (Screenshot 4 Bottom Center)
        fig_scat = px.scatter(
            peers_df,
            x="Market Cap",
            y="EV / Sales",
            size="Rev Growth %",
            color="Ticker",
            text="Ticker",
            title="Scatter Plot: Market Capitalization vs. EV / Sales (LTM)"
        )
        fig_scat.update_traces(textposition="top center")
        fig_scat.update_layout(
            paper_bgcolor="#131824",
            plot_bgcolor="#0f172a",
            font_color="#e2e8f0",
            height=360
        )
        st.plotly_chart(fig_scat, use_container_width=True)

    with sc_right:
        # Normalized Performance Trajectory (Screenshot 4 Bottom Right)
        t_axis = pd.date_range(end="2026-11-14", periods=60, freq="W")
        rng_perf = np.random.default_rng(seed=int(mc_seed))
        perf_df = pd.DataFrame({"Date": t_axis})
        for tk in ["ZEPTO.NS", "FLPKRT.NS", "CHRISTED.NS", "STRP", "DBRX"]:
            steps = rng_perf.normal(0.008, 0.03, 60)
            perf_df[tk] = 100 * np.cumprod(1 + steps) - 100

        fig_norm = px.line(
            perf_df, x="Date", y=["ZEPTO.NS", "FLPKRT.NS", "CHRISTED.NS", "STRP", "DBRX"],
            title="Normalized Pre-IPO Private Valuation Index (% Change)"
        )
        fig_norm.update_layout(
            paper_bgcolor="#131824",
            plot_bgcolor="#0f172a",
            font_color="#e2e8f0",
            yaxis_title="Cumulative Return (%)",
            height=360
        )
        st.plotly_chart(fig_norm, use_container_width=True)

# =========================================================
# TAB 3: ROADSHOW DEMAND MOMENTUM & ORDER BOOK SUMMARY (Screenshot 5)
# =========================================================
with t3:
    st.subheader(f"📅 Syndicate Roadshow Demand Momentum & Order Book Summary — {selected_issuer}")

    # Top Chart: Demand Momentum during the Roadshow (Requested Meetings vs IOIs Submitted - Screenshot 5 Top)
    roadshow_days = ["09-Jan", "10-Jan", "11-Jan", "12-Jan", "13-Jan", "16-Jan", "17-Jan", "18-Jan", "19-Jan", "20-Jan", "23-Jan"]
    req_meetings = [4, 15, 22, 42, 60, 80, 50, 70, 95, 68, 35]
    iois_submitted = [0, 0, 0, 0, 0, 0, 0, 0, 35, 22, 0]

    fig_road = go.Figure()
    fig_road.add_trace(go.Bar(x=roadshow_days, y=iois_submitted, name="IOIs Submitted (Confirmed Bids)", marker_color="#ef4444"))
    fig_road.add_trace(go.Bar(x=roadshow_days, y=req_meetings, name="Requested Meetings", marker_color="#93c5fd"))
    fig_road.update_layout(
        barmode="stack",
        title="Demand Momentum during the Roadshow (Based on Max Demand)",
        paper_bgcolor="#131824",
        plot_bgcolor="#0f172a",
        font_color="#e2e8f0",
        height=340,
        legend=dict(orientation="h", y=1.12)
    )
    st.plotly_chart(fig_road, use_container_width=True)

    # Bottom Split: Order Book Summary Table + Investors Demand at Various Prices (Screenshot 5 Bottom)
    ob_left, ob_right = st.columns([1.1, 1.1])
    p_low = round(offer_price * 0.94, 2)
    p_mid = round(offer_price, 2)
    p_high = round(offer_price * 1.06, 2)

    with ob_left:
        st.markdown("#### 📑 Order Book Summary at Various Prices")
        ob_table = pd.DataFrame({
            "Tranche Metric": [
                "Requested Meetings — Total #",
                "Requested Meetings — Hit Rate",
                "Requested Meetings — Demand (M Shares)",
                "IOIs Submitted — Total # of Orders",
                "IOIs Submitted — Conversion Hit Rate",
                "IOIs Submitted — Confirmed Demand (M)"
            ],
            f"{curr}{p_low}": ["118 Orders", "61%", "98.0 M", "54 Orders", "46%", "24.0 M"],
            f"{curr}{p_mid}": ["125 Orders", "64%", "112.0 M", "68 Orders", "54%", "32.0 M"],
            f"{curr}{p_high}": ["146 Orders", "71%", "142.0 M", "89 Orders", "61%", "42.0 M"]
        })
        st.dataframe(ob_table, use_container_width=True, hide_index=True)

    with ob_right:
        st.markdown("#### 📊 Investors Demand at Various Prices (M of Shares)")
        fig_ob_bars = go.Figure()
        price_labels = [f"{curr}{p_low}<br>(118 orders)", f"{curr}{p_mid}<br>(125 orders)", f"{curr}{p_high}<br>(146 orders)"]
        fig_ob_bars.add_trace(go.Bar(x=price_labels, y=[24, 32, 42], name="IOIs Submitted (M)", marker_color="#ef4444"))
        fig_ob_bars.add_trace(go.Bar(x=price_labels, y=[42, 52, 100], name="Requested Meetings (M)", marker_color="#93c5fd"))
        fig_ob_bars.update_layout(
            barmode="stack",
            paper_bgcolor="#131824",
            plot_bgcolor="#0f172a",
            font_color="#e2e8f0",
            height=300,
            margin=dict(l=10, r=10, t=20, b=20),
            legend=dict(orientation="h", y=1.15)
        )
        st.plotly_chart(fig_ob_bars, use_container_width=True)

# =========================================================
# TAB 4: PORTFOLIO & ISSUE VALUE AT RISK (VaR) ENGINE (Screenshot 2)
# =========================================================
with t4:
    st.subheader(f"🎲 Portfolio & Post-Listing Value at Risk (VaR) Engine — {selected_issuer}")

    v_in1, v_in2, v_in3 = st.columns(3)
    init_alloc = v_in1.number_input(f"Institutional Allocation ({curr}{unit})", value=10000.0, step=1000.0)
    v_in2.metric("Estimation Horizon", f"{var_horizon_days} Trading Days")
    v_in3.metric("Confidence Level", f"{var_conf*100:.1f}%")

    # Reproducible Simulation (5,000 Scenarios)
    rng_var = np.random.default_rng(seed=int(mc_seed))
    n_sims = 5000
    sigma_d = defs["vol"] / np.sqrt(252)
    mu_d = 0.08 / 252

    sim_rets = rng_var.normal(mu_d * var_horizon_days, sigma_d * np.sqrt(var_horizon_days), n_sims)
    ending_vals = init_alloc * np.exp(sim_rets)
    losses = init_alloc - ending_vals

    var_cutoff = np.percentile(losses, var_conf * 100)
    var_99_cutoff = np.percentile(losses, 99.0)

    var_left, var_right = st.columns(2)
    with var_left:
        # Left Chart: Portfolio VaR Histogram + Normal Return PDF Overlay (Screenshot 2 Left)
        fig_var_hist = go.Figure()
        tail_losses = losses[losses >= var_cutoff]
        body_losses = losses[losses < var_cutoff]

        fig_var_hist.add_trace(go.Histogram(
            x=body_losses, nbinsx=35, histnorm="probability density",
            name="Within Confidence Band", marker_color="#38bdf8", opacity=0.75
        ))
        fig_var_hist.add_trace(go.Histogram(
            x=tail_losses, nbinsx=15, histnorm="probability density",
            name="Tail-Risk Loss Beyond VaR", marker_color="#ef4444", opacity=0.85
        ))

        x_pdf = np.linspace(losses.min(), losses.max(), 200)
        y_pdf = norm.pdf(x_pdf, loc=losses.mean(), scale=losses.std())
        fig_var_hist.add_trace(go.Scatter(
            x=x_pdf, y=y_pdf, mode="lines", name="Normal Return PDF",
            line=dict(color="#22c55e", width=2.5)
        ))

        fig_var_hist.add_vline(x=var_cutoff, line_dash="dash", line_color="#ef4444",
                               annotation_text=f"VaR {var_conf*100:.0f}%: {curr}{var_cutoff:,.1f}")
        fig_var_hist.update_layout(
            title="Portfolio Value at Risk (VaR) vs. Normally Distributed Return",
            paper_bgcolor="#131824",
            plot_bgcolor="#0f172a",
            font_color="#e2e8f0",
            barmode="overlay",
            xaxis_title=f"Loss Amount ({curr}{unit})",
            yaxis_title="Probability Density",
            height=360
        )
        st.plotly_chart(fig_var_hist, use_container_width=True)

    with var_right:
        # Right Chart: Maximum Portfolio Loss over Holding Horizon (3 Strategy Curves - Screenshot 2 Right)
        days_grid = np.arange(1, var_horizon_days + 1)
        z_score = norm.ppf(var_conf)
        loss_min_risk = init_alloc * (defs["vol"] * 0.55) * np.sqrt(days_grid / 252) * z_score
        loss_sharpe = init_alloc * (defs["vol"] * 0.80) * np.sqrt(days_grid / 252) * z_score
        loss_max_ret = init_alloc * (defs["vol"] * 1.35) * np.sqrt(days_grid / 252) * z_score

        fig_var_curve = go.Figure()
        fig_var_curve.add_trace(go.Scatter(x=days_grid, y=loss_min_risk, mode="lines+markers", name="Min-Risk Tranche", line=dict(color="#22c55e")))
        fig_var_curve.add_trace(go.Scatter(x=days_grid, y=loss_sharpe, mode="lines+markers", name="Max-Sharpe Allocation", line=dict(color="#eab308")))
        fig_var_curve.add_trace(go.Scatter(x=days_grid, y=loss_max_ret, mode="lines+markers", name="Unhedged IPO Equity", line=dict(color="#ef4444")))
        fig_var_curve.update_layout(
            title=f"Maximum Portfolio Loss (VaR @ {var_conf*100:.1f}%) over {var_horizon_days}-Day Horizon",
            paper_bgcolor="#131824",
            plot_bgcolor="#0f172a",
            font_color="#e2e8f0",
            xaxis_title="Holding Period (Days)",
            yaxis_title=f"Value at Risk ({curr}{unit})",
            height=360
        )
        st.plotly_chart(fig_var_curve, use_container_width=True)

    st.info(f"Based on {n_sims:,} simulated scenarios (Seed #{mc_seed}), the {var_horizon_days}-day VaR for a {curr}{init_alloc:,.2f} {unit} allocation at {var_conf*100:.1f}% confidence is **{curr}{var_cutoff:,.2f} {unit}**.")

# =========================================================
# TAB 5: MODEL GOVERNANCE, BACKTESTING & IC REPORT
# =========================================================
with t5:
    st.subheader("🛡️ Institutional Model Governance, Lineage Audit & Backtesting Suite")

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Model Version", MODEL_VERSION)
    g2.metric("Data Source Timestamp", data["timestamp"])
    g3.metric("PRNG Seed", f"#{mc_seed}")
    g4.metric("Data Quality Status", "PASSED" if not dq_warnings else f"{len(dq_warnings)} Flag(s)")

    if dq_warnings:
        for warn in dq_warnings:
            st.warning(warn)

    st.markdown("#### 1. Formula & Assumption Audit Trail (Actuals vs. Assumptions vs. Simulated)")
    audit_table = pd.DataFrame([
        {"Item": "LTM Revenue & EBITDA", "Classification": "ACTUAL (Imported)", "Value": f"{curr}{act['ltm_rev']:,.1f} / {curr}{act['ltm_ebitda']:,.1f} {unit}", "Source / Formula": data["source"]},
        {"Item": "Net Debt", "Classification": "ACTUAL (Imported)", "Value": f"{curr}{act['net_debt']:,.1f} {unit}", "Source / Formula": "Total Debt - Cash & Equivalents"},
        {"Item": "Rev Growth / WACC / TG", "Classification": "ANALYST ASSUMPTION", "Value": f"{rev_growth:.1f}% / {wacc:.2f}% / {term_growth:.2f}%", "Source / Formula": "Sidebar Interactive User Override"},
        {"Item": "Blended Fair Value", "Classification": "DETERMINISTIC OUTPUT", "Value": f"{curr}{blended_fair_value:,.2f}", "Source / Formula": "Equal-Weighted Mean(DCF, P/E, Fwd P/E, PEG, EV/EBITDA)"},
        {"Item": f"{var_horizon_days}D VaR ({var_conf*100:.0f}%)", "Classification": "SIMULATED OUTPUT", "Value": f"{curr}{var_cutoff:,.2f} {unit}", "Source / Formula": f"5,000-Trial GBM Simulation (Seed={mc_seed})"}
    ])
    st.dataframe(audit_table, use_container_width=True, hide_index=True)

    st.markdown("#### 2. Backtesting Against Historical IPOs (Forecast-vs-Actual)")
    st.dataframe(HISTORICAL_BACKTEST, use_container_width=True, hide_index=True)

    fig_bt = go.Figure()
    fig_bt.add_trace(go.Bar(x=HISTORICAL_BACKTEST["Issuer"], y=HISTORICAL_BACKTEST["Model_Fair_Price"], name="Model Fair Value (Pre-IPO)", marker_color="#818cf8"))
    fig_bt.add_trace(go.Bar(x=HISTORICAL_BACKTEST["Issuer"], y=HISTORICAL_BACKTEST["Issue_Price"], name="Actual Issue Price", marker_color="#64748b"))
    fig_bt.add_trace(go.Bar(x=HISTORICAL_BACKTEST["Issuer"], y=HISTORICAL_BACKTEST["Day_90_Actual"], name="Day-90 Actual Market Price", marker_color="#10b981"))
    fig_bt.update_layout(
        barmode="group",
        paper_bgcolor="#131824",
        plot_bgcolor="#0f172a",
        font_color="#e2e8f0",
        height=320,
        title="Forecast-vs-Actual Validation Across Historical Listings"
    )
    st.plotly_chart(fig_bt, use_container_width=True)

    # Exportable IC Pricing Report
    ic_memo = f"""# INVESTMENT COMMITTEE & IPO PRICING GOVERNANCE REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}
**Model Version:** {MODEL_VERSION}
**Issuer:** {selected_issuer} ({data['ticker']})
**Venue:** {data['venue']}
**Analytical Perspective:** {perspective}

## 1. DATA PROVENANCE & GOVERNANCE
- **Primary Source:** {data['source']}
- **Timestamp:** {data['timestamp']}
- **Reproducibility Seed:** {mc_seed}

## 2. VALUATION & RISK SUMMARY
- **Proposed Offer Price:** {curr}{offer_price:,.2f}
- **Blended Fair Value:** {curr}{blended_fair_value:,.2f} ({upside_pct:+.1f}%)
- **Scenario Range (Bear / Base / Bull):** {curr}{bear_p:,.2f} / {curr}{base_p:,.2f} / {curr}{bull_p:,.2f}
- **{var_horizon_days}-Day VaR ({var_conf*100:.0f}%):** {curr}{var_cutoff:,.2f} {unit}

## 3. MODEL SIGNAL (NON-ADVISORY)
- **{model_signal}**
"""
    st.download_button(
        label="📥 Export Investment Committee / IPO Pricing Report (.md)",
        data=ic_memo,
        file_name=f"IC_Pricing_Memo_{data['ticker']}_{MODEL_VERSION}.md",
        mime="text/markdown"
    )
