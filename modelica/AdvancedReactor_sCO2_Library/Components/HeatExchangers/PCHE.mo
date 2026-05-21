within AdvancedReactor_sCO2_Library.Components.HeatExchangers;
model PCHE
  "Printed-circuit heat exchanger — NTU-effectiveness method
   + optional ROM/correlation switch + ASME BPVC Section VIII Div.1 simplified check.
   Reference: docs/03_phase3_modelica.md §§ 3.3 + 3.6."
  extends Modelica.Icons.UnderConstruction;

  // ── Geometry ──
  parameter Integer N_channels = 1000  "Number of micro-channels";
  parameter Modelica.Units.SI.Length D_ch   = 0.002
    "Channel equivalent (hydraulic) diameter (m)";
  parameter Modelica.Units.SI.Length L      = 0.6
    "Heat exchanger length (m)";
  parameter Modelica.Units.SI.Length d_wall = 0.0015
    "Wall (separator) thickness (m)";
  parameter Real zeta = 1.0
    "Pressure-drop correction factor (zigzag/airfoil geometries: > 1)";

  // ── ROM/correlation switch (Phase 2 § 2.6.4 bridge) ──
  parameter Boolean useROM = false
    "true: use PCHE_ROM_FMU from ExternalROM/ (§ 2.6.4); false: Gnielinski correlation";

  // ── Design-point thermal parameters (placeholder; replace with media-coupled equations) ──
  parameter Modelica.Units.SI.SpecificHeatCapacity Cp_hot  = 1500
    "Hot-side specific heat (J/(kg·K)) — molten salt FLiBe nominal";
  parameter Modelica.Units.SI.SpecificHeatCapacity Cp_cold = 1250
    "Cold-side specific heat (J/(kg·K)) — sCO₂ nominal at PCHE conditions";
  parameter Modelica.Units.SI.MassFlowRate mdot_hot  = 25.0  "Hot-side mass flow (kg/s)";
  parameter Modelica.Units.SI.MassFlowRate mdot_cold = 35.0  "Cold-side mass flow (kg/s)";
  parameter Modelica.Units.SI.ThermalConductance UA_design = 5e5
    "Design overall heat conductance (W/K) — calibrate against CFD or vendor data";
  parameter Modelica.Units.SI.Temperature T_hot_in  = 873.15  "Hot-side inlet temperature (K)";
  parameter Modelica.Units.SI.Temperature T_cold_in = 423.15  "Cold-side inlet temperature (K)";

  // ── ASME BPVC Section VIII Div.1 simplified check (§ 3.6) ──
  // DISCLAIMER: order-of-magnitude sanity check only.
  // NOT engineering certification. Real pressure-boundary design must be performed
  // and third-party verified by ASME-certified engineers.
  parameter Modelica.Units.SI.Pressure P_hot  = 0.5e6
    "Hot-side (salt) design pressure (Pa)";
  parameter Modelica.Units.SI.Pressure P_cold = 20e6
    "Cold-side (sCO₂) design pressure (Pa)";
  parameter Modelica.Units.SI.Pressure allowable_stress = 110e6
    "Allowable stress S (Pa) — default ≈ Inconel 617 at 650 °C; correct from ASME II-D";
  parameter Real weld_efficiency = 0.85
    "Weld joint efficiency E (diffusion-bonded PCHE: 0.7–0.85; use 0.7 conservatively)";
  parameter Boolean enable_asme_check = true
    "Enable ASME BPVC simplified wall-thickness assertion";

  // ── Working variables ──
  Modelica.Units.SI.ThermalConductance UA   "Overall heat conductance (W/K)";
  Real C_min   "Minimum heat capacity rate (W/K)";
  Real C_max   "Maximum heat capacity rate (W/K)";
  Real Cr      "Heat capacity ratio C_min/C_max (0–1)";
  Real NTU     "Number of transfer units";
  Real eps     "Heat exchanger effectiveness 0–1";
  Modelica.Units.SI.HeatFlowRate Q   "Heat duty (W)";
  Modelica.Units.SI.Length required_thickness
    "ASME simplified minimum wall thickness (m)";

  // ── Fluid ports (skeleton — full Medium coupling deferred to integration milestone) ──
  Modelica.Fluid.Interfaces.FluidPort_a hotInlet(
    redeclare package Medium = Modelica.Media.Water.StandardWater);
  Modelica.Fluid.Interfaces.FluidPort_b hotOutlet(
    redeclare package Medium = Modelica.Media.Water.StandardWater);
  Modelica.Fluid.Interfaces.FluidPort_a coldInlet(
    redeclare package Medium = AdvancedReactor_sCO2_Library.Media.sCO2);
  Modelica.Fluid.Interfaces.FluidPort_b coldOutlet(
    redeclare package Medium = AdvancedReactor_sCO2_Library.Media.sCO2);

equation
  // NTU-effectiveness method (counter-flow)
  C_min = min(Cp_hot * mdot_hot, Cp_cold * mdot_cold);
  C_max = max(Cp_hot * mdot_hot, Cp_cold * mdot_cold);
  Cr    = C_min / C_max;
  UA    = UA_design;
  NTU   = UA / C_min;
  eps   = (1 - exp(-NTU * (1 - Cr))) / (1 - Cr * exp(-NTU * (1 - Cr)));
  Q     = eps * C_min * (T_hot_in - T_cold_in);

  // ROM/correlation switch — heat-transfer coefficient closure
  // (Phase 2 ROM bridge: Nu_avg, dp_tot supplied by PCHE_ROM_FMU when useROM = true)
  if useROM then
    // PLACEHOLDER: connect to ExternalROM/PCHE_ROM_FMU.fmu inputs
    // (Re_local, T_local, P_local) -> (Nu_avg, dp_tot)
    // h_conv = Nu_avg * k_fluid / D_ch;
  else
    // PLACEHOLDER: Gnielinski correlation (Re > 3 000, smooth circular channel)
    // f = (0.79 * log(Re) - 1.64) ^ (-2);
    // Nu_avg = (f/8) * (Re - 1000) * Pr / (1 + 12.7 * sqrt(f/8) * (Pr^(2/3) - 1));
    // h_conv = Nu_avg * k_fluid / D_ch;
  end if;

  // ASME BPVC Section VIII Div.1 simplified thin-wall cylinder formula
  //   t_min = (P · D) / (2·S·E − 1.2·P)
  required_thickness = max(P_hot, P_cold) * D_ch /
                       (2 * allowable_stress * weld_efficiency
                        - 1.2 * max(P_hot, P_cold));

  if enable_asme_check then
    assert(d_wall >= required_thickness,
      "PCHE wall thickness d_wall is below the ASME BPVC Section VIII Div.1 simplified minimum. "
      + "This thin-wall cylinder approximation is a sanity check only and not a substitute for formal stress analysis.",
      level = AssertionLevel.warning);
  end if;

  // Steady mass balance — placeholder isenthalpic pass-through
  hotInlet.m_flow + hotOutlet.m_flow = 0;
  coldInlet.m_flow + coldOutlet.m_flow = 0;
  hotOutlet.h_outflow  = inStream(hotInlet.h_outflow);
  hotInlet.h_outflow   = inStream(hotOutlet.h_outflow);
  coldOutlet.h_outflow = inStream(coldInlet.h_outflow);
  coldInlet.h_outflow  = inStream(coldOutlet.h_outflow);

  annotation (Documentation(info = "<html>
    <h4>Printed-Circuit Heat Exchanger (PCHE) — TMSR sCO₂ intermediate loop</h4>
    <p><b>Reference:</b> docs/03_phase3_modelica.md §§ 3.3 (NTU/ROM) + 3.6 (ASME).</p>

    <h5>Method</h5>
    <ul>
      <li>NTU-effectiveness counter-flow heat balance</li>
      <li>Switchable closure: <code>useROM = true</code> hooks the FMU exported by Phase 2
          (rom/exported/wrap_as_fmu.py); <code>useROM = false</code> uses Gnielinski (smooth
          channel, Re &gt; 3 000) as a fallback</li>
      <li>ASME BPVC Section VIII Div.1 thin-wall cylinder formula:
          t_min = (P · D) / (2·S·E − 1.2·P)</li>
    </ul>

    <h5>Disclaimer (§ 3.6)</h5>
    <p>The ASME assertion is an order-of-magnitude sanity check only. PCHE micro-channels are
       diffusion-bonded multi-plate structures, not simple cylinders. This component is
       <b>not</b> engineering certification. Real nuclear pressure-boundary equipment must be
       designed and verified by ASME-certified engineers per the full code process.</p>

    <h5>Status</h5>
    <p><b>UnderConstruction</b> — heat-transfer closure (Gnielinski / ROM-FMU coupling) and
       full Medium-side property calls land at the Phase 3 month-12 milestone. Currently the
       NTU equations use design-point Cp values; replace with Medium calls at integration time.</p>
  </html>"));
end PCHE;
