within AdvancedReactor_sCO2_Library.Tests;
model ValidationTests
  "Aggregate validation suite — checks that every published model compiles"
  extends Modelica.Icons.Example;

  AdvancedReactor_sCO2_Library.Components.Valves.ThrottleValve              v1;
  AdvancedReactor_sCO2_Library.Components.Valves.BypassValve                v2;
  AdvancedReactor_sCO2_Library.Components.Turbomachinery.Compressor         c;
  AdvancedReactor_sCO2_Library.Components.Turbomachinery.ReCompressor       rc;
  AdvancedReactor_sCO2_Library.Components.Turbomachinery.Turbine            t;
  AdvancedReactor_sCO2_Library.Components.HeatExchangers.IntermediateHeatExchanger
                                                                            ihx;
  AdvancedReactor_sCO2_Library.Components.HeatExchangers.PCHE               pche;
  AdvancedReactor_sCO2_Library.Components.HeatExchangers.TritiumPermeationLayer
                                                                            tritium;
  AdvancedReactor_sCO2_Library.Components.Reactor.MoltenSaltReactor         msr;
  AdvancedReactor_sCO2_Library.Components.Reactor.OnlineFuellingTransient   refuel;

  annotation (Documentation(info = "<html>
    <p>Reference: docs/03_phase3_modelica.md § 3.8 (CI for Phase 3 — OpenModelica).</p>
    <p>The CI workflow runs:</p>
    <pre>
      docker run --rm -v $PWD:/lib openmodelica/openmodelica:v1.22.0-minimal \\
        omc /lib/Tests/ValidationTests.mo
    </pre>
    <p>Failure to compile any individual model is caught here.</p>
  </html>"));
end ValidationTests;
