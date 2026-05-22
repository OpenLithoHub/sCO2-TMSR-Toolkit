within AdvancedReactor_sCO2_Library.Components.Reactor;
model OnlineFuellingTransient
  "Simplified online refueling / fission-product removal transient for TMSR-LF1.
   Point-kinetics approximation with 6 delayed-neutron groups — spatial neutronics not modeled.
   Reference: docs/03_phase3_modelica.md § 3.7."
  extends Modelica.Icons.UnderConstruction;

  // ── Reactor point-kinetics parameters ──
  // PLACEHOLDER: every literature-grade default below is an indicative
  // value for Th-U fuel pending SINAP TMSR-LF1 publication of measured
  // operating parameters — see docs/known_gaps.md#tmsr-lf1.
  parameter Real beta_eff = 0.003
    "Effective delayed neutron fraction — TMSR Th-U fuel is lower than U-Pu; verify from literature";
  parameter Real Lambda = 1e-4
    "Prompt neutron generation time (s)";

  // 6-group delayed-neutron data (defaults: U-235 thermal, indicative only — replace with Th-U values)
  parameter Real[6] beta_i =
    {0.000215, 0.001424, 0.001274, 0.002568, 0.000748, 0.000273}
    "Delayed-neutron group fractions (sum ≈ beta_eff)";
  parameter Real[6] lambda_i =
    {0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01}
    "Delayed-neutron group decay constants (s⁻¹)";

  // ── Reactivity feedback ──
  parameter Real alpha_T = -3.0e-5
    "Temperature reactivity coefficient (1/K) — negative for TMSR (stabilizing); literature value";
  parameter Modelica.Units.SI.Temperature T_core_nominal = 923.15
    "Nominal core outlet temperature (K)";

  // ── Lumped core thermal model (very simplified) ──
  parameter Modelica.Units.SI.Power P_thermal_nominal = 2e6
    "TMSR-LF1 nominal thermal power (W) — 2 MWth";
  parameter Modelica.Units.SI.HeatCapacity C_core = 5e6
    "Lumped core heat capacity (J/K) — calibrate against published TMSR-LF1 data";
  parameter Modelica.Units.SI.ThermalConductance UA_to_loop = 5e3
    "Heat-removal conductance to primary salt loop (W/K)";
  parameter Modelica.Units.SI.Temperature T_loop_in = 873.15
    "Primary loop return temperature (K)";

  // ── Online-fuelling perturbation input ──
  Modelica.Blocks.Interfaces.RealInput delta_rho_fuelling
    "Reactivity insertion from fuel addition / fission product removal (dimensionless reactivity, NOT pcm).
     Convert: rho [-] = pcm * 1e-5. Typical refueling batch: ±5 pcm = ±5e-5";

  // ── Outputs ──
  Modelica.Blocks.Interfaces.RealOutput P_normalized
    "Normalized reactor power (0–1)";
  Modelica.Blocks.Interfaces.RealOutput T_core_K
    "Core outlet temperature (K)";

  // ── State variables ──
  Real n(start = 1.0, fixed = true)
    "Normalized neutron flux (1.0 = nominal full power)";
  Real[6] C_i(each start = 1.0, each fixed = true)
    "Delayed-neutron precursor concentrations (normalized)";
  Real rho
    "Total reactivity (dimensionless)";
  Modelica.Units.SI.Temperature T_core(start = 923.15, fixed = true);

equation
  // Point-kinetics: prompt-neutron balance
  der(n) = (rho - beta_eff) / Lambda * n + sum(lambda_i .* C_i);

  // Delayed-neutron precursor balances (vectorised)
  for i in 1:6 loop
    der(C_i[i]) = beta_i[i] / Lambda * n - lambda_i[i] * C_i[i];
  end for;

  // Total reactivity = temperature feedback + online-fuelling perturbation
  rho = alpha_T * (T_core - T_core_nominal) + delta_rho_fuelling;

  // Lumped core energy balance: P_gen − P_removed = C·dT/dt
  C_core * der(T_core) = n * P_thermal_nominal - UA_to_loop * (T_core - T_loop_in);

  // Outputs
  P_normalized = n;
  T_core_K     = T_core;

  annotation (Documentation(info = "<html>
    <h4>TMSR-LF1 Online-Refueling Transient — point-kinetics module</h4>
    <p><b>Reference:</b> docs/03_phase3_modelica.md § 3.7. Status: speculative advanced extension,
       framed against confirmed public milestones only.</p>

    <h5>Confirmed TMSR-LF1 milestones (basis for the scenario)</h5>
    <ul>
      <li>Oct 2023 — first criticality (SINAP)</li>
      <li>Jun 2024 — full rated 2 MWth operation (SINAP)</li>
      <li>Oct 2024 — world-first online thorium addition without shutdown (SINAP)</li>
      <li>Nov 2025 — Th-U conversion / Th-233 breeding demonstrated (SINAP/CNNC)</li>
    </ul>

    <h5>What this model does NOT include</h5>
    <ul>
      <li>Spatial neutronics — point-kinetics only; use a dedicated solver (OpenMC, Serpent) for spatial detail</li>
      <li>Salt chemistry dynamics during fuel addition</li>
      <li>Fission-product removal kinetics (noble-gas sparging, etc.)</li>
      <li>Validated β_eff / λ_i / α_T for Th-U fuel — defaults are U-235 thermal placeholders</li>
    </ul>

    <h5>Use responsibly</h5>
    <ul>
      <li>Document everywhere that this is a simplified point-kinetics model</li>
      <li>Validate transient shape against published TMSR-LF1 data when available</li>
      <li>Do not claim quantitative accuracy without experimental calibration</li>
    </ul>

    <h5>Reactivity unit convention</h5>
    <p>delta_rho_fuelling is <b>dimensionless reactivity</b> (Δk/k), not pcm.
       Convert via 1 pcm = 1·10⁻⁵. A ±5 pcm refueling batch is ±5·10⁻⁵.</p>
  </html>"));
end OnlineFuellingTransient;
