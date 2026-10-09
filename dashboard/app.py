"""Accessible Streamlit what-if dashboard for the supply-chain POC.

Accessibility notes:
- Every input has an explicit, visible label (never placeholder-only).
- Results are exposed as tables and captions, not color-only cues.
- Status symbols are always paired with text (✓/⚠ plus words).
- A skip link jumps past the sidebar to the main content.
- Contrast-friendly color usage; no meaning conveyed by color alone.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.experiments import evaluate_scenario  # noqa: E402

st.set_page_config(page_title="Supply Chain Multi-Agent POC", layout="wide")

st.markdown(
    """
    <style>
    .skip-link { position:absolute; left:-9999px; }
    .skip-link:focus { left:8px; top:8px; background:#000; color:#fff; padding:8px; z-index:9999;}
    :focus-visible { outline: 3px solid #1a5fb4 !important; outline-offset: 2px; }
    button[data-testid="stDeployButton"], [data-testid="stDeployButton"], .stAppDeployButton { display: none !important; }
    </style>
    <a class="skip-link" href="#main">Skip to main content</a>
    """,
    unsafe_allow_html=True,
)

st.title("Supply-Chain Response — What-if Planner")
st.caption(
    "Compare reorder rules, MILP optimization, and the multi-agent "
    "coordinator under a supplier disruption."
)

# ---- Sidebar: scenario controls ----
with st.sidebar:
    st.header("Scenario controls")
    supplier = st.selectbox("Disrupted supplier", ["S1", "S2"], help="Supplier that goes offline.")
    duration = st.slider("Disruption duration (days)", 1, 14, 7)
    start_day = st.slider("Disruption start day", 1, 20, 10)
    demand_increase = st.slider("Demand increase (%)", 0, 50, 0)
    transport_increase = st.slider("Transport cost increase (%)", 0, 50, 0)
    service_target = st.slider("Service target (%)", 80, 99, 95)
    run_button = st.button("Run scenario", type="primary", use_container_width=True)

st.markdown('<span id="main"></span>', unsafe_allow_html=True)
st.header("Results")

if run_button:
    scenario = {
        "name": f"{supplier}-{duration}D-D{int(demand_increase)}-T{int(transport_increase)}",
        "disruption": {"supplier": supplier, "start": start_day, "duration": duration},
        "demand_mult": 1 + demand_increase / 100,
        "transport_mult": 1 + transport_increase / 100,
    }
    demand = pd.read_csv(DATA / "demand.csv")
    suppliers = pd.read_csv(DATA / "suppliers.csv")
    warehouses = pd.read_csv(DATA / "warehouses.csv")
    customers = pd.read_csv(DATA / "customers.csv")
    inventory = pd.read_csv(DATA / "inventory.csv")
    scenarios_df = pd.read_csv(DATA / "scenarios.csv")
    constraints = pd.read_csv(DATA / "constraints.csv")
    transport = pd.read_csv(DATA / "transport.csv")

    with st.spinner("Running coordinator and optimization models…"):
        rows, accepted, rejected = evaluate_scenario(
            scenario, demand, suppliers, warehouses, customers, inventory,
            scenarios_df, constraints, transport,
        )
    st.session_state["rows"] = rows
    st.session_state["accepted"] = accepted
    st.session_state["rejected"] = rejected

if "rows" in st.session_state:
    rows = st.session_state["rows"]
    accepted = st.session_state["accepted"]
    rejected = st.session_state["rejected"]

    df = pd.DataFrame(rows)

    st.subheader("Approach comparison")
    st.dataframe(df, use_container_width=True, hide_index=True)

    import plotly.express as px

    st.subheader("Trade-off visuals")
    chart_df = df.melt(id_vars=["approach"], value_vars=["cost", "backorders"],
                       var_name="metric", value_name="value")
    st.plotly_chart(px.bar(chart_df, x="approach", y="value", color="metric",
                           barmode="group", title="Cost vs backorders by approach"),
                    use_container_width=True)

    st.subheader("Recommendations accepted by the coordinator")
    if accepted:
        for rec in accepted:
            p = rec.recommendation
            qty = f"{p.quantity:.0f} units" if p.quantity is not None else "n/a"
            if p.source and p.destination:
                route = f"{p.source} → {p.destination}"
            elif p.destination:
                route = str(p.destination)
            else:
                route = "—"
            st.markdown(
                f"- **{p.action.replace('_', ' ').title()}** — {route}, "
                f"{qty}. *Why:* {rec.reason} "
                f"(confidence {rec.confidence:.0%}, expected cost {rec.expected_cost:,.0f})"
            )
            if rec.constraints_checked:
                st.caption("Constraints checked: " + ", ".join(rec.constraints_checked))
    else:
        st.write("No recommendations were needed for this scenario.")

    if rejected:
        st.subheader("Recommendations rejected")
        for r in rejected:
            st.write(f"- {r['agent']}: {r['reason']}")

    st.subheader("Trade-off summary")
    pivot = df.set_index("approach")[["cost", "backorders", "runtime_s"]]
    st.dataframe(pivot.style.format({"cost": "₹{:,.0f}", "backorders": "{:,.0f}", "runtime_s": "{:.3f}s"}), use_container_width=True)

    st.subheader("Human approval gate")
    st.info(
        "The coordinator's plan is **proposed, not executed**. A planner must "
        "explicitly approve it before any transaction would run."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Approve plan"):
            st.success("Plan approved. (Simulation only — no transactions executed.)")
    with col2:
        if st.button("Request modification"):
            st.warning("Modification requested — adjust scenario controls and re-run.")
    with col3:
        if st.button("Reject plan"):
            st.error("Plan rejected. (Simulation only — no transactions executed.)")
else:
    st.info("Set scenario controls in the sidebar and choose **Run scenario**.")
