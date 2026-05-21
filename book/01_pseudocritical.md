---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# 1. The Physics of the sCO₂ Pseudo-Critical Line

## 1.1 Problem statement

Above the critical pressure ($P > 7.38\ \text{MPa}$), CO₂ has no first-order
phase transition — but it still exhibits a sharp peak in specific heat $C_p$
at a specific temperature for each pressure. The locus of these $C_p$ peaks
is called the **pseudo-critical line**.

For sCO₂ Brayton cycles operating at 15–25 MPa, the compressor inlet must
sit *near* this line — but not on it — because the violent property gradient
on the line itself causes numerical instability and unpredictable real-cycle
performance.

## 1.2 Mathematical description

For a fixed pressure $P$ above the critical pressure $P_c$, the
pseudo-critical temperature is the temperature that maximises specific heat:

$$
T_{pc}(P) \;=\; \arg\max_T\; C_p(T, P)
\quad\text{for}\quad P > P_c
$$

The locus $\{(T_{pc}(P), P) : P > P_c\}$ is the pseudo-critical line.

## 1.3 Code implementation

```{code-cell} ipython3
import sys
from pathlib import Path
sys.path.insert(0, str(Path("..").resolve() / "src"))

from sco2_property_explorer import find_pseudocritical_temp

# Pseudo-critical T at three engineering pressures
for P_MPa in (8.0, 15.0, 20.0, 25.0):
    T_pc = find_pseudocritical_temp(P_MPa * 1e6)
    print(f"P = {P_MPa:5.1f} MPa   T_pc = {T_pc - 273.15:6.2f} °C")
```

## 1.4 Numerical validation

```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP

T = np.linspace(300, 400, 400)
fig, ax = plt.subplots(figsize=(9, 5))
for P_MPa in (8, 15, 20, 25):
    Cp = [CP.PropsSI("C", "T", t, "P", P_MPa * 1e6, "CO2") for t in T]
    ax.plot(T - 273.15, np.array(Cp) / 1000, label=f"{P_MPa} MPa")
ax.axvline(31.1, color="red", linestyle="--", alpha=0.4,
           label="Critical T (only at 7.38 MPa)")
ax.set_xlabel("Temperature (°C)")
ax.set_ylabel("Cp (kJ/kg·K)")
ax.set_title("Cp(T) at engineering pressures — peaks shift right with P")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()
```

## 1.5 Engineering implication

Compressor inlet conditions for a sCO₂ cycle should:

- Sit on the **dense (right) side** of the pseudo-critical line — gives the
  highest $\rho$ and lowest compressor work
- Avoid the immediate vicinity of the line itself — $\partial C_p / \partial T$
  is too large for stable mass-flow control
- Track the line as $P$ rises across the cycle — the line is a *locus*, not
  a single point

The white curve in the Streamlit app's "Pseudo-Critical Line" tab is exactly
this locus. Hovering over it gives the operating-point design target.

## 1.6 References

- Span & Wagner (1996), *J. Phys. Chem. Ref. Data* — the EOS underlying CoolProp's CO₂ implementation
- Dostal (2004), MIT thesis MIT-ANP-TR-100 — first full sCO₂ Brayton cycle design study
