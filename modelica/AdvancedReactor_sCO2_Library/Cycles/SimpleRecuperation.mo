within AdvancedReactor_sCO2_Library.Cycles;
model SimpleRecuperation
  "Simple recuperation Brayton cycle — sCO2 (skeleton)"

  // Component instances — wiring left as an exercise pending Media.sCO2 LUT.
  AdvancedReactor_sCO2_Library.Components.Turbomachinery.Compressor      mainCompressor;
  AdvancedReactor_sCO2_Library.Components.Turbomachinery.Turbine          turbine;
  AdvancedReactor_sCO2_Library.Components.HeatExchangers.IntermediateHeatExchanger
                                                                          recuperator;

  annotation (Documentation(info="<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.2.</p>
    <p>Recuperation cycle template — the simplest sCO2 layout. Use as a
    smoke-test for the medium model and component connectors.</p>
  </html>"));
end SimpleRecuperation;
