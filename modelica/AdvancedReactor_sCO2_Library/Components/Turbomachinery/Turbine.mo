within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model Turbine
  "Adiabatic turbine — isentropic-efficiency model with optional BYOD off-design map.
   Reference: docs/03_phase3_modelica.md § 3.2 + docs/00 § Black Hole 1 (BYOD interface)."

  // ── Design-point parameters ──
  // PLACEHOLDER: scalar isentropic-efficiency default — full turbine
  // performance map (η vs. corrected mass flow / pressure ratio / speed)
  // is a Gap-1 commercial secret. See docs/known_gaps.md#compressor-maps.
  parameter Real eta_isen_design = 0.90
    "Design-point isentropic efficiency (-) — engineering-typical value, not source-anchored";

  // ── BYOD (Bring Your Own Data) off-design map interface ──
  // Mirrors Compressor.mo so industrial users with a real map can plug
  // it in symmetrically. CSV columns: phi, psi, eta.
  parameter Boolean useExternalMap = false
    "true: read off-design map via Modelica.Blocks.Tables; false: use eta_isen_design constant";
  parameter String mapFileName = ""
    "Path to BYOD turbine map CSV (when useExternalMap = true)";

  Modelica.Blocks.Interfaces.RealInput  h_in    "Inlet specific enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  h_isen  "Isentropic outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  mdot    "Mass flow rate (kg/s)";
  Modelica.Blocks.Interfaces.RealOutput h_out   "Real outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealOutput W       "Turbine power output (W)";

  Real eta_isen   "Isentropic efficiency at the current operating point (-)";

equation
  // Off-design closure — constant for the skeleton; replace with table lookup
  // when useExternalMap = true and mapFileName is populated.
  // PLACEHOLDER: WARNING — see docs/known_gaps.md#compressor-maps
  eta_isen = eta_isen_design;

  h_out = h_in - eta_isen * (h_in - h_isen);
  W     = mdot * (h_in - h_out);

  annotation (Documentation(info="<html>
    <p><b>Reference:</b> docs/03_phase3_modelica.md § 3.2.</p>
    <p><b>Black Hole 1 escape (docs/00 § Data Black Holes):</b> commercial turbine
       maps are not public. This component defaults to a scalar isentropic
       efficiency. Industrial users provide proprietary maps via the
       <code>mapFileName</code> CSV (<code>phi, psi, eta</code> columns) and set
       <code>useExternalMap = true</code>.</p>
    <p><b>Status:</b> off-design map (W = f(ṁ, P_ratio, N)) is a future deliverable;
       the skeleton uses a fixed isentropic efficiency.</p>
  </html>"));
end Turbine;
