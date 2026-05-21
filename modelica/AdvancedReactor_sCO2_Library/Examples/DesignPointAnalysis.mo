within AdvancedReactor_sCO2_Library.Examples;
model DesignPointAnalysis
  "Steady-state design-point evaluation of the recompression cycle"
  extends Modelica.Icons.Example;

  AdvancedReactor_sCO2_Library.Cycles.RecompressionCycle cycle;

  annotation (
    experiment(StopTime = 1, Tolerance = 1e-6),
    Documentation(info = "<html>
      <p>Reference: docs/03_phase3_modelica.md § 3.2.</p>
      <p>Run the recompression cycle to convergence at design point.
      Currently a placeholder — exercise once the cycle's connector wiring
      is complete.</p>
    </html>"));
end DesignPointAnalysis;
