"""Wrap a trained ONNX ROM as an FMI 2.0 FMU.

Reference: docs/02_phase2_cfd_rom.md § 2.6.4

Build:
    pythonfmu build -f wrap_as_fmu.py
Output:
    PCHE_ROM_FMU.fmu  →  drop into modelica/AdvancedReactor_sCO2_Library/ExternalROM/

FMI version note: docs default = 2.0 (mature in OpenModelica). Switch to FMI 3.0
via pythonfmu3 only if your workflow is Dymola or Python-only.
"""

from __future__ import annotations

import os

import numpy as np

try:
    from pythonfmu import Fmi2Causality, Fmi2Slave, Integer, Real
    _PYTHONFMU_OK = True
except ImportError:  # pragma: no cover — pythonfmu only required at build time
    # Stub so the module imports cleanly in environments without pythonfmu.
    # Instantiating PCHE_ROM_FMU will raise; `pythonfmu build` will fail loudly.
    _PYTHONFMU_OK = False

    class _Missing:
        def __init__(self, *a, **kw):
            raise SystemExit(
                "pythonfmu is required to build this FMU. `pip install pythonfmu`."
            )

    Fmi2Slave = _Missing  # type: ignore[assignment,misc]
    Fmi2Causality = _Missing  # type: ignore[assignment,misc]
    Integer = _Missing  # type: ignore[assignment,misc]
    Real = _Missing  # type: ignore[assignment,misc]


class PCHE_ROM_FMU(Fmi2Slave):
    author = "OpenLithoHub Contributors"
    description = "PCHE ROM trained on OpenFOAM CFD data (sCO2)"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inputs
        self.T_in = 305.4
        self.register_variable(Real("T_in", causality=Fmi2Causality.input))
        self.P_in = 8e6
        self.register_variable(Real("P_in", causality=Fmi2Causality.input))
        self.mdot = 0.1
        self.register_variable(Real("mdot", causality=Fmi2Causality.input))
        self.geom = 1
        self.register_variable(Integer("geom", causality=Fmi2Causality.input))

        # Outputs
        self.Nu_avg = 0.0
        self.register_variable(Real("Nu_avg", causality=Fmi2Causality.output))
        self.dp_tot = 0.0
        self.register_variable(Real("dp_tot", causality=Fmi2Causality.output))

        # Lazy load ONNX + scalers from the package's directory
        here = os.path.dirname(__file__)
        try:
            import onnxruntime as ort  # local import — keep FMU import surface small
        except ImportError as e:
            raise SystemExit(
                "onnxruntime not installed. `pip install onnxruntime`."
            ) from e

        self.session = ort.InferenceSession(os.path.join(here, "pche_rom.onnx"))
        sc = np.load(os.path.join(here, "scalers.npz"))
        self.xm, self.xsd = sc["x_mean"], sc["x_scale"]
        self.ym, self.ysd = sc["y_mean"], sc["y_scale"]

    def do_step(self, current_time, step_size):
        x = np.array(
            [[self.T_in, self.P_in, self.mdot, float(self.geom)]], dtype=np.float32
        )
        xn = (x - self.xm) / self.xsd
        yn = self.session.run(None, {"features": xn})[0]
        y = yn * self.ysd + self.ym
        self.Nu_avg = float(y[0, 0])
        self.dp_tot = float(y[0, 1])
        return True
