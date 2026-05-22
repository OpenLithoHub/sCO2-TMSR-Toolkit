# Phase 3 — OpenModelica Component Library

> **Goal:** Build a modular simulation library reusable by researchers worldwide
> **Project name:** `AdvancedReactor-sCO2-Library` (English name, international audience)
> **Timeline:** Months 8–18

---

## 3.1 Modelica Language Primer

Modelica is an equation-based language, not a procedural one.
The mental model shift is significant — take it seriously.

```modelica
// Example: simplest sCO₂ throttle valve component
// File: Components/Valves/ThrottleValve.mo

model ThrottleValve
  "Simple throttle valve — sCO₂ power cycle"

  Modelica.Fluid.Interfaces.FluidPort_a port_a(
    redeclare package Medium = Media.sCO2)    "Inlet";
  Modelica.Fluid.Interfaces.FluidPort_b port_b(
    redeclare package Medium = Media.sCO2)    "Outlet";

  parameter Real Cv = 10.0               "Flow coefficient";
  parameter Real opening(min=0, max=1) = 1.0  "Opening fraction 0–1";

  Real dp    "Pressure drop (Pa)";
  Real mdot  "Mass flow rate (kg/s)";

equation
  dp   = port_a.p - port_b.p;
  mdot = Cv * opening * sqrt(abs(dp)) * sign(dp);

  // Throttling is an isenthalpic process
  port_a.h_outflow = inStream(port_b.h_outflow);
  port_b.h_outflow = inStream(port_a.h_outflow);

  port_a.m_flow + port_b.m_flow = 0;
  port_a.m_flow = mdot;

  annotation(Documentation(info="<html>
    <p>Simple throttle valve, applicable to sCO₂ power cycle system simulation.</p>
    <p>The isenthalpic assumption is acceptable when dp/p &lt; 0.1.</p>
  </html>"));
end ThrottleValve;
```

## 3.2 Library Architecture

```
AdvancedReactor-sCO2-Library/
├── package.mo
├── Media/
│   └── sCO2.mo                          # sCO₂ medium model (calls property table)
├── Components/
│   ├── HeatExchangers/
│   │   ├── PCHE.mo                      # printed-circuit HX (ASME check § 3.6; ROM option § 2.6.5)
│   │   ├── IntermediateHeatExchanger.mo # salt side + CO₂ side
│   │   └── TritiumPermeationLayer.mo    # tritium permeation extension (§ 3.5, optional)
│   ├── Turbomachinery/
│   │   ├── Compressor.mo                  # scalar isentropic-efficiency defaults + BYOD CSV interface (η=0.85, ṁ=100, PR=2.5; not source-anchored — see § 3.2.1)
│   │   ├── ReCompressor.mo                # recompression cycle (extends Compressor with η=0.83)
│   │   ├── Turbine.mo                     # scalar isentropic-efficiency default + symmetric BYOD CSV interface (η=0.90)
│   │   └── LabyrinthSeal.mo               # Egli labyrinth-seal model — defaults from Wright2010 §5.5 (see data_extracts/wright2010_sand2010-0171.md)
│   ├── Reactor/
│   │   ├── MoltenSaltReactor.mo         # simplified MSR thermal-hydraulic model
│   │   ├── ReactorPowerControl.mo
│   │   └── OnlineFuellingTransient.mo   # online-refueling transient module (§ 3.7, optional)
│   └── Valves/
│       ├── ThrottleValve.mo
│       └── BypassValve.mo
├── Cycles/
│   ├── SimpleRecuperation.mo
│   ├── RecompressionCycle.mo
│   └── TMSR_sCO2_Full.mo
├── ExternalROM/
│   └── PCHE_ROM_FMU.fmu                 # Phase 2 ROM output dropped here
├── Examples/
│   ├── DesignPointAnalysis.mo
│   ├── LoadFollowing.mo
│   └── StartupSequence.mo
├── Tests/
│   └── ValidationTests.mo
└── docs/
    ├── UserGuide.md
    └── ComponentReference.md
```

### 3.2.1 Turbomachinery Component — Primary References

The Turbomachinery components inherit defaults from the Sandia 10 MWe / 1 kg·s⁻¹
sCO₂ test loop reports already on local disk (per
[`docs/data_extracts/_acquisition_log.md`](data_extracts/_acquisition_log.md)).
Treat each as a **default seed**, not a hard constraint — industrial users override
via the BYOD interface (§ 0 / strategy doc, Black Hole 1).

| Component | Default-source reference | Locator | Use |
|---|---|---|---|
| `Compressor.mo` (current scalar defaults) | engineering-typical values, not source-anchored | n/a | `eta_isen_design = 0.85`, `mdot_design = 100 kg/s`, `PR_design = 2.5` — placeholder until Table 5.1 wheel geometry is consumed (future deliverable) |
| `Compressor.mo` (planned geometry upgrade) | `Wright2010_SAND2010_0171` Table 5.1 | `docs/data_extracts/wright2010_sand2010-0171.md` "Table 5.1 main-compressor wheel" | Tip diameter, blade angles, exducer width, design speed/flow as wheel-geometry defaults — **not yet in `Compressor.mo`**, planned upgrade path |
| `Compressor.mo` (windage loss, planned) | `Vrancik1968_NASA_TN_D4849` Eq. 5–6 (primary, single-pass extracted 2026-05-22) | `docs/data_extracts/vrancik1968_nasa-tn-d4849.md` | `P_windage = π·C_d(Re)·ρ·r⁴·ω³·L_r` — direct formula. **Confidence A.** 7 % maximum experimental error per Vrancik 1968 § "Experimental verification", p.6. **Not yet implemented in `Compressor.mo`**; reference equation reserved for future deliverable. |
| `Turbine.mo` (current scalar defaults) | engineering-typical value | n/a | `eta_isen_design = 0.90` — symmetric BYOD interface (`useExternalMap` / `mapFileName`) added 2026-05-22 to mirror `Compressor.mo`, even though the off-design table lookup is a future deliverable |
| `LabyrinthSeal.mo` | `Wright2010_SAND2010_0171` §5.5 + Table 5.3 | `docs/data_extracts/wright2010_sand2010-0171.md` "§5.5 Egli labyrinth seal" | Egli leakage correlation as the seal default; teeth count and clearance as Table 5.3 reference |
| `Compressor.mo` condensing-mode comparison | `Wright2011_SAND2010_8840` (first-pass extracted) | `docs/data_extracts/wright2011_sand2010-8840.md` | LWR-temperature condensing-cycle Table 2-1 (14 modelled state points) + Table 4-1 measured rows — once transcribed, populates condensing-mode rows in `SNL_compressor_data.csv` |
| `IntermediateHeatExchanger.mo` chiller side (future `case04_chiller`) | `Wright2010_SAND2010_0171` Table 3.2 | same wright2010 extract doc | Tube OD 38.1 mm / wall 2.4 mm / coil 19.15 m — geometry seed for engineering-scale chiller benchmark |

> Cross-references to strategy doc: BYOD interface for compressor maps — `00_strategy.md` Black Hole 1; PCHE pipeline ingesting confidential geometry — Black Hole 2.

## 3.3 Core Component — PCHE Heat Exchanger

```modelica
model PCHE
  "Printed-circuit heat exchanger — NTU-effectiveness method
   + optional ROM / correlation switch + ASME simplified check"

  replaceable package Medium_hot  = Media.MoltenSalt  "Hot-side medium (molten salt)";
  replaceable package Medium_cold = Media.sCO2         "Cold-side medium (sCO₂)";

  parameter Integer N_channels = 1000;
  parameter Modelica.Units.SI.Length D_ch   = 0.002   "Channel equivalent diameter (m)";
  parameter Modelica.Units.SI.Length L      = 0.6     "Heat exchanger length (m)";
  parameter Modelica.Units.SI.Length d_wall = 0.0015  "Wall (separator) thickness (m)";
  parameter Real zeta = 1.0  "Pressure-drop correction factor (zigzag geometry)";
  parameter Boolean useROM = false
    "true: use ROM-FMU (§ 2.6.4); false: use Gnielinski correlation";

  Modelica.Fluid.Interfaces.FluidPort_a hotInlet;
  Modelica.Fluid.Interfaces.FluidPort_b hotOutlet;
  Modelica.Fluid.Interfaces.FluidPort_a coldInlet;
  Modelica.Fluid.Interfaces.FluidPort_b coldOutlet;

  Real UA   "Overall heat conductance (W/K)";
  Real NTU  "Number of transfer units";
  Real eps  "Heat exchanger effectiveness 0–1";
  Real Q    "Heat duty (W)";

equation
  // NTU-effectiveness method (counter-flow)
  NTU = UA / min(Cp_hot * mdot_hot, Cp_cold * mdot_cold);
  eps = (1 - exp(-NTU * (1 - Cr))) / (1 - Cr * exp(-NTU * (1 - Cr)));
  Q   = eps * min(Cp_hot * mdot_hot, Cp_cold * mdot_cold) * (T_hot_in - T_cold_in);

  if useROM then
    // Nu_avg and dp_tot supplied by PCHE_ROM_FMU (see ExternalROM/)
    // h_conv = Nu_avg * k_fluid / D_ch;
  else
    // Gnielinski correlation (valid for Re > 3 000, smooth circular channel)
    // h_conv = ...;
  end if;

end PCHE;
```

## 3.4 FMU Export — the "Ecosystem Bridge" Step

```bash
# Export FMU from OpenModelica (FMI 2.0 — default, well-supported)
# In OMShell:
loadFile("AdvancedReactor-sCO2-Library/package.mo");
buildModelFMU(AdvancedReactor.Cycles.RecompressionCycle,
              version="2.0",
              fmuType="me");
# Output: RecompressionCycle.fmu

# Validate (Python)
pip install fmpy
python3 -c "
from fmpy import simulate_fmu
result = simulate_fmu('RecompressionCycle.fmu',
                      start_time=0, stop_time=3600,
                      start_values={'turbine.inlet.T': 823.15})
print('Simulation complete. Final efficiency:', result['efficiency'][-1])
"
```

**FMI 3.0 upgrade path (v1.4 note):**
FMI 3.0 (standard released 2023, current: 3.0.1) adds clocked variables and binary data types.
- `fmpy` supports FMI 3.0 for simulation and validation
- `pythonfmu3` (separate package from `pythonfmu`) builds FMI 3.0 FMUs from Python
- **OpenModelica's FMI 3.0 *export* is still incomplete as of 2025** — do not switch if your workflow uses OMShell to build FMUs
- **Dymola** has full FMI 3.0 export support

**Recommendation:** use FMI 2.0 as the default throughout Phase 3.
Note FMI 3.0 as an upgrade path in the documentation for Dymola users.

## 3.5 Optional Extension — Tritium Permeation & Mass Transport

> **Difficulty warning:** high. Do not attempt this before completing §§ 3.1–3.4.
> If completed with capacity to spare, this module can elevate the library
> from "excellent" to "repeatedly cited in MSR/HTGR literature".

### 3.5.1 Why This Is a Real Pain Point

MSR and HTGR engineers have long struggled with:
```
Fuel salt / hot gas → (produces tritium ³H) → diffuses through PCHE metal wall
→ enters sCO₂ side → travels through turbine, cooler, compressor
→ may reach the atmosphere (regulatory challenge)
```

Tritium's small size and high diffusivity allow it to penetrate Inconel 617, Haynes 230,
and other typical PCHE alloys easily at 500–700 °C.
**No publicly available, Modelica-callable tritium permeation component exists anywhere.**

### 3.5.2 Physical Model

Steady-state permeation flux through a metal wall:

$$J = \frac{\Phi(T)}{d} \left( \sqrt{p_{H,\text{hot}}} - \sqrt{p_{H,\text{cold}}} \right)$$

- **J**: tritium permeation flux (mol·m⁻²·s⁻¹)
- **Φ(T)**: permeability (Arrhenius form): `Φ = Φ₀ · exp(−Eₐ / RT)`
- **d**: wall thickness (m)
- **√p**: Sieverts' law — dissolved concentration of hydrogen isotopes in metal is proportional to the square root of their partial pressure in the gas phase

> Terminology note: use **Sieverts' law** (solubility) + **Fick's law** (diffusion) —
> not "Richardson's law" (that refers to thermionic emission).
> Domain experts will notice the distinction immediately.

### 3.5.3 Modelica Skeleton

```modelica
model TritiumPermeationLayer
  "Steady-state tritium permeation through PCHE metal wall (simplified)"

  parameter Modelica.Units.SI.Area   A_wall  = 50.0   "Total heat-transfer wall area (m²)";
  parameter Modelica.Units.SI.Length d_wall  = 0.0015  "PCHE wall thickness (m)";
  parameter Real Phi_0 = 2.0e-7
    "Permeability pre-factor Φ₀ (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵) — material-specific, check literature";
  parameter Modelica.Units.SI.MolarEnergy E_a = 45e3
    "Permeation activation energy Eₐ (J/mol) — typical for Inconel 617";

  Modelica.Blocks.Interfaces.RealInput  p_T_hot   "Hot-side tritium partial pressure (Pa)";
  Modelica.Blocks.Interfaces.RealInput  p_T_cold  "Cold-side (sCO₂) tritium partial pressure (Pa)";
  Modelica.Blocks.Interfaces.RealInput  T_wall    "Mean wall temperature (K)";
  Modelica.Blocks.Interfaces.RealOutput mdot_T    "Tritium permeation molar flow rate (mol/s)";

  Real Phi  "Permeability Φ(T)";
  Real R = 8.314;

equation
  Phi    = Phi_0 * exp(-E_a / (R * T_wall));
  mdot_T = (A_wall * Phi / d_wall) *
           (sqrt(max(p_T_hot, 0)) - sqrt(max(p_T_cold, 0)));

  annotation(Documentation(info="<html>
    <p><b>Limitations:</b></p>
    <ul>
      <li>Steady-state model; transient tritium accumulation in the wall is not modeled</li>
      <li>Surface dissociation/recombination rate-limiting effects ignored (non-negligible at low partial pressure)</li>
      <li>Φ₀ and Eₐ are strongly material- and surface-condition-dependent; defaults are indicative only</li>
    </ul>
    <p><b>References:</b></p>
    <ul>
      <li>Causey et al., Tritium Barriers and Permeation, SAND2008-1141</li>
      <li>Forcey et al., J. Nucl. Mater. (1988) — Inconel series data</li>
    </ul>
  </html>"));
end TritiumPermeationLayer;
```

### 3.5.4 Starting Strategy

1. **Steady-state first, transient later.** The steady-state model fits in ~50 lines; transient requires discretizing wall concentration — one order of magnitude more complex.
2. **Do not try to measure permeability yourself.** Transcribe Φ₀ and Eₐ from the published literature into `data/permeability_constants.csv`.
3. **Validate in isolation from PCHE.mo first.** Write a standalone test case with fixed T and partial-pressure difference; verify flux order-of-magnitude against literature.
4. **Declare limitations openly.** List "this model is not applicable to…" clearly in the README and component docs. Transparency attracts experts who will contribute improvements — hiding limitations drives them away.

## 3.6 Industrial-Standard Awareness — ASME BPVC Simplified Check

> **Important disclaimer:** this section adds only a "does this meet minimum-spec order-of-magnitude" hint to the simulation model.
> **It is not engineering certification of any kind.**
> Real nuclear pressure-boundary equipment must be designed, reviewed, and third-party verified by ASME-certified engineers
> following the full code process. The purpose of including this code is to signal
> that the library author understands the rules of the industry.

### 3.6.1 Why Add This

Nuclear (like aerospace) is an extremely conservative, code-driven industry.
A simulation library that is thermodynamically accurate but shows **zero awareness
of pressure-boundary mechanical constraints** will be dismissed as a "toy" by industrial engineers.
Adding a few `assert` lines for wall-thickness compliance sends a clear signal:
*"the author understands both the thermodynamics and the regulatory context."*

### 3.6.2 ASME BPVC Simplified Wall-Thickness Formula (thin-wall cylinder)

$$t_{\min} = \frac{P \cdot D}{2 \cdot S \cdot E - 1.2 \cdot P}$$

- **P**: design pressure differential (Pa)
- **D**: channel equivalent diameter (m)
- **S**: allowable material stress (Pa) — temperature-dependent; must be read from ASME II-D stress tables
- **E**: weld joint efficiency (1.0 for solid plate; 0.7–0.85 for welded)

> PCHE micro-channels are diffusion-bonded multi-plate structures, not simple cylinders.
> This formula is used only as a **conservative lower-bound estimate** to trigger an
> "is this far below code minimum" check — not as a substitute for real stress analysis.

### 3.6.3 Modelica Implementation

```modelica
model PCHE
  // ... (geometry and thermal parameters from § 3.3)

  // ── ASME simplified compliance check (v1.3+) ──
  parameter Modelica.Units.SI.Pressure allowable_stress = 110e6
    "Allowable stress S (Pa) — default is approximate Inconel 617 at 650 °C;
     must be corrected from ASME II-D for actual material and temperature";
  parameter Real weld_efficiency = 0.85
    "Weld joint efficiency E (diffusion-bonded PCHE: 0.7–0.85; use 0.7 conservatively)";
  parameter Boolean enable_asme_check = true;

  Modelica.Units.SI.Length required_thickness
    "Minimum wall thickness estimated per ASME BPVC Section VIII Div.1 (m)";

equation
  // ... (NTU-effectiveness equations from § 3.3)

  required_thickness = (max(P_hot, P_cold)) * D_ch /
                       (2 * allowable_stress * weld_efficiency
                        - 1.2 * max(P_hot, P_cold));

  if enable_asme_check then
    assert(d_wall >= required_thickness,
      "WARNING: PCHE wall thickness d_wall = " + String(d_wall*1000) +
      " mm is below the ASME BPVC Section VIII simplified minimum of " +
      String(required_thickness*1000) + " mm. " +
      "Note: this check is a thin-wall cylinder approximation only — not a substitute for formal stress analysis.",
      level = AssertionLevel.warning);
  end if;

end PCHE;
```

## 3.7 Optional Advanced Extension — TMSR-LF1 Online-Refueling Transient Module (v1.4)

> **Difficulty:** High. Requires a solid Phase 3 mainline (§§ 3.1–3.4) before attempting.
> **Status:** speculative advanced extension — framed to match confirmed public milestones,
> not vendor roadmaps or unpublished claims.

### 3.7.1 Background — Confirmed TMSR-LF1 Milestones

SINAP (Shanghai Institute of Applied Physics, CAS) TMSR-LF1 (2 MWth):

| Date | Milestone | Source |
|------|-----------|--------|
| Oct 2023 | First criticality achieved | SINAP public announcement |
| Jun 2024 | Full rated power operation | SINAP public announcement |
| Oct 2024 | First online thorium addition without shutdown (world first) | SINAP public announcement |
| Nov 2025 | Th-U conversion confirmed; Th-233 breeding demonstrated | SINAP/CNNC announcement |

The Oct 2024 milestone — online fuel addition without shutdown — is a **confirmed world first**
for a molten-salt reactor and introduces a class of transient disturbances not present in solid-fuel reactors.

### 3.7.2 What "Online Refueling Transient" Means for System Simulation

When fuel salt is added or fission products are removed while the reactor is at power:

```
Reactivity step (positive or negative) → core power perturbation
→ thermal-hydraulic response (salt flow, T change) → sCO₂ cycle sees altered heat input
→ compressor/turbine operating point shifts → control system response
```

This is a *coupled neutronics + thermal-hydraulics + power-cycle* transient.
A simplified system-level model (ignoring spatial neutronics) can capture the
dominant dynamics using a point-kinetics approximation.

### 3.7.3 Modelica Skeleton

```modelica
model OnlineFuellingTransient
  "Simplified online refueling / fission product removal transient for TMSR-LF1
   Uses point-kinetics approximation — spatial neutronics not modeled"

  // ── Reactor point-kinetics parameters ──
  parameter Real beta_eff = 0.003
    "Effective delayed neutron fraction — TMSR with Th-U fuel is lower than U-Pu; verify from literature";
  parameter Real Lambda = 1e-4    "Prompt neutron lifetime (s)";
  parameter Real[6] beta_i        "Delayed neutron group fractions";
  parameter Real[6] lambda_i      "Delayed neutron group decay constants (s⁻¹)";

  // ── Online fuelling perturbation input ──
  Modelica.Blocks.Interfaces.RealInput delta_rho_fuelling
    "Reactivity insertion from fuel addition / fission product removal (pcm)
     Typical range: ±5 pcm per refueling batch (estimate — verify against SINAP publications)";

  // ── Outputs ──
  Modelica.Blocks.Interfaces.RealOutput P_normalized  "Normalized reactor power (0–1)";
  Modelica.Blocks.Interfaces.RealOutput T_core_K      "Core outlet temperature (K)";

  Real n      "Normalized neutron flux";
  Real[6] C_i "Delayed neutron precursor concentrations";
  Real rho    "Total reactivity (pcm)";

equation
  // Point-kinetics equations
  der(n) = (rho - beta_eff) / Lambda * n + sum(lambda_i .* C_i);
  for i in 1:6 loop
    der(C_i[i]) = beta_i[i] / Lambda * n - lambda_i[i] * C_i[i];
  end for;

  // Total reactivity: feedback + fuelling perturbation
  // alpha_T: temperature feedback coefficient (negative for TMSR — stabilizing)
  rho = alpha_T * (T_core_K - T_core_nominal) + delta_rho_fuelling;

  P_normalized = n;

  annotation(Documentation(info="<html>
    <p><b>Module scope and confirmed basis (v1.4):</b></p>
    <ul>
      <li>TMSR-LF1 first criticality: Oct 2023 (SINAP confirmed)</li>
      <li>Full power operation: Jun 2024 (SINAP confirmed)</li>
      <li>World-first online thorium addition without shutdown: Oct 2024 (SINAP confirmed)</li>
      <li>Th-U conversion demonstrated: Nov 2025 (SINAP/CNNC confirmed)</li>
    </ul>
    <p><b>What this model does NOT include:</b></p>
    <ul>
      <li>Spatial neutronics (requires a dedicated neutronics solver like OpenMC)</li>
      <li>Salt chemistry dynamics during fuel addition</li>
      <li>Fission product removal kinetics (noble gas sparging, etc.)</li>
      <li>Validated beta_eff / lambda_i for Th-U fuel — use published estimates conservatively</li>
    </ul>
    <p><b>How to use responsibly:</b></p>
    <ul>
      <li>Declare this is a simplified point-kinetics model in all documentation</li>
      <li>Validate power transient shape against any available TMSR-LF1 published data</li>
      <li>Do not claim quantitative accuracy without experimental calibration</li>
    </ul>
  </html>"));
end OnlineFuellingTransient;
```

### 3.7.4 Integration with Full System Model

```modelica
// In TMSR_sCO2_Full.mo
model TMSR_sCO2_Full
  // ... existing reactor + cycle components

  OnlineFuellingTransient onlineRefuel
    "Optional: activated when simulating fuel addition transients";

  // Connect reactor power output to heat source of the intermediate heat exchanger
  connect(onlineRefuel.P_normalized, reactor.power_fraction);
  connect(onlineRefuel.T_core_K, intermediateHX.T_hot_in);

  // Scenario: step input of +3 pcm reactivity at t = 100 s (simulates fuel addition)
  onlineRefuel.delta_rho_fuelling = if time > 100 then 3.0 else 0.0;
end TMSR_sCO2_Full;
```

### 3.7.5 Value Proposition

| Dimension | Without online-refueling module | With this module |
|-----------|--------------------------------|-----------------|
| Reactor type simulated | Solid-fuel (batch refueling only) | Liquid-fuel MSR with continuous/online refueling |
| Transient scenarios | Load-following, startup/shutdown | + refueling-induced power perturbations |
| Differentiation from other open tools | Standard | **First open Modelica module addressing this transient class** |
| Required validation data | Any sCO₂ cycle data | TMSR-LF1 public operational data (as it becomes available) |

---

## 3.8 Living Documentation — Jupyter Book + Binder

> Streamlit addresses "trial barrier" — get an engineer to a working plot in 30 seconds.
> Jupyter Book addresses "readable derivation + one-click reproduction" — equations, code, and output together.
> The two are complementary: Streamlit is the engineer-facing demo window; Jupyter Book is the researcher-facing living document.

### Repository Structure Addition

```
sco2-tmsr-toolkit/
├── book/
│   ├── _config.yml
│   ├── _toc.yml
│   ├── intro.md
│   ├── 01_pseudocritical.ipynb
│   ├── 02_mixture_effects.ipynb
│   ├── 03_ts_diagram.ipynb
│   ├── 04_snl_validation.ipynb
│   └── references.bib
├── requirements.txt
└── postBuild
```

### Configuration

```yaml
# book/_config.yml
title: "sCO₂-TMSR-Toolkit — Living Documentation"
author: your-name
copyright: "2025"

execute:
  execute_notebooks: cache

repository:
  url: https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit
  path_to_book: book
  branch: main

launch_buttons:
  binderhub_url: "https://mybinder.org"
  colab_url: "https://colab.research.google.com"
  thebe: true

html:
  use_issues_button: true
  use_repository_button: true
  use_edit_page_button: true

bibtex_bibfiles:
  - references.bib
```

```yaml
# book/_toc.yml
format: jb-book
root: intro
chapters:
  - file: 01_pseudocritical
  - file: 02_mixture_effects
  - file: 03_ts_diagram
  - file: 04_snl_validation
```

### Auto-Deploy to GitHub Pages

```yaml
# .github/workflows/build-book.yml
name: Build & Deploy Jupyter Book

on:
  push:
    branches: [main]
    paths: ['book/**']

jobs:
  deploy-book:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -U jupyter-book matplotlib "CoolProp>=7.1" numpy pandas
      - run: jupyter-book build book/
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: book/_build/html
```

### Binder Dependencies

```
# requirements.txt
CoolProp>=7.1
numpy
pandas
matplotlib
streamlit
scipy
pytest
```

### Notebook Structure Convention

Every notebook follows: **Problem → Equations → Code → Conclusion**

```markdown
# 1. The Physics of the sCO₂ Pseudo-Critical Line

## 1.1 Problem statement
Above the critical pressure (P > 7.38 MPa), CO₂ has no phase transition...

## 1.2 Mathematical description
$$T_{pc}(P) = \arg\max_T \; C_p(T, P)$$

## 1.3 Code implementation
[code cell: find_pseudocritical_temp function]

## 1.4 Numerical validation
[code cell: Cp(T) curves at 8, 15, 25 MPa with peak markers]

## 1.5 Engineering implication
The compressor inlet must avoid the high-gradient region near the pseudo-critical line...
```

### CI for Phase 3 (OpenModelica)

```yaml
- name: OpenModelica compile check
  run: |
    docker run --rm -v $PWD:/lib openmodelica/openmodelica:v1.22.0-minimal \
      omc /lib/Tests/ValidationTests.mo
```

---

*← Back to [Phase 2](02_phase2_cfd_rom.md) | Back to [README](OVERVIEW.md)*
