within AdvancedReactor_sCO2_Library.Components.Reactor;
model MoltenSaltReactor
  "Simplified molten-salt reactor thermal-hydraulic core (no spatial neutronics)"

  parameter Modelica.Units.SI.Power P_nominal = 2e6   "Nominal thermal power (W)";
  parameter Modelica.Units.SI.HeatCapacity C_core = 5e6
    "Lumped core heat capacity (J/K)";
  parameter Modelica.Units.SI.Temperature T_inlet_design = 873.15
    "Design-point salt inlet temperature (K)";

  Modelica.Blocks.Interfaces.RealInput  power_fraction  "Reactor power fraction (0-1)";
  Modelica.Blocks.Interfaces.RealInput  T_salt_in       "Salt inlet T (K)";
  Modelica.Blocks.Interfaces.RealInput  mdot_salt       "Salt mass flow (kg/s)";
  Modelica.Blocks.Interfaces.RealInput  Cp_salt         "Salt Cp (J/kg/K)";
  Modelica.Blocks.Interfaces.RealOutput T_salt_out      "Salt outlet T (K)";

  Real Q_core   "Core thermal power (W)";
  Real T_core   "Lumped core temperature (K)";

initial equation
  T_core = T_inlet_design;

equation
  Q_core = power_fraction * P_nominal;
  C_core * der(T_core) = Q_core - mdot_salt * Cp_salt * (T_core - T_salt_in);
  T_salt_out = T_core;

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.2.</p>
    <p><b>What this is NOT:</b></p>
    <ul>
      <li>Not a spatial neutronics model — see <code>OnlineFuellingTransient</code> for point-kinetics</li>
      <li>Not a chemistry-aware model — fission product evolution is out of scope</li>
    </ul>
  </html>"));
end MoltenSaltReactor;
