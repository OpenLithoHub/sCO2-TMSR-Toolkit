within AdvancedReactor_sCO2_Library.Examples;
model StartupSequence
  "Cold-start sequence — placeholder template"
  extends Modelica.Icons.Example;
  AdvancedReactor_sCO2_Library.Cycles.TMSR_sCO2_Full plant;

  annotation (
    experiment(StopTime = 7200, Tolerance = 1e-5),
    Documentation(info = "<html>
      <p>Cold-start sequence — placeholder for future startup-trajectory work.</p>
    </html>"));
end StartupSequence;
