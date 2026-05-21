within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model ReCompressor
  "Recompression-branch compressor — kept distinct from main compressor"
  extends Compressor(eta_isen_design = 0.83);
  annotation (Documentation(info="<html>
    <p>Recompression branch typically runs at higher inlet temperature than
    the main compressor — slightly lower default efficiency captures that.
    See docs § 3.2 + Dostal 2004 thesis Fig. 6.5.</p>
  </html>"));
end ReCompressor;
