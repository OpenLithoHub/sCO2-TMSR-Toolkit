# Data Acquisition Log

> **Purpose:** track every public-report acquisition attempt this project
> makes, so the data pipeline is reproducible and credit/blame for any
> sourced number is auditable. Companion file to `docs/citation_protocol.md`.
>
> **Scope:** only sources we plan to *transcribe values from* — not every
> paper we read. If a source is on this log, it is on track to become a
> `references.bib` entry plus a `docs/data_extracts/<key>.md`.

---

## Acquisition policy

For each candidate source:

1. **Try direct fetch first** (`curl -L -o ...` against the canonical URL —
   OSTI, NASA-TR, DOI publisher landing).
2. **If direct fetch fails** (403 / 404 / SSL / timeout), retry once via
   a local HTTP proxy if one is available
   (`curl --proxy http://<your-local-proxy>:<port> ...`).
3. **If proxy also fails**, mark `blocked`, record the HTTP status or
   error, and move on. Do not retry in a tight loop.
4. **On success**, save the PDF to `~/Downloads/` (do **not** commit it
   to the repo — citation_protocol.md § 7), then create the
   `docs/data_extracts/<key>.md` extract document and add the BibTeX
   entry to `docs/references.bib` *before* transcribing any numbers.
5. **Record everything below** — even failures. A blocked source today
   may be reachable tomorrow; the log is the only audit trail.

PDFs themselves are **never** committed to this repo. Only extract
documents and BibTeX entries cross the repo boundary.

---

## Status legend

| Status | Meaning |
|---|---|
| `pending`     | not yet attempted |
| `downloaded`  | PDF on local disk; extract doc not yet started |
| `extracted`   | `docs/data_extracts/<key>.md` exists with at least one entry |
| `transcribed` | at least one row in a benchmark CSV references this source |
| `blocked`     | direct + proxy both failed; documented and skipped |
| `skipped`     | deliberately deprioritised (low ROI vs. effort) |

---

## Candidate source table

Sources are ordered by acquisition priority (highest first). Priority
is set by:

1. how directly the source feeds an existing CSV / case / Modelica file,
2. how unique the data is (replaceable vs. irreplaceable),
3. legal accessibility (US gov reports first, then open journals,
   commercial publishers last).

| # | BibTeX key | Title (short) | Canonical URL | Priority | Status | Last attempt | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `SpanWagner1996_CO2_EOS` | Span & Wagner CO₂ reference EOS, *J. Phys. Chem. Ref. Data* 25(6) 1509 | https://doi.org/10.1063/1.555991 | P0 | **blocked** | 2026-05-21 | AIP publisher behind Cloudflare WAF; both direct + proxy return 403. Re-attempt via institutional access or NIST Standard Reference Data instead. |
| 2 | `Vrancik1968_NASA_TN_D4849` | Prediction of windage power loss in alternators, NASA TN D-4849 | https://ntrs.nasa.gov/citations/19680027690 | P0 | **downloaded** | 2026-05-21 | NTRS direct. 749 KB / 21 pages. EOF verified. |
| 3 | `Wright2011_SAND2010_8840` | Wright, Radel, Conboy, Rochau — Modeling and Experimental Results for Condensing sCO2 Power Cycles, SAND2010-8840 | https://www.osti.gov/biblio/1030354 | P0 | **extracted** | 2026-05-22 | OSTI biblio 1030354 in fact dereferences to SAND2010-8840 (Jan 2011 LDRD, condensing cycles for LWRs), not SAND2011-7779 ("Overview…") which was the original mis-keyed entry. PDF on disk; first-pass extract done — see `wright2011_sand2010-8840.md`. |
| 4 | `Conboy2014_SAND2014_2098` | Conboy et al., Performance Characteristics of an Operating sCO2 Brayton Cycle, SAND2014-2098 | https://www.osti.gov/biblio/1177045 | P0 | **blocked** | 2026-05-22 | **Source-identity error (2026-05-22):** PDF at OSTI 1177045 is in fact SAND2014-3136 *"Effects of Increasing Tip Velocity on Wind Turbine Rotor Design"* by Resor/Maniaci/Berg/Richards — NOT a sCO₂ paper. Original 2026-05-21 row keyed the OSTI biblio ID 1177045 to a Conboy/Wright/Pasch sCO₂ title borrowed from a separate cite. OSTI search API queries (`Conboy+Wright+Pasch`, `Conboy+Pasch+Brayton+SAND2014`, `Conboy+sCO2+Brayton+performance+characteristics`) return no public Conboy/Wright/Pasch publication with that title — likely an ASME Turbo Expo or non-OSTI conference paper. BibTeX key retired in `docs/references.bib`; extract doc rewritten as a retirement notice; downstream cites (Gap 1, Gap 5, 00_strategy.md, 01_phase1_properties.md) cleaned up. Local PDF deleted (wind-turbine report, not useful here). Future genuine Conboy/Wright/Pasch sCO₂ acquisition will use a *new* BibTeX key (e.g., `Conboy2014_ASME_GT2014`). |
| 5 | `Conboy2012_LDRD_10MWe` | Conboy et al., Modeling of a sCO2 Power Cycle for Nuclear Energy Applications, SAND/LDRD 2012 | search OSTI: `Conboy 10 MWe recompression sCO2` | P1 | **blocked** | 2026-05-21 | No matching OSTI biblio entry found by author/topic search. Likely SNL-internal LDRD that was never publicly released; supersede with Conboy2014 + later post-2018 OSTI biblio (`1574791`, `1543307`) which cover the 10 MWe cycle modeling work. |
| 6 | `Dostal2004_MIT_PhD` | V. Dostal, A Supercritical CO₂ Cycle for Next Generation Nuclear Reactors, MIT PhD thesis 2004 | https://web.mit.edu/22.33/www/dostal.pdf | P1 | **downloaded** | 2026-05-22 | MIT DSpace canonical (`dspace.mit.edu/handle/1721.1/17746`) returns CloudFront WAF 405 captcha; recovered via `web.mit.edu/22.33/www/dostal.pdf` + local HTTP proxy + curl `-C -` resume. 6.6 MB. EOF verified. |
| 7 | `Kim2014_NED_PCHE` | Kim, Lee, Kim, Cha, *Nucl. Eng. Des.* 270 (2014) 73–81 | https://doi.org/10.1016/j.nucengdes.2014.01.006 | P1 | **blocked** | 2026-05-21 | Elsevier sciencedirect paywall via `linkinghub`. Open-access version not found on author webpage. Substitute candidate: any NRELOSTI numerical-investigation paper on PCHE zigzag channels. Re-attempt via institutional access. |
| 8 | `Held2025_BYU_pilot` | Extended Duration Operation of a Pilot-Scale sCO₂ Test Loop (BYU/Echogen 1.26 MWth pilot, San Rafael Energy Research Center) | https://www.osti.gov/biblio/2575689 | P2 | **transcribed** | 2026-05-22 | Originally logged as `Allison2025_STEP_extended` on the assumption it was a substitute for the unreleased DOE STEP Phase 1 final report. Source-identity correction 2026-05-22: paper is in fact the BYU/Echogen pilot (DOE FE award DE-FE0031928), not STEP. BibTeX key + extract doc + CSV all renamed. Table 2 transcribed into `BYU_pilot_data.csv`; CoolProp enthalpy agrees with paper h to ≤ 0.03 % at all 10 state points. |
| 9 | `Galvas1973_NASA_TN_D7487` | Galvas, Centrifugal compressor design code (CCODP), NASA TN D-7487 | https://ntrs.nasa.gov/citations/19730019918 | P3 | pending | — | Indirect cite. NASA-TR — should follow the same NTRS API path that worked for Vrancik. Defer until ROM physical constraints become a near-term task. |
| 10 | `Ngo2007_ETFS_PCHE` | Ngo et al., *Exp. Therm. Fluid Sci.* 32 (2007) 560–570 | https://doi.org/10.1016/j.expthermflusci.2007.06.006 | P3 | pending | — | Elsevier paywall expected; bundle attempt with future Kim2014 retry. |
| 11 | `Humrickhouse2012_INL_EXT_11_23265` | Humrickhouse et al., Tritium Permeability of Incoloy 800H and Inconel 617, INL/EXT-11-23265 Rev.1 | https://www.osti.gov/biblio/1056010 | P0 | **extracted** | 2026-05-22 | OSTI direct purl/1056010, 2.27 MB, EOF verified. Anchors Gap 4 Worst/Best Inconel 617 envelope (Table 1 p.13 ref [11] + § 4 conclusions p.43). Originally pursued via Causey SAND2008-1141 — that report not publicly indexed by OSTI search API; Humrickhouse2012 substituted as the primary US-public source. |
| 12 | `Calderoni2010_INL_EXT_10_19387` | Calderoni & Ebner, Hydrogen Permeability of Incoloy 800H, Inconel 617, and Haynes 230, INL/EXT-10-19387 | https://www.osti.gov/biblio/989876 | P1 | **downloaded** | 2026-05-22 | OSTI direct purl/989876, 2.79 MB, EOF verified. Companion to Humrickhouse2012; held as cross-check for the Worst-case Inconel 617 envelope. Cover-page-only read-through 2026-05-22; values not yet transcribed. |

Ordering rule: P0 sources unblock CSV transcription work in flight; P1
unblocks the next `case0X` or Modelica milestone; P2 are nice-to-haves.

---

## Attempt records

For each acquisition attempt, append a section here. **Do not edit
prior records** — append a new attempt with a fresh date. The history
is the audit trail.

Template:

```markdown
### YYYY-MM-DD — `BibTeXKey`

- **Method:** direct | proxy | manual-browser
- **Command / URL:** `curl -L -o ~/Downloads/<key>.pdf <url>`
- **Outcome:** success (NN MB, NN pages) | HTTP 403 | timeout | redirect to login wall
- **Next action:** extract started | retry with proxy | mark blocked | ask user for institutional access
```

---

<!-- attempt records appended below -->

### 2026-05-21 — `Vrancik1968_NASA_TN_D4849`

- **Method:** direct (no proxy)
- **Command / URL:** `curl -L --max-time 120 -o ~/Downloads/Vrancik1968_NASA_TN_D4849.pdf "https://ntrs.nasa.gov/api/citations/19680027690/downloads/19680027690.pdf"`
- **Outcome:** success (749 014 bytes, 21 pages, %%EOF present)
- **Note:** the original biblio ID guessed from the OSTI extract (`19680025815`) was wrong; the correct NTRS submission ID was `19680027690`, found via NTRS search API `q=Vrancik+windage`.
- **Next action:** stub `docs/data_extracts/vrancik1968_nasa-tn-d4849.md` created; full read-through pending.

### 2026-05-21 — `Wright2011_SAND2011_7779`

- **Method:** direct (after HTTP/2 connection-drop on first attempt)
- **Command / URL:** `curl -L --http1.1 --max-time 600 -o ~/Downloads/Wright2011_SAND2011_7779.pdf "https://www.osti.gov/servlets/purl/1030354"`
- **Outcome:** success on third attempt (4 628 017 bytes = full content-length, %%EOF present)
- **Note:** OSTI's HTTP/2 frontend dropped the stream twice mid-transfer. Forcing `--http1.1` resolved it.
- **Next action:** stub `docs/data_extracts/wright2011_sand2011-7779.md` created.

### 2026-05-21 — `Conboy2014_SAND2014_2098`

- **Method:** direct
- **Command / URL:** `curl -L --http1.1 --max-time 600 -o ~/Downloads/Conboy2014_SAND2014_2098.pdf "https://www.osti.gov/servlets/purl/1177045"`
- **Outcome:** success first attempt (2 774 899 bytes, %%EOF present).
- **Next action:** stub `docs/data_extracts/conboy2014_sand2014-2098.md` created.

### 2026-05-21 — `Conboy2012_LDRD_10MWe`

- **Method:** direct (OSTI v1 records search API)
- **Command / URL:** `https://www.osti.gov/api/v1/records?q=Conboy+supercritical+CO2+recompression`, `Conboy+sandia+2012+supercritical+CO2`, etc.
- **Outcome:** **no match.** No SAND2012-* entry by Conboy on supercritical-CO₂ topics is publicly indexed by OSTI. Manual probing of nearby biblio IDs (1054754, 1059786) returned unrelated reports.
- **Next action:** mark blocked. Use `Conboy2014_SAND2014_2098` plus later modeling-only OSTI entries (e.g. `1574791` "Dynamic Modeling and Control of a 10 MWe sCO₂ RCBC", 2019) as functional substitutes. Add to candidate-source table when one of those becomes the primary cite.

### 2026-05-21 — `SpanWagner1996_CO2_EOS`

- **Method:** direct then attempted proxy
- **Command / URL:** `curl -sIL "https://doi.org/10.1063/1.555991"` → 302 to `pubs.aip.org/jpr/article/.../A-New-Equation-of-State-for-Carbon-Dioxide` → 403 (Cloudflare WAF block).
- **Outcome:** **blocked.** AIP publisher gates the page behind Cloudflare; even DOI resolver redirects through the same WAF.
- **Next action:** alternative — NIST Standard Reference Data (SRD 23 / REFPROP documentation) tabulates Span-Wagner reference values as A-grade ground-truth without requiring the original paper. Defer paper acquisition to institutional-library route. The repo's CoolProp self-consistency CSV (`coolprop_self_consistency.csv`) covers the regression-detection use case in the meantime.

### 2026-05-21 — `Kim2014_NED_PCHE`

- **Method:** direct
- **Command / URL:** `curl -sIL "https://doi.org/10.1016/j.nucengdes.2014.01.006"` → 302 to `linkinghub.elsevier.com/retrieve/pii/S0029549314000302` → 200 landing page (PDF behind subscription).
- **Outcome:** **blocked** at full-text retrieval. Landing page accessible but PDF requires Elsevier subscription.
- **Next action:** retry via institutional access. Until then, `cases/case02_zigzag_channel` will continue to use the geometry already cited from this paper (no quantitative numbers transcribed yet, so the paywall does not block existing CI).

### 2026-05-22 — `Dostal2004_MIT_PhD`

- **Method:** direct (failed multiple times) → proxy + `-C -` resume
- **Commands attempted:**
  1. `curl https://dspace.mit.edu/handle/1721.1/17746` → HTTP/2 405 (CloudFront WAF captcha).
  2. `curl https://web.mit.edu/22.33/www/dostal.pdf` → HTTP/2 200 but stream truncated at ~1.7 MB / 6.6 MB (server resets connection ~14 minutes in).
  3. Same URL via a local HTTP proxy with `--http1.1 -C - --retry 5` → also truncated.
  4. Direct retry the next day with `--http1.1 --proxy http://<your-local-proxy>:<port> -C -` → completed in a single 6.6 MB transfer (full content-length, %%EOF present).
- **Outcome:** success after the per-day rate limit on the MIT host cleared.
- **Next action:** stub `docs/data_extracts/dostal2004_mit-phd.md` created.

### 2026-05-22 — `Allison2025_STEP_extended` (STEP substitute)

- **Method:** direct (failed) → proxy + `-C -` resume across many attempts
- **Command:** `curl -L --http1.1 --max-time 600 --connect-timeout 30 --proxy http://<your-local-proxy>:<port> -C - "https://www.osti.gov/servlets/purl/2575689"` — invoked 12 times with the resume flag accumulating bytes.
- **Outcome:** success after 12 attempts. Final size 15 246 152 bytes (= server `Content-Length`), %%EOF present.
- **Note:** the OSTI server reproducibly drops connections after 1–5 MB even via proxy, but `-C -` (HTTP Range resume) makes progress monotonic.
- **Next action:** stub `docs/data_extracts/allison2025_step_extended.md` created. STEP Phase 1 final report remains unreleased; this conference paper is the cite-of-record until DOE publishes.

### 2026-05-22 — `Wright2011_SAND2011_7779` → `Wright2011_SAND2010_8840` (source-identity correction)

- **Method:** read-through verification of the PDF cover and metadata,
  cross-checked against OSTI biblio 1030354.
- **Command / URL:**
  `curl -sL "https://www.osti.gov/biblio/1030354" | grep citation_technical_report_number`
  → `<meta name="citation_technical_report_number" content="SAND2010-8840" />`
- **Outcome:** the PDF previously logged on 2026-05-21 as
  `Wright2011_SAND2011_7779` ("Overview of Supercritical CO2 Power
  Cycle Development at Sandia") is in fact **SAND2010-8840**
  ("Modeling and Experimental Results for Condensing Supercritical
  CO2 Power Cycles", S. A. Wright, R. F. Radel, T. M. Conboy, G. E.
  Rochau, January 2011). The OSTI biblio ID 1030354 was correct on
  the row; the title/SAND number entered alongside it were wrong —
  pulled from a different SNL Wright-et-al. report. The previous
  attempt record (above) is preserved per § 5 ("never edit prior
  records"); this entry is the correction.
- **Next action:**
  - BibTeX key updated `Wright2011_SAND2011_7779` →
    `Wright2011_SAND2010_8840` in `docs/references.bib`.
  - Extract stub renamed `wright2011_sand2011-7779.md` →
    `wright2011_sand2010-8840.md`; first-pass content (Table 2-1,
    §1.2 fluid densities, §2.2 Table 2-1 14-state-point block, §4 /
    Table 4-1 pointer, §5 test-results overview) added.
  - SAND2011-7779 ("Overview…") remains a *separate* candidate
    source — not yet acquired. Add as a new row to the candidate
    table when its OSTI ID is determined.
  - Future acquisitions: `curl … | grep
    citation_technical_report_number` *before* committing the
    BibTeX entry. Would have caught the original mis-key in seconds.

### 2026-05-22 — `Allison2025_STEP_extended` → `Held2025_BYU_pilot` (source-identity correction)

- **Method:** first-pass read-through of the PDF (pages 1–10, all
  tables) on 2026-05-22.
- **Outcome:** the paper previously logged on 2026-05-22 as
  `Allison2025_STEP_extended` and treated as a substitute citation
  for the unreleased DOE STEP Phase 1 final report is in fact a
  separate work: **T. J. Held et al., "Extended Duration Operation
  of a Pilot-Scale Supercritical CO₂ Test Loop", ASME GT2025-152150,
  Memphis TN, June 2025**. It describes the **BYU/Echogen 1.26 MWth
  pilot at the San Rafael Energy Research Center** (DOE FE award
  `DE-FE0031928`), not the Southwest Research Institute–led 10 MWe
  STEP demonstration. STEP and the BYU pilot are two distinct
  DOE-funded sCO₂ pilot programmes.
- **Detection trigger:** the PDF cover page lists Held + 7 BYU /
  Echogen / SRERC co-authors (no Allison), the DOE acknowledgement
  cites award `DE-FE0031928` (a BYU project), and the system
  schematic in Figure 3 / Table 2 describes a 5.5 kg/s 1.26 MW
  loop, not a 10 MWe STEP-class system. None of the four
  cross-checks reaches the same conclusion as the OSTI biblio
  metadata, which used "Allison" as a generic conference-paper
  authorship tag.
- **Next action:**
  - BibTeX key updated `Allison2025_STEP_extended` →
    `Held2025_BYU_pilot` in `docs/references.bib`; full author list
    + venue + DOE award number added.
  - Extract stub renamed `allison2025_step_extended.md` →
    `held2025_byu_pilot.md`; replaced "stub — read-through pending"
    with full Table 1 / 2 / 3 transcription and topology /
    operations / pump notes.
  - CSV renamed `STEP_phase1_data.csv` (header-only placeholder)
    → `BYU_pilot_data.csv` (6 component-pair rows transcribed
    from Table 2). Independent transcription confidence comes from
    a CoolProp enthalpy cross-check: H('T', T, 'P', P, CO2) agrees
    with the paper's tabulated h to ≤ 0.03 % at all 10 state
    points.
  - Three repo-wide doc updates in the same change set:
    `docs/known_gaps.md` Gap 5 rewritten; `docs/01_phase1_properties.md`
    § 1.6 STEP/BYU split; `validation/experimental_data/data_sources.md`
    BYU section added with row tags + correction note.
  - Future STEP Phase 1 final, when released, will get a *new*
    BibTeX key and a *new* `STEP_phase1_data.csv`. Do **not**
    back-fill BYU pilot rows under that filename.

### 2026-05-22 — `Humrickhouse2012_INL_EXT_11_23265` + `Calderoni2010_INL_EXT_10_19387` (Gap 4 anchor swap)

- **Method:** OSTI search API + direct PDF fetch (no proxy needed).
- **Background:** Gap 4 (Tritium permeation envelope in
  `TritiumPermeationLayer.mo`) originally cited Causey et al.
  *Tritium Barriers and Permeation* SAND2008-1141 + Forcey 1988
  *J. Nucl. Mater.* as the literature anchor. Causey SAND2008-1141 is
  **not publicly indexed by the OSTI search API** (queried with
  `Causey+tritium+barriers+permeation`, `Causey+Karnesky+Cowgill+SAND2008`,
  `Tritium Barriers and Tritium Diffusion`, `report_number=SAND2008-1141`
  — no matches). Forcey 1988 is paywalled at *J. Nucl. Mater.* without
  an open-access mirror. **Substituted** as the primary anchor with
  the OSTI-indexed INL pair below — both directly measure Inconel 617
  hydrogen / tritium permeability with the same experimental apparatus.
- **Commands:**
  - `curl -L --http1.1 --max-time 300 -o ~/Downloads/Hu2011_INL_INL-EXT-11-23265.pdf "https://www.osti.gov/servlets/purl/1056010"` — 2 265 232 bytes, %%EOF verified.
  - `curl -L --http1.1 --max-time 300 -o ~/Downloads/Stutzke2010_INL_INL-EXT-10-19387.pdf "https://www.osti.gov/servlets/purl/989876"` — 2 787 172 bytes, %%EOF verified.
- **Outcome:** both PDFs on disk, both single-shot direct, no proxy
  needed. Humrickhouse2012 single-pass read-through (cover, body
  pp.10–47, Appendix B); cover-page-only for Calderoni2010 (held as
  cross-check, values not transcribed).
- **Next action:**
  - BibTeX entries `Humrickhouse2012_INL_EXT_11_23265` and
    `Calderoni2010_INL_EXT_10_19387` added.
  - Extract documents `humrickhouse2012_inl-ext-11-23265.md` (full)
    and `calderoni2010_inl-ext-10-19387.md` (index-only) created.
  - `TritiumPermeationLayer.mo` Worst defaults updated to
    Φ₀=7.04e-6 mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵, Eₐ=89.1 kJ/mol (Humrickhouse Table 1
    p.13 ref [11], unit conversion ÷7.66e4 + 1 kcal/mol = 4.184 kJ/mol).
    Best defaults updated to Φ₀=7.04e-8, Eₐ=89.1 kJ/mol per § 4
    conclusions p.43 ("approximately two orders of magnitude lower
    … attributed to Cr₂O₃ surface oxide").
  - `docs/known_gaps.md` Gap 4 status / placeholder / upstream lines
    updated; Causey + Forcey demoted to context-only references.
  - SAND2008-1141 Causey row remains absent from candidate-source
    table — re-add only if a publicly indexed copy is located.

### 2026-05-22 — `Conboy2014_SAND2014_2098` (correction — source-identity error)

- **Method:** cover-page verification of the local PDF + OSTI metadata
  + OSTI search API.
- **What was checked:**
  - `pdftotext -layout -f 1 -l 2 ~/Downloads/Conboy2014_SAND2014_2098.pdf`
    → cover-page title is *"Effects of Increasing Tip Velocity on Wind
    Turbine Rotor Design"*, authors Resor / Maniaci / Berg / Richards,
    SAND2014-3136.
  - `curl -sL "https://www.osti.gov/biblio/1177045"` →
    `citation_technical_report_number: SAND2014--3136` (confirms the
    biblio ID was always pointing at the wind-turbine report, not a
    Conboy/Wright/Pasch sCO₂ paper).
  - OSTI search API queries `Conboy+Wright+Pasch`,
    `Conboy+Pasch+Brayton+SAND2014`,
    `Conboy+sCO2+Brayton+performance+characteristics` → no public match
    for the alleged Conboy/Wright/Pasch sCO₂ paper. It is plausibly an
    ASME Turbo Expo or SAND conference paper that was never deposited
    on OSTI.
- **Outcome:** the BibTeX key `Conboy2014_SAND2014_2098` was always
  invalid in this repo. The original 2026-05-21 row in this log keyed
  the OSTI biblio ID 1177045 to a Conboy/Wright/Pasch title (and
  matching SAND number) that came from a separate cite — the biblio ID
  was *correct for SAND2014-3136*, the title and SAND number were
  *wrong*. Mirror of the same defect that afflicted the original
  Wright2011 row (correct OSTI ID, wrong title/SAND).
- **Next action:**
  - BibTeX entry removed from `docs/references.bib`.
  - Extract doc `docs/data_extracts/conboy2014_sand2014-2098.md`
    rewritten as a retirement notice with the full forensic trail.
  - Candidate-source table row 4 updated to `status = blocked` with the
    correction summary (this attempt record is the long form).
  - Downstream cites cleaned up: `docs/00_strategy.md` § BYOD, 
    `docs/01_phase1_properties.md` § SNL, `docs/known_gaps.md` Gap 1 +
    Gap 5 upstream lines.
  - Local PDF deleted from `~/Downloads/` (wind-turbine report, not
    useful here).
  - **Future genuine acquisition** of a real Conboy/Wright/Pasch sCO₂
    paper will use a *new* BibTeX key (e.g., `Conboy2014_ASME_GT2014`
    once the venue is confirmed) — do not re-use the retired
    `Conboy2014_SAND2014_2098` key.
  - **Process improvement:** as with the Wright2011 case, future
    acquisition rows should run
    `curl -sL "<osti-url>" | grep citation_technical_report_number`
    and compare to the table-row SAND number *before* committing the
    BibTeX entry. This would have caught both errors in seconds.

