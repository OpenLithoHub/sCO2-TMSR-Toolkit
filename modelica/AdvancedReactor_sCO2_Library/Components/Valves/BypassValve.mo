within AdvancedReactor_sCO2_Library.Components.Valves;
model BypassValve
  "Bypass valve — opens to divert mass flow around the recuperator during transients"
  extends ThrottleValve(Cv = 5.0);

  annotation (Documentation(info="<html>
    <p>Same isenthalpic core as ThrottleValve, with a smaller default Cv that
    reflects the typical bypass-line sizing.</p>
  </html>"));
end BypassValve;
