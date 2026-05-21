within AdvancedReactor_sCO2_Library.Examples;
model LoadFollowing
  "Reactor power ramp 100% -> 50% -> 100% — cycle response demonstration"
  extends Modelica.Icons.Example;

  AdvancedReactor_sCO2_Library.Cycles.TMSR_sCO2_Full plant;
  Modelica.Blocks.Sources.TimeTable powerCmd(
    table = [0, 1.0; 600, 1.0; 900, 0.5; 2400, 0.5; 2700, 1.0; 3600, 1.0]);

  annotation (
    experiment(StopTime = 3600, Tolerance = 1e-5),
    Documentation(info = "<html>
      <p>Reference: docs/03_phase3_modelica.md milestone month 16.</p>
    </html>"));
end LoadFollowing;
