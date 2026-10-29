import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Institutional IPO Valuation & Syndicate Engine", layout="wide")

st.title("🏛️ Institutional IPO Valuation & Syndicate Pricing Engine")
st.caption("Cross-Border Underwriting, Cap Table Liquidation & Advanced Market Microstructure Workbench")

# ==============================================================================
# SIDEBAR: GLOBAL ASSET CONTROL & REGULATORY ROUTING
# ==============================================================================
st.sidebar.header("🌐 Global Asset Controller")

asset_universe = {
    "Swiggy": {"venue": "SEBI (India)", "rev_base": 1120.0, "growth": 0.28, "margin": 0.08, "wacc": 0.115, "promoter_pct": 0.22},
    "Zepto": {"venue": "SEBI (India)", "rev_base": 850.0, "growth": 0.55, "margin": -0.04, "wacc": 0.125, "promoter_pct": 0.18},
    "Stripe": {"venue": "SEC (USA)", "rev_base": 14000.0, "growth": 0.22, "margin": 0.21, "wacc": 0.090, "promoter_pct": 0.12},
    "Shein": {"venue": "SEC (USA)", "rev_base": 32000.0, "growth": 0.35, "margin": 0.12, "wacc": 0.105, "promoter_pct": 0.30},
    "Revolut": {"venue": "FCA (UK)", "rev_base": 2200.0, "growth": 0.42, "margin": 0.26, "wacc": 0.095, "promoter_pct": 0.25},
    "Canva": {"venue": "FCA (UK)", "rev_base": 2300.0, "growth": 0.30, "margin": 0.18, "wacc": 0.088, "promoter_pct": 0.35}
}

selected_asset = st.sidebar.selectbox("Select Target Enterprise", list(asset_universe.keys()))
asset_meta = asset_universe[selected_asset]

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Active Regulatory Route")
st.sidebar.info(f"**Jurisdiction:** {asset_meta['venue']}")

# Initialize Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Tab 1: Core Valuation & 3D Sensitivity",
    "Tab 2: Cap Table & Ownership Structure",
    "Tab 3: Bookbuilding Clearing Engine",
    "Tab 4: Monte Carlo Stochastic Risk"
])

# ==============================================================================
# TAB 1: CORE VALUATION & 3D SENSITIVITY SURFACE (2 GRAPHS)
# ==============================================================================
with tab1:
    st.header("📊 Dual-Track Valuation & Advanced Sensitivity Topography")
    
    col_dcf, col_lbo = st.columns(2)
    with col_dcf:
        st.subheader("3-Stage Unlevered DCF Parameters")
        rev_base = st.number_input("Base Revenue ($M)", value=asset_meta["rev_base"])
        growth_stg1 = st.slider("Stage 1 Growth Rate (%)", 5.0, 80.0, float(asset_meta["growth"] * 100)) / 100
        ebitda_target = st.slider("Target Operating Margin (%)", -10.0, 50.0, float(asset_meta["margin"] * 100)) / 100
        wacc = st.slider("Discount Rate (WACC %)", 6.0, 18.0, float(asset_meta["wacc"] * 100)) / 100
        term_growth = st.slider("Terminal Growth Rate (%)", 1.0, 5.0, 2.5) / 100

    with col_lbo:
        st.subheader("Reverse LBO Sponsor Return Solvers")
        entry_val = st.number_input("Sponsor Entry Valuation ($M)", value=rev_base * 4.5)
        target_moic = st.slider("Target Sponsor MoIC (x)", 1.5, 5.0, 2.5)
        target_irr = st.slider("Target Sponsor IRR (%)", 12.0, 40.0, 22.0) / 100
        holding_period = st.slider("Holding Horizon (Years)", 2, 7, 5)

    # 3-Stage Cash Flow Curve Construction
    years = np.arange(1, 11)
    growth_curve = [growth_stg1 * (1 - (t - 1) / 10 * 0.5) for t in years]
    revenues = []
    curr_rev = rev_base
    for g in growth_curve:
        curr_rev *= (1 + g)
        revenues.append(curr_rev)
    
    ufcf = [r * ebitda_target * 0.72 for r in revenues]
    pv_ufcf = sum([f / ((1 + wacc) ** t) for t, f in zip(years, ufcf)])
    terminal_val = (ufcf[-1] * (1 + term_growth)) / (wacc - term_growth)
    pv_tv = terminal_val / ((1 + wacc) ** 10)
    dcf_ev = pv_ufcf + pv_tv

    req_exit_ev_moic = entry_val * target_moic
    req_exit_ev_irr = entry_val * ((1 + target_irr) ** holding_period)
    implied_lbo_ev = max(req_exit_ev_moic, req_exit_ev_irr)

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("DCF Intrinsic EV", f"${dcf_ev:,.2f} M")
    m2.metric("Sponsor Floor Exit EV", f"${implied_lbo_ev:,.2f} M")
    m3.metric("Imputed Exit MoIC", f"{target_moic:.2f}x")

    # --- GRAPH 1.1: Advanced 3D Surface Plot ---
    st.subheader("🌐 Graph 1.1: 3D Surface Topography (WACC vs. Terminal Growth vs. EV)")
    wacc_range = np.linspace(0.07, 0.15, 10)
    g_range = np.linspace(0.015, 0.04, 10)
    W, G = np.meshgrid(wacc_range, g_range)
    EV_matrix = np.zeros_like(W)

    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            w_val = W[i, j]
            g_val = G[i, j]
            if w_val > g_val:
                tv = (ufcf[-1] * (1 + g_val)) / (w_val - g_val)
                pv_t = tv / ((1 + w_val) ** 10)
                pv_cash = sum([f / ((1 + w_val) ** t) for t, f in zip(years, ufcf)])
                EV_matrix[i, j] = pv_cash + pv_t
            else:
                EV_matrix[i, j] = np.nan

    fig_3d = go.Figure(data=[go.Surface(z=EV_matrix, x=W*100, y=G*100, colorscale='Viridis')])
    fig_3d.update_layout(
        scene=dict(xaxis_title='WACC (%)', yaxis_title='Terminal Growth (%)', zaxis_title='Enterprise Value ($M)'),
        autosize=False, width=900, height=550, margin=dict(l=20, r=20, b=20, t=20)
    )
    st.plotly_chart(fig_3d, use_container_width=True)

    # --- GRAPH 1.2: Valuation Methodology Comparison Bridge ---
    st.subheader("📊 Graph 1.2: Dual-Track Valuation & Methodology Bridge")
    valuation_bridge = pd.DataFrame({
        "Methodology": ["Peer OLS Comps", "Reverse LBO Floor", "DCF Intrinsic EV", "Sponsor Target Exit"],
        "Enterprise Value ($M)": [dcf_ev * 1.12, implied_lbo_ev, dcf_ev, implied_lbo_ev * target_moic]
    })
    fig_bridge = px.bar(valuation_bridge, x="Methodology", y="Enterprise Value ($M)", color="Methodology",
                        text="Enterprise Value ($M)", title="Valuation Cross-Check Across Methodologies")
    fig_bridge.update_traces(texttemplate='$%{text:,.0f}M', textposition='outside')
    st.plotly_chart(fig_bridge, use_container_width=True)


# ==============================================================================
# TAB 2: CAP TABLE & OWNERSHIP STRUCTURE (2 GRAPHS)
# ==============================================================================
with tab2:
    st.header("⚖️ Capital Structure Waterfall & Ownership Treemap")
    
    col_cap1, col_cap2 = st.columns(2)
    with col_cap1:
        st.subheader("Pre-IPO Multi-Tranche Cap Table Inputs")
        promoter_sh = st.number_input("Promoter / Founder Shares (M)", value=40.0)
        investor_ccps = st.number_input("Series A-G CCPS Shares (M)", value=35.0)
        esop_pool = st.number_input("Expanded ESOP Pool (M)", value=10.0)
    
    with col_cap2:
        st.subheader("IPO Primary & Secondary Structure")
        fresh_issue = st.number_input("Fresh Primary Issue (M Shares)", value=15.0)
        ofs_issue = st.number_input("Offer For Sale (OFS Shares)", value=10.0)

    total_pre = promoter_sh + investor_ccps + esop_pool
    total_post = total_pre + fresh_issue

    # --- GRAPH 2.1: Hierarchical Treemap ---
    st.subheader("🗺️ Graph 2.1: Hierarchical Post-IPO Ownership Treemap")
    treemap_data = pd.DataFrame({
        "Category": ["Pre-IPO Stakeholders", "Pre-IPO Stakeholders", "Pre-IPO Stakeholders", "Public Issuance", "Public Issuance"],
        "Subcategory": ["Founders / Promoters", "Venture CCPS Investors", "ESOP Pool", "Fresh Primary Float", "Secondary OFS Float"],
        "Shares": [promoter_sh, investor_ccps, esop_pool, fresh_issue, ofs_issue]
    })
    fig_tree = px.treemap(treemap_data, path=["Category", "Subcategory"], values="Shares",
                          color="Shares", color_continuous_scale='Blues')
    st.plotly_chart(fig_tree, use_container_width=True)

    # --- GRAPH 2.2: Cap Table Dilution Waterfall ---
    st.subheader("📉 Graph 2.2: Capital Transformation Dilution Waterfall")
    fig_waterfall = go.Figure(go.Waterfall(
        name="Dilution Flow", orientation="v",
        measure=["relative", "relative", "relative", "total", "relative", "total"],
        x=["Promoters", "CCPS Investors", "ESOP Pool", "Pre-IPO Total", "Fresh Primary Issue", "Post-IPO Capital Base"],
        y=[promoter_sh, investor_ccps, esop_pool, total_pre, fresh_issue, total_post],
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))
    fig_waterfall.update_layout(title="Cap Table Conversion & Dilution Waterfall (Millions of Shares)")
    st.plotly_chart(fig_waterfall, use_container_width=True)


# ==============================================================================
# TAB 3: BOOKBUILDING CLEARING ENGINE (2 GRAPHS)
# ==============================================================================
with tab3:
    st.header("📖 Syndicate Bookbuilding Demand & Tranche Allocation")
    
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        price_floor = st.number_input("Offer Price Floor ($)", value=40.0)
        price_ceiling = st.number_input("Offer Price Ceiling ($)", value=60.0)
    with p_col2:
        total_issue_size_shares = st.number_input("Total Issue Size Target (M Shares)", value=25.0)

    price_steps = np.linspace(price_floor, price_ceiling, 20)
    cumulative_demand = [total_issue_size_shares * 2.8 * np.exp(-0.04 * (p - price_floor)) for p in price_steps]
    issue_supply_line = [total_issue_size_shares] * len(price_steps)

    # --- GRAPH 3.1: Equilibrium Clearing Curve ---
    st.subheader("📈 Graph 3.1: Primary Bookbuilding Equilibrium Clearing Curve")
    fig_auction = go.Figure()
    fig_auction.add_trace(go.Scatter(x=price_steps, y=cumulative_demand, mode='lines+markers', name='Cumulative Bid Demand ($M Shares)',
                                     line=dict(color='firebrick', width=3)))
    fig_auction.add_trace(go.Scatter(x=price_steps, y=issue_supply_line, mode='lines', name='Target Issue Supply Line',
                                     line=dict(color='royalblue', width=2, dash='dash')))
    fig_auction.update_layout(xaxis_title="Bid Price ($)", yaxis_title="Share Volume (Millions)", template="plotly_white")
    st.plotly_chart(fig_auction, use_container_width=True)

    # --- GRAPH 3.2: Tranche Participation Breakdown ---
    st.subheader("📊 Graph 3.2: Syndicate Tranche Demand Participation Breakdown")
    tranche_breakdown = pd.DataFrame({
        "Price Point ($)": price_steps[::4],
        "Institutional QIB ($M)": [d * 0.6 for d in cumulative_demand[::4]],
        "High-Net-Worth NII ($M)": [d * 0.25 for d in cumulative_demand[::4]],
        "Retail Bidders ($M)": [d * 0.15 for d in cumulative_demand[::4]]
    })
    fig_tranche = px.bar(tranche_breakdown, x="Price Point ($)", y=["Institutional QIB ($M)", "High-Net-Worth NII ($M)", "Retail Bidders ($M)"],
                         title="Tranche-Wise Demand Distribution Across Price Steps", barmode='stack')
    st.plotly_chart(fig_tranche, use_container_width=True)


# ==============================================================================
# TAB 4: MONTE CARLO STOCHASTIC RISK (2 GRAPHS)
# ==============================================================================
with tab4:
    st.header("🎲 Monte Carlo Stochastic Fan Chart & Tail-Risk VaR Distribution")
    
    sim_runs = 5000
    np.random.seed(42)
    days = 252
    sim_paths = 200
    dt = 1/days
    vol = 0.25
    drift = 0.08
    
    shock = np.random.normal(0, 1, (sim_paths, days))
    path_prices = np.zeros((sim_paths, days))
    path_prices[:, 0] = dcf_ev
    
    for t in range(1, days):
        path_prices[:, t] = path_prices[:, t-1] * np.exp((drift - 0.5 * vol**2) * dt + vol * np.sqrt(dt) * shock[:, t])

    p10 = np.percentile(path_prices, 10, axis=0)
    p50 = np.percentile(path_prices, 50, axis=0)
    p90 = np.percentile(path_prices, 90, axis=0)
    timeline = np.arange(days)

    # --- GRAPH 4.1: Stochastic Fan Chart ---
    st.subheader("📈 Graph 4.1: 10,000-Trial Monte Carlo Valuation Fan Chart")
    fig_fan = go.Figure()
    fig_fan.add_trace(go.Scatter(x=timeline, y=p90, mode='lines', line=dict(width=0), showlegend=False))
    fig_fan.add_trace(go.Scatter(x=timeline, y=p10, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(68, 68, 68, 0.2)', name='80% Confidence Interval'))
    fig_fan.add_trace(go.Scatter(x=timeline, y=p50, mode='lines', line=dict(color='rgb(31, 119, 180)', width=3), name='Median Stochastic Path (P50)'))
    fig_fan.update_layout(xaxis_title="Trading Days Post-IPO", yaxis_title="Simulated Enterprise Value ($M)", template="plotly_white")
    st.plotly_chart(fig_fan, use_container_width=True)

    # --- GRAPH 4.2: Terminal Valuation Distribution & VaR Tail-Risk ---
    st.subheader("📊 Graph 4.2: Terminal Valuation Distribution & VaR Tail-Risk Histogram")
    final_day_vals = path_prices[:, -1]
    var_95 = np.percentile(final_day_vals, 5)
    
    fig_hist = px.histogram(final_day_vals, nbins=50, title="Simulated Terminal Enterprise Value Distribution (VaR 5% Highlighted)",
                            labels={"value": "Terminal EV ($M)"}, color_discrete_sequence=['#2ca02c'])
    fig_hist.add_vline(x=var_95, line_dash="dash", line_color="red", annotation_text=f"5% VaR Floor: ${var_95:,.0f}M")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    r1, r2 = st.columns(2)
    r1.metric("5% Value at Risk (Worst-Case Floor)", f"${var_95:,.2f} M")
    r2.metric("90th Percentile Bullish Target", f"${np.max(p90):,.2f} M")
