# Case 03 — Airfoil-Fin Channel (LES Reference)

> **Reference:** docs/02_phase2_cfd_rom.md § 2.5.3
>
> **Why this case matters:** airfoil-fin PCHE channels are the cutting-edge
> geometry developed for next-generation sCO₂ heat exchangers. RANS is
> unreliable for the unsteady wake structure behind each fin row — LES is
> the reference standard.

## Hardware reality

| Hardware | Wall-time |
|----------|-----------|
| 64-core CPU / 128 GB RAM (cloud recommended) | ~3 days |

This case **must not be run on a laptop**. See docs/02 § 2.5.2 for the
recommended cloud workflow (AWS EC2 Spot c6i.4xlarge / Google Cloud Spot).

## Status

🚧 **Skeleton.** All system/ and constant/ dict files will follow case01's
structure with three substitutions:
- `simulationType LES;` in `constant/turbulenceProperties`
- `LESModel WALE;` (or Smagorinsky) in `constant/LESProperties`
- Time-step adapted to CFL ≤ 0.3 with `maxCo 0.3` in `system/controlDict`

The full dict set will land once the cloud-Spot workflow has been validated
on case02 first (see milestone § Phase 2 month 7).
