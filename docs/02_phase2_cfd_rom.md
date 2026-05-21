# Phase 2 — PCHE CFD Benchmarks & ROM Surrogate

> **Goal:** Build an open-source CFD benchmark library for printed-circuit heat exchangers (PCHE)
> **Independent GitHub repo:** `sCO2-PCHE-Benchmark`
> **Timeline:** Months 4–8

---

## 2.1 Why PCHE Is the Critical Component

```
Heat transfer path in a molten-salt reactor:
Molten salt (700 °C) → [PCHE] → sCO₂ (550 °C, high-pressure side) → Turbine

PCHE characteristics:
- Micro-channel diameter: 0.5–2 mm
- Pressure rating: up to 30 MPa
- Effectiveness: >95% (far exceeds conventional heat exchangers)
- Challenge: sCO₂ property discontinuities near the critical point make the
  heat-transfer coefficient highly unstable
```

## 2.2 Repository Structure

```
sCO2-PCHE-Benchmark/
├── README.md
├── CONTRIBUTING.md
├── .gitignore                        # must exclude OpenFOAM time-step directories (§ 2.5.1)
├── .gitattributes                    # Git LFS configuration (§ 2.5.1)
├── .github/workflows/
├── validation/
│   └── experimental_data/
│       ├── Kim2016_PCHE.csv          # tabulated data from published literature
│       └── data_sources.md          # data provenance and copyright notes (important!)
├── cases/
│   ├── case01_straight_channel/
│   │   ├── 0/                        # OpenFOAM initial conditions
│   │   ├── constant/                 # physical constants (sCO₂ properties)
│   │   ├── system/                   # solver settings
│   │   ├── Allrun
│   │   └── README.md
│   ├── case02_zigzag_channel/
│   └── case03_airfoil_channel/
├── postProcessing/
│   ├── plot_Nu_vs_Re.py
│   └── validate_against_exp.py
├── rom/
│   ├── dataset/
│   ├── train_rom.py
│   └── exported/
└── docs/
    ├── mesh_generation.md
    └── solver_settings.md
```

## 2.3 Key Technical Challenge — sCO₂ Properties in OpenFOAM

OpenFOAM does not support CoolProp natively.
Options: compile a plugin, or use a look-up table (recommended for newcomers).

```bash
# Method A (recommended): use the property LUT generated in Phase 1 (§ 1.7)
python3 tools/export_lut.py   # generates sco2_lut.csv and sco2_lut_openfoam.dat
```

```cpp
// Method B (advanced): write a dedicated sCO₂ thermodynamic class for OpenFOAM
// File: src/thermophysicalModels/specie/thermo/sCO2Thermo/sCO2Thermo.H
// Approach: bilinear interpolation from the look-up table
// This is a good standalone OpenFOAM contribution direction
class sCO2Thermo { ... };
```

## 2.4 Case01 Step-by-Step — Straight-Channel Baseline

```bash
# blockMeshDict key parameters:
# Straight channel: 2 mm diameter, 50 mm length, D-section approximated as rectangular
# Reynolds number range: 1 000–30 000 (covers typical engineering operating points)

blockMesh                  # generate mesh
checkMesh                  # validate mesh quality — must show zero errors
buoyantPimpleFoam          # run solver (with heat transfer)
# or: rhoPimpleFoam (compressible flow)

# Post-processing: extract Nusselt number
postProcess -func 'wallHeatFlux' -latestTime
python3 postProcessing/plot_Nu_vs_Re.py
```

## 2.5 Large Files & Compute — Avoiding "Repository Explosion / Local Machine Death"

Phase 2 is where projects most commonly stall, for two reasons:
1. **OpenFOAM output volume is enormous** — a single PCHE micro-channel case (mesh + time-step fields) can be several GB to tens of GB. Pushing directly to GitHub triggers the 100 MB single-file limit and can get the repository flagged.
2. **Local compute is nowhere near enough** — a laptop running RANS on a micro-channel can take days; LES/DNS is out of the question.

### 2.5.1 Large-File Version Control

**Step 1: use `.gitignore` to exclude the vast majority of intermediate outputs**

```gitignore
# .gitignore template (place at repository root)

# OpenFOAM time-step directories (exclude all except 0/)
cases/*/[1-9]*/
cases/*/processor*/
cases/*/postProcessing/*/[1-9]*/

# Mesh intermediate files
cases/*/constant/polyMesh/*.gz
cases/*/constant/polyMesh/sets/

# Logs and lock files
cases/*/log.*
cases/*/*.foam

# Property table outputs (keep the generation script; exclude the output)
*.lut.dat
sco2_properties_table_full.csv

# Python cache
__pycache__/
*.pyc
.ipynb_checkpoints/

.DS_Store
Thumbs.db
```

**Step 2: use Git LFS for benchmark data that must be retained long-term**

```bash
sudo apt install git-lfs
git lfs install

# Track only "benchmark results" — large but rarely changing
git lfs track "validation/benchmark_fields/*.vtu"
git lfs track "validation/benchmark_fields/*.tar.gz"

git add .gitattributes
git commit -m "Configure Git LFS for benchmark field data"
```

> **GitHub LFS free quota:** 1 GB bandwidth + 1 GB storage per month.
> Beyond this, consider migrating large benchmark data to Zenodo (free, DOI, permanent archive).
> **Recommended:** upload any file >50 MB to Zenodo; keep only a download script and SHA256 checksum in the repo.

**Step 3: consider DVC for tracking data ↔ code version correspondence**

```bash
pip install dvc[s3]
dvc init
dvc remote add -d storage s3://your-bucket/sco2-benchmark

dvc add validation/benchmark_fields/case01_results.vtu
git add validation/benchmark_fields/case01_results.vtu.dvc
git commit -m "Track Case01 benchmark results via DVC"
dvc push
```

### 2.5.2 Cloud Compute Strategy

| Option | Best for | Cost note |
|--------|----------|-----------|
| **AWS EC2 Spot** | Single LES / complex transient run | 60–90% cheaper than on-demand; may be preempted — write checkpoints |
| **Google Cloud Spot VM** | Same as above | Similar to AWS Spot |
| **University HPC trial account** | Long-term academic cases | Usually free; suitable for Phase 3 cycle dynamics |
| **National supercomputer allocation** | High-priority projects | China: USTC, Shanghai SC, Qinghai SC — public application channels available |
| **Google Colab + Docker** | Teaching demos and small cases | Free; OpenFOAM deployment complex; demo use only |

```bash
# Typical workflow for OpenFOAM on AWS EC2 Spot (c6i.4xlarge, ~$0.20/hr spot)
sudo apt update && sudo apt install -y openfoam11
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit.git
cd sCO2-TMSR-Toolkit
git lfs pull --include="cases/case01_straight_channel/**"
cd cases/case01_straight_channel && ./Allrun
# After completion: sync key results to S3 or Zenodo, then terminate the instance
```

### 2.5.3 Reproducibility Notice in README

```markdown
## Reproducibility

| Case | Recommended hardware | Estimated wall time |
|------|---------------------|---------------------|
| Case01 straight-channel RANS | 8-core CPU / 16 GB RAM | ~2 hours |
| Case02 zigzag-channel RANS | 16-core CPU / 32 GB RAM | ~8 hours |
| Case03 airfoil-channel LES | 64-core CPU / 128 GB RAM (cloud recommended) | ~3 days |

Full benchmark data (field snapshots, convergence history) available at [Zenodo DOI: xxx](https://zenodo.org/...).
```

---

## 2.6 CFD-Driven Reduced-Order Model (ROM / Surrogate)

> **Prerequisites:** complete Case01 (§ 2.4) and at least one Case02 steady-state run,
> accumulating at least 200 converged results across different operating conditions.
> Training on fewer samples produces a model with false precision — worse than Gnielinski.
>
> **Difficulty:** High. Requires intersection of ML tooling and CFD data processing.
> Recommended window: months 6–8, overlapping the tail of Phase 2.

### 2.6.1 Why a ROM Is Needed

```
Classical approach: use Gnielinski correlation (Nu = f(Re, Pr)) for convective heat transfer
Reality: Gnielinski is strictly valid for smooth circular tubes only.
         For PCHE zigzag and airfoil channels:
         - Flow is periodically disturbed, separated, and reattached
         - Near-critical sCO₂ property changes overlap with geometric effects
         - Multiple published papers document "significant" deviation for these geometries
```

The engineering solution: replace Gnielinski in the system simulation with
a surrogate trained on CFD data. Re-running CFD at every time step is impossible
(one steady-state case takes hours), so the surrogate must return results in milliseconds.

> **Honest boundary:** ROM accuracy is bounded by training-data coverage.
> A ROM is not a universal replacement — it packages "the operating space already computed by CFD"
> into a fast callable function. Out-of-distribution inputs must trigger an explicit warning.

### 2.6.2 Data Extraction

```python
# File: rom/dataset/extract_from_cfd.py
# Batch-parse OpenFOAM converged steady-state results.
# Input features:  T_in, P_in, mass_flow, geometry_id (straight=0, zigzag=1, airfoil=2)
# Output labels:   avg_Nu_overall, total_pressure_drop_Pa

import numpy as np
import pandas as pd
from pathlib import Path


def parse_case(case_dir: Path):
    with open(case_dir / '0' / 'U') as f:
        T_in = ...   # parse from boundaryField
        u_in = ...
    with open(case_dir / '0' / 'p') as f:
        P_in = ...

    nu_file = case_dir / 'postProcessing' / 'wallHeatFlux' / 'latest' / 'wallHeatFlux.dat'
    Nu_avg = compute_avg_Nu_from_heatflux(nu_file)

    dp_file = case_dir / 'postProcessing' / 'pressureDifference' / 'latest' / 'pd.dat'
    dp_total = float(open(dp_file).readlines()[-1].split()[-1])

    geom_map = {'straight': 0, 'zigzag': 1, 'airfoil': 2}
    geom_id = geom_map[case_dir.parent.name.split('_')[1]]

    return {
        'T_in_K': T_in, 'P_in_Pa': P_in,
        'mass_flow_kg_s': u_in * area * rho_in,
        'geometry_id': geom_id,
        'Nu_avg': Nu_avg, 'dp_total_Pa': dp_total,
    }


def collect_all(cases_root='cases/'):
    rows = []
    for case in Path(cases_root).glob('case*/run_*'):
        try:
            rows.append(parse_case(case))
        except Exception as e:
            print(f'⚠ Skipping {case}: {e}')
    df = pd.DataFrame(rows)
    df.to_csv('rom/dataset/training_set.csv', index=False)
    print(f'✅ Extracted {len(df)} samples')
    return df
```

> **Recommended data scale:** at least 50–100 converged results per channel geometry,
> 200+ samples total. Cover the engineering T/P range (T_in: 305–823 K, P_in: 7.5–25 MPa, ṁ: 0.05–0.5 kg/s).

### 2.6.3 Training a Lightweight Surrogate

Deliberately choose the **simplest, most transparent** approach.

```python
# File: rom/train_rom.py
# A 3-hidden-layer MLP mapping (T_in, P_in, mass_flow, geom_id) → (Nu_avg, dp_total)
#
# Design choice rationale:
#   - Not GP/Kriging: slow to train once samples exceed a few hundred
#   - Not XGBoost: harder to export as ONNX/FMU for embedding in Modelica
#   - Neural network: fast inference + straightforward ONNX export

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('rom/dataset/training_set.csv')
X = df[['T_in_K', 'P_in_Pa', 'mass_flow_kg_s', 'geometry_id']].values
y = df[['Nu_avg', 'dp_total_Pa']].values

xs, ys = StandardScaler(), StandardScaler()
Xn, yn = xs.fit_transform(X), ys.fit_transform(y)
X_train, X_val, y_train, y_val = train_test_split(Xn, yn, test_size=0.2, random_state=42)


class PCHE_ROM(nn.Module):
    def __init__(self, in_dim=4, out_dim=2, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, out_dim),
        )
    def forward(self, x):
        return self.net(x)


model = PCHE_ROM()
opt   = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-5)
loss_fn = nn.MSELoss()

Xt = torch.tensor(X_train, dtype=torch.float32)
yt = torch.tensor(y_train, dtype=torch.float32)
Xv = torch.tensor(X_val,   dtype=torch.float32)
yv = torch.tensor(y_val,   dtype=torch.float32)

for epoch in range(2000):
    model.train()
    loss = loss_fn(model(Xt), yt)
    opt.zero_grad(); loss.backward(); opt.step()
    if epoch % 200 == 0:
        model.eval()
        with torch.no_grad():
            val_loss = loss_fn(model(Xv), yv).item()
        print(f'Epoch {epoch:4d} | train={loss.item():.5f} val={val_loss:.5f}')

model.eval()
with torch.no_grad():
    pred_val = ys.inverse_transform(model(Xv).numpy())
true_val  = ys.inverse_transform(y_val)
mape_Nu = np.mean(np.abs((pred_val[:,0]-true_val[:,0]) / true_val[:,0])) * 100
mape_dp = np.mean(np.abs((pred_val[:,1]-true_val[:,1]) / true_val[:,1])) * 100
print(f'Validation MAPE: Nu_avg = {mape_Nu:.2f}%, dp_total = {mape_dp:.2f}%')

np.savez('rom/exported/scalers.npz',
         x_mean=xs.mean_, x_scale=xs.scale_,
         y_mean=ys.mean_, y_scale=ys.scale_)

dummy = torch.randn(1, 4)
torch.onnx.export(model, dummy, 'rom/exported/pche_rom.onnx',
                  input_names=['features'], output_names=['Nu_dp'],
                  dynamic_axes={'features': {0: 'batch'}},
                  opset_version=17)
print('✅ ONNX exported: rom/exported/pche_rom.onnx')
```

#### 2.6.3a Optional Extension — Physics-Informed Loss (v1.4)

This is an optional enhancement, not a requirement for the base ROM.
The idea: add an energy-balance penalty term to the training loss
so predictions are penalized when they violate macroscopic conservation.

**Important framing:** this is **not** a full Physics-Informed Neural Network (PINN).
Full PINNs embed PDE residuals (e.g., Navier-Stokes at every collocation point).
What follows is a simpler "physics-informed loss" that penalizes gross energy-balance violations
at the channel level — useful but more modest.

```python
# Add to train_rom.py after defining loss_fn

import CoolProp.CoolProp as CP

def energy_balance_penalty(T_in, P_in, mdot, Nu_pred, dp_pred,
                            D_ch=0.002, L=0.6, N_ch=1000,
                            T_wall=None):
    """
    Penalize predictions that violate the channel energy balance:
      Q_conv = h * A_s * (T_wall - T_bulk)  should be consistent with mdot * Cp * dT

    This is a soft constraint — it guides training, not a hard physical solver.
    Only apply when T_wall estimates are available from CFD post-processing.
    If T_wall data is unavailable, skip this penalty.
    """
    if T_wall is None:
        return torch.tensor(0.0)

    # Fluid properties at inlet (detach from graph — used as constants)
    with torch.no_grad():
        try:
            k = CP.PropsSI('L', 'T', float(T_in.mean()), 'P', float(P_in.mean()), 'CO2')
            Cp = CP.PropsSI('C', 'T', float(T_in.mean()), 'P', float(P_in.mean()), 'CO2')
        except Exception:
            return torch.tensor(0.0)

    h_conv  = Nu_pred * k / D_ch
    A_surf  = torch.tensor(np.pi * D_ch * L * N_ch, dtype=torch.float32)
    dT_wall = T_wall - T_in
    Q_conv  = h_conv * A_surf * dT_wall
    Q_fluid = mdot * Cp * dT_wall   # approximate; assumes uniform dT

    penalty = torch.mean((Q_conv - Q_fluid) ** 2) / (Q_fluid.detach() ** 2 + 1e-8).mean()
    return penalty

# In the training loop, replace:
#   loss = loss_fn(model(Xt), yt)
# with:
#   pred = model(Xt)
#   data_loss = loss_fn(pred, yt)
#   phys_loss = energy_balance_penalty(
#       T_in=Xt[:,0], P_in=Xt[:,1], mdot=Xt[:,2],
#       Nu_pred=pred[:,0], dp_pred=pred[:,1],
#       T_wall=T_wall_tensor)   # requires T_wall in training data
#   lambda_phys = 0.05          # tune: too large → fights data; too small → no effect
#   loss = data_loss + lambda_phys * phys_loss
```

**When does this actually help?**
- Training data is sparse in a physically important region (near pseudo-critical T)
- The MLP has started over-fitting individual cases

**When does it hurt or add noise?**
- T_wall estimates are inaccurate (common in early CFD post-processing)
- `lambda_phys` is set too high, fighting the data loss

**Recommendation:** run the baseline MLP first (§ 2.6.3). Add the penalty only if
validation MAPE is >10% and you have reliable T_wall data from CFD.

### 2.6.4 Wrap as FMU for Modelica

```python
# File: rom/exported/wrap_as_fmu.py
# Tools: pythonfmu (FMI 2.0, stable) or pythonfmu3 (FMI 3.0, experimental)
#
# FMI version note (v1.4):
#   FMI 2.0 is the safe default — well-supported in OpenModelica, Dymola, fmpy.
#   FMI 3.0 (released 2023) is supported by Dymola and pythonfmu3,
#   but OpenModelica's FMI 3.0 export/import is still incomplete as of 2025.
#   Use FMI 3.0 only if your workflow is Dymola-based or Python-only (fmpy).

from pythonfmu import Fmi2Causality, Fmi2Slave, Real, Integer
import onnxruntime as ort
import numpy as np, os

class PCHE_ROM_FMU(Fmi2Slave):
    author      = "your-name"
    description = "PCHE ROM trained on OpenFOAM CFD data (sCO₂)"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.T_in = 305.4; self.register_variable(Real("T_in", causality=Fmi2Causality.input))
        self.P_in = 8e6;   self.register_variable(Real("P_in", causality=Fmi2Causality.input))
        self.mdot = 0.1;   self.register_variable(Real("mdot", causality=Fmi2Causality.input))
        self.geom = 1;     self.register_variable(Integer("geom", causality=Fmi2Causality.input))
        self.Nu_avg = 0.0; self.register_variable(Real("Nu_avg", causality=Fmi2Causality.output))
        self.dp_tot = 0.0; self.register_variable(Real("dp_tot", causality=Fmi2Causality.output))

        here = os.path.dirname(__file__)
        self.session = ort.InferenceSession(os.path.join(here, "pche_rom.onnx"))
        sc = np.load(os.path.join(here, "scalers.npz"))
        self.xm, self.xs = sc['x_mean'], sc['x_scale']
        self.ym, self.ysd = sc['y_mean'], sc['y_scale']

    def do_step(self, current_time, step_size):
        x  = np.array([[self.T_in, self.P_in, self.mdot, self.geom]], dtype=np.float32)
        xn = (x - self.xm) / self.xs
        yn = self.session.run(None, {'features': xn})[0]
        y  = yn * self.ysd + self.ym
        self.Nu_avg, self.dp_tot = float(y[0,0]), float(y[0,1])
        return True

# Build: pythonfmu build -f wrap_as_fmu.py
# Output: PCHE_ROM_FMU.fmu  — drop into the Phase 3 Modelica project
```

### 2.6.5 ROM Accuracy Declaration (mandatory)

```markdown
## ROM Applicability & Accuracy

| Dimension | Training data coverage | Out-of-range behavior |
|-----------|----------------------|----------------------|
| T_in | 305–823 K | Must not extrapolate |
| P_in | 7.5–25 MPa | Must not extrapolate |
| mass_flow | 0.05–0.5 kg/s | Must not extrapolate |
| Geometry | straight, zigzag, airfoil (one typical size each) | Other geometries require retraining |

**Validation-set MAPE:** Nu_avg ≈ X%, dp_total ≈ Y% (fill in after actual training)

**Known limitations:**
- Training data is RANS (k-ω SST) only — no LES high-fidelity data; under-predicts fluctuation-dominated regimes
- Two-phase region excluded from training data
- Geometry is a discrete variable — cannot interpolate to new channel shapes
```

---

*← Back to [Phase 1](01_phase1_properties.md) | Next: [Phase 3 — Modelica →](03_phase3_modelica.md)*
