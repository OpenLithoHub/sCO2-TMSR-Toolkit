within AdvancedReactor_sCO2_Library.Components.Turbomachinery;
model ReCompressor
  "Recompression-branch compressor — kept distinct from main compressor"
  // Inherits Gap-1 placeholder note from Compressor.mo
  // (docs/known_gaps.md#compressor-maps).
  // Inherits the Wright2010 Table 5.1 wheel-geometry block and the Vrancik 1968
  // windage closure verbatim from Compressor. The recompression branch in the
  // SNL 10 MWe loop runs a different wheel; override r_tip / b2 / omega_design
  // / L_rotor / rho_cavity at instantiation when a recompression-specific
  // geometry or operating cavity density is known.
  extends Compressor(eta_isen_design = 0.83);
  annotation (Documentation(info="<html>
    <p>Recompression branch typically runs at higher inlet temperature than
    the main compressor — slightly lower default efficiency captures that.
    See docs § 3.2 + Dostal 2004 thesis Fig. 6.5.</p>
    <p><b>Defaults note:</b> wheel geometry and windage parameters are
    inherited from <code>Compressor</code> (Wright2010 Table 5.1 main-compressor
    wheel). For recompression-specific machines, override these parameters
    at instantiation.</p>
  </html>"));
end ReCompressor;
