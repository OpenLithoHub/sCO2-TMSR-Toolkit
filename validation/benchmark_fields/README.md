# Benchmark Field Data

> **Reference:** docs/02_phase2_cfd_rom.md § 2.5
>
> **Storage policy:**
>
> | Size | Where | Retrieval |
> |------|-------|-----------|
> | < 50 MB | Git LFS in this directory | `git lfs pull` |
> | ≥ 50 MB | Zenodo (free, DOI, permanent) | per-release download script + SHA256 checksum |
>
> **GitHub LFS free quota:** 1 GB bandwidth + 1 GB storage per month.
> Once benchmark data starts accumulating, migrate everything > 50 MB to
> Zenodo and keep only the download script + checksum here.

## Provenance

Every file in this directory must have an entry in `data_sources.md`
(one level up — `validation/experimental_data/data_sources.md`) with:

- Originating CFD case (commit hash + case ID)
- Mesh statistics, residuals at convergence
- Software stack (OpenFOAM version, sCO2 thermo class)
- SHA256 checksum

## Status

🚧 Empty. First entry will land after Phase 2 month 5 milestone (case01
converged result published to Zenodo).
