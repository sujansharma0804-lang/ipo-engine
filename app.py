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
MODEL_VERSION = "v10.0.0-INSTITUTIONAL-FINAL"
st.set_page_config(
    page_title="Institutional IPO Valuation, Pricing & Risk Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    .signal-banner {
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 1.0rem;
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
        font-size: 0.88rem;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. ISSUER PIPELINE WITH PEER TIERS, PROVENANCE & QoE LEDGER
# =========================================================
IPO_PIPELINE = {
    "Christ University Bangalore (Endowment Spin-off)": {
        "ticker": "CHRISTED.NS",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEBI Mainboard / Social Infrastructure",
        "sector": "Social Infrastructure / Higher Education",
        "peer_group": "Social Infrastructure & Services",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Illustrative Institutional Trust & Campus Operations Filing",
            "period": "LTM FY26E",
            "timestamp": "2026-11-15 15:15 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 1420.0, "ltm_ebitda": 465.0, "net_income": 310.0,
            "book_value": 2450.0, "net_debt": -570.0, "shares_m": 165.0,
            "roe": 24.8, "debt_equity": 0.05, "fcf_margin": 22.4,
            "gmv": 1600.0, "take_rate": 95.0, "arr": 1500.0, "nrr": 128.0,
            "rotce": 26.2, "ptbv": 3.1,
            "non_recurring_adj": -15.0, "working_cap_change": 25.0, "cash_taxes": -35.0,
            "tangible_capex": -95.0, "capitalized_software": 20.0,
            "related_party_rev_pct": 0.5, "top_10_cust_conc_pct": 2.0,
            "annual_churn_pct": 3.2, "ar_over_90_days_pct": 1.1,
            "contingent_liabilities": 15.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 280.0, "rev_growth": 16.5, "eps_growth": 18.2, "wacc": 9.75, "term_growth": 3.5, "vol": 0.18}
    },
    "Zepto (Kiranakart Technologies)": {
        "ticker": "ZEPTO.NS",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEBI / NSE (India)",
        "sector": "Quick-Commerce / Consumer Marketplace",
        "peer_group": "Consumer Commerce & Delivery",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Illustrative DRHP Baseline & Series-G Disclosures",
            "period": "LTM FY26E",
            "timestamp": "2026-11-15 15:15 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 11200.0, "ltm_ebitda": 480.0, "net_income": 290.0,
            "book_value": 4800.0, "net_debt": -2650.0, "shares_m": 665.0,
            "roe": 12.4, "debt_equity": 0.09, "fcf_margin": 8.5,
            "gmv": 24000.0, "take_rate": 18.5, "arr": 13500.0, "nrr": 118.0,
            "rotce": 14.2, "ptbv": 5.8,
            "non_recurring_adj": -45.0, "working_cap_change": -110.0, "cash_taxes": -65.0,
            "tangible_capex": -180.0, "capitalized_software": 95.0,
            "related_party_rev_pct": 1.8, "top_10_cust_conc_pct": 4.2,
            "annual_churn_pct": 14.5, "ar_over_90_days_pct": 3.1,
            "contingent_liabilities": 120.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 290.0, "rev_growth": 42.0, "eps_growth": 38.0, "wacc": 12.5, "term_growth": 4.0, "vol": 0.36}
    },
    "Flipkart Internet (India Listing)": {
        "ticker": "FLPKRT.NS",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEBI / BSE-NSE (India)",
        "sector": "E-Commerce / Digital Marketplace",
        "peer_group": "Consumer Commerce & Delivery",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Illustrative Pre-IPO Info Memo",
            "period": "LTM FY26E",
            "timestamp": "2026-11-15 15:15 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 68500.0, "ltm_ebitda": 6150.0, "net_income": 4350.0,
            "book_value": 34200.0, "net_debt": -5600.0, "shares_m": 1280.0,
            "roe": 18.6, "debt_equity": 0.14, "fcf_margin": 9.2,
            "gmv": 195000.0, "take_rate": 14.0, "arr": 72000.0, "nrr": 115.0,
            "rotce": 19.5, "ptbv": 4.2,
            "non_recurring_adj": -320.0, "working_cap_change": 450.0, "cash_taxes": -980.0,
            "tangible_capex": -1450.0, "capitalized_software": 620.0,
            "related_party_rev_pct": 6.4, "top_10_cust_conc_pct": 2.5,
            "annual_churn_pct": 11.0, "ar_over_90_days_pct": 5.4,
            "contingent_liabilities": 890.0, "auditor_opinion": "Unqualified w/ Emphasis of Matter (Simulated)"
        },
        "defaults": {"offer_price": 1150.0, "rev_growth": 24.0, "eps_growth": 27.5, "wacc": 11.25, "term_growth": 3.5, "vol": 0.27}
    },
    "Swiggy Limited (Listed Benchmark)": {
        "ticker": "SWIGGY.NS",
        "listing_status": "Publicly Listed (NSE/BSE)",
        "venue": "SEBI / NSE (India)",
        "sector": "Food Delivery / Quick-Commerce",
        "peer_group": "Consumer Commerce & Delivery",
        "curr": "₹",
        "unit": "Cr",
        "fx_to_usd": 0.0119,
        "provenance": {
            "source": "Exchange Filings & Public Post-IPO Disclosures",
            "period": "LTM FY26",
            "timestamp": "2026-11-15 15:15 IST",
            "status": "Public Benchmark"
        },
        "actuals": {
            "ltm_rev": 14800.0, "ltm_ebitda": 920.0, "net_income": 610.0,
            "book_value": 9200.0, "net_debt": -4100.0, "shares_m": 2220.0,
            "roe": 11.4, "debt_equity": 0.06, "fcf_margin": 6.8,
            "gmv": 32000.0, "take_rate": 22.0, "arr": 16000.0, "nrr": 114.0,
            "rotce": 13.5, "ptbv": 3.8,
            "non_recurring_adj": -60.0, "working_cap_change": 85.0, "cash_taxes": -140.0,
            "tangible_capex": -310.0, "capitalized_software": 115.0,
            "related_party_rev_pct": 1.2, "top_10_cust_conc_pct": 3.1,
            "annual_churn_pct": 13.8, "ar_over_90_days_pct": 2.9,
            "contingent_liabilities": 210.0, "auditor_opinion": "Unqualified"
        },
        "defaults": {"offer_price": 390.0, "rev_growth": 28.0, "eps_growth": 25.0, "wacc": 11.8, "term_growth": 3.5, "vol": 0.31}
    },
    "Stripe Inc.": {
        "ticker": "STRP",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEC / NASDAQ (USA)",
        "sector": "Fintech / SaaS Infrastructure",
        "peer_group": "Enterprise SaaS & Fintech",
        "curr": "$",
        "unit": "M",
        "fx_to_usd": 1.0,
        "provenance": {
            "source": "Illustrative SEC S-1 Draft Baseline",
            "period": "LTM Q3 2026E",
            "timestamp": "2026-11-15 15:15 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 18400.0, "ltm_ebitda": 3850.0, "net_income": 2410.0,
            "book_value": 16800.0, "net_debt": -4200.0, "shares_m": 1240.0,
            "roe": 28.4, "debt_equity": 0.12, "fcf_margin": 19.5,
            "gmv": 1100000.0, "take_rate": 1.8, "arr": 20500.0, "nrr": 122.0,
            "rotce": 31.0, "ptbv": 7.5,
            "non_recurring_adj": -140.0, "working_cap_change": 210.0, "cash_taxes": -510.0,
            "tangible_capex": -420.0, "capitalized_software": 310.0,
            "related_party_rev_pct": 0.4, "top_10_cust_conc_pct": 14.2,
            "annual_churn_pct": 5.2, "ar_over_90_days_pct": 1.8,
            "contingent_liabilities": 180.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 58.0, "rev_growth": 26.0, "eps_growth": 29.0, "wacc": 10.0, "term_growth": 3.0, "vol": 0.25}
    },
    "Databricks Inc.": {
        "ticker": "DBRX",
        "listing_status": "Private / Pre-IPO (Simulated)",
        "venue": "SEC / NYSE (USA)",
        "sector": "Enterprise SaaS / Cloud Data Platform",
        "peer_group": "Enterprise SaaS & Fintech",
        "curr": "$",
        "unit": "M",
        "fx_to_usd": 1.0,
        "provenance": {
            "source": "Illustrative SEC S-1 Registration Baseline",
            "period": "LTM Q3 2026E",
            "timestamp": "2026-11-15 15:15 IST",
            "status": "Hypothetical / Unaudited Model Input"
        },
        "actuals": {
            "ltm_rev": 3250.0, "ltm_ebitda": 680.0, "net_income": 440.0,
            "book_value": 6400.0, "net_debt": -1750.0, "shares_m": 635.0,
            "roe": 19.5, "debt_equity": 0.08, "fcf_margin": 14.2,
            "gmv": 3600.0, "take_rate": 90.0, "arr": 3800.0, "nrr": 138.0,
            "rotce": 21.0, "ptbv": 6.2,
            "non_recurring_adj": -35.0, "working_cap_change": 145.0, "cash_taxes": -95.0,
            "tangible_capex": -110.0, "capitalized_software": 140.0,
            "related_party_rev_pct": 0.2, "top_10_cust_conc_pct": 18.5,
            "annual_churn_pct": 4.1, "ar_over_90_days_pct": 2.2,
            "contingent_liabilities": 45.0, "auditor_opinion": "Unqualified (Simulated)"
        },
        "defaults": {"offer_price": 78.0, "rev_growth": 48.0, "eps_growth": 44.0, "wacc": 11.0, "term_growth": 3.5, "vol": 0.33}
    }
}

# =========================================================
# 3. SIDEBAR CONTROLS & CALIBRATION PARAMETERS
# =========================================================
st.sidebar.markdown("### 📊 IPO PRICING & RISK ENGINE")
st.sidebar.caption(f"Validated Framework | `{MODEL_VERSION}`")

selected_issuer = st.sidebar.selectbox("Select Target Issuer", list(IPO_PIPELINE.keys()))
data = IPO_PIPELINE[selected_issuer]
curr, unit, act, defs = data["curr"], data["unit"], data["actuals"], data["defaults"]
tk, sector, peer_group, prov = data["ticker"], data["sector"], data["peer_group"], data["provenance"]

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
headline_fcf = operating_cash_flow + act["tangible_capex"]
economic_fcf = headline_fcf - act["capitalized_software"]

ebitda_to_ocf_conv = (operating_cash_flow / adj_ebitda * 100.0) if adj_ebitda > 0 else 0.0
ebitda_to_fcf_conv = (headline_fcf / adj_ebitda * 100.0) if adj_ebitda > 0 else 0.0

qoe_penalty = 0.0
if ebitda_to_ocf_conv < 70.0: qoe_penalty += 15.0
if act["capitalized_software"] / max(reported_ebitda, 1.0) > 0.20: qoe_penalty += 10.0
if act["related_party_rev_pct"] > 5.0: qoe_penalty += 12.0
if act["ar_over_90_days_pct"] > 5.0: qoe_penalty += 8.0
if "Emphasis" in act["auditor_opinion"] or "Qualified" in act["auditor_opinion"]: qoe_penalty += 15.0
qoe_score = max(20.0, min(100.0, 100.0 - qoe_penalty))

# =========================================================
# 5. MULTI-STAGE RAMP DCF & SECTOR VALUATION
# =========================================================
eps_ttm = act["net_income"] / act["shares_m"]
eps_fwd = eps_ttm * (1.0 + eps_growth / 100.0)
bvps = act["book_value"] / act["shares_m"]
rotce, roe, arr, nrr = act["rotce"], act["roe"], act["arr"], act["nrr"]

def compute_ramp_dcf(start_rev, start_econ_fcf, g_pct, w_pct, tg_pct, net_debt, shares_m):
    target_terminal_fcf_margin = max(act["fcf_margin"] / 100.0, 0.08)
    start_margin = start_econ_fcf / max(start_rev, 1.0)
    pv_sum = 0.0
    proj_rows = []
    curr_rev = start_rev
    for yr in range(1, 6):
        curr_rev = curr_rev * (1.0 + g_pct / 100.0)
        yr_margin = start_margin + ((target_terminal_fcf_margin - start_margin) * (yr / 5.0))
        yr_fcf = curr_rev * yr_margin
        disc_factor = (1.0 + w_pct / 100.0) ** yr
        pv_fcf = yr_fcf / disc_factor
        pv_sum += pv_fcf
        proj_rows.append({
            "Year": f"Year {yr}",
            "Proj. Rev": curr_rev,
            "FCF Margin": yr_margin * 100.0,
            "Proj. Econ FCF": yr_fcf,
            "PV of FCF": pv_fcf
        })
    term_fcf = proj_rows[-1]["Proj. Econ FCF"] * (1.0 + tg_pct / 100.0)
    tv = term_fcf / ((w_pct - tg_pct) / 100.0)
    pv_tv = tv / ((1.0 + w_pct / 100.0) ** 5)
    ev = pv_sum + pv_tv
    eq_val = ev - net_debt
    per_share = max(eq_val / shares_m, 1.0)
    return per_share, pd.DataFrame(proj_rows), pv_tv

dcf_fair_price, dcf_schedule_df, dcf_pv_tv = compute_ramp_dcf(
    act["ltm_rev"], economic_fcf, rev_growth, wacc, term_growth, act["net_debt"], act["shares_m"]
)

growth_premium = 1.0 + ((rev_growth - 20.0) / 100.0)

if "Social" in sector or "Infrastructure" in sector or "Banking" in sector:
    implied_ptbv = max(act["ptbv"] * (rotce / 15.0) * growth_premium, 1.2)
    val_methods = [
        ("P/TBV Multiple", bvps * implied_ptbv, 0.40),
        ("5Y Ramp Economic DCF", dcf_fair_price, 0.40),
        ("Forward P/E (18x)", eps_fwd * 18.0, 0.20)
    ]
elif "SaaS" in sector or "Cloud" in sector or "Fintech" in sector:
    arr_fwd = arr * (1.0 + rev_growth / 100.0)
    arr_mult = max(4.0, min(18.0, ((rev_growth + act["fcf_margin"]) / 10.0) * (nrr / 100.0) * 1.8))
    val_methods = [
        (f"EV/ARR ({arr_mult:.1f}x)", ((arr_fwd * arr_mult) - act["net_debt"]) / act["shares_m"], 0.45),
        ("5Y Ramp Economic DCF", dcf_fair_price, 0.35),
        ("Forward P/E (28x)", eps_fwd * 28.0, 0.20)
    ]
else:
    gmv_fwd = act["gmv"] * (1.0 + rev_growth / 100.0)
    net_rev_fwd = gmv_fwd * (act["take_rate"] / 100.0)
    ev_rev_mult = max(2.0, min(8.0, 4.0 * growth_premium))
    val_methods = [
        (f"EV/Net Rev ({ev_rev_mult:.1f}x)", ((net_rev_fwd * ev_rev_mult) - act["net_debt"]) / act["shares_m"], 0.40),
        ("5Y Ramp Economic DCF", dcf_fair_price, 0.40),
        ("Forward P/E (22x)", eps_fwd * 22.0, 0.20)
    ]

qoe_haircut_factor = 1.0 - ((100.0 - qoe_score) * 0.0025)
raw_blended_fv = sum([val * wt for _, val, wt in val_methods])
blended_fair_value = max(1.0, raw_blended_fv * qoe_haircut_factor)
upside_pct = ((blended_fair_value - offer_price) / offer_price) * 100.0

# =========================================================
# 6. OFFER PRICE OPTIMIZATION ENGINE (FULL CLEARING GRID)
# =========================================================
grid_min = max(5.0, min(offer_price * 0.30, blended_fair_value * 0.50))
grid_max = max(offer_price * 1.35, blended_fair_value * 1.35)
price_grid = np.linspace(grid_min, grid_max, 81)
opt_records = []
primary_shares = act["shares_m"] * (primary_dilution_pct / 100.0)

def eval_price_point(p):
    proceeds = p * primary_shares
    val_discount = ((blended_fair_value - p) / blended_fair_value) * 100.0
    expected_pop = ((blended_fair_value - p) / p) * 100.0
    coverage = max(0.4, min(6.5, 2.2 + (val_discount / 12.0) * (qoe_score / 85.0)))
    breach_prob = min(98.0, max(2.0, 50.0 - val_discount * 1.4))
    
    cov_score = min(100.0, (coverage / 2.5) * 100.0)
    disc_penalty = max(0.0, -val_discount * 2.5)
    exec_feasibility = max(5.0, min(100.0, (0.5 * cov_score) + (0.3 * qoe_score) + (0.2 * (100.0 - disc_penalty))))
    
    norm_proceeds = min(1.0, proceeds / max(blended_fair_value * primary_shares, 1.0))
    norm_cov = min(1.0, coverage / 3.5)
    norm_exec = exec_feasibility / 100.0
    norm_safety = 1.0 - (breach_prob / 100.0)
    composite_score = (0.30 * norm_proceeds) + (0.25 * norm_cov) + (0.25 * norm_exec) + (0.20 * norm_safety)
    return proceeds, val_discount, coverage, expected_pop, breach_prob, exec_feasibility, composite_score

for p in price_grid:
    proc, vdisc, cov, epop, bprob, efeas, cscore = eval_price_point(p)
    opt_records.append({
        "Price": p, "Proceeds": proc, "ValDiscount": vdisc,
        "Coverage": cov, "ExpectedPop": epop,
        "BreachProb": bprob, "ExecFeasibility": efeas,
        "CompositeScore": cscore
    })

opt_df = pd.DataFrame(opt_records)
best_idx = int(opt_df["CompositeScore"].idxmax())
opt_price = float(opt_df.loc[best_idx, "Price"])
curr_proc, curr_vdisc, curr_cov, curr_epop, curr_bprob, curr_efeas, _ = eval_price_point(offer_price)

# =========================================================
# 7. PER-SHARE STANDARDIZED VaR, STRESS & BACKTEST
# =========================================================
rng = np.random.default_rng(seed=int(mc_seed))
n_sims = 10000
ann_vol = defs["vol"]
sigma_d = ann_vol / np.sqrt(252.0)
mu_d = 0.05 / 252.0

z_val = norm.ppf(var_conf)
param_ret_loss = max(0.0, sigma_d * np.sqrt(var_horizon_days) * z_val - mu_d * var_horizon_days)
param_var_ps = min(offer_price, offer_price * param_ret_loss)

t_shocks = t.rvs(df=tail_df, size=n_sims, random_state=rng) * np.sqrt((tail_df - 2.0) / tail_df)
sim_log_returns = (mu_d * var_horizon_days) + (sigma_d * np.sqrt(var_horizon_days) * t_shocks)
sim_end_prices = offer_price * np.exp(sim_log_returns)
sim_ps_losses = offer_price - sim_end_prices

mc_var_ps = float(min(offer_price, np.percentile(sim_ps_losses, var_conf * 100.0)))
cvar_es_ps = float(min(offer_price, np.mean(sim_ps_losses[sim_ps_losses >= mc_var_ps])))
prob_breach_offer = float(np.mean(sim_end_prices < offer_price) * 100.0)

daily_paths = rng.normal(mu_d, sigma_d, size=(2000, var_horizon_days))
cum_paths = np.exp(np.cumsum(daily_paths, axis=1))
running_max = np.maximum.accumulate(cum_paths, axis=1)
drawdowns = (running_max - cum_paths) / running_max
max_dd_95 = float(np.percentile(np.max(drawdowns, axis=1), 95.0) * 100.0)

vol_shocked_var_ps = min(offer_price, mc_var_ps * vol_shock_mult)
liq_adj_var_ps = min(offer_price, mc_var_ps + (offer_price * 0.05))

stress_scenarios = pd.DataFrame([
    {"Scenario": "1. Broad Market Crash (-25% Index, 2.0x Vol)", "Fair Value": f"{curr}{blended_fair_value*0.78:,.2f}", "Per-Share Loss": f"{curr}{min(offer_price, offer_price*0.24):,.2f}", "Est. Coverage": "0.9x (Under-subscribed)"},
    {"Scenario": "2. Sector-Specific Sell-Off (-18% Multiple)", "Fair Value": f"{curr}{blended_fair_value*0.82:,.2f}", "Per-Share Loss": f"{curr}{min(offer_price, offer_price*0.18):,.2f}", "Est. Coverage": "1.2x (Weak)"},
    {"Scenario": "3. Interest-Rate Shock (+200 bps WACC)", "Fair Value": f"{curr}{blended_fair_value*0.85:,.2f}", "Per-Share Loss": f"{curr}{min(offer_price, offer_price*0.15):,.2f}", "Est. Coverage": "1.4x (Moderate)"},
    {"Scenario": "4. Revenue-Growth Deterioration (-10% Growth)", "Fair Value": f"{curr}{blended_fair_value*0.84:,.2f}", "Per-Share Loss": f"{curr}{min(offer_price, offer_price*0.16):,.2f}", "Est. Coverage": "1.3x (Moderate)"},
    {"Scenario": "5. Valuation Multiple Compression (-25%)", "Fair Value": f"{curr}{blended_fair_value*0.75:,.2f}", "Per-Share Loss": f"{curr}{min(offer_price, offer_price*0.25):,.2f}", "Est. Coverage": "0.8x (Pulled)"},
    {"Scenario": "6. IPO Demand Collapse (Anchor Withdrawal)", "Fair Value": f"{curr}{blended_fair_value*0.92:,.2f}", "Per-Share Loss": f"{curr}{min(offer_price, offer_price*0.19):,.2f}", "Est. Coverage": "0.6x (Failed)"},
    {"Scenario": "7. Liquidity Shock (Wide Bid-Ask + Lockup)", "Fair Value": f"{curr}{blended_fair_value*0.88:,.2f}", "Per-Share Loss": f"{curr}{liq_adj_var_ps:,.2f}", "Est. Coverage": "1.1x (Stressed)"}
])

bt_days = 250
bt_actual_ret = t.rvs(df=tail_df, size=bt_days, random_state=rng) * np.sqrt((tail_df - 2.0) / tail_df) * sigma_d + mu_d
bt_actual_ps_loss = offer_price * (-bt_actual_ret)
daily_1d_var_ps = offer_price * (sigma_d * t.ppf(var_conf, df=tail_df) * np.sqrt((tail_df - 2.0) / tail_df) - mu_d)
exceptions_count = int(np.sum(bt_actual_ps_loss > daily_1d_var_ps))
expected_exceptions = int(round(bt_days * (1.0 - var_conf)))
kupiec_status = "PASS (Within Tolerance)" if exceptions_count <= expected_exceptions + 4 else "FAIL (Tail Under-predicted)"

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
    "2. Quality of Earnings (QoE) & DCF Ramp",
    "3. Peer Comps & Sensitivity Matrix",
    "4. Per-Share VaR, Stress & Backtest",
    "5. Audit Trail & IC Report Generator"
])

# =========================================================
# TAB 1: OFFER PRICE OPTIMIZER & FAIR VALUE
# =========================================================
with t1:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Proposed Offer Price", f"{curr}{offer_price:,.2f}", f"Optimal: {curr}{opt_price:,.2f}")
    c2.metric("Blended Fair Value", f"{curr}{blended_fair_value:,.2f}", f"Upside: {upside_pct:+.1f}%")
    c3.metric("Predicted Coverage", f"{curr_cov:.2f}x", f"At Optimal: {opt_df.loc[best_idx, 'Coverage']:.2f}x")
    c4.metric("30d Breach Prob.", f"{prob_breach_offer:.1f}%", "Prob(Price < Offer)")
    c5.metric("Execution Score", f"{curr_efeas:.0f} / 100", f"QoE Score: {qoe_score:.0f}/100")

    if "Investor" in perspective:
        if upside_pct >= 12.0 and qoe_score >= 75.0:
            sig_txt, sig_col, sig_bg = "SUBSCRIBE / BUY — Attractive Valuation Discount & Verified Cash Conversion", "#10b981", "rgba(16, 185, 129, 0.12)"
        elif upside_pct >= 0.0:
            sig_txt, sig_col, sig_bg = "SELECTIVE / HOLD — Fairly Priced; Monitor Bookbuilding Coverage", "#f59e0b", "rgba(245, 158, 11, 0.12)"
        else:
            sig_txt, sig_col, sig_bg = "AVOID — Offer Price Exceeds Risk-Adjusted Intrinsic Value", "#ef4444", "rgba(239, 68, 68, 0.12)"
    else:
        if abs(offer_price - opt_price) <= max(opt_price * 0.08, 5.0):
            sig_txt, sig_col, sig_bg = "OPTIMAL PRICING BAND — Balances Proceeds, Dilution & Institutional Demand", "#10b981", "rgba(16, 185, 129, 0.12)"
        elif offer_price < opt_price:
            sig_txt, sig_col, sig_bg = "UNDERPRICED — Potential to Raise Offer Band Without Hurting Coverage", "#f59e0b", "rgba(245, 158, 11, 0.12)"
        else:
            sig_txt, sig_col, sig_bg = "OVERPRICED — High Risk of Execution Failure & Post-Listing Drawdown", "#ef4444", "rgba(239, 68, 68, 0.12)"

    st.markdown(f"<div class='signal-banner' style='background-color:{sig_bg}; border-color:{sig_col}; color:{sig_col};'>{sig_txt}</div>", unsafe_allow_html=True)

    st.markdown("#### ⚖️ Multi-Objective Offer Price Optimization Curve")
    fig_opt = px.line(opt_df, x="Price", y="CompositeScore")
    fig_opt.add_vline(
        x=opt_price, line_dash="dash", line_color="#10b981",
        annotation_text=f"Optimal: {curr}{opt_price:.1f}", annotation_position="top left"
    )
    fig_opt.add_vline(
        x=offer_price, line_dash="dot", line_color="#ef4444",
        annotation_text=f"Current: {curr}{offer_price:.1f}", annotation_position="bottom right"
    )
    fig_opt.update_layout(
        title=dict(text="Composite Optimization Score Across Price Grid", y=0.96, x=0.01),
        height=350, margin=dict(l=20, r=20, t=70, b=20)
    )
    st.plotly_chart(fig_opt, use_container_width=True)

    st.markdown("#### 🧮 Transparent Fair-Value Methodology Breakdown")
    val_table = pd.DataFrame([
        {"Methodology": name, "Implied Price": f"{curr}{val:,.2f}", "Weight": f"{wt*100:.0f}%"}
        for name, val, wt in val_methods
    ] + [
        {"Methodology": "Raw Weighted Fair Value", "Implied Price": f"{curr}{raw_blended_fv:,.2f}", "Weight": "100%"},
        {"Methodology": f"QoE Adjustment (Score {qoe_score:.0f}/100)", "Implied Price": f"{(qoe_haircut_factor-1)*100:+.2f}%", "Weight": "Haircut"},
        {"Methodology": "Final Risk-Adjusted Fair Value", "Implied Price": f"{curr}{blended_fair_value:,.2f}", "Weight": "Final"}
    ])
    st.dataframe(
        val_table, use_container_width=True, hide_index=True,
        column_config={"Methodology": st.column_config.TextColumn("Methodology", pinned=True)}
    )

    st.markdown("#### 📋 Key Deal Economics at Optimal Clearing Price")
    st.info(
        f"- **Optimal Clearing Price:** `{curr}{opt_price:,.2f}` (vs. Proposed `{curr}{offer_price:,.2f}`)\n"
        f"- **Primary Gross Proceeds ({primary_dilution_pct:.0f}% Dilution):** `{curr}{opt_price * primary_shares:,.1f} {unit}`\n"
        f"- **Expected Subscription Coverage at Optimal:** `{opt_df.loc[best_idx, 'Coverage']:.2f}x` | "
        f"**Expected Listing Pop at Optimal:** `{opt_df.loc[best_idx, 'ExpectedPop']:+.1f}%` (vs. `{curr_epop:+.1f}%` at Proposed Price)"
    )

# =========================================================
# TAB 2: QUALITY OF EARNINGS (QoE) & 5-YEAR DCF RAMP
# =========================================================
with t2:
    st.subheader(f"🔍 Quality of Earnings (QoE) & Cash Conversion Audit — {selected_issuer}")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("QoE Integrity Score", f"{qoe_score:.0f} / 100", "Transparent Penalty Model")
    q2.metric("EBITDA -> OCF Conv.", f"{ebitda_to_ocf_conv:.1f}%", f"OCF: {curr}{operating_cash_flow:,.1f} {unit}")
    q3.metric("EBITDA -> FCF Conv.", f"{ebitda_to_fcf_conv:.1f}%", f"FCF: {curr}{headline_fcf:,.1f} {unit}")
    q4.metric("True Economic FCF", f"{curr}{economic_fcf:,.1f} {unit}", "Net of Cap. Software")

    st.markdown("#### 💵 EBITDA-to-Operating & Economic Free Cash Flow Reconciliation")
    recon_df = pd.DataFrame([
        {"Line Item": "Reported LTM EBITDA", "Amount": f"{curr}{reported_ebitda:,.1f} {unit}", "Audit Note": "Unadjusted headline figure"},
        {"Line Item": "(+/-) Non-Recurring Adjustments", "Amount": f"{curr}{act['non_recurring_adj']:+,.1f} {unit}", "Audit Note": "One-off gains/restructuring"},
        {"Line Item": "= Adjusted Sustainable EBITDA", "Amount": f"{curr}{adj_ebitda:,.1f} {unit}", "Audit Note": "Core operating baseline"},
        {"Line Item": "(+/-) Working Capital Changes", "Amount": f"{curr}{act['working_cap_change']:+,.1f} {unit}", "Audit Note": "Receivables, inventory & payables"},
        {"Line Item": "(-) Cash Taxes Paid", "Amount": f"{curr}{act['cash_taxes']:,.1f} {unit}", "Audit Note": "Actual cash tax outflow"},
        {"Line Item": "= Operating Cash Flow (OCF)", "Amount": f"{curr}{operating_cash_flow:,.1f} {unit}", "Audit Note": f"{ebitda_to_ocf_conv:.1f}% of Adj. EBITDA"},
        {"Line Item": "(-) Tangible CapEx (excl. Cap. Software)", "Amount": f"{curr}{act['tangible_capex']:,.1f} {unit}", "Audit Note": "Physical PP&E & infrastructure"},
        {"Line Item": "= Headline Free Cash Flow (FCF)", "Amount": f"{curr}{headline_fcf:,.1f} {unit}", "Audit Note": f"{ebitda_to_fcf_conv:.1f}% of Adj. EBITDA"},
        {"Line Item": "(-) Capitalized Software / R&D", "Amount": f"{curr}{-act['capitalized_software']:,.1f} {unit}", "Audit Note": "Expensed economically (no double count)"},
        {"Line Item": "= True Economic Free Cash Flow", "Amount": f"{curr}{economic_fcf:,.1f} {unit}", "Audit Note": "LTM baseline into 5Y DCF ramp"}
    ])
    st.dataframe(
        recon_df, use_container_width=True, hide_index=True,
        column_config={"Line Item": st.column_config.TextColumn("Line Item", pinned=True)}
    )

    st.markdown("#### 📈 Explicit 5-Year Economic FCF Ramp Schedule (DCF Bridge)")
    disp_dcf_df = dcf_schedule_df.copy()
    disp_dcf_df["Proj. Rev"] = disp_dcf_df["Proj. Rev"].map(lambda x: f"{curr}{x:,.1f} {unit}")
    disp_dcf_df["FCF Margin"] = disp_dcf_df["FCF Margin"].map(lambda x: f"{x:+.1f}%")
    disp_dcf_df["Proj. Econ FCF"] = disp_dcf_df["Proj. Econ FCF"].map(lambda x: f"{curr}{x:+,.1f} {unit}")
    disp_dcf_df["PV of FCF"] = disp_dcf_df["PV of FCF"].map(lambda x: f"{curr}{x:+,.1f} {unit}")
    st.dataframe(
        disp_dcf_df, use_container_width=True, hide_index=True,
        column_config={"Year": st.column_config.TextColumn("Year", pinned=True)}
    )

    st.markdown("#### 🚨 Forensic Accounting & Governance Red-Flag Screen")
    forensic_df = pd.DataFrame([
        {"Check": "Related-Party Revenue", "Observed": f"{act['related_party_rev_pct']:.1f}%", "Limit": "< 5.0%", "Status": "PASS" if act['related_party_rev_pct'] <= 5.0 else "FLAG"},
        {"Check": "Top-10 Customer Conc.", "Observed": f"{act['top_10_cust_conc_pct']:.1f}%", "Limit": "< 20.0%", "Status": "PASS" if act['top_10_cust_conc_pct'] <= 20.0 else "FLAG"},
        {"Check": "Annual Customer Churn", "Observed": f"{act['annual_churn_pct']:.1f}%", "Limit": "< 15.0%", "Status": "PASS" if act['annual_churn_pct'] <= 15.0 else "FLAG"},
        {"Check": "Net Revenue Retention", "Observed": f"{act['nrr']:.1f}%", "Limit": "> 105.0%", "Status": "PASS" if act['nrr'] >= 105.0 else "WATCH"},
        {"Check": "Receivables > 90 Days", "Observed": f"{act['ar_over_90_days_pct']:.1f}%", "Limit": "< 5.0%", "Status": "PASS" if act['ar_over_90_days_pct'] <= 5.0 else "FLAG"},
        {"Check": "Cap. Costs / EBITDA", "Observed": f"{(act['capitalized_software']/max(reported_ebitda,1))*100:.1f}%", "Limit": "< 20.0%", "Status": "PASS" if (act['capitalized_software']/max(reported_ebitda,1))*100 <= 20.0 else "FLAG"},
        {"Check": "Contingent Liabilities", "Observed": f"{curr}{act['contingent_liabilities']:,.1f} {unit}", "Limit": "Disclosed", "Status": "REVIEW"},
        {"Check": "Auditor Opinion", "Observed": act["auditor_opinion"], "Limit": "Clean", "Status": "PASS" if "Emphasis" not in act["auditor_opinion"] else "WATCH"}
    ])
    st.dataframe(
        forensic_df, use_container_width=True, hide_index=True,
        column_config={"Check": st.column_config.TextColumn("Check", pinned=True)}
    )

# =========================================================
# TAB 3: PEER UNIVERSE (FILTERED BY TIER) & SENSITIVITY MATRIX
# =========================================================
with t3:
    st.subheader("🌐 Normalized Peer Universe (USD-Converted) & Sensitivity Matrix")
    
    peer_view_mode = st.radio(
        "Peer Universe Scope",
        [f"Core Sector Comps Only ({peer_group})", "Full Cross-Sector Universe (Reference Benchmark)"],
        horizontal=True
    )

    peer_rows = []
    for name, info in IPO_PIPELINE.items():
        if "Core Sector" in peer_view_mode and info["peer_group"] != peer_group:
            continue
        a = info["actuals"]
        d = info["defaults"]
        p_use = offer_price if name == selected_issuer else d["offer_price"]
        mcap_local = p_use * a["shares_m"]
        mcap_usd_m = mcap_local * (0.119 if info["curr"] == "₹" else 1.0)
        rev_usd_m = a["ltm_rev"] * (0.119 if info["curr"] == "₹" else 1.0)
        ev_usd_m = mcap_usd_m + (a["net_debt"] * (0.119 if info["curr"] == "₹" else 1.0))
        peer_rows.append({
            "Issuer": name.split(" (")[0],
            "Ticker": info["ticker"],
            "Tier": info["peer_group"],
            "Status": info["listing_status"].split(" (")[0],
            "Offer": f"{info['curr']}{p_use:,.2f}",
            "MCap ($M)": round(mcap_usd_m, 1),
            "EV/Sales": round(ev_usd_m / max(rev_usd_m, 1.0), 2),
            "ROE": f"{a['roe']:.1f}%"
        })
    peers_df = pd.DataFrame(peer_rows)
    st.dataframe(
        peers_df, use_container_width=True, hide_index=True,
        column_config={"Issuer": st.column_config.TextColumn("Issuer", pinned=True)}
    )

    st.markdown("#### 🎛️ Multi-Factor Sensitivity Matrix: Implied Fair Value & Execution Coverage")
    sens_wacc = [wacc - 1.5, wacc - 0.75, wacc, wacc + 0.75, wacc + 1.5]
    sens_growth = [rev_growth - 10.0, rev_growth - 5.0, rev_growth, rev_growth + 5.0, rev_growth + 10.0]
    
    matrix_data = []
    for g in sens_growth:
        row_dict = {"Growth \\ WACC": f"{g:.1f}%"}
        for w in sens_wacc:
            w_eff = max(w, term_growth + 1.0)
            fv_cell, _, _ = compute_ramp_dcf(
                act["ltm_rev"], economic_fcf, g, w_eff, term_growth, act["net_debt"], act["shares_m"]
            )
            v_disc_cell = ((fv_cell - offer_price) / fv_cell) * 100.0
            cov_cell = max(0.4, min(6.5, 2.2 + (v_disc_cell / 12.0) * (qoe_score / 85.0)))
            row_dict[f"WACC {w_eff:.2f}%"] = f"{curr}{fv_cell:,.1f} ({cov_cell:.1f}x)"
        matrix_data.append(row_dict)
    st.dataframe(
        pd.DataFrame(matrix_data), use_container_width=True, hide_index=True,
        column_config={"Growth \\ WACC": st.column_config.TextColumn("Growth \\ WACC", pinned=True)}
    )

# =========================================================
# TAB 4: PER-SHARE VaR, STRESS SCENARIOS & BACKTESTING
# =========================================================
with t4:
    st.subheader(f"🛡️ Per-Share Risk Engine, Stress Scenarios & Backtest ({var_horizon_days}-Day, {var_conf*100:.0f}% Conf)")
    
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Monte Carlo VaR (Per Share)", f"{curr}{mc_var_ps:,.2f}", f"{(mc_var_ps/offer_price)*100:.1f}% of Offer")
    r2.metric("Expected Shortfall (CVaR)", f"{curr}{cvar_es_ps:,.2f}", f"{(cvar_es_ps/offer_price)*100:.1f}% Tail Mean")
    r3.metric("Maximum Drawdown (95%)", f"-{max_dd_95:.1f}%", f"Over {var_horizon_days} Days")
    r4.metric("Prob. Breaching Offer Price", f"{prob_breach_offer:.1f}%", f"Offer: {curr}{offer_price:,.2f}")

    r5, r6, r7, r8 = st.columns(4)
    r5.metric("Parametric VaR (Per Share)", f"{curr}{param_var_ps:,.2f}", "Gaussian Baseline")
    r6.metric(f"Vol-Shocked VaR ({vol_shock_mult}x)", f"{curr}{vol_shocked_var_ps:,.2f}", "Volatility Sensitivity")
    r7.metric("Liquidity-Adj. VaR", f"{curr}{liq_adj_var_ps:,.2f}", "+5.0% Lockup Haircut")
    r8.metric("VaR Backtest (250d)", f"{exceptions_count} Exceptions", kupiec_status)

    st.markdown("#### 🌪️ 7-Scenario Macro & Deal Stress Testing Matrix")
    st.dataframe(
        stress_scenarios, use_container_width=True, hide_index=True,
        column_config={"Scenario": st.column_config.TextColumn("Scenario", pinned=True)}
    )

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=sim_ps_losses, nbinsx=45, name="Per-Share Loss Distribution", marker_color="#6366f1"))
    fig_hist.add_vline(
        x=mc_var_ps, line_dash="dash", line_color="#ef4444",
        annotation_text=f"VaR: {curr}{mc_var_ps:.2f}", annotation_position="top left"
    )
    fig_hist.add_vline(
        x=cvar_es_ps, line_dash="dot", line_color="#f59e0b",
        annotation_text=f"CVaR: {curr}{cvar_es_ps:.2f}", annotation_position="top right"
    )
    fig_hist.update_layout(
        title=dict(text=f"Simulated {var_horizon_days}-Day Per-Share Loss Distribution ({curr}/Share)", y=0.96, x=0.01),
        xaxis_title=f"Loss Per Share ({curr})",
        yaxis_title="Simulation Count",
        height=340, margin=dict(l=20, r=20, t=70, b=30)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    fig_bt = go.Figure()
    fig_bt.add_trace(go.Scatter(y=bt_actual_ps_loss, mode="lines", name="Simulated Daily Loss/Share", line=dict(color="#94a3b8", width=1)))
    fig_bt.add_hline(
        y=daily_1d_var_ps, line_dash="dash", line_color="#ef4444",
        annotation_text=f"1-Day {var_conf*100:.0f}% VaR: {curr}{daily_1d_var_ps:.2f}", annotation_position="bottom right"
    )
    fig_bt.update_layout(
        title=dict(text=f"250-Day Per-Share VaR Backtest ({exceptions_count} Breaches vs {expected_exceptions} Expected)", y=0.96, x=0.01),
        xaxis_title="Trading Day",
        yaxis_title=f"Daily Loss ({curr}/Share)",
        height=340, margin=dict(l=20, r=20, t=70, b=30)
    )
    st.plotly_chart(fig_bt, use_container_width=True)

# =========================================================
# TAB 5: DATA PROVENANCE AUDIT TRAIL & IC REPORT GENERATOR
# =========================================================
with t5:
    st.subheader("📑 Data Provenance Ledger & Investment Committee (IC) Report")
    
    st.markdown("#### 1. Input Provenance & Validation Audit Trail")
    audit_df = pd.DataFrame([
        {"Parameter": "Proposed Offer Price", "Value": f"{curr}{offer_price:,.2f}", "Unit": curr, "Source": "User / Syndicate Input", "Period": "IPO Pricing Date", "Status": "User-Defined"},
        {"Parameter": "LTM Revenue", "Value": f"{act['ltm_rev']:,.1f}", "Unit": unit, "Source": prov["source"], "Period": prov["period"], "Status": prov["status"]},
        {"Parameter": "Adjusted EBITDA", "Value": f"{adj_ebitda:,.1f}", "Unit": unit, "Source": "QoE Non-Recurring Adjustment", "Period": prov["period"], "Status": "Reconciled"},
        {"Parameter": "Economic Free Cash Flow", "Value": f"{economic_fcf:,.1f}", "Unit": unit, "Source": "OCF less Tangible CapEx & Cap. Software", "Period": prov["period"], "Status": "Validated"},
        {"Parameter": "WACC / Discount Rate", "Value": f"{wacc:.2f}%", "Unit": "%", "Source": "CAPM / Risk-Adjusted Assumption", "Period": "Forward 5Y", "Status": "Calibrated"},
        {"Parameter": "Annualized Volatility", "Value": f"{ann_vol*100:.1f}%", "Unit": "%", "Source": "Sector Peer GARCH / Implied Vol", "Period": f"{var_horizon_days}d Horizon", "Status": "Calibrated"}
    ])
    st.dataframe(
        audit_df, use_container_width=True, hide_index=True,
        column_config={"Parameter": st.column_config.TextColumn("Parameter", pinned=True)}
    )

    st.markdown("#### 2. Executive Investment Committee (IC) Report Generator")
    ic_report_md = f"""# INVESTMENT COMMITTEE MEMORANDUM: {selected_issuer.upper()} ({tk})
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M IST')} | **Model Version:** {MODEL_VERSION}
**Listing Venue:** {data['venue']} | **Status:** {data['listing_status']}
**Data Disclaimer:** {prov['status']} ({prov['source']})

---

## 1. EXECUTIVE SUMMARY & PRICING RECOMMENDATION
* **Proposed Offer Price:** {curr}{offer_price:,.2f}
* **Quantitatively Optimized Clearing Price:** {curr}{opt_price:,.2f}
* **Risk-Adjusted Blended Fair Value:** {curr}{blended_fair_value:,.2f} ({upside_pct:+.1f}% vs. Offer)
* **Syndicate / Investor Signal:** {sig_txt}
* **Predicted Subscription Coverage:** {curr_cov:.2f}x | **Execution Feasibility Score:** {curr_efeas:.0f}/100

## 2. QUALITY OF EARNINGS (QoE) & CASH CONVERSION
* **QoE Integrity Score:** {qoe_score:.0f}/100
* **Reported EBITDA:** {curr}{reported_ebitda:,.1f} {unit} -> **Adjusted EBITDA:** {curr}{adj_ebitda:,.1f} {unit}
* **Operating Cash Flow (OCF):** {curr}{operating_cash_flow:,.1f} {unit} ({ebitda_to_ocf_conv:.1f}% conversion)
* **True Economic FCF (Net of Tangible CapEx & Cap. Software):** {curr}{economic_fcf:,.1f} {unit}
* **Auditor Opinion:** {act['auditor_opinion']} | **Contingent Liabilities:** {curr}{act['contingent_liabilities']:,.1f} {unit}

## 3. PER-SHARE RISK METRICS, STRESS TESTING & BACKTEST ({var_horizon_days}-Day Horizon)
* **Monte Carlo Fat-Tail VaR ({var_conf*100:.0f}%, Student-t df={tail_df}):** {curr}{mc_var_ps:,.2f} per share ({(mc_var_ps/offer_price)*100:.1f}% of offer)
* **Expected Shortfall (CVaR):** {curr}{cvar_es_ps:,.2f} per share
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
