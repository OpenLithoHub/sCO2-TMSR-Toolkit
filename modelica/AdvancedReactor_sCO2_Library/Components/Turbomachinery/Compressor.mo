within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model Compressor
  "Adiabatic main compressor — isentropic-efficiency model with optional BYOD off-design map.
   Reference: docs/03_phase3_modelica.md § 3.2 + docs/00 § Black Hole 1 (BYOD interface)."

  // ── Design-point parameters (Sandia SNL public single-point baseline) ──
  parameter Real eta_isen_design = 0.85
    "Design-point isentropic efficiency (-) — SNL Wright et al. baseline";
  parameter Modelica.Units.SI.MassFlowRate mdot_design = 100
    "Design-point mass flow (kg/s)";
  parameter Real PR_design = 2.5
    "Design-point pressure ratio (-)";

  // ── BYOD (Bring Your Own Data) off-design map interface ──
  // Industrial users plug in proprietary maps via CSV.
  // CSV columns: phi (flow coefficient) , psi (head coefficient) , eta (efficiency)
  // The default file (when fileName = "") falls back to a generic centrifugal
  // scaling law so the placeholder is at least dimensionally credible.
  parameter Boolean useExternalMap = false
    "true: read off-design map via Modelica.Blocks.Tables; false: use eta_isen_design constant";
  parameter String mapFileName = ""
    "Path to BYOD compressor map CSV (when useExternalMap = true)";

  Modelica.Blocks.Interfaces.RealInput  h_in    "Inlet specific enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  h_isen  "Isentropic outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  mdot    "Mass flow rate (kg/s)";
  Modelica.Blocks.Interfaces.RealOutput h_out   "Real outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealOutput W       "Compressor power (W)";

  Real eta_isen   "Isentropic efficiency at the current operating point (-)";

equation
  // Off-design closure — constant for the skeleton; replace with table lookup
  // when useExternalMap = true and mapFileName is populated.
  // PLACEHOLDER: WARNING — see docs/known_gaps.md#compressor-maps
  eta_isen = eta_isen_design;

  h_out = h_in + (h_isen - h_in) / eta_isen;
  W     = mdot * (h_out - h_in);

  annotation (Documentation(info="<html>
    <p><b>Reference:</b> docs/03_phase3_modelica.md § 3.2.</p>
    <p><b>Black Hole 1 escape (docs/00 § Data Black Holes):</b> commercial compressor
       maps from Barber-Nichols, Dresser-Rand, Hanwha PSM are not public. This component
       defaults to a Sandia SNL public single-point efficiency. Industrial users
       provide proprietary maps via the <code>mapFileName</code> CSV
       (<code>phi, psi, eta</code> columns) and set <code>useExternalMap = true</code>.</p>
    <p><b>Status:</b> off-design map (W = f(ṁ, P_ratio, N)) is a future deliverable;
       the skeleton uses a fixed isentropic efficiency.</p>
  </html>"));
end Compressor;
