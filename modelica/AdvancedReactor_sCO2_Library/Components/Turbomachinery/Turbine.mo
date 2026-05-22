within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model Turbine
  "Adiabatic turbine — isentropic-efficiency model with optional BYOD off-design map.
   Reference: docs/03_phase3_modelica.md § 3.2 + docs/00 § Black Hole 1 (BYOD interface)."

  // ── Design-point parameters ──
  // PLACEHOLDER: scalar performance defaults are engineering-typical values,
  // not page-anchored extractions. Like Compressor.mo, the off-design map
  // below is the actual deliverable; the scalars are kept for tooling that
  // doesn't exercise the table.
  parameter Real eta_isen_design = 0.90
    "Design-point isentropic efficiency (-) — engineering-typical value, not source-anchored";
  parameter Modelica.Units.SI.MassFlowRate mdot_design = 100
    "Design-point mass flow (kg/s) — engineering-typical value, not source-anchored";
  parameter Real PR_design = 2.5
    "Design-point pressure ratio (-) — engineering-typical value, not source-anchored";

  // ── Wheel geometry (placeholder — no Wright2010 turbine analogue to Table 5.1) ──
  // Wright2010 SAND2010-0171 documents the main-compressor wheel in Table 5.1
  // but does not publish an equivalent table for the turbine wheel. The radius
  // and design speed below are engineering-typical for the same SNL 10 MWe
  // class loop, exposed as parameters so industrial users can override.
  parameter Modelica.Units.SI.Length r_tip = 0.0186817
    "Turbine impeller tip radius r_tip (m) — same class as Wright2010 main compressor";
  parameter Modelica.Units.SI.AngularVelocity omega_design =
    2 * Modelica.Constants.pi * 75000 / 60
    "Design shaft speed ω_design (rad/s) — Wright2010 Table 3.1 (75 000 rpm)";

  // ── BYOD (Bring Your Own Data) off-design map interface ──
  // Mirrors Compressor.mo so industrial users with a real map can plug
  // it in symmetrically. CSV columns: phi, psi, eta.
  //
  // Convert CSV → Modelica .txt with the same converter the compressor
  // uses, just point --table-name at turbine_map:
  //   python -m tools.compressor_map_to_modelica \\
  //     validation/turbine_maps/sandia_main_turbine.csv \\
  //     --table-name turbine_map \\
  //     -o validation/turbine_maps/sandia_main_turbine.txt
  //
  // The default in-line table mirrors `validation/turbine_maps/sandia_main_turbine.csv`
  // (Confidence C placeholder — generic centripetal turbine surge-to-choke shape
  // around the Wright2010 design φ band). Both stay in sync because the
  // CSV → .txt converter also re-emits this Modelica table block.
  parameter Boolean useExternalMap = false
    "true: read off-design map via Modelica.Blocks.Tables; false: use the in-line default table";
  parameter String mapFileName = ""
    "Path to BYOD turbine map .txt (Modelica table format) when useExternalMap = true";
  parameter String mapTableName = "turbine_map"
    "Table identifier inside the .txt file (the `#1` header name)";
  parameter Real default_map[:, 3] = [
    0.012, 1.05, 0.74;
    0.016, 1.00, 0.82;
    0.020, 0.94, 0.88;
    0.024, 0.88, 0.90;
    0.026, 0.85, 0.90;
    0.028, 0.81, 0.89;
    0.032, 0.74, 0.85;
    0.036, 0.66, 0.79;
    0.040, 0.55, 0.70]
    "Inline default off-design map [phi, psi, eta] — placeholder; mirrors validation/turbine_maps/sandia_main_turbine.csv";

  // Inlet density at the turbine — Wright2010 §3 design-point turbine inlet
  // is ~73 kg/m³ (high-T side). Override per machine when a medium model is
  // wired into the cycle.
  parameter Modelica.Units.SI.Density rho_in_design = 73.0
    "Turbine inlet density (kg/m³) — Wright2010 design-point default; override per machine";

  // ── Inputs / outputs ──
  Modelica.Blocks.Interfaces.RealInput  h_in    "Inlet specific enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  h_isen  "Isentropic outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  mdot    "Mass flow rate (kg/s)";
  Modelica.Blocks.Interfaces.RealOutput h_out   "Real outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealOutput W       "Turbine power output (W)";

  Real eta_isen   "Isentropic efficiency at the current operating point (-)";
  Real psi_op     "Head coefficient at the current operating point (-)";
  Real phi_op     "Flow coefficient at the current operating point (-)";

  // CombiTable1Dv: 1D table, key = phi, returns [psi, eta]. Same wiring as
  // Compressor.mo so the BYOD discipline is symmetric across the train.
  Modelica.Blocks.Tables.CombiTable1Dv map(
    table             = default_map,
    columns           = {2, 3},
    tableOnFile       = useExternalMap,
    fileName          = mapFileName,
    tableName         = mapTableName,
    smoothness        = Modelica.Blocks.Types.Smoothness.LinearSegments,
    extrapolation     = Modelica.Blocks.Types.Extrapolation.HoldLastPoint)
    "BYOD off-design map: phi → (psi, eta)";

equation
  // Flow coefficient at the current operating point.
  // φ = ṁ / (ρ · ω · r_tip³) — standard turbomachinery non-dimensional form.
  phi_op = mdot / (rho_in_design * omega_design * r_tip^3);

  // Drive the BYOD table — `map.u[1]` holds the key, `map.y[1:2]` returns
  // the [psi, eta] columns.
  map.u[1] = phi_op;
  psi_op   = map.y[1];
  eta_isen = map.y[2];

  // Turbine produces work (h_in > h_out): real outlet enthalpy is the
  // isentropic value pulled back toward h_in by (1 - eta_isen).
  h_out = h_in - eta_isen * (h_in - h_isen);
  W     = mdot * (h_in - h_out);

  annotation (Documentation(info="<html>
    <p><b>Reference:</b> docs/03_phase3_modelica.md § 3.2.</p>
    <p><b>Black Hole 1 escape (docs/00 § Data Black Holes):</b> commercial turbine
       maps are not public. This component defaults to a placeholder centripetal
       turbine map keyed on flow coefficient φ. Industrial users provide
       proprietary maps via the <code>mapFileName</code> .txt file (1D table
       with columns [psi, eta]).</p>
    <p><b>Status:</b> off-design map (φ → ψ, η) is wired through
       <code>Modelica.Blocks.Tables.CombiTable1Dv</code>; default table is the
       in-line placeholder mirrored from
       <code>validation/turbine_maps/sandia_main_turbine.csv</code> (Confidence C).
       Wheel-geometry block is intentionally limited to (r_tip, ω_design) — Wright2010
       SAND2010-0171 publishes Table 5.1 only for the main compressor; no public
       turbine analogue is available. Override the geometry parameters when adopting
       a different machine.</p>
  </html>"));
end Turbine;
