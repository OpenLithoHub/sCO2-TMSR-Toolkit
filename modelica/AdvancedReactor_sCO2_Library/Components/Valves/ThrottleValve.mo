within AdvancedReactor_sCO2_Library.Components.Valves;
model ThrottleValve
  "Simple throttle valve — sCO2 power cycle (isenthalpic assumption)"

  Modelica.Fluid.Interfaces.FluidPort_a port_a(
    redeclare package Medium = AdvancedReactor_sCO2_Library.Media.sCO2)
    "Inlet";
  Modelica.Fluid.Interfaces.FluidPort_b port_b(
    redeclare package Medium = AdvancedReactor_sCO2_Library.Media.sCO2)
    "Outlet";

  parameter Real Cv = 10.0                     "Flow coefficient";
  parameter Real opening(min=0, max=1) = 1.0   "Opening fraction 0-1";

  Real dp     "Pressure drop (Pa)";
  Real mdot   "Mass flow rate (kg/s)";
equation
  dp   = port_a.p - port_b.p;
  mdot = Cv * opening * sqrt(abs(dp)) * sign(dp);

  // Throttling is isenthalpic.
  port_a.h_outflow = inStream(port_b.h_outflow);
  port_b.h_outflow = inStream(port_a.h_outflow);

  port_a.m_flow + port_b.m_flow = 0;
  port_a.m_flow = mdot;

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.1.</p>
    <p>The isenthalpic assumption is acceptable when dp/p &lt; 0.1.</p>
  </html>"));
end ThrottleValve;
