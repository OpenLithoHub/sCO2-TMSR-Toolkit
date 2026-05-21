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
   the local HTTP proxy `192.168.1.3:7890`
   (`curl --proxy http://192.168.1.3:7890 ...`).
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
| 3 | `Wright2011_SAND2011_7779` | Wright et al., Overview of sCO2 Power Cycle Development at Sandia, SAND2011-7779 | https://www.osti.gov/biblio/1030354 | P0 | **downloaded** | 2026-05-21 | OSTI direct (`/servlets/purl/1030354`). 4.4 MB. Connection-drop required HTTP/1.1 + 600 s timeout. EOF verified. |
| 4 | `Conboy2014_SAND2014_2098` | Conboy et al., Performance Characteristics of an Operating sCO2 Brayton Cycle, SAND2014-2098 | https://www.osti.gov/biblio/1177045 | P0 | **downloaded** | 2026-05-21 | OSTI direct. 2.6 MB. EOF verified. |
| 5 | `Conboy2012_LDRD_10MWe` | Conboy et al., Modeling of a sCO2 Power Cycle for Nuclear Energy Applications, SAND/LDRD 2012 | search OSTI: `Conboy 10 MWe recompression sCO2` | P1 | **blocked** | 2026-05-21 | No matching OSTI biblio entry found by author/topic search. Likely SNL-internal LDRD that was never publicly released; supersede with Conboy2014 + later post-2018 OSTI biblio (`1574791`, `1543307`) which cover the 10 MWe cycle modeling work. |
| 6 | `Dostal2004_MIT_PhD` | V. Dostal, A Supercritical CO₂ Cycle for Next Generation Nuclear Reactors, MIT PhD thesis 2004 | https://web.mit.edu/22.33/www/dostal.pdf | P1 | **downloaded** | 2026-05-22 | MIT DSpace canonical (`dspace.mit.edu/handle/1721.1/17746`) returns CloudFront WAF 405 captcha; recovered via `web.mit.edu/22.33/www/dostal.pdf` + 192.168.1.3:7890 proxy + curl `-C -` resume. 6.6 MB. EOF verified. |
| 7 | `Kim2014_NED_PCHE` | Kim, Lee, Kim, Cha, *Nucl. Eng. Des.* 270 (2014) 73–81 | https://doi.org/10.1016/j.nucengdes.2014.01.006 | P1 | **blocked** | 2026-05-21 | Elsevier sciencedirect paywall via `linkinghub`. Open-access version not found on author webpage. Substitute candidate: any NRELOSTI numerical-investigation paper on PCHE zigzag channels. Re-attempt via institutional access. |
| 8 | `Allison2025_STEP_extended` | Extended Duration Operation of a Pilot-Scale sCO₂ Test Loop (STEP project) | https://www.osti.gov/biblio/2575689 | P2 | **downloaded** | 2026-05-22 | Substitute for the unreleased DOE STEP Phase 1 final report. OSTI direct + proxy + multi-segment resume (12 attempts, accumulated). 14.5 MB / 15246152 bytes exact. EOF verified. |
| 9 | `Galvas1973_NASA_TN_D7487` | Galvas, Centrifugal compressor design code (CCODP), NASA TN D-7487 | https://ntrs.nasa.gov/citations/19730019918 | P3 | pending | — | Indirect cite. NASA-TR — should follow the same NTRS API path that worked for Vrancik. Defer until ROM physical constraints become a near-term task. |
| 10 | `Ngo2007_ETFS_PCHE` | Ngo et al., *Exp. Therm. Fluid Sci.* 32 (2007) 560–570 | https://doi.org/10.1016/j.expthermflusci.2007.06.006 | P3 | pending | — | Elsevier paywall expected; bundle attempt with future Kim2014 retry. |

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
  3. Same URL via proxy `192.168.1.3:7890` with `--http1.1 -C - --retry 5` → also truncated.
  4. Direct retry the next day with `--http1.1 --proxy 192.168.1.3:7890 -C -` → completed in a single 6.6 MB transfer (full content-length, %%EOF present).
- **Outcome:** success after the per-day rate limit on the MIT host cleared.
- **Next action:** stub `docs/data_extracts/dostal2004_mit-phd.md` created.

### 2026-05-22 — `Allison2025_STEP_extended` (STEP substitute)

- **Method:** direct (failed) → proxy + `-C -` resume across many attempts
- **Command:** `curl -L --http1.1 --max-time 600 --connect-timeout 30 --proxy http://192.168.1.3:7890 -C - "https://www.osti.gov/servlets/purl/2575689"` — invoked 12 times with the resume flag accumulating bytes.
- **Outcome:** success after 12 attempts. Final size 15 246 152 bytes (= server `Content-Length`), %%EOF present.
- **Note:** the OSTI server reproducibly drops connections after 1–5 MB even via proxy, but `-C -` (HTTP Range resume) makes progress monotonic.
- **Next action:** stub `docs/data_extracts/allison2025_step_extended.md` created. STEP Phase 1 final report remains unreleased; this conference paper is the cite-of-record until DOE publishes.
