# Phase 0 & Phase 1 — sCO₂ Property Tools

> **Goal:** Leave a first substantial contribution in the CoolProp project
> **Expected output:** 1–2 merged PRs, or one independent Python package on PyPI
> **Timeline:** Months 1–3 (Phase 0 runs in parallel from week 0)

---

## Phase 0 — Knowledge Preparation (Weeks 0–6, parallel to all phases)

**Do not write any code before filling these knowledge gaps.
Skipping this step produces code that no one in the community will trust.**

### 0.1 Required Reading

| Category | Resource | Goal |
|----------|----------|------|
| Thermodynamics fundamentals | MIT OCW 2.006 or Cengel *Thermodynamics* chapters 1–10 | Read T-s diagrams; understand efficiency definitions |
| sCO₂ cycles | Dostal 2004 MIT PhD thesis (free, Google-findable) | Understand why sCO₂ outperforms steam |
| Critical-point physics | NIST WebBook CO₂ property tables | Develop intuition for the dramatic property changes near the critical point |
| Open-source code reading | CoolProp GitHub + official docs | Understand project structure and contribution workflow |

### 0.2 Environment Setup Checklist

```bash
# Python environment (CoolProp >= 7.1 required for improved near-critical stability)
pip install "CoolProp>=7.1" numpy scipy matplotlib jupyter pandas streamlit

# Verify installation — compute CO₂ density near the critical point
python -c "
import CoolProp.CoolProp as CP
T_crit = CP.PropsSI('Tcrit', 'CO2')   # K
P_crit = CP.PropsSI('Pcrit', 'CO2')   # Pa
rho = CP.PropsSI('D', 'T', T_crit+0.5, 'P', P_crit*1.01, 'CO2')
print(f'Near-critical density: {rho:.2f} kg/m³')
print(f'CoolProp version: {CP.__version__}')
"

# Git configuration
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### 0.3 AI-Assisted Coding Guidance (v1.4)

AI coding tools (GitHub Copilot, Claude, Cursor) are useful in specific, bounded situations.
Use them as an accelerant for mechanical tasks — not as a substitute for domain understanding.

**High-value use cases in this project:**

| Task | Why AI helps | Caution |
|------|-------------|---------|
| Generating OpenFOAM `thermophysicalProperties` dict skeletons | Boilerplate-heavy format with rigid syntax | Always validate physical values against CoolProp |
| Counting equations vs. unknowns in a Modelica model | Tedious but mechanical | Final DAE-index check must be done in OMShell |
| Translating technical docs (Chinese ↔ English) | Time-saving for PR descriptions and comments | Review all thermodynamics terminology carefully |
| Writing `pytest` fixtures and parametrize decorators | Repetitive structure | Do not let AI write the expected physical values |
| First-draft docstrings in English | Helpful for non-native speakers | Verify unit conventions match CoolProp SI defaults |

**What AI cannot reliably do in this domain:**
- Determine whether a CFD mesh is physically appropriate for near-critical sCO₂
- Choose correct turbulence model closure for PCHE zigzag channels
- Assess whether a Modelica `assert` level should be `warning` vs. `error`
- Validate Arrhenius parameters for tritium permeation against literature

**Practical guidance:** Use AI to write the skeleton, then fill in the physics yourself.
If you cannot verify what the AI generated, do not commit it.

---

## Phase 1 — sCO₂ Property Contributions (Months 1–3)

### 1.1 Understanding the Target Problem

sCO₂ near the critical point (31.1 °C ± 5 °C, 7.38 MPa ± 1 MPa) presents three computational challenges:

```
Problem 1: Specific heat Cp diverges at the critical point → numerical instability
Problem 2: Impurity mixtures (CO₂ + He, CO₂ + H₂O) shift the critical point
Problem 3: Insufficient accuracy at high T/P conditions (500 °C, 25 MPa)
```

### 1.2 First Practical Task — Diagnostic Visualization Tool

**Do not start by modifying core library code.**
Build a diagnostic tool first — it helps you genuinely understand the problem
and is itself a valuable community contribution.

```python
# File: sco2_property_explorer.py
# Purpose: visualize sCO₂ property fields including the pseudo-critical line
#          (the pseudo-critical line has more engineering significance than the critical point itself)

import CoolProp.CoolProp as CP
import numpy as np
import matplotlib.pyplot as plt


def find_pseudocritical_temp(P, fluid='CO2', T_search_range=(305, 800)):
    """
    Find the temperature of the local Cp maximum at a given pressure.

    Physical meaning: above the critical pressure (P > 7.38 MPa) CO₂ has no
    phase transition, but Cp still peaks at a specific temperature.
    All such peak points form the "pseudo-critical line".
    Engineering cycles (15–25 MPa) must be designed around this line.
    """
    T_arr = np.linspace(*T_search_range, 500)
    Cp_arr = []
    for T in T_arr:
        try:
            Cp_arr.append(CP.PropsSI('C', 'T', T, 'P', P, fluid))
        except Exception:
            Cp_arr.append(np.nan)
    Cp_arr = np.array(Cp_arr)
    idx = np.nanargmax(Cp_arr)
    return T_arr[idx]


def plot_cp_with_pseudocritical(fluid='CO2', T_range=(300, 400),
                                 P_range=(7e6, 25e6), grid=200):
    """
    Plot a Cp contour map overlaid with the pseudo-critical line.

    Note: T_range extends to 400 K (~127 °C) because at high pressures
    (20+ MPa) the pseudo-critical temperature rises significantly above 31 °C.
    """
    T_arr = np.linspace(*T_range, grid)
    P_arr = np.linspace(*P_range, grid)
    T_grid, P_grid = np.meshgrid(T_arr, P_arr)

    Cp_grid = np.zeros_like(T_grid)
    for i in range(grid):
        for j in range(grid):
            try:
                Cp_grid[i, j] = CP.PropsSI('C', 'T', T_grid[i, j],
                                            'P', P_grid[i, j], fluid)
            except Exception:
                Cp_grid[i, j] = np.nan

    P_line = np.linspace(*P_range, 80)
    T_pc = [find_pseudocritical_temp(P, fluid, (T_range[0], T_range[1]))
            for P in P_line]

    fig, ax = plt.subplots(figsize=(11, 7))
    c = ax.contourf(T_grid - 273.15, P_grid / 1e6, Cp_grid / 1000,
                    levels=50, cmap='inferno')
    plt.colorbar(c, label='Cp (kJ/kg·K)')
    ax.axvline(31.1, color='cyan', linestyle='--', alpha=0.5,
               label='Critical temperature 31.1 °C (only meaningful at 7.38 MPa)')
    ax.axhline(7.38, color='lime', linestyle='--', alpha=0.5,
               label='Critical pressure 7.38 MPa')
    ax.plot(np.array(T_pc) - 273.15, P_line / 1e6,
            color='white', linewidth=2.5, label='Pseudo-critical line (engineering design reference)')

    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Pressure (MPa)')
    ax.set_title(f'{fluid} Specific Heat Cp + Pseudo-Critical Line\n'
                 f'Engineering cycles (15–25 MPa) should track the white line, not the critical point')
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig('sco2_cp_pseudocritical.png', dpi=150)
    return fig
```

### 1.3 Differentiating Contribution — sCO₂ Mixture Properties

This is the core entry point identified in the strategy — and a genuine weak spot in CoolProp.

**Literature search keywords (Google Scholar):**
```
"supercritical CO2 mixture thermophysical properties"
"CO2 helium mixture equation of state"
"impurity effects on sCO2 cycle efficiency"
```

Focus on:
- REFPROP mixture models (NIST; algorithms partly published)
- Span & Wagner (1996) CO₂ equation of state (the basis of CoolProp — read it)

```python
# File: sco2_mixture_validation.py
# Purpose: compare CoolProp mixture results against published experimental data
#
# Key trap: adding an impurity converts the CO₂ "critical point" into a
# "phase envelope" (dew point + bubble point). At certain T/P the mixture
# can enter a two-phase region, causing solver crashes.
# This script includes a phase-state guard that emits a physical warning
# instead of a code exception when the two-phase region is encountered.

import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI, PhaseSI

PHASE_NAMES = {
    'liquid': 'liquid',
    'gas': 'gas',
    'supercritical': 'supercritical',
    'supercritical_liquid': 'supercritical_liquid',
    'supercritical_gas': 'supercritical_gas',
    'twophase': 'TWO-PHASE ⚠',
    'unknown': 'unknown',
}


def check_phase(T, P, fluid='CO2'):
    try:
        return PhaseSI('T', T, 'P', P, fluid)
    except Exception:
        return 'unknown'


def calc_mixture_properties(T, P, x_he, verbose=True):
    """
    Compute CO₂-He mixture properties.
    T: temperature (K), P: pressure (Pa), x_he: He mole fraction
    """
    phase = check_phase(T, P)
    if phase == 'twophase':
        print(f"⚠  Physical warning: T={T-273.15:.1f} °C, P={P/1e6:.2f} MPa is in the two-phase region!")
        print(f"   Impurity-induced phase-envelope shift may cause liquid-gas coexistence here.")
        print(f"   Engineering design must avoid this operating window entirely.")
        return None

    rho_pure = PropsSI('D', 'T', T, 'P', P, 'CO2')
    cp_pure  = PropsSI('C', 'T', T, 'P', P, 'CO2')

    try:
        mixture = f'HEOS::CO2[{1-x_he:.4f}]&Helium[{x_he:.4f}]'
        rho_mix = PropsSI('D', 'T', T, 'P', P, mixture)
        cp_mix  = PropsSI('C', 'T', T, 'P', P, mixture)

        if verbose:
            print(f"T={T-273.15:.1f} °C | P={P/1e6:.2f} MPa | x_He={x_he*100:.2f}% | Phase: {PHASE_NAMES.get(phase, phase)}")
            print(f"  Density: pure CO₂={rho_pure:.2f} → mixture={rho_mix:.2f} kg/m³  (Δ={100*(rho_mix-rho_pure)/rho_pure:+.2f}%)")
            print(f"  Cp:      pure CO₂={cp_pure:.0f} → mixture={cp_mix:.0f} J/kg·K  (Δ={100*(cp_mix-cp_pure)/cp_pure:+.2f}%)")

        return {'rho_pure': rho_pure, 'rho_mix': rho_mix,
                'cp_pure': cp_pure, 'cp_mix': cp_mix, 'phase': phase}

    except Exception as e:
        print(f"⚠  Mixture calculation failed (log this as an Issue!): {e}")
        return None
```

### 1.4 How to Submit Contributions to CoolProp

```bash
# 1. Fork the project on GitHub: https://github.com/CoolProp/CoolProp → Fork

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/CoolProp.git
cd CoolProp

# 3. Create a feature branch
git checkout -b feature/sco2-mixture-validation-tools

# 4. Add your tests under wrappers/Python/CoolProp/tests/
#    Add example notebooks under doc/

# 5. Pre-submission check
python -m pytest wrappers/Python/CoolProp/tests/ -v

# 6. Push and open a PR
git push origin feature/sco2-mixture-validation-tools
```

**PR description template (write in English — CoolProp is an international project):**

> CoolProp's core maintainers (e.g., Ian Bell) are extremely busy researchers.
> A clear PR description dramatically speeds up the merge and is the first step
> in building a professional profile. PRs written in other languages are likely to be overlooked.

```markdown
**Title:** [Feature/Tools] Add diagnostic visualization and mixture validation
           scripts for sCO2 near critical point

**Description:**
This PR introduces two utility scripts for engineers and researchers working
on sCO2 power cycles (e.g., advanced nuclear reactors, CSP).

**Motivation:**
1. Calculating thermophysical properties of sCO2 near the critical point
   (31.1 °C, 7.38 MPa) often causes numerical instability due to diverging Cp.
2. The effect of impurities (e.g., He or H2O) on the shift of the
   pseudo-critical line is a critical but often overlooked issue in cycle design.

**Changes Proposed:**
- `sco2_property_explorer.py`: Cp contour plots to identify high-gradient regions;
  includes pseudo-critical line fitting.
- `sco2_mixture_validation.py`: Baseline script comparing pure CO₂ vs. mixtures;
  includes phase-state checking to handle two-phase warnings.

**Checklist:**
- [x] Code is properly commented
- [x] Plots use non-interactive backend (safe for CI/CD)
- [x] Phase-state guard prevents crash in two-phase region
- [ ] Needs review from thermodynamic modeling experts on mixture limits
```

### 1.5 Workflow — Issue-Driven Development

**Never write a month of code and then open a PR.**
Core scientific computing libraries are tightly coupled; code written without
maintainer buy-in may be rejected for architectural reasons with no fault on either side.

Correct workflow:
```
1. Open an Issue first (Feature Request / Discussion)
   Example title:
   "Discussion: Best practices for simulating sCO2 + Helium mixtures
    near critical point for nuclear power applications"

   Include:
   - Your engineering context (nuclear sCO₂ cycle)
   - The specific problem (mixture accuracy near the critical point)
   - What tool you plan to write (validation script, visualization)
   - Ask the maintainers: "Does this direction seem valuable? Known pitfalls?"

2. Wait for a response (typically 3–14 days)
   Likely outcomes:
   ✅ Maintainer replies with key references or points to existing code → saves you significant time
   ✅ Other users express the same need → your PR priority rises automatically
   ⚠  No reply → proceed as planned; no cost

3. Write the code; reference the Issue number in the PR
   Include "Closes #XXX" in the PR description
```

### 1.6 Obtaining Free Experimental Benchmark Data

sCO₂ corrosion data is hard to find. **Thermodynamic cycle and compressor test data is publicly available.**

**Sandia National Laboratories (SNL)**
- SNL built and operated the world's first sCO₂ test loop (~10 MWe class)
- Test reports available free on OSTI: `https://www.osti.gov`
- Search: `supercritical CO2 test loop Sandia`
- Key series: Wright et al. (2010–2016) — compressor inlet T/P, efficiency measurements

**STEP Demonstration Project (v1.4 update)**
- DOE-funded 10 MWe sCO₂ demonstration project
- **Phase 1 (simple cycle, ~500 °C):** operating data publicly released — use as an additional validation source alongside Sandia
- **Phase 2 (RCBC, ~715 °C):** in progress as of 2025; data expected upon completion
- Search: `STEP sCO2 demonstration project DOE Southwest Research Institute`
- Do not cite "715 °C RCBC operating data" as publicly available — it is not yet

**Adding STEP Phase 1 to CI:**

```python
# File: validation/experimental_data/STEP_phase1_data.csv
# Columns: T_inlet_K, P_inlet_Pa, T_outlet_K, P_outlet_Pa, efficiency_measured
# Source: [cite specific STEP public report + DOI]

# tests/test_sco2_properties.py — extend the benchmark set:
STEP_PHASE1_POINTS = [
    # (T_K, P_Pa, expected_density_kg_m3, tolerance_pct)
    # Fill from STEP Phase 1 public report — verify values before committing
]

@pytest.mark.parametrize("T, P, rho_expected, tol_pct", STEP_PHASE1_POINTS)
def test_density_against_step_phase1(T, P, rho_expected, tol_pct):
    """Density vs. STEP Phase 1 public data (simple cycle, ~500 °C)."""
    rho_calc = CP.PropsSI('D', 'T', T, 'P', P, 'CO2')
    rel_err = abs(rho_calc - rho_expected) / rho_expected * 100
    assert rel_err < tol_pct
```

**Practical approach:**

```python
# Manually transcribe public SNL/STEP report data to CSV
# File: validation/experimental_data/SNL_compressor_data.csv
# Columns: T_inlet_K, P_inlet_Pa, T_outlet_K, P_outlet_Pa, efficiency_measured

import pandas as pd
import CoolProp.CoolProp as CP

df = pd.read_csv('SNL_compressor_data.csv')
df['rho_inlet_coolprop'] = df.apply(
    lambda r: CP.PropsSI('D', 'T', r.T_inlet_K, 'P', r.P_inlet_Pa, 'CO2'), axis=1)
df['rho_error_pct'] = (df['rho_inlet_coolprop'] - df['rho_inlet_measured']) \
                       / df['rho_inlet_measured'] * 100
print(df[['T_inlet_K', 'P_inlet_Pa', 'rho_error_pct']].to_string())
# This error report is a standalone engineering evaluation worth publishing as a technical note
```

### 1.7 Phase Bridge — LUT Export (Phase 1 → Phase 2)

Phase 2 OpenFOAM needs property data for every mesh cell at every time step.
Calling CoolProp in real time would increase runtime by 10–100×.
Pre-generating a Look-Up Table (LUT) is the standard engineering solution
and the natural bridge between phases.

```python
# File: tools/export_lut.py

import CoolProp.CoolProp as CP
import numpy as np
import pandas as pd


def export_sco2_lut(T_min=300, T_max=900, P_min=7.5e6, P_max=25e6,
                    n_T=200, n_P=100, output_prefix='sco2_lut'):
    """
    Generate a sCO₂ property look-up table.

    Coverage:
    - T: 300–900 K (27–627 °C) — compressor inlet through turbine outlet
    - P: 7.5–25 MPa — low-pressure side through high-pressure side
    - 200×100 = 20 000 points balances accuracy and file size
    """
    T_arr = np.linspace(T_min, T_max, n_T)
    P_arr = np.linspace(P_min, P_max, n_P)

    rows = []
    skipped = 0
    for T in T_arr:
        for P in P_arr:
            try:
                rows.append({
                    'T':   T,
                    'P':   P,
                    'rho': CP.PropsSI('D', 'T', T, 'P', P, 'CO2'),
                    'Cp':  CP.PropsSI('C', 'T', T, 'P', P, 'CO2'),
                    'mu':  CP.PropsSI('V', 'T', T, 'P', P, 'CO2'),
                    'k':   CP.PropsSI('L', 'T', T, 'P', P, 'CO2'),
                    'h':   CP.PropsSI('H', 'T', T, 'P', P, 'CO2'),
                })
            except Exception:
                skipped += 1

    df = pd.DataFrame(rows)
    df.to_csv(f'{output_prefix}.csv', index=False)

    with open(f'{output_prefix}_openfoam.dat', 'w') as f:
        f.write("// sCO2 property table generated by sco2-tmsr-toolkit\n")
        f.write("// Columns: T[K] p[Pa] rho[kg/m3] Cp[J/kgK] mu[Pa.s] k[W/mK]\n")
        for _, r in df.iterrows():
            f.write(f"{r.T:.2f} {r.P:.0f} {r.rho:.4f} {r.Cp:.2f} {r.mu:.6e} {r.k:.6f}\n")

    print(f"LUT complete: {len(rows)} valid points, {skipped} skipped")
    return df
```

### 1.8 Impact Multiplier — Streamlit Web Application

**Principle:** an interactive web page has roughly 10× the reach of a Python script.
A local `.png` requires the viewer to install Python → install CoolProp → run the script → see one figure.
A web app: click the link, use it immediately. **Trial barrier drops from 30 minutes to 30 seconds.**

```python
# File: app/streamlit_app.py
# Launch: streamlit run app/streamlit_app.py

import streamlit as st
from sco2_property_explorer import plot_cp_with_pseudocritical, find_pseudocritical_temp
from sco2_mixture_validation import calc_mixture_properties

st.set_page_config(page_title="sCO₂ Property Diagnostics", page_icon="🔬", layout="wide")
st.title("sCO₂ Pseudo-Critical Line & Mixture Property Diagnostics")
st.markdown("For advanced nuclear reactor power cycle design (TMSR / HTGR)")

tab1, tab2 = st.tabs(["Pseudo-Critical Line", "Impurity Mixture Analysis"])

with tab1:
    col1, col2 = st.columns([1, 3])
    with col1:
        T_max_C   = st.slider("Temperature upper limit (°C)", 50, 700, 400)
        P_min_MPa = st.slider("Pressure lower limit (MPa)", 7.4, 15.0, 7.5, step=0.1)
        P_max_MPa = st.slider("Pressure upper limit (MPa)", 15.0, 30.0, 25.0, step=0.5)
        grid      = st.select_slider("Grid density", [50, 100, 200, 300], value=100)
    with col2:
        with st.spinner("Computing property field..."):
            fig = plot_cp_with_pseudocritical(
                T_range=(300, T_max_C + 273.15),
                P_range=(P_min_MPa * 1e6, P_max_MPa * 1e6),
                grid=grid)
            st.pyplot(fig)

with tab2:
    T_C      = st.number_input("Temperature (°C)", value=35.0)
    P_MPa    = st.number_input("Pressure (MPa)", value=8.0)
    x_he_pct = st.slider("Helium impurity mole fraction (%)", 0.0, 5.0, 1.0, step=0.1)

    if st.button("Calculate"):
        result = calc_mixture_properties(T=T_C+273.15, P=P_MPa*1e6,
                                         x_he=x_he_pct/100, verbose=False)
        if result is None:
            st.error("⚠ Operating point is in the two-phase region or solver failed — adjust T/P")
        else:
            c1, c2 = st.columns(2)
            c1.metric("Pure CO₂ density (kg/m³)", f"{result['rho_pure']:.2f}")
            c2.metric("Mixture density (kg/m³)",  f"{result['rho_mix']:.2f}",
                      delta=f"{100*(result['rho_mix']-result['rho_pure'])/result['rho_pure']:+.2f}%")
            c1.metric("Pure CO₂ Cp (J/kg·K)", f"{result['cp_pure']:.0f}")
            c2.metric("Mixture Cp (J/kg·K)",  f"{result['cp_mix']:.0f}",
                      delta=f"{100*(result['cp_mix']-result['cp_pure'])/result['cp_pure']:+.2f}%")

st.markdown("---")
st.caption("Powered by CoolProp · Open Source · MIT License")
```

```bash
# Deploy to Streamlit Community Cloud (free)
# 1. Push repo to GitHub
# 2. Log in at https://share.streamlit.io
# 3. Connect repo → get a public URL (e.g., sco2-tools.streamlit.app)
# 4. Add the link to the top of your GitHub README
```

### CI/CD — GitHub Actions for Phase 1

```yaml
# File: .github/workflows/python-tests.yml

name: Python Tests & Benchmark

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install "CoolProp>=7.1" numpy scipy matplotlib pandas pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/ -v --cov=sco2_tools --cov-report=xml

      - name: Run SNL benchmark validation
        run: |
          python tools/validate_against_sandia.py \
            --tolerance 5.0 \
            --data validation/experimental_data/SNL_compressor_data.csv

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

```python
# File: tests/test_sco2_properties.py

import pytest
import CoolProp.CoolProp as CP

# Public data points from Sandia Wright et al. 2010 reports (illustrative)
SANDIA_BENCHMARK_POINTS = [
    # (T_K, P_Pa, expected_density_kg_m3, tolerance_pct)
    (305.4, 7.69e6, 632.0, 5.0),
    (351.2, 20.0e6, 745.5, 5.0),
    (773.15, 20.0e6, 142.3, 3.0),
]

@pytest.mark.parametrize("T, P, rho_expected, tol_pct", SANDIA_BENCHMARK_POINTS)
def test_density_against_sandia(T, P, rho_expected, tol_pct):
    rho_calc = CP.PropsSI('D', 'T', T, 'P', P, 'CO2')
    rel_err = abs(rho_calc - rho_expected) / rho_expected * 100
    assert rel_err < tol_pct, (
        f"Density deviation {rel_err:.2f}% exceeds tolerance {tol_pct}% "
        f"(T={T-273.15:.1f} °C, P={P/1e6:.1f} MPa, "
        f"calculated={rho_calc:.1f}, reference={rho_expected:.1f})")

def test_pseudocritical_line_monotonic():
    """Pseudo-critical temperature must increase monotonically with pressure."""
    from sco2_property_explorer import find_pseudocritical_temp
    T_pc_8  = find_pseudocritical_temp(8.0e6)
    T_pc_20 = find_pseudocritical_temp(20.0e6)
    assert T_pc_20 > T_pc_8, "Pseudo-critical temperature must rise with pressure"
```

### README Badges

```markdown
# sCO₂-TMSR-Toolkit

[![Tests](https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit/actions/workflows/python-tests.yml/badge.svg)](https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit/actions/workflows/python-tests.yml)
[![Coverage](https://codecov.io/gh/OpenLithoHub/sCO2-TMSR-Toolkit/branch/main/graph/badge.svg)](https://codecov.io/gh/OpenLithoHub/sCO2-TMSR-Toolkit)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sco2-tmsr-toolkit.streamlit.app)
[![Jupyter Book](https://jupyterbook.org/badge.svg)](https://OpenLithoHub.github.io/sCO2-TMSR-Toolkit)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxxxx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

### Minimum Viable Starting Point

> **v1.4 reminder:** After reading all the above, you may want to immediately
> set up Jupyter Book or start training a ROM. **Do not.**
> All v1.4 increments depend on a solid v1.3 mainline. Do these four things first:

```bash
# Step 1 (30 min): install and run the visualization
pip install "CoolProp>=7.1" numpy matplotlib
python3 -c "
import CoolProp.CoolProp as CP
import numpy as np, matplotlib.pyplot as plt

T = np.linspace(300, 320, 500)
P = 8e6
Cp = [CP.PropsSI('C','T',t,'P',P,'CO2') for t in T]
plt.plot(T-273.15, np.array(Cp)/1000)
plt.xlabel('Temperature (°C)'); plt.ylabel('Cp (kJ/kg·K)')
plt.title('sCO₂ near-critical Cp spike (P=8 MPa)')
plt.axvline(31.1, color='r', linestyle='--', label='Critical temperature')
plt.legend(); plt.grid(); plt.show()
"

# Step 2 (2 h): read the CoolProp Issues list
# Open: https://github.com/CoolProp/CoolProp/issues
# Search: "CO2" or "supercritical" — find what people are struggling with

# Step 3 (1 day): create a GitHub repo and make the first commit
# Repo name: sco2-tmsr-toolkit  (or fork from this repo)

# Step 4 (half day): configure CI + Streamlit skeleton
# - Add the simplest GitHub Actions workflow (even just `python -c "import CoolProp"`)
#   so the README shows a green passing badge from day one
# - Write a 20-line Streamlit placeholder app and deploy to Streamlit Cloud
#   so your next forum post or email can include a real, clickable URL
```

---

*← Back to [README.md](OVERVIEW.md) | Next: [Phase 2 — CFD & ROM →](02_phase2_cfd_rom.md)*
