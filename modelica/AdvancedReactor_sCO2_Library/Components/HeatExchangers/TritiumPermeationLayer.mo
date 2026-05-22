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

  // Worst-Case constants (no oxide barrier).
  // Anchor: Humrickhouse 2012 INL/EXT-11-23265 Table 1, p.13, ref [11]
  // (Mori 1974), the highest-K0 of three independent literature values
  // for hydrogen permeability of Inconel 617:
  //   K0 = 5.39e-1 cm^3 H2 (STP) / (cm s atm^0.5)  (table footnote
  //                                                 conversion: ÷ 7.66e4
  //                                                 → 7.04e-6 SI),
  //   Q  = 21.3 kcal/mol                            (× 4.184 = 89.1 kJ/mol).
  // Confidence A.
  parameter Real Phi_0_worst = 7.04e-6
    "Worst-case Φ₀ (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵) — no oxide; Humrickhouse2012 T1 p.13 ref[11]";
  parameter Modelica.Units.SI.MolarEnergy E_a_worst = 89.1e3
    "Worst-case Eₐ (J/mol) — no oxide; Humrickhouse2012 T1 p.13 ref[11]";

  // Best-Case constants (intact oxide barrier).
  // Anchor: Humrickhouse 2012 INL/EXT-11-23265 § 4 conclusions p.43:
  // "approximately two orders of magnitude lower than previously
  // measured for hydrogen", attributed to Cr2O3 surface oxide. Eₐ
  // unchanged on the working hypothesis that oxide reduces magnitude
  // (K0) rather than the activation energy of the rate-limiting step.
  // Confidence A.
  parameter Real Phi_0_best = 7.04e-8
    "Best-case Φ₀ (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵) — intact oxide (Worst ÷100); Humrickhouse2012 §4 p.43";
  parameter Modelica.Units.SI.MolarEnergy E_a_best = 89.1e3
    "Best-case Eₐ (J/mol) — same Arrhenius slope; Humrickhouse2012 §4 p.43";

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
      <li>Humrickhouse, Pawelko, Shimada, Winston,
          <i>Tritium Permeability of Incoloy 800H and Inconel 617</i>,
          INL/EXT-11-23265 Rev. 1 (2012) — primary anchor for the
          Worst-case (Table 1 ref [11]) and Best-case (§ 4 conclusions,
          two-orders-of-magnitude oxide reduction) Arrhenius envelopes.</li>
      <li>Calderoni, Ebner,
          <i>Hydrogen Permeability of Incoloy 800H, Inconel 617, and
          Haynes 230 Alloys</i>, INL/EXT-10-19387 (2010) — companion
          FY-10 hydrogen-only report; cross-check.</li>
      <li>Causey et al., <i>Tritium Barriers and Permeation</i>,
          SAND2008-1141 — secondary review reference (PDF not publicly
          indexed by OSTI; cited for context only).</li>
    </ul>

    <h5>Validation strategy</h5>
    <p>Per § 3.5.4: validate in isolation from PCHE.mo first — fix T_wall and the partial-pressure
       difference, verify flux order-of-magnitude against published literature, and only then
       integrate into the full system model.</p>
  </html>"));
end TritiumPermeationLayer;
