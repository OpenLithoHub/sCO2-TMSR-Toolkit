# Component Reference

> Per-component parameter and equation summary. For background and rationale
> see `docs/03_phase3_modelica.md` in the repository root.

---

## `Components.HeatExchangers.IntermediateHeatExchanger`

Salt → sCO₂ intermediate heat exchanger, NTU-effectiveness counter-flow.

| Parameter              | Default | Unit  | Notes                              |
| ---------------------- | ------- | ----- | ---------------------------------- |
| `UA_design`            | 1.5e6   | W/K   | Calibrate against vendor/CFD data  |
| `Cp_hot` / `Cp_cold`   | 1500 / 1250 | J/(kg·K) | Salt FLiBe / sCO₂ nominal     |
| `mdot_hot` / `mdot_cold`| 25 / 35  | kg/s | Nominal design point               |

Equations: `NTU = UA/C_min`, `eps = (1−exp(−NTU(1−Cr))) / (1−Cr·exp(−NTU(1−Cr)))`,
`Q = eps·C_min·(T_hot_in − T_cold_in)`.

---

## `Components.HeatExchangers.PCHE` (§ 3.3 + § 3.6)

Printed-circuit heat exchanger with a ROM/correlation switch and an ASME
simplified wall-thickness assertion.

| Parameter              | Default  | Unit  | Notes                                     |
| ---------------------- | -------- | ----- | ----------------------------------------- |
| `N_channels`           | 1000     | —     | Number of micro-channels                  |
| `D_ch`                 | 0.002    | m     | Channel hydraulic diameter                |
| `L`                    | 0.6      | m     | HX length                                 |
| `d_wall`               | 0.0015   | m     | Separator wall thickness                  |
| `useROM`               | false    | —     | true → load `ExternalROM/PCHE_ROM_FMU.fmu` |
| `P_hot` / `P_cold`     | 0.5e6 / 20e6 | Pa | Design pressures                          |
| `allowable_stress`     | 110e6    | Pa    | ≈ Inconel 617 at 650 °C; correct from ASME II-D |
| `weld_efficiency`      | 0.85     | —     | Diffusion-bonded PCHE: 0.7–0.85           |
| `enable_asme_check`    | true     | —     | Toggle the wall-thickness assertion       |

ASME formula (thin-wall cylinder, BPVC Section VIII Div.1):
```
t_min = (P · D) / (2·S·E − 1.2·P)
```
The assertion fires at `level = AssertionLevel.warning`; it is **not**
engineering certification (see § 3.6 disclaimer).

---

## `Components.HeatExchangers.TritiumPermeationLayer` (§ 3.5)

Steady-state tritium permeation through a metal wall using Sieverts + Arrhenius.

| Parameter              | Default   | Unit                         | Notes                                |
| ---------------------- | --------- | ---------------------------- | ------------------------------------ |
| `A_wall`               | 50.0      | m²                           | Total wall area                      |
| `d_wall`               | 0.0015    | m                            | Wall thickness                       |
| `Phi_0`                | 2.0e-7    | mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵           | Permeability pre-factor              |
| `E_a`                  | 45e3      | J/mol                        | Activation energy (Inconel 617 typ.) |

Equations: `Φ(T) = Φ₀·exp(−Eₐ/RT)`, `J = (Φ/d)·(√p_hot − √p_cold)`,
`ṁ_T = A_wall · J`.

Inputs: `p_T_hot`, `p_T_cold`, `T_wall`. Output: `mdot_T` (mol/s).

---

## `Components.Turbomachinery.{Compressor, ReCompressor, Turbine}`

Isentropic-efficiency turbomachinery with map-based pressure ratio. See
individual `.mo` files for parameter lists.

---

## `Components.Reactor.MoltenSaltReactor`

Lumped thermal-hydraulic MSR core. Inputs: salt mass flow, inlet temperature.
Outputs: outlet temperature, thermal power.

## `Components.Reactor.ReactorPowerControl`

PI controller — power_setpoint → reactivity command. Tunable proportional and
integral gains.

## `Components.Reactor.OnlineFuellingTransient` (§ 3.7)

Point-kinetics with 6 delayed-neutron groups + lumped core energy balance.

| Parameter            | Default                                                             | Notes                              |
| -------------------- | ------------------------------------------------------------------- | ---------------------------------- |
| `beta_eff`           | 0.003                                                               | TMSR Th-U fuel; verify             |
| `Lambda`             | 1e-4 s                                                              | Prompt neutron generation time     |
| `beta_i[6]`          | U-235 thermal defaults                                              | **Replace with Th-U values**       |
| `lambda_i[6]`        | U-235 thermal defaults                                              | **Replace with Th-U values**       |
| `alpha_T`            | -3.0e-5 1/K                                                         | Negative (stabilizing) for TMSR    |
| `P_thermal_nominal`  | 2 MWth                                                              | TMSR-LF1 design                    |

Reactivity units: `delta_rho_fuelling` is **dimensionless** (Δk/k), not pcm.
Convert with 1 pcm = 1·10⁻⁵. A ±5 pcm refueling batch is ±5·10⁻⁵.

---

## `Components.Valves.{ThrottleValve, BypassValve}`

Isenthalpic throttling: `mdot = Cv · opening · sign(dp) · √|dp|`,
`port_a.h_outflow = inStream(port_b.h_outflow)` (and reverse).

---

## `Cycles.{SimpleRecuperation, RecompressionCycle, TMSR_sCO2_Full}`

Pre-wired cycle topologies that connect the components above. `TMSR_sCO2_Full`
is the canonical integration model used by `Examples/LoadFollowing` and
`Examples/StartupSequence`.

---

## `Media.sCO2`

Placeholder Modelica.Media-compliant medium for sCO₂. Full CoolProp coupling
lands at the Phase 3 month-12 milestone (see `docs/03 § 3.4`).

---

## See also

- [`UserGuide.md`](UserGuide.md) — quick-start, ROM bridge, repository layout.
- `Tests/ValidationTests.mo` — compile-time smoke test (every component must
  instantiate cleanly).
