within AdvancedReactor_sCO2_Library.Components.HeatExchangers;
model TritiumPermeationLayer
  "Steady-state tritium permeation through a PCHE metal wall (Sieverts + Arrhenius).
   Reference: docs/03_phase3_modelica.md § 3.5."
  extends Modelica.Icons.UnderConstruction;

  // ── Geometry ──
  parameter Modelica.Units.SI.Area   A_wall  = 50.0
    "Total heat-transfer wall area (m²)";
  parameter Modelica.Units.SI.Length d_wall  = 0.0015
    "PCHE wall thickness (m)";

  // ── Material permeability (Arrhenius form: Φ = Φ₀·exp(−Eₐ/RT)) ──
  // Reference: docs/known_gaps.md#tritium-constants. Reported Φ₀/Eₐ for
  // Inconel 617 varies by 10×–100× across papers because the surface
  // oxide layer dominates the result. Per Gap 4 escape strategy the
  // honest output is a *bracket* — Worst_Case / Best_Case / Custom.
  // Picking a single literature value would imply a precision the data
  // does not support.
  //
  // Preset:
  //   1 = Worst_Case  (no oxide barrier; literature-maximum Inconel 617:
  //                    high Φ₀, low Eₐ → upper-bound permeation)
  //   2 = Best_Case   (intact oxide barrier; literature-minimum Inconel 617:
  //                    low Φ₀, high Eₐ → lower-bound permeation)
  //   3 = Custom      (use Phi_0_user / E_a_user — user must cite source)
  parameter Integer preset = 1
    "1=Worst, 2=Best, 3=Custom — see docs/known_gaps.md#tritium-constants";

  // Worst-Case constants (no oxide barrier; Causey SAND2008-1141 upper
  // envelope for Inconel-series alloys; Φ₀ ≈ 2e-6 mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵,
  // Eₐ ≈ 42 kJ/mol).
  parameter Real Phi_0_worst = 2.0e-6
    "Worst-case Φ₀ (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵) — no oxide barrier";
  parameter Modelica.Units.SI.MolarEnergy E_a_worst = 42e3
    "Worst-case Eₐ (J/mol) — no oxide barrier";

  // Best-Case constants (intact oxide barrier; Forcey J. Nucl. Mater. 1988
  // lower envelope; Φ₀ ≈ 2e-8 mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵, Eₐ ≈ 55 kJ/mol).
  parameter Real Phi_0_best = 2.0e-8
    "Best-case Φ₀ (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵) — intact oxide barrier";
  parameter Modelica.Units.SI.MolarEnergy E_a_best = 55e3
    "Best-case Eₐ (J/mol) — intact oxide barrier";

  // Custom channel — user must cite source in any published result.
  parameter Real Phi_0_user = 2.0e-7
    "Custom Φ₀ (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵) — used only when preset=3; cite source";
  parameter Modelica.Units.SI.MolarEnergy E_a_user = 45e3
    "Custom Eₐ (J/mol) — used only when preset=3; cite source";

  // Effective Φ₀ and Eₐ selected by preset (final parameter values).
  final parameter Real Phi_0 =
    if preset == 1 then Phi_0_worst
    elseif preset == 2 then Phi_0_best
    else Phi_0_user
    "Effective Φ₀ at the selected preset";
  final parameter Modelica.Units.SI.MolarEnergy E_a =
    if preset == 1 then E_a_worst
    elseif preset == 2 then E_a_best
    else E_a_user
    "Effective Eₐ at the selected preset";

  constant Real R = Modelica.Constants.R
    "Universal gas constant (J/(mol·K))";

  // ── Inputs / outputs ──
  Modelica.Blocks.Interfaces.RealInput  p_T_hot
    "Hot-side tritium partial pressure (Pa)";
  Modelica.Blocks.Interfaces.RealInput  p_T_cold
    "Cold-side (sCO₂) tritium partial pressure (Pa)";
  Modelica.Blocks.Interfaces.RealInput  T_wall
    "Mean wall temperature (K)";
  Modelica.Blocks.Interfaces.RealOutput mdot_T
    "Tritium permeation molar flow rate (mol/s)";

  // ── Working variables ──
  Real Phi  "Permeability Φ(T) at current wall temperature";
  Real J    "Permeation flux (mol·m⁻²·s⁻¹)";

equation
  // Arrhenius temperature dependence
  Phi = Phi_0 * exp(-E_a / (R * max(T_wall, 1.0)));

  // Sieverts' law: J = (Φ/d) · (√p_hot − √p_cold)
  // (max(·,0) guards against numerical negatives near zero partial pressure)
  J = (Phi / d_wall) * (sqrt(max(p_T_hot, 0.0)) - sqrt(max(p_T_cold, 0.0)));

  mdot_T = A_wall * J;

  annotation (Documentation(info = "<html>
    <h4>Tritium permeation layer — steady-state Sieverts + Arrhenius model</h4>
    <p><b>Reference:</b> docs/03_phase3_modelica.md § 3.5.</p>

    <h5>Equations</h5>
    <pre>
      Φ(T) = Φ₀ · exp(−Eₐ / (R·T))
      J    = (Φ / d) · (√p_hot − √p_cold)            [Sieverts + Fick]
      ṁ_T  = A_wall · J
    </pre>
    <p>Use <b>Sieverts' law</b> (solubility) + <b>Fick's law</b> (diffusion).
       Not Richardson's law (that refers to thermionic emission — common terminology error).</p>

    <h5>Limitations (declare openly per § 3.5.4)</h5>
    <ul>
      <li>Steady-state only — transient tritium accumulation in the wall is not modeled</li>
      <li>Surface dissociation/recombination rate-limiting effects ignored
          (non-negligible at low partial pressure)</li>
      <li>Φ₀ and Eₐ are strongly material- and surface-condition-dependent;
          defaults are indicative for Inconel 617 only</li>
      <li>No coupling to oxide/nitride tritium permeation barriers (TPB coatings)</li>
    </ul>

    <h5>References</h5>
    <ul>
      <li>Causey et al., <i>Tritium Barriers and Permeation</i>, SAND2008-1141</li>
      <li>Forcey et al., <i>J. Nucl. Mater.</i> (1988) — Inconel-series permeability data</li>
    </ul>

    <h5>Validation strategy</h5>
    <p>Per § 3.5.4: validate in isolation from PCHE.mo first — fix T_wall and the partial-pressure
       difference, verify flux order-of-magnitude against published literature, and only then
       integrate into the full system model.</p>
  </html>"));
end TritiumPermeationLayer;
