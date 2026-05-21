within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model Turbine
  "Adiabatic turbine — isentropic-efficiency model"

  parameter Real eta_isen = 0.90   "Isentropic efficiency (-)";

  Modelica.Blocks.Interfaces.RealInput  h_in    "Inlet specific enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  h_isen  "Isentropic outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealInput  mdot    "Mass flow rate (kg/s)";
  Modelica.Blocks.Interfaces.RealOutput h_out   "Real outlet enthalpy (J/kg)";
  Modelica.Blocks.Interfaces.RealOutput W       "Turbine power output (W)";

equation
  h_out = h_in - eta_isen * (h_in - h_isen);
  W     = mdot * (h_in - h_out);

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.2.</p>
  </html>"));
end Turbine;
