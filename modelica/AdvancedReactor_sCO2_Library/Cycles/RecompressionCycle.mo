within AdvancedReactor_sCO2_Library.Cycles;
model RecompressionCycle
  "Recompression Brayton cycle — sCO2 (skeleton, Dostal 2004 architecture)"

  AdvancedReactor_sCO2_Library.Components.Turbomachinery.Compressor      mainCompressor;
  AdvancedReactor_sCO2_Library.Components.Turbomachinery.ReCompressor    reCompressor;
  AdvancedReactor_sCO2_Library.Components.Turbomachinery.Turbine          turbine;
  AdvancedReactor_sCO2_Library.Components.HeatExchangers.IntermediateHeatExchanger
                                                                          highTRecuperator;
  AdvancedReactor_sCO2_Library.Components.HeatExchangers.IntermediateHeatExchanger
                                                                          lowTRecuperator;

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.2 + Dostal 2004 thesis.</p>
    <p>Target benchmark: reproduce Dostal 2004 Fig. 6.5 efficiency curves
    once the medium model and component connectors are wired.</p>
  </html>"));
end RecompressionCycle;
