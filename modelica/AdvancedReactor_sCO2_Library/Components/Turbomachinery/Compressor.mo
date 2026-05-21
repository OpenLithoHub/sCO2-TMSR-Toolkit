within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model Compressor
  "Adiabatic main compressor — isentropic-efficiency model"

  parameter Real eta_isen = 0.85   "Isentropic efficiency (-)";
  parameter Modelica.Units.SI.MassFlowRate mdot_design = 100
    "Design-point mass flow (kg/s)";

  Modelica.Blocks.Interfaces.RealInput  h_in    "Inlet specific enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  h_isen  "Isentropic outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  mdot    "Mass flow rate (kg/s)";
  Modelica.Blocks.Interfaces.RealOutput h_out   "Real outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealOutput W       "Compressor power (W)";

equation
  h_out = h_in + (h_isen - h_in) / eta_isen;
  W     = mdot * (h_out - h_in);

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.2.</p>
    <p>Off-design map (W = f(mdot, P_ratio, N)) is a future deliverable — the
    skeleton uses fixed isentropic efficiency.</p>
  </html>"));
end Compressor;
