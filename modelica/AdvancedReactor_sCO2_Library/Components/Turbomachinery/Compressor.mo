within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model Compressor
  "Adiabatic main compressor — isentropic-efficiency model with optional BYOD off-design map.
   Reference: docs/03_phase3_modelica.md § 3.2 + docs/00 § Black Hole 1 (BYOD interface)."

  // ── Design-point parameters ──
  // PLACEHOLDER: scalar performance defaults are engineering-typical values,
  // not page-anchored extractions. The wheel-geometry block below is now
  // anchored to Wright2010 SAND2010-0171 Table 5.1 (Confidence A); see
  // docs/data_extracts/wright2010_sand2010-0171.md "Table 5.1 main-compressor
  // wheel geometry" and docs/03_phase3_modelica.md § 3.2.1.
  parameter Real eta_isen_design = 0.85
    "Design-point isentropic efficiency (-) — engineering-typical value, not source-anchored";
  parameter Modelica.Units.SI.MassFlowRate mdot_design = 100
    "Design-point mass flow (kg/s) — engineering-typical value, not source-anchored";
  parameter Real PR_design = 2.5
    "Design-point pressure ratio (-) — engineering-typical value, not source-anchored";

  // ── Wheel geometry (Wright2010 SAND2010-0171 Table 5.1 main-compressor wheel) ──
  // Source: docs/data_extracts/wright2010_sand2010-0171.md "Table 5.1
  // main-compressor wheel geometry" [Confidence A]. The 10 MWe SNL test loop
  // wheel; defaults reproduce p.54 verbatim. Override per industrial machine.
  parameter Modelica.Units.SI.Length r_tip = 0.0186817
    "Impeller tip radius r_tip (m) — Wright2010 Table 5.1 (≈ 18.7 mm)";
  parameter Modelica.Units.SI.Length b2 = 0.00171
    "Impeller exducer blade height b₂ (m) — Wright2010 Table 5.1 (1.71 mm)";
  parameter Modelica.Units.SI.Angle beta_2b =
    Modelica.Constants.pi * (-50) / 180
    "Back-swept blade exit angle β₂b (rad) — Wright2010 Table 5.1 (-50°)";
  parameter Integer Z_blades = 12
    "Blade count Z_r (-) — Wright2010 Table 5.1";
  parameter Modelica.Units.SI.Length blade_thickness = 0.000762
    "Blade thickness (m) — Wright2010 Table 5.1 (0.762 mm)";
  parameter Modelica.Units.SI.Length r_shroud_inlet = 0.00937
    "Inducer shroud radius r_s1 (m) — Wright2010 Table 5.1 (9.37 mm)";
  parameter Modelica.Units.SI.Length r_hub_inlet = 0.00254
    "Inducer hub radius r_h1 (m) — Wright2010 Table 5.1 (2.54 mm)";
  parameter Modelica.Units.SI.Angle beta_1bt =
    Modelica.Constants.pi * 50 / 180
    "Inducer-tip blade angle β₁bt (rad) — Wright2010 Table 5.1 (+50°)";
  parameter Modelica.Units.SI.Angle alpha_diff =
    Modelica.Constants.pi * 71.5 / 180
    "Vaned-diffuser leading-edge angle α₂ (rad) — Wright2010 Table 5.1 (71.5°)";
  parameter Modelica.Units.SI.Length tip_clearance = 0.000254
    "Impeller tip-to-shroud clearance (m) — Wright2010 Table 5.1 (0.254 mm)";
  parameter Modelica.Units.SI.AngularVelocity omega_design =
    2 * Modelica.Constants.pi * 75000 / 60
    "Design shaft speed ω_design (rad/s) — Wright2010 Table 3.1 (75 000 rpm)";

  // ── BYOD (Bring Your Own Data) off-design map interface ──
  // Industrial users plug in proprietary maps via CSV → .txt converter.
  //
  // CSV columns (validation/compressor_maps/*.csv):
  //   phi  (flow coefficient, -)
  //   psi  (head coefficient, -)
  //   eta  (isentropic efficiency, -)
  //
  // Convert to Modelica's .txt table format with
  //   python -m tools.compressor_map_to_modelica \\
  //     validation/compressor_maps/sandia_main_compressor.csv \\
  //     -o validation/compressor_maps/sandia_main_compressor.txt
  // and point mapFileName at the .txt file. The two-column lookup output
  // is [psi, eta] keyed on phi.
  //
  // The default in-line table below carries the same Sandia placeholder
  // rows as `validation/compressor_maps/sandia_main_compressor.csv`
  // (Wright2010 design point + generic centrifugal surge-to-choke shape,
  // Confidence C). Both stay in sync because the CSV → .txt converter
  // also re-emits this Modelica table block.
  parameter Boolean useExternalMap = false
    "true: read off-design map via Modelica.Blocks.Tables; false: use the in-line default table";
  parameter String mapFileName = ""
    "Path to BYOD compressor map .txt (Modelica table format) when useExternalMap = true";
  parameter String mapTableName = "compressor_map"
    "Table identifier inside the .txt file (the `#1` header name)";
  parameter Real default_map[:, 3] = [
    0.010, 0.62, 0.55;
    0.014, 0.70, 0.68;
    0.018, 0.75, 0.78;
    0.022, 0.78, 0.84;
    0.024, 0.78, 0.85;
    0.026, 0.77, 0.83;
    0.030, 0.73, 0.78;
    0.035, 0.66, 0.70;
    0.040, 0.55, 0.58]
    "Inline default off-design map [phi, psi, eta] — Sandia placeholder; mirrors validation/compressor_maps/sandia_main_compressor.csv";

  // ── Windage loss (Vrancik 1968 NASA-TN-D-4849, Eq. 5–6) ──
  // Source: docs/data_extracts/vrancik1968_nasa-tn-d4849.md [Confidence A].
  //   Eq. 5  W_windage = π · C_d(Re) · ρ · r⁴ · ω³ · L
  //   Eq. 6  1/√C_d = 2.04 + 1.768·ln(Re·√C_d)        (turbulent)
  //   laminar fallback (between Eq. 4 and 5, p.5):  C_d = 2 / Re
  // Vrancik § "Experimental verification" (p.6) reports 7 % maximum error.
  // Eq. 6 is implicit; we expose the closure choice rather than embed a
  // Newton iterator inside this skeleton model. Industrial users override
  // C_d directly, or set use_implicit_Cd to fall back to the laminar form.
  parameter Boolean enable_windage = false
    "true: add Vrancik 1968 rotor windage to W (subtracted from useful power)";
  parameter Modelica.Units.SI.Length L_rotor = 0.05
    "Rotor wetted length L_r (m) — order-of-magnitude default; override per machine";
  parameter Modelica.Units.SI.Length t_gap = 0.000254
    "Rotor-to-housing radial gap (m) — defaults to tip clearance";
  parameter Modelica.Units.SI.Density rho_cavity = 5
    "Rotor-cavity gas density (kg/m³) — Wright2010 §5.4 ~150–200 psia drives ~5 kg/m³ for sCO₂; override per machine";
  parameter Modelica.Units.SI.DynamicViscosity mu_cavity = 1.8e-5
    "Rotor-cavity dynamic viscosity (Pa·s) — air-like default; override for sCO₂ rotor cavities";
  parameter Real Cd_user = 0.03
    "Skin-friction coefficient C_d (-) — default mid-range of Vrancik 1968 (0.01–0.06 for Re=1e4–1e8)";
  parameter Boolean use_laminar_Cd = false
    "true: override Cd_user with laminar closure C_d = 2/Re (Vrancik 1968 p.5)";

  // ── Inputs / outputs ──
  Modelica.Blocks.Interfaces.RealInput  h_in    "Inlet specific enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  h_isen  "Isentropic outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  mdot    "Mass flow rate (kg/s)";
  Modelica.Blocks.Interfaces.RealOutput h_out   "Real outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealOutput W       "Compressor power (W)";
  Modelica.Blocks.Interfaces.RealOutput W_windage
    "Vrancik 1968 windage loss (W); 0 when enable_windage=false";

  // Inlet density used to compute the off-design flow coefficient. Default
  // tracks the Wright2010 design-point compressor inlet (608 kg/m³). When a
  // medium model is wired into the cycle, override at instantiation —
  // exposing this as a parameter rather than a RealInput keeps the
  // connector signature backwards-compatible with skeleton cycles
  // (RecompressionCycle / SimpleRecuperation) that don't yet plumb density.
  parameter Modelica.Units.SI.Density rho_in_design = 608.0
    "Inlet density (kg/m³) — Wright2010 design-point default; override per machine";

  Real eta_isen   "Isentropic efficiency at the current operating point (-)";
  Real psi_op     "Head coefficient at the current operating point (-)";
  Real phi_op     "Flow coefficient at the current operating point (-)";
  Real Re_windage "Rotor-gap Reynolds number used in Vrancik C_d closure";
  Real Cd_eff     "Effective skin-friction coefficient C_d used at runtime";

  // CombiTable1Dv: 1D table, key = phi, returns [psi, eta]. We keep the
  // table fileName / tableName parameters wired to BYOD inputs so industrial
  // users can swap maps without recompiling the model.
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
  // Standard centrifugal definition: φ = ṁ / (ρ · ω · r_tip³).
  phi_op = mdot / (rho_in_design * omega_design * r_tip^3);

  // Drive the BYOD table — `map.u[1]` holds the key, `map.y[1:2]` returns
  // the [psi, eta] columns. When useExternalMap = false the in-line
  // `default_map` table is consulted; otherwise the .txt file at
  // `mapFileName` is loaded at simulation start.
  map.u[1] = phi_op;
  psi_op   = map.y[1];
  eta_isen = map.y[2];

  // Vrancik 1968 rotor-gap Reynolds number (p.2 SYMBOLS):
  //   Re = ρ · r · t_gap · ω / μ  (annular Couette form used in §5.4 application)
  // Guard against zero ω at simulation t=0 with a small floor.
  Re_windage = rho_cavity * r_tip * t_gap * max(omega_design, 1e-3) / mu_cavity;
  Cd_eff = if use_laminar_Cd then 2 / max(Re_windage, 1.0) else Cd_user;

  // Vrancik Eq. 5  W = π · C_d · ρ · r⁴ · ω³ · L   (verbatim)
  W_windage = if enable_windage then
                Modelica.Constants.pi * Cd_eff * rho_cavity
                * r_tip^4 * omega_design^3 * L_rotor
              else 0;

  h_out = h_in + (h_isen - h_in) / max(eta_isen, 1e-3);
  W     = mdot * (h_out - h_in) + W_windage;

  annotation (Documentation(info="<html>
    <p><b>Reference:</b> docs/03_phase3_modelica.md § 3.2.</p>
    <p><b>Black Hole 1 escape (docs/00 § Data Black Holes):</b> commercial compressor
       maps from Barber-Nichols, Dresser-Rand, Hanwha PSM are not public. This component
       defaults to a Sandia SNL public single-point efficiency. Industrial users
       provide proprietary maps via the <code>mapFileName</code> .txt file
       (1D table keyed on flow coefficient φ, with columns [psi, eta]). The
       CSV in <code>validation/compressor_maps/sandia_main_compressor.csv</code>
       is the documented placeholder; use
       <code>tools/compressor_map_to_modelica.py</code> to convert any CSV to
       the .txt table format Modelica.Blocks.Tables expects.</p>
    <p><b>Status:</b> off-design map (φ → ψ, η) is now wired through
       <code>Modelica.Blocks.Tables.CombiTable1Dv</code>; default table is the
       in-line Sandia placeholder. Wheel geometry (r_tip, b₂, β₂b, Z_r, α₂,
       tip clearance, design ω) is source-anchored to Wright2010 SAND2010-0171
       Table 5.1 (Confidence A) — see
       <code>docs/data_extracts/wright2010_sand2010-0171.md</code>. Rotor windage
       (Vrancik 1968 NASA-TN-D-4849 Eq. 5–6, Confidence A) is wired as an
       opt-in correction (<code>enable_windage = true</code>); the default
       <code>C_d = 0.03</code> is the mid-range of Vrancik's Re=10⁴–10⁸ band.
       Vrancik's reported 7 % experimental error is the empirical tolerance
       to apply when using this output as a soft constraint.</p>
  </html>"));
end Compressor;
