within AdvancedReactor_sCO2_Library.Components.HeatExchangers;
model IntermediateHeatExchanger
  "Salt-side / sCO2-side intermediate heat exchanger — NTU-effectiveness skeleton"

  parameter Modelica.Units.SI.Area A = 100
    "Heat-transfer area (m^2)";
  parameter Modelica.Units.SI.CoefficientOfHeatTransfer U = 1500
    "Overall heat-transfer coefficient (W/m^2/K) — placeholder";

  Modelica.Blocks.Interfaces.RealInput  T_hot_in    "Hot-side inlet T (K)";
  Modelica.Blocks.Interfaces.RealInput  T_cold_in   "Cold-side inlet T (K)";
  Modelica.Blocks.Interfaces.RealInput  C_hot       "Hot-side heat capacity rate (W/K)";
  Modelica.Blocks.Interfaces.RealInput  C_cold      "Cold-side heat capacity rate (W/K)";
  Modelica.Blocks.Interfaces.RealOutput Q           "Heat duty (W)";
  Modelica.Blocks.Interfaces.RealOutput T_hot_out   "Hot-side outlet T (K)";
  Modelica.Blocks.Interfaces.RealOutput T_cold_out  "Cold-side outlet T (K)";

  Real Cmin    "min(C_hot, C_cold)";
  Real Cr      "Capacity ratio Cmin/Cmax";
  Real NTU     "Number of transfer units";
  Real eps     "Counter-flow effectiveness";

equation
  Cmin = min(C_hot, C_cold);
  Cr   = Cmin / max(C_hot, C_cold);
  NTU  = U * A / Cmin;
  eps  = (1 - exp(-NTU * (1 - Cr))) / (1 - Cr * exp(-NTU * (1 - Cr)));

  Q          = eps * Cmin * (T_hot_in - T_cold_in);
  T_hot_out  = T_hot_in  - Q / C_hot;
  T_cold_out = T_cold_in + Q / C_cold;

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.2.</p>
    <p>Skeleton — fluid-port version (replacing the RealInput connectors)
    will follow once the <code>Media.MoltenSalt</code> placeholder is
    implemented.</p>
  </html>"));
end IntermediateHeatExchanger;
