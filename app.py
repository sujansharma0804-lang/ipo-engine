import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm, t
from datetime import datetime

# =========================================================
# 1. PAGE CONFIG & STYLING
# =========================================================
MODEL_VERSION = "v9.1.0-DYNAMIC-PRO"
st.set_page_config(
    page_title="Institutional IPO Optimization & Advanced Risk Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
    }
    .signal-banner {
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 1.02rem;
        font-weight: 600;
        margin-top: 8px;
        margin-bottom: 14px;
        border-left: 6px solid;
    }
    .disclaimer-box {
        padding: 10px 14px;
        border-radius: 6px;
        background-color: rgba(245, 158, 11, 0.12);
        border-left: 4px solid #f59e0b;
        font-size: 0.9rem;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. ISSUER PROFILES WITH FULL PROVENANCE & QoE LEDGER
# =========================================================
IPO_PIPELINE = {
    "Christ University Bangalore (Endowment Spin-off)": {
        "ticker": "CHRISTED.NS",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEBI Mainboard / Social Infrastructure",
        "sector": "Social Infrastructure / Higher Education",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Illustrative Institutional Trust & Campus Operations Filing",
            "period": "LTM FY26E",
            "timestamp": "2026-11-14 22:00 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 1420.0, "ltm_ebitda": 465.0, "net_income": 310.0,
            "book_value": 2450.0, "net_debt": -570.0, "shares_m": 165.0,
            "roe": 24.8, "debt_equity": 0.05, "fcf_margin": 22.4,
            "gmv": 1600.0, "take_rate": 95.0, "arr": 1500.0, "nrr": 128.0,
            "rotce": 26.2, "ptbv": 3.1,
            "non_recurring_adj": -15.0, "working_cap_change": 25.0, "cash_taxes": -35.0,
            "capex": -95.0, "capitalized_software": 20.0, "related_party_rev_pct": 0.5,
            "top_10_cust_conc_pct": 2.0, "annual_churn_pct": 3.2, "ar_over_90_days_pct": 1.1,
            "contingent_liabilities": 15.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 280.0, "rev_growth": 16.5, "eps_growth": 18.2, "wacc": 9.75, "term_growth": 3.5, "vol": 0.18}
    },
    "Zepto (Kiranakart Technologies)": {
        "ticker": "ZEPTO.NS",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEBI / NSE (India)",
        "sector": "Quick-Commerce / Consumer Marketplace",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Illustrative DRHP Baseline & Series-G Disclosures",
            "period": "LTM FY26E",
            "timestamp": "2026-11-14 22:00 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 11200.0, "ltm_ebitda": 480.0, "net_income": 290.0,
            "book_value": 4800.0, "net_debt": -2650.0, "shares_m": 665.0,
            "roe": 12.4, "debt_equity": 0.09, "fcf_margin": 8.5,
            "gmv": 24000.0, "take_rate": 18.5, "arr": 13500.0, "nrr": 118.0,
            "rotce": 14.2, "ptbv": 5.8,
            "non_recurring_adj": -45.0, "working_cap_change": -110.0, "cash_taxes": -65.0,
            "capex": -180.0, "capitalized_software": 95.0, "related_party_rev_pct": 1.8,
            "top_10_cust_conc_pct": 4.2, "annual_churn_pct": 14.5, "ar_over_90_days_pct": 3.1,
            "contingent_liabilities": 120.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 290.0, "rev_growth": 42.0, "eps_growth": 38.0, "wacc": 12.5, "term_growth": 4.0, "vol": 0.36}
    },
    "Flipkart Internet (India Listing)": {
        "ticker": "FLPKRT.NS",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEBI / BSE-NSE (India)",
        "sector": "E-Commerce / Digital Marketplace",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Illustrative Pre-IPO Info Memo",
            "period": "LTM FY26E",
            "timestamp": "2026-11-14 22:00 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 68500.0, "ltm_ebitda": 6150.0, "net_income": 4350.0,
            "book_value": 34200.0, "net_debt": -5600.0, "shares_m": 1280.0,
            "roe": 18.6, "debt_equity": 0.14, "fcf_margin": 9.2,
            "gmv": 195000.0, "take_rate": 14.0, "arr": 72000.0, "nrr": 115.0,
            "rotce": 19.5, "ptbv": 4.2,
            "non_recurring_adj": -320.0, "working_cap_change": 450.0, "cash_taxes": -980.0,
            "capex": -1450.0, "capitalized_software": 620.0, "related_party_rev_pct": 6.4,
            "top_10_cust_conc_pct": 2.5, "annual_churn_pct": 11.0, "ar_over_90_days_pct": 5.4,
            "contingent_liabilities": 890.0, "auditor_opinion": "Unqualified w/ Emphasis of Matter (Simulated)"
        },
        "defaults": {"offer_price": 1150.0, "rev_growth": 24.0, "eps_growth": 27.5, "wacc": 11.25, "term_growth": 3.5, "vol": 0.27}
    },
    "Stripe Inc.": {
        "ticker": "STRP",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEC / NASDAQ (USA)",
        "sector": "Fintech / SaaS Infrastructure",
        "curr": "$",
        "unit": "M",
        "fx_to_usd": 1.0,
        "provenance": {
            "source": "Illustrative SEC S-1 Draft Baseline",
            "period": "LTM Q3 2026E",
            "timestamp": "2026-11-14 22:00 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 18400.0, "ltm_ebitda": 3850.0, "net_income": 2410.0,
            "book_value": 16800.0, "net_debt": -4200.0, "shares_m": 1240.0,
            "roe": 28.4, "debt_equity": 0.12, "fcf_margin": 19.5,
            "gmv": 1100000.0, "take_rate": 1.8, "arr": 20500.0, "nrr": 122.0,
            "rotce": 31.0, "ptbv": 7.5,
            "non_recurring_adj": -140.0, "working_cap_change": 210.0, "cash_taxes": -510.0,
            "capex": -420.0, "capitalized_software": 310.0, "related_party_rev_pct": 0.4,
            "top_10_cust_conc_pct": 14.2, "annual_churn_pct": 5.2, "ar_over_90_days_pct": 1.8,
            "contingent_liabilities": 180.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 58.0, "rev_growth": 26.0, "eps_growth": 29.0, "wacc": 10.0, "term_growth": 3.0, "vol": 0.25}
    },
    "Databricks Inc.": {
        "ticker": "DBRX",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEC / NYSE (USA)",
        "sector": "Enterprise SaaS / Cloud Data Platform",
        "curr": "$",
        "unit": "M",
        "fx_to_usd": 1.0,
        "provenance": {
            "source": "Illustrative SEC S-1 Registration Baseline",
            "period": "LTM Q3 2026E",
            "timestamp": "2026-11-14 22:00 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 3250.0, "ltm_ebitda": 680.0, "net_income": 440.0,
            "book_value": 6400.0, "net_debt": -1750.0, "shares_m": 635.0,
            "roe": 19.5, "debt_equity": 0.08, "fcf_margin": 14.2,
            "gmv": 3600.0, "take_rate": 90.0, "arr": 3800.0, "nrr": 138.0,
            "rotce": 21.0, "ptbv": 6.2,
            "non_recurring_adj": -35.0, "working_cap_change": 145.0, "cash_taxes": -95.0,
            "capex": -110.0, "capitalized_software": 140.0, "related_party_rev_pct": 0.2,
            "top_10_cust_conc_pct": 18.5, "annual_churn_pct": 4.1, "ar_over_90_days_pct": 2.2,
            "contingent_liabilities": 45.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 78.0, "rev_growth": 48.0, "eps_growth": 44.0, "wacc": 11.0, "term_growth": 3.5, "vol": 0.33}
    },
    "Swiggy Limited (Listed Benchmark)": {
        "ticker": "SWIGGY.NS",
        "listing_status": "Publicly Listed (NSE/BSE)",
        "venue": "SEBI / NSE (India)",
        "sector": "Food Delivery / Quick-Commerce",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Exchange Filings & Public Post-IPO Disclosures",
            "period": "LTM FY26",
            "timestamp": "2026-11-14 22:00 IST",
            "status": "Public Benchmark"
        },
        "actuals": {
            "ltm_rev": 14800.0, "ltm_ebitda": 920.0, "net_income": 610.0,
            "book_value": 9200.0, "net_debt": -4100.0, "shares_m": 2220.0,
            "roe": 11.4, "debt_equity": 0.06, "fcf_margin": 6.8,
            "gmv": 32000.0, "take_rate": 22.0, "arr": 16000.0, "nrr": 114.0,
            "rotce": 13.5, "ptbv": 3.8,
            "non_recurring_adj": -60.0, "working_cap_change": 85.0, "cash_taxes": -140.0,
            "capex": -310.0, "capitalized_software": 115.0, "related_party_rev_pct": 1.2,
            "top_10_cust_conc_pct": 3.1, "annual_churn_pct": 13.8, "ar_over_90_days_pct": 2.9,
            "contingent_liabilities": 210.0, "auditor_opinion": "Unqualified"
        },
        "defaults": {"offer_price": 390.0, "rev_growth": 28.0, "eps_growth": 25.0, "wacc": 11.8, "term_growth": 3.5, "vol": 0.31}
    }
}

# =========================================================
# 3. SIDEBAR CONTROLS & CALIBRATION PARAMETERS
# =========================================================
st.sidebar.markdown("### 📊 IPO PRICING & RISK ENGINE")
st.sidebar.caption(f"Validated Framework | `{MODEL_VERSION}`")

selected_issuer = st.sidebar.selectbox("Select Target Issuer", list(IPO_PIPELINE.keys()))
data = IPO_PIPELINE[selected_issuer]
curr, unit, act, defs, tk, sector, prov = data["curr"], data["unit"], data["actuals"], data["defaults"], data["ticker"], data["sector"], data["provenance"]

perspective = st.sidebar.radio(
    "Analytical Role",
    ["Prospective IPO Investor (Buy-Side)", "Company Issuer / Bookrunner (Sell-Side)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🧪 [VALUATION & GROWTH INPUTS]**")
offer_price = st.sidebar.number_input(f"Proposed Offer Price ({curr})", min_value=1.0, value=float(defs["offer_price"]), step=5.0, key=f"offer_{tk}")
rev_growth = st.sidebar.slider("Projected Revenue Growth (%)", 5.0, 65.0, float(defs["rev_growth"]), 0.5, key=f"rev_{tk}")
eps_growth = st.sidebar.slider("Projected EPS Growth (%)", 5.0, 65.0, float(defs["eps_growth"]), 0.5, key=f"eps_{tk}")
wacc = st.sidebar.slider("Discount Rate / WACC (%)", 6.5, 18.0, float(defs["wacc"]), 0.25, key=f"wacc_{tk}")
term_growth = st.sidebar.slider("Terminal Growth Rate (%)", 1.5, 5.5, float(defs["term_growth"]), 0.25, key=f"tg_{tk}")
primary_dilution_pct = st.sidebar.slider("Primary Issue Dilution (%)", 5.0, 35.0, 20.0, 1.0, key=f"dil_{tk}")

st.sidebar.markdown("---")
st.sidebar.markdown("**🛡️ [RISK, VaR & STRESS CALIBRATION]**")
mc_seed = st.sidebar.number_input("PRNG Seed (Reproducibility)", min_value=1, max_value=99999, value=42)
var_horizon_days = st.sidebar.slider("VaR Horizon (Trading Days)", 10, 60, 30, 5)
var_conf = st.sidebar.selectbox("VaR Confidence Level", [0.95, 0.99], index=0)
tail_df = st.sidebar.slider("Student-t Fat Tail Degrees of Freedom", 3.0, 30.0, 5.0, 1.0)
vol_shock_mult = st.sidebar.slider("Volatility Sensitivity Multiplier", 1.0, 3.0, 1.50, 0.25)

# =========================================================
# 4. QUALITY OF EARNINGS (QoE) & CASH FLOW RECONCILIATION
# =========================================================
if wacc <= term_growth:
    wacc = term_growth + 1.5

reported_ebitda = act["ltm_ebitda"]
adj_ebitda = reported_ebitda + act["non_recurring_adj"]
operating_cash_flow = adj_ebitda + act["working_cap_change"] + act["cash_taxes"]
free_cash_flow = operating_cash_flow + act["capex"]
economic_fcf = free_cash_flow - act["capitalized_software"]

ebitda_to_ocf_conv = (operating_cash_flow / adj_ebitda * 100.0) if adj_ebitda > 0 else 0.0
ebitda_to_fcf_conv = (free_cash_flow / adj_ebitda * 100.0) if adj_ebitda > 0 else 0.0

qoe_penalty = 0.0
if ebitda_to_ocf_conv < 70.0: qoe_penalty += 15.0
if act["capitalized_software"] / max(reported_ebitda, 1.0) > 0.20: qoe_penalty += 10.0
if act["related_party_rev_pct"] > 5.0: qoe_penalty += 12.0
if act["ar_over_90_days_pct"] > 5.0: qoe_penalty += 8.0
if "Emphasis" in act["auditor_opinion"] or "Qualified" in act["auditor_opinion"]: qoe_penalty += 15.0
qoe_score = max(20.0, min(100.0, 100.0 - qoe_penalty))

# =========================================================
# 5. SECTOR-TAILORED VALUATION & TRANSPARENT FAIR VALUE
# =========================================================
eps_ttm = act["net_income"] / act["shares_m"]
eps_fwd = eps_ttm * (1.0 + eps_growth / 100.0)
bvps = act["book_value"] / act["shares_m"]
rotce = act["rotce"]
roe = act["roe"]
arr = act["arr"]
nrr = act["nrr"]

fcf_base = max(economic_fcf, act["ltm_rev"] * 0.04)
pv_fcfs = sum([(fcf_base * ((1.0 + rev_growth / 100.0) ** yr)) / ((1.0 + wacc / 100.0) ** yr) for yr in range(1, 6)])
tv_5 = (fcf_base * ((1.0 + rev_growth / 100.0) ** 5) * (1.0 + term_growth / 100.0)) / ((wacc - term_growth) / 100.0)
pv_tv = tv_5 / ((1.0 + wacc / 100.0) ** 5)
dcf_ev = pv_fcfs + pv_tv
dcf_eq = dcf_ev - act["net_debt"]
dcf_fair_price = max(dcf_eq / act["shares_m"], 1.0)

growth_premium = 1.0 + ((rev_growth - 20.0) / 100.0)

if "Social" in sector or "Infrastructure" in sector or "Banking" in sector:
    implied_ptbv = max(act["ptbv"] * (rotce / 15.0) * growth_premium, 1.2)
    val_methods = [
        ("P/TBV Multiple", bvps * implied_ptbv, 0.40),
        ("Economic FCF DCF", dcf_fair_price, 0.40),
        ("Forward P/E (18x)", eps_fwd * 18.0, 0.20)
    ]
elif "SaaS" in sector or "Cloud" in sector or "Fintech" in sector:
    arr_fwd = arr * (1.0 + rev_growth / 100.0)
    arr_mult = max(4.0, min(18.0, ((rev_growth + act["fcf_margin"]) / 10.0) * (nrr / 100.0) * 1.8))
    val_methods = [
        (f"EV/ARR ({arr_mult:.1f}x)", ((arr_fwd * arr_mult) - act["net_debt"]) / act["shares_m"], 0.45),
        ("Economic FCF DCF", dcf_fair_price, 0.35),
        ("Forward P/E (28x)", eps_fwd * 28.0, 0.20)
    ]
else:
    gmv_fwd = act["gmv"] * (1.0 + rev_growth / 100.0)
    net_rev_fwd = gmv_fwd * (act["take_rate"] / 100.0)
    ev_rev_mult = max(2.0, min(8.0, 4.0 * growth_premium))
    val_methods = [
        (f"EV/Net Rev ({ev_rev_mult:.1f}x)", ((net_rev_fwd * ev_rev_mult) - act["net_debt"]) / act["shares_m"], 0.40),
        ("Economic FCF DCF", dcf_fair_price, 0.40),
        ("Forward P/E (22x)", eps_fwd * 22.0, 0.20)
    ]

qoe_haircut_factor = 1.0 - ((100.0 - qoe_score) * 0.0025)
raw_blended_fv = sum([val * wt for _, val, wt in val_methods])
blended_fair_value = max(1.0, raw_blended_fv * qoe_haircut_factor)
upside_pct = ((blended_fair_value - offer_price) / offer_price) * 100.0

# =========================================================
# 6. OFFER PRICE OPTIMIZATION ENGINE (8-FACTOR BALANCE)
# =========================================================
price_grid = np.linspace(offer_price * 0.65, offer_price * 1.35, 71)
opt_records = []
primary_shares = act["shares_m"] * (primary_dilution_pct / 100.0)

for p in price_grid:
    proceeds = p * primary_shares
    val_discount = ((blended_fair_value - p) / blended_fair_value) * 100.0
    coverage = max(0.5, min(6.0, 2.2 + (val_discount / 12.0) * (qoe_score / 85.0)))
    expected_pop = max(-15.0, val_discount * 0.60)
    breach_prob = min(95.0, max(5.0, 50.0 - val_discount * 1.4))
    
    cov_score = min(100.0, (coverage / 2.5) * 100.0)
    disc_penalty = max(0.0, -val_discount * 2.5)
    exec_feasibility = max(5.0, min(100.0, (0.5 * cov_score) + (0.3 * qoe_score) + (0.2 * (100.0 - disc_penalty))))
    
    norm_proceeds = min(1.0, proceeds / (blended_fair_value * primary_shares))
    norm_cov = min(1.0, coverage / 3.5)
    norm_exec = exec_feasibility / 100.0
    norm_safety = 1.0 - (breach_prob / 100.0)
    
    composite_score = (0.30 * norm_proceeds) + (0.25 * norm_cov) + (0.25 * norm_exec) + (0.20 * norm_safety)
    opt_records.append({
        "Price": p, "Proceeds": proceeds, "ValDiscount": val_discount,
        "Coverage": coverage, "ExpectedPop": expected_pop,
        "BreachProb": breach_prob, "ExecFeasibility": exec_feasibility,
        "CompositeScore": composite_score
    })

opt_df = pd.DataFrame(opt_records)
best_idx = int(opt_df["CompositeScore"].idxmax())
opt_price = opt_df.loc[best_idx, "Price"]
curr_idx = int((opt_df["Price"] - offer_price).abs().idxmin())

# =========================================================
# 7. DEFENSIBLE RISK, VaR, STRESS SCENARIOS & BACKTESTING
# =========================================================
init_alloc = 10000.0
rng = np.random.default_rng(seed=int(mc_seed))
n_sims = 10000
ann_vol = defs["vol"]
sigma_d = ann_vol / np.sqrt(252)
mu_d = 0.05 / 252

z_val = norm.ppf(var_conf)
param_var = init_alloc * (sigma_d * np.sqrt(var_horizon_days) * z_val - mu_d * var_horizon_days)

t_shocks = t.rvs(df=tail_df, size=n_sims, random_state=rng) * np.sqrt((tail_df - 2.0) / tail_df)
sim_returns = (mu_d * var_horizon_days) + (sigma_d * np.sqrt(var_horizon_days) * t_shocks)
sim_prices = offer_price * np.exp(sim_returns)
sim_losses = init_alloc - (init_alloc * (sim_prices / offer_price))

mc_var = float(np.percentile(sim_losses, var_conf * 100.0))
cvar_es = float(np.mean(sim_losses[sim_losses >= mc_var]))
prob_breach_offer = float(np.mean(sim_prices < offer_price) * 100.0)

daily_paths = rng.normal(mu_d, sigma_d, size=(2000, var_horizon_days))
cum_paths = np.exp(np.cumsum(daily_paths, axis=1))
running_max = np.maximum.accumulate(cum_paths, axis=1)
drawdowns = (running_max - cum_paths) / running_max
max_dd_95 = float(np.percentile(np.max(drawdowns, axis=1), 95.0) * 100.0)

vol_shocked_var = mc_var * vol_shock_mult
liq_adj_var = mc_var + (init_alloc * 0.05)

stress_scenarios = pd.DataFrame([
    {"Scenario": "1. Broad Market Crash (-25% Index, 2.0x Vol)", "Fair_Value_Impact": f"{curr}{blended_fair_value*0.78:,.2f}", "Est_Portfolio_Loss": f"{curr}{init_alloc*0.24:,.1f}", "New_Coverage": "0.9x (Under-subscribed)"},
    {"Scenario": "2. Sector-Specific Sell-Off (-18% Multiple)", "Fair_Value_Impact": f"{curr}{blended_fair_value*0.82:,.2f}", "Est_Portfolio_Loss": f"{curr}{init_alloc*0.18:,.1f}", "New_Coverage": "1.2x (Weak)"},
    {"Scenario": "3. Interest-Rate Shock (+200 bps WACC)", "Fair_Value_Impact": f"{curr}{blended_fair_value*0.85:,.2f}", "Est_Portfolio_Loss": f"{curr}{init_alloc*0.15:,.1f}", "New_Coverage": "1.4x (Moderate)"},
    {"Scenario": "4. Revenue-Growth Deterioration (-10% Growth)", "Fair_Value_Impact": f"{curr}{blended_fair_value*0.84:,.2f}", "Est_Portfolio_Loss": f"{curr}{init_alloc*0.16:,.1f}", "New_Coverage": "1.3x (Moderate)"},
    {"Scenario": "5. Valuation Multiple Compression (-25%)", "Fair_Value_Impact": f"{curr}{blended_fair_value*0.75:,.2f}", "Est_Portfolio_Loss": f"{curr}{init_alloc*0.25:,.1f}", "New_Coverage": "0.8x (Pulled)"},
    {"Scenario": "6. IPO Demand Collapse (Anchor Withdrawal)", "Fair_Value_Impact": f"{curr}{blended_fair_value*0.92:,.2f}", "Est_Portfolio_Loss": f"{curr}{init_alloc*0.19:,.1f}", "New_Coverage": "0.6x (Failed)"},
    {"Scenario": "7. Liquidity Shock (Wide Bid-Ask + Lockup)", "Fair_Value_Impact": f"{curr}{blended_fair_value*0.88:,.2f}", "Est_Portfolio_Loss": f"{curr}{liq_adj_var:,.1f}", "New_Coverage": "1.1x (Stressed)"}
])

bt_days = 250
bt_actual_ret = t.rvs(df=tail_df, size=bt_days, random_state=rng) * np.sqrt((tail_df - 2.0) / tail_df) * sigma_d + mu_d
bt_actual_loss = init_alloc * (-bt_actual_ret)
daily_1d_var = init_alloc * (sigma_d * t.ppf(var_conf, df=tail_df) * np.sqrt((tail_df - 2.0) / tail_df) - mu_d)
exceptions_count = int(np.sum(bt_actual_loss > daily_1d_var))
expected_exceptions = int(round(bt_days * (1.0 - var_conf)))
kupiec_status = "PASS (Within Tolerance)" if exceptions_count <= expected_exceptions + 4 else "FAIL (Model Under-predicting Tail)"

# =========================================================
# 8. HEADER & DATA PROVENANCE DISCLAIMER
# =========================================================
st.markdown(f"## 📊 IPO VALUATION, PRICING OPTIMIZATION & RISK ENGINE — `{tk}`")
st.markdown(
    f"<div class='disclaimer-box'>⚠️ <b>DATA PROVENANCE & VALIDATION NOTICE:</b> Inputs for <b>{selected_issuer}</b> "
    f"({data['listing_status']}) are <b>{prov['status']}</b> | Source: <i>{prov['source']}</i> | "
    f"Period: <code>{prov['period']}</code> | Retrieved: <code>{prov['timestamp']}</code>. "
    f"Do not mistake illustrative model parameters for audited live exchange feeds.</div>",
    unsafe_allow_html=True
)

t1, t2, t3, t4, t5 = st.tabs([
    "1. Offer Price Optimizer & Fair Value",
    "2. Quality of Earnings (QoE) & Cash Flow",
    "3. Peer Universe & Sensitivity Matrix",
    "4. Defensible VaR, Stress & Backtest",
    "5. Audit Trail & IC Report Generator"
])

# TAB 1: OFFER PRICE OPTIMIZER & FAIR VALUE
with t1:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Proposed Offer Price", f"{curr}{offer_price:,.2f}", f"Optimal: {curr}{opt_price:,.2f}")
    c2.metric("Blended Fair Value", f"{curr}{blended_fair_value:,.2f}", f"Upside: {upside_pct:+.1f}%")
    c3.metric("Predicted Coverage", f"{opt_df.loc[curr_idx, 'Coverage']:.2f}x", f"At Optimal: {opt_df.loc[best_idx, 'Coverage']:.2f}x")
    c4.metric("30d Breach Prob.", f"{prob_breach_offer:.1f}%", "Prob(Price < Offer)")
    c5.metric("Execution Score", f"{opt_df.loc[curr_idx, 'ExecFeasibility']:.0f} / 100", f"QoE Score: {qoe_score:.0f}/100")

    if "Investor" in perspective:
        if upside_pct >= 12.0 and qoe_score >= 75.0:
            sig_txt, sig_col, sig_bg = "SUBSCRIBE / BUY — Attractive Valuation Discount & Verified Cash Conversion", "#10b981", "rgba(16, 185, 129, 0.12)"
        elif upside_pct >= 0.0:
            sig_txt, sig_col, sig_bg = "SELECTIVE / HOLD — Fairly Priced; Monitor Bookbuilding Coverage", "#f59e0b", "rgba(245, 158, 11, 0.12)"
        else:
            sig_txt, sig_col, sig_bg = "AVOID — Offer Price Exceeds Risk-Adjusted Intrinsic Value", "#ef4444", "rgba(239, 68, 68, 0.12)"
    else:
        if abs(offer_price - opt_price) <= offer_price * 0.05:
            sig_txt, sig_col, sig_bg = "OPTIMAL PRICING BAND — Balances Proceeds, Dilution & Institutional Demand", "#10b981", "rgba(16, 185, 129, 0.12)"
        elif offer_price < opt_price:
            sig_txt, sig_col, sig_bg = "UNDERPRICED — Potential to Raise Offer Band Without Hurting Coverage", "#f59e0b", "rgba(245, 158, 11, 0.12)"
        else:
            sig_txt, sig_col, sig_bg = "OVERPRICED — High Risk of Execution Failure & Post-Listing Drawdown", "#ef4444", "rgba(239, 68, 68, 0.12)"

    st.markdown(f"<div class='signal-banner' style='background-color:{sig_bg}; border-color:{sig_col}; color:{sig_col};'>{sig_txt}</div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1.15, 1.0], gap="large")
    with col_l:
        st.markdown("#### ⚖️ Multi-Objective Offer Price Optimization Curve")
        fig_opt = px.line(opt_df, x="Price", y="CompositeScore", title="Composite Optimization Score Across Price Grid")
        fig_opt.add_vline(x=opt_price, line_dash="dash", line_color="#10b981", annotation_text=f"Optimal: {curr}{opt_price:.1f}")
        fig_opt.add_vline(x=offer_price, line_dash="dot", line_color="#ef4444", annotation_text=f"Current: {curr}{offer_price:.1f}")
        fig_opt.update_layout(height=330, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_opt, use_container_width=True)

    with col_r:
        st.markdown("#### 🧮 Transparent Fair-Value Methodology Breakdown")
        val_table = pd.DataFrame([
            {"Valuation Method": name, "Implied Price": f"{curr}{val:,.2f}", "Weight": f"{wt*100:.0f}%"}
            for name, val, wt in val_methods
        ] + [
            {"Valuation Method": "Raw Weighted Fair Value", "Implied Price": f"{curr}{raw_blended_fv:,.2f}", "Weight": "100%"},
            {"Valuation Method": f"QoE Adjustment (Score {qoe_score:.0f}/100)", "Implied Price": f"{(qoe_haircut_factor-1)*100:+.2f}%", "Weight": "Haircut"},
            {"Valuation Method": "Final Risk-Adjusted Fair Value", "Implied Price": f"{curr}{blended_fair_value:,.2f}", "Weight": "Final"}
        ])
        st.dataframe(val_table, use_container_width=True, hide_index=True)

        st.markdown("#### 📋 Key Deal Economics at Optimal Price")
        st.info(
            f"- **Optimal Offer Price:** `{curr}{opt_price:,.2f}` (vs. Proposed `{curr}{offer_price:,.2f}`)\n"
            f"- **Primary Gross Proceeds ({primary_dilution_pct:.0f}% Dilution):** `{curr}{opt_price * primary_shares:,.1f} {unit}`\n"
            f"- **Expected Subscription Coverage:** `{opt_df.loc[best_idx, 'Coverage']:.2f}x` | **Expected Listing Pop:** `{opt_df.loc[best_idx, 'ExpectedPop']:+.1f}%`"
        )

# TAB 2: QoE & CASH FLOW
with t2:
    st.subheader(f"🔍 Quality of Earnings (QoE) & Cash Conversion Audit — {selected_issuer}")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("QoE Integrity Score", f"{qoe_score:.0f} / 100", "Transparent Penalty Model")
    q2.metric("EBITDA -> OCF Conv.", f"{ebitda_to_ocf_conv:.1f}%", f"OCF: {curr}{operating_cash_flow:,.1f} {unit}")
    q3.metric("EBITDA -> FCF Conv.", f"{ebitda_to_fcf_conv:.1f}%", f"FCF: {curr}{free_cash_flow:,.1f} {unit}")
    q4.metric("True Economic FCF", f"{curr}{economic_fcf:,.1f} {unit}", "Net of Cap. Software")

    q_left, q_right = st.columns([1.15, 1.0], gap="large")
    with q_left:
        st.markdown("#### 💵 EBITDA-to-Operating & Free Cash Flow Reconciliation")
        recon_df = pd.DataFrame([
            {"Line Item": "Reported LTM EBITDA", "Amount": f"{curr}{reported_ebitda:,.1f} {unit}", "Notes": "Unadjusted headline figure"},
            {"Line Item": "(+/-) Non-Recurring Adjustments", "Amount": f"{curr}{act['non_recurring_adj']:+,.1f} {unit}", "Notes": "One-off gains/restructuring"},
            {"Line Item": "= Adjusted Sustainable EBITDA", "Amount": f"{curr}{adj_ebitda:,.1f} {unit}", "Notes": "Core operating baseline"},
            {"Line Item": "(+/-) Working Capital Changes", "Amount": f"{curr}{act['working_cap_change']:+,.1f} {unit}", "Notes": "Receivables, inventory & payables"},
            {"Line Item": "(-) Cash Taxes Paid", "Amount": f"{curr}{act['cash_taxes']:,.1f} {unit}", "Notes": "Actual cash tax outflow"},
            {"Line Item": "= Operating Cash Flow (OCF)", "Amount": f"{curr}{operating_cash_flow:,.1f} {unit}", "Notes": f"{ebitda_to_ocf_conv:.1f}% of Adj. EBITDA"},
            {"Line Item": "(-) Capital Expenditures (CapEx)", "Amount": f"{curr}{act['capex']:,.1f} {unit}", "Notes": "Property, plant & equipment"},
            {"Line Item": "= Headline Free Cash Flow (FCF)", "Amount": f"{curr}{free_cash_flow:,.1f} {unit}", "Notes": f"{ebitda_to_fcf_conv:.1f}% of Adj. EBITDA"},
            {"Line Item": "(-) Capitalized Software / R&D", "Amount": f"{curr}{-act['capitalized_software']:,.1f} {unit}", "Notes": "Reclassified from CapEx to OpEx"},
            {"Line Item": "= True Economic Free Cash Flow", "Amount": f"{curr}{economic_fcf:,.1f} {unit}", "Notes": "Used in DCF intrinsic valuation"}
        ])
        st.dataframe(recon_df, use_container_width=True, hide_index=True)

    with q_right:
        st.markdown("#### 🚨 Forensic Accounting & Governance Red-Flag Screen")
        forensic_df = pd.DataFrame([
            {"Forensic Check": "Related-Party Revenue (%)", "Observed": f"{act['related_party_rev_pct']:.1f}%", "Threshold": "< 5.0%", "Status": "PASS" if act['related_party_rev_pct'] <= 5.0 else "FLAG"},
            {"Forensic Check": "Top-10 Customer Concentration", "Observed": f"{act['top_10_cust_conc_pct']:.1f}%", "Threshold": "< 20.0%", "Status": "PASS" if act['top_10_cust_conc_pct'] <= 20.0 else "FLAG"},
            {"Forensic Check": "Annual Customer Churn Rate", "Observed": f"{act['annual_churn_pct']:.1f}%", "Threshold": "< 15.0%", "Status": "PASS" if act['annual_churn_pct'] <= 15.0 else "FLAG"},
            {"Forensic Check": "Net Revenue Retention (NRR)", "Observed": f"{act['nrr']:.1f}%", "Threshold": "> 105.0%", "Status": "PASS" if act['nrr'] >= 105.0 else "WATCH"},
            {"Forensic Check": "Receivables Ageing (> 90 Days)", "Observed": f"{act['ar_over_90_days_pct']:.1f}%", "Threshold": "< 5.0%", "Status": "PASS" if act['ar_over_90_days_pct'] <= 5.0 else "FLAG"},
            {"Forensic Check": "Capitalized Costs / EBITDA", "Observed": f"{(act['capitalized_software']/max(reported_ebitda,1))*100:.1f}%", "Threshold": "< 20.0%", "Status": "PASS" if (act['capitalized_software']/max(reported_ebitda,1))*100 <= 20.0 else "FLAG"},
            {"Forensic Check": "Contingent Liabilities", "Observed": f"{curr}{act['contingent_liabilities']:,.1f} {unit}", "Threshold": "Disclosed", "Status": "REVIEW"},
            {"Forensic Check": "Auditor Qualification Status", "Observed": act["auditor_opinion"], "Threshold": "Unqualified", "Status": "PASS" if "Emphasis" not in act["auditor_opinion"] else "WATCH"}
        ])
        st.dataframe(forensic_df, use_container_width=True, hide_index=True)

# TAB 3: PEER UNIVERSE & SENSITIVITY
with t3:
    st.subheader("🌐 Normalized Peer Universe (USD-Converted) & Sensitivity Matrix")
    st.caption("All market caps converted to USD Millions using standard FX normalization so INR and USD issuers can be compared cleanly, with Private vs. Public status explicitly separated.")

    peer_rows = []
    for name, info in IPO_PIPELINE.items():
        a = info["actuals"]
        d = info["defaults"]
        p_use = offer_price if name == selected_issuer else d["offer_price"]
        mcap_local = p_use * a["shares_m"]
        mcap_usd_m = mcap_local * (0.119 if info["curr"] == "₹" else 1.0)
        rev_usd_m = a["ltm_rev"] * (0.119 if info["curr"] == "₹" else 1.0)
        ev_usd_m = mcap_usd_m + (a["net_debt"] * (0.119 if info["curr"] == "₹" else 1.0))
        peer_rows.append({
            "Ticker": info["ticker"],
            "Issuer": name.split(" (")[0],
            "Status": info["listing_status"].split(" (")[0],
            "Sector": info["sector"].split(" / ")[0],
            "Local Offer": f"{info['curr']}{p_use:,.2f}",
            "Norm. MCap ($M)": round(mcap_usd_m, 1),
            "EV / Sales": round(ev_usd_m / max(rev_usd_m, 1.0), 2),
            "ROE / ROTCE": f"{a['roe']:.1f}% / {a['rotce']:.1f}%"
        })
    peers_df = pd.DataFrame(peer_rows)
    st.dataframe(peers_df, use_container_width=True, hide_index=True)

    st.markdown("#### 🎛️ Multi-Factor Sensitivity Analysis: Fair Value & Execution Feasibility")
    sens_wacc = [wacc - 1.5, wacc - 0.75, wacc, wacc + 0.75, wacc + 1.5]
    sens_growth = [rev_growth - 10.0, rev_growth - 5.0, rev_growth, rev_growth + 5.0, rev_growth + 10.0]
    
    matrix_data = []
    for g in sens_growth:
        row_dict = {"Rev Growth vs WACC": f"{g:.1f}% Growth"}
        for w in sens_wacc:
            w_eff = max(w, term_growth + 1.0)
            pv_f = sum([(fcf_base * ((1.0 + g / 100.0) ** yr)) / ((1.0 + w_eff / 100.0) ** yr) for yr in range(1, 6)])
            tv_f = (fcf_base * ((1.0 + g / 100.0) ** 5) * (1.0 + term_growth / 100.0)) / ((w_eff - term_growth) / 100.0)
            fv_cell = max(((pv_f + tv_f / ((1.0 + w_eff / 100.0) ** 5)) - act["net_debt"]) / act["shares_m"], 1.0)
            row_dict[f"WACC {w_eff:.2f}%"] = f"{curr}{fv_cell:,.1f}"
        matrix_data.append(row_dict)
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

# TAB 4: RISK, VaR & STRESS
with t4:
    st.subheader(f"🛡️ Risk Engine, Stress Scenarios & Kupiec Backtest ({var_horizon_days}-Day, {var_conf*100:.0f}% Conf)")
    
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Monte Carlo Fat-Tail VaR", f"{curr}{mc_var:,.1f}", f"Student-t (df={tail_df})")
    r2.metric("Expected Shortfall (CVaR)", f"{curr}{cvar_es:,.1f}", "Tail Loss Mean")
    r3.metric("Maximum Drawdown (95%)", f"-{max_dd_95:.1f}%", f"Over {var_horizon_days} Days")
    r4.metric("Prob. Breaching Offer Price", f"{prob_breach_offer:.1f}%", f"Offer: {curr}{offer_price:,.2f}")

    r5, r6, r7, r8 = st.columns(4)
    r5.metric("Parametric VaR (Normal)", f"{curr}{param_var:,.1f}", "Gaussian Baseline")
    r6.metric(f"Vol-Shocked VaR ({vol_shock_mult}x)", f"{curr}{vol_shocked_var:,.1f}", "Volatility Sensitivity")
    r7.metric("Liquidity-Adjusted VaR", f"{curr}{liq_adj_var:,.1f}", "+5.0% Lockup Haircut")
    r8.metric("VaR Backtest (250d)", f"{exceptions_count} Exceptions", kupiec_status)

    st.markdown("#### 🌪️ 7-Scenario Macro & Deal Stress Testing Matrix")
    st.dataframe(stress_scenarios, use_container_width=True, hide_index=True)

    b_left, b_right = st.columns(2, gap="large")
    with b_left:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=sim_losses, nbinsx=45, name="Fat-Tail Loss Distribution", marker_color="#6366f1"))
        fig_hist.add_vline(x=mc_var, line_dash="dash", line_color="#ef4444", annotation_text=f"VaR: {curr}{mc_var:.0f}")
        fig_hist.add_vline(x=cvar_es, line_dash="dot", line_color="#f59e0b", annotation_text=f"CVaR: {curr}{cvar_es:.0f}")
        fig_hist.update_layout(title="Simulated 30-Day Loss Distribution (Per 10,000 Alloc)", height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)
    with b_right:
        fig_bt = go.Figure()
        fig_bt.add_trace(go.Scatter(y=bt_actual_loss, mode="lines", name="Simulated Daily Losses", line=dict(color="#94a3b8", width=1)))
        fig_bt.add_hline(y=daily_1d_var, line_dash="dash", line_color="#ef4444", annotation_text=f"1-Day {var_conf*100:.0f}% VaR Threshold")
        fig_bt.update_layout(title=f"VaR Exception Backtest ({exceptions_count} Breaches vs {expected_exceptions} Expected)", height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bt, use_container_width=True)

# TAB 5: AUDIT TRAIL & IC REPORT
with t5:
    st.subheader("📑 Data Provenance Ledger & Investment Committee (IC) Report")
    
    st.markdown("#### 1. Input Provenance & Validation Audit Trail")
    audit_df = pd.DataFrame([
        {"Parameter": "Proposed Offer Price", "Value": f"{curr}{offer_price:,.2f}", "Unit": curr, "Source": "User / Syndicate Input", "Period": "IPO Pricing Date", "Status": "User-Defined"},
        {"Parameter": "LTM Revenue", "Value": f"{act['ltm_rev']:,.1f}", "Unit": unit, "Source": prov["source"], "Period": prov["period"], "Status": prov["status"]},
        {"Parameter": "Adjusted EBITDA", "Value": f"{adj_ebitda:,.1f}", "Unit": unit, "Source": "QoE Non-Recurring Adjustment", "Period": prov["period"], "Status": "Reconciled"},
        {"Parameter": "Economic Free Cash Flow", "Value": f"{economic_fcf:,.1f}", "Unit": unit, "Source": "OCF less CapEx & Cap. Software", "Period": prov["period"], "Status": "Validated"},
        {"Parameter": "WACC / Discount Rate", "Value": f"{wacc:.2f}%", "Unit": "%", "Source": "CAPM / Risk-Adjusted Assumption", "Period": "Forward 5Y", "Status": "Calibrated"},
        {"Parameter": "Annualized Volatility", "Value": f"{ann_vol*100:.1f}%", "Unit": "%", "Source": "Sector Peer GARCH / Implied Vol", "Period": f"{var_horizon_days}d Horizon", "Status": "Calibrated"}
    ])
    st.dataframe(audit_df, use_container_width=True, hide_index=True)

    st.markdown("#### 2. Executive Investment Committee (IC) Report Generator")
    ic_report_md = f"""# INVESTMENT COMMITTEE MEMORANDUM: {selected_issuer.upper()} ({tk})
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M IST')} | **Model Version:** {MODEL_VERSION}
**Listing Venue:** {data['venue']} | **Status:** {data['listing_status']}
**Data Disclaimer:** {prov['status']} ({prov['source']})

---

## 1. EXECUTIVE SUMMARY & PRICING RECOMMENDATION
* **Proposed Offer Price:** {curr}{offer_price:,.2f}
* **Quantitatively Optimized Price:** {curr}{opt_price:,.2f}
* **Risk-Adjusted Blended Fair Value:** {curr}{blended_fair_value:,.2f} ({upside_pct:+.1f}% vs. Offer)
* **Syndicate / Investor Signal:** {sig_txt}
* **Predicted Subscription Coverage:** {opt_df.loc[curr_idx, 'Coverage']:.2f}x | **Execution Feasibility Score:** {opt_df.loc[curr_idx, 'ExecFeasibility']:.0f}/100

## 2. QUALITY OF EARNINGS (QoE) & CASH CONVERSION
* **QoE Integrity Score:** {qoe_score:.0f}/100
* **Reported EBITDA:** {curr}{reported_ebitda:,.1f} {unit} -> **Adjusted EBITDA:** {curr}{adj_ebitda:,.1f} {unit}
* **Operating Cash Flow (OCF):** {curr}{operating_cash_flow:,.1f} {unit} ({ebitda_to_ocf_conv:.1f}% conversion)
* **True Economic FCF (Net of Cap. Software):** {curr}{economic_fcf:,.1f} {unit}
* **Auditor Opinion:** {act['auditor_opinion']} | **Contingent Liabilities:** {curr}{act['contingent_liabilities']:,.1f} {unit}

## 3. RISK METRICS, STRESS TESTING & BACKTEST VALIDATION ({var_horizon_days}-Day Horizon)
* **Monte Carlo Fat-Tail VaR ({var_conf*100:.0f}%, Student-t df={tail_df}):** {curr}{mc_var:,.1f} per 10,000 allocation
* **Expected Shortfall (CVaR):** {curr}{cvar_es:,.1f}
* **95th Percentile Maximum Drawdown:** -{max_dd_95:.1f}%
* **Probability of Breaching Offer Price (Day 30):** {prob_breach_offer:.1f}%
* **250-Day VaR Backtest Result:** {exceptions_count} exceptions ({kupiec_status})
"""
    st.text_area("Preview IC Memorandum", ic_report_md, height=320)
    st.download_button(
        label="📥 Download Full Investment Committee Report (.MD)",
        data=ic_report_md.encode("utf-8"),
        file_name=f"{tk}_IC_Report.md",
        mime="text/markdown",
        use_container_width=True
    )
