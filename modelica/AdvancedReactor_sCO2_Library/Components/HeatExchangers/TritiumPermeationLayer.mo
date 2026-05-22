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
  // PLACEHOLDER: defaults below are indicative only — see
  // docs/known_gaps.md#tritium-constants. Reported Φ₀/Eₐ for Inconel 617
  // varies by 10×–100× across papers because the surface oxide layer
  // dominates the result. Bracket the answer rather than trust a single
  // constant: the full Best/Worst/Custom preset interface is tracked at
  // docs/known_gaps.md#tritium-constants.
  parameter Real Phi_0 = 2.0e-7
    "Permeability pre-factor Φ₀ (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵) — material-specific; verify from literature";
  parameter Modelica.Units.SI.MolarEnergy E_a = 45e3
    "Permeation activation energy Eₐ (J/mol) — typical for Inconel 617";

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
