"""
Streamlit web app — sCO2 property diagnostics.

Reference: docs/01_phase1_properties.md § 1.8

Launch locally:
    streamlit run app/streamlit_app.py

Deploy: push to GitHub, connect at https://share.streamlit.io
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Make src/ importable when running `streamlit run app/streamlit_app.py` from repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from sco2_mixture_validation import calc_mixture_properties  # noqa: E402
from sco2_property_explorer import plot_cp_with_pseudocritical  # noqa: E402

st.set_page_config(
    page_title="sCO₂ Property Diagnostics", page_icon="🔬", layout="wide"
)
st.title("sCO₂ Pseudo-Critical Line & Mixture Property Diagnostics")
st.markdown("For advanced nuclear reactor power cycle design (TMSR / HTGR)")

tab1, tab2 = st.tabs(["Pseudo-Critical Line", "Impurity Mixture Analysis"])

with tab1:
    col1, col2 = st.columns([1, 3])
    with col1:
        T_max_C = st.slider("Temperature upper limit (°C)", 50, 700, 400)
        P_min_MPa = st.slider("Pressure lower limit (MPa)", 7.4, 15.0, 7.5, step=0.1)
        P_max_MPa = st.slider("Pressure upper limit (MPa)", 15.0, 30.0, 25.0, step=0.5)
        grid = st.select_slider("Grid density", [50, 100, 200, 300], value=100)
    with col2:
        with st.spinner("Computing property field..."):
            fig = plot_cp_with_pseudocritical(
                T_range=(300.0, T_max_C + 273.15),
                P_range=(P_min_MPa * 1e6, P_max_MPa * 1e6),
                grid=grid,
                output_path=None,
            )
            st.pyplot(fig)

with tab2:
    T_C = st.number_input("Temperature (°C)", value=35.0)
    P_MPa = st.number_input("Pressure (MPa)", value=8.0)
    x_he_pct = st.slider(
        "Helium impurity mole fraction (%)", 0.0, 5.0, 1.0, step=0.1
    )

    if st.button("Calculate"):
        result = calc_mixture_properties(
            T=T_C + 273.15, P=P_MPa * 1e6, x_he=x_he_pct / 100.0, verbose=False
        )
        if result is None:
            st.error(
                "⚠ Operating point is in the two-phase region or solver "
                "failed — adjust T/P"
            )
        else:
            c1, c2 = st.columns(2)
            c1.metric("Pure CO₂ density (kg/m³)", f"{result.rho_pure:.2f}")
            c2.metric(
                "Mixture density (kg/m³)",
                f"{result.rho_mix:.2f}",
                delta=f"{result.rho_delta_pct:+.2f}%",
            )
            c1.metric("Pure CO₂ Cp (J/kg·K)", f"{result.cp_pure:.0f}")
            c2.metric(
                "Mixture Cp (J/kg·K)",
                f"{result.cp_mix:.0f}",
                delta=f"{result.cp_delta_pct:+.2f}%",
            )
            st.caption(f"Phase: {result.phase}")

st.markdown("---")
st.caption("Powered by CoolProp · Open Source · Apache-2.0 (code) / CC BY-SA 4.0 (docs)")
