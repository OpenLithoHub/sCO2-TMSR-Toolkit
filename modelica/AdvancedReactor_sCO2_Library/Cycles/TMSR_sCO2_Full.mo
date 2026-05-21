within AdvancedReactor_sCO2_Library.Cycles;
model TMSR_sCO2_Full
  "Coupled TMSR + sCO2 recompression cycle (skeleton)"

  AdvancedReactor_sCO2_Library.Components.Reactor.MoltenSaltReactor          reactor;
  AdvancedReactor_sCO2_Library.Components.Reactor.ReactorPowerControl        powerCtrl;
  AdvancedReactor_sCO2_Library.Components.HeatExchangers.IntermediateHeatExchanger
                                                                              intermediateHX;
  AdvancedReactor_sCO2_Library.Cycles.RecompressionCycle                      cycle;
  AdvancedReactor_sCO2_Library.Components.Reactor.OnlineFuellingTransient    onlineRefuel
    "Optional — activate to simulate fuel-addition transients";

equation
  // Skeleton wiring — connectors completed once Media.sCO2 LUT is in place.
  // connect(onlineRefuel.P_normalized,   reactor.power_fraction);
  // connect(onlineRefuel.T_core_K,       intermediateHX.T_hot_in);

  // Example transient driver: +3 pcm reactivity step at t = 100 s.
  // OnlineFuellingTransient.delta_rho_fuelling expects dimensionless reactivity (Δk/k).
  // 3 pcm = 3e-5.
  onlineRefuel.delta_rho_fuelling = if time > 100 then 3.0e-5 else 0.0;

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.7.4.</p>
    <p>Full coupled simulation: TMSR-LF1-class core + intermediate HX + sCO2
    recompression cycle + optional online-refueling transient. The
    <code>OnlineFuellingTransient</code> component is the v1.4 advanced extension.</p>
  </html>"));
end TMSR_sCO2_Full;
