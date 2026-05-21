within ;
package AdvancedReactor_sCO2_Library
  "Open Modelica library for sCO2 Brayton cycles coupled to advanced reactors (TMSR / HTGR)"

  extends Modelica.Icons.Package;

  annotation (
    Documentation(info="<html>
      <h3>AdvancedReactor_sCO2_Library</h3>
      <p>Modular component library for system-level simulation of supercritical
      CO2 Brayton cycles coupled to molten-salt and high-temperature gas reactors.</p>

      <p><b>Phase 3 deliverable</b> of the sCO2-TMSR-Toolkit
      (see <code>docs/03_phase3_modelica.md</code>).</p>

      <h4>Status</h4>
      <p>🚧 <i>Skeleton.</i> Most components currently contain only the equation
      structure and parameter declarations specified in the Phase 3 docs;
      validation against published benchmarks (Dostal 2004) is a future milestone.</p>

      <h4>Library layout</h4>
      <ul>
        <li><code>Media</code> — fluid media (sCO2, MoltenSalt)</li>
        <li><code>Components</code> — heat exchangers, turbomachinery, reactor, valves</li>
        <li><code>Cycles</code> — composed Brayton cycle templates</li>
        <li><code>ExternalROM</code> — drop-in directory for FMUs from Phase 2</li>
        <li><code>Examples</code> — runnable design-point and transient scenarios</li>
        <li><code>Tests</code> — automated validation cases</li>
      </ul>

      <h4>License</h4>
      <p>Apache-2.0 for code; CC BY-SA 4.0 for documentation strings.</p>
    </html>"),
    uses(Modelica(version="4.0.0")),
    version="0.1.0",
    versionDate="2026-05-21");

end AdvancedReactor_sCO2_Library;
