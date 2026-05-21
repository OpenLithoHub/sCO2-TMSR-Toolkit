# Citation & Data Provenance Protocol

> **Why this exists:** The core value of this toolkit is *framework + ingestion
> interfaces*, not ground-truth data. For that to work, every external number
> we cite must be auditable back to its source. Sloppy citations are a more
> serious bug than sloppy code — they propagate silently into CI and into
> downstream user dependencies.

This file defines the rules. The single source of truth for bibliographic
records is `docs/references.bib`.

---

## 1. Citation Key Format

**Pattern:** `FirstAuthorYYYY[_disambig]` (e.g. `Wright2010_SAND2010_0171`)

The `_disambig` suffix is required when:
- the same first-author + year appears for multiple works in `references.bib`,
- the work has a canonical identifier worth surfacing (technical-report
  number, ISBN, DOI), in which case use that identifier as disambiguator.

**Examples:**
- `Wright2010_SAND2010_0171` — SAND report
- `Vrancik1968_NASA_TN_D4849` — NASA TN
- `Kim2016_PCHE` — journal article (no canonical ID, simple topic suffix OK)

Citation keys are case-sensitive. Use exactly the spelling that appears in
`references.bib`. Do not invent variants.

---

## 2. Locator Format (for in-text references)

When citing, append a *locator* so the reader can verify the claim without
reading the whole work:

```
[Wright2010_SAND2010_0171, Table 2.1, p.23]
[Wright2010_SAND2010_0171, §5.3.1, p.54]
[Wright2010_SAND2010_0171, Figure 5-13, p.60]
[Vrancik1968_NASA_TN_D4849, Eq. 4.2]
```

Allowed locator types: `Table N.N`, `Figure N-N`, `§ N.N`, `Eq. N.N`,
`p.NN`, `pp.NN-NN`. Combine when useful: `[..., §5.3.1, p.54]`.

When the source is a single page (e.g., a one-page abstract or a CSV
extracted from a download), the locator may be omitted.

---

## 3. Confidence Levels

Every transcribed value carries a confidence grade. Grades are coarse on
purpose — they capture *how much human judgement was needed to read the
number off the source*, not the source's intrinsic accuracy.

| Grade | Meaning | Example | CI tolerance |
|-------|---------|---------|--------------|
| **A** | Tabulated numerical value, unambiguous, transcribed verbatim | Table 2.1 design-point T₁ = 305.3 K | strict (≤1%) |
| **B** | Stated in narrative prose, often rounded | "0.608 kg/L" in §2.3 | loose (≤5%) |
| **C** | Read off a figure, or reconstructed from indirect clues | Figure 5-9 valve-closure trajectory | very loose (≤15%); never used as a hard CI gate |
| **D** | Author's qualitative claim with no quantitative backing | "windage is significant" | not transcribed; cite for context only |

CSV files that feed `validate_against_sandia.py` carry a `confidence`
column with these grades. The validator picks tolerance from the grade
unless overridden via `--tolerance`.

---

## 4. CSV `source_ref` Naming Convention

Each row in a benchmark CSV must carry a `source_ref` value of the form:

```
<CitationKeyShortForm>_<LocatorTag>
```

Where `LocatorTag` is a short, table/figure-grained identifier the reader
can match to the locator in `references.bib` notes. **Examples currently
in use** (`validation/experimental_data/SNL_compressor_data.csv`):

```
Wright2010_SAND_T2.1_design       — Table 2.1, design point row
Wright2010_SAND_T2.1_vapor        — Table 2.1, vapor-side row
Wright2010_SAND_S2.3_pseudocrit   — §2.3 narrative, pseudo-crit density
Wright2010_SAND_S5.3.1_CBC081202  — §5.3.1 spin-test record
Wright2010_SAND_F5.11_perfmap     — Figure 5-11 caption
Wright2010_SAND_F5.13_design      — Figure 5-13 labels
```

Rules:
- Short citation form (`Wright2010_SAND`) is allowed in CSV columns to
  keep rows readable; full key (`Wright2010_SAND2010_0171`) lives in
  `references.bib` and `docs/data_extracts/*.md`.
- LocatorTag prefix: `T` for Table, `F` for Figure, `S` for Section,
  followed by the original numbering. This is the same shorthand humans
  use when annotating PDFs.
- One CSV row = one source citation. Do not aggregate.

---

## 5. Transcription Procedure

When you transcribe data from a new source:

1. **Add a BibTeX entry** to `docs/references.bib` first. Without an
   entry, the transcription has nowhere to point and CI will reject it
   (TODO: `scripts/check_citations.py`).
2. **Create a data-extract document** under `docs/data_extracts/` named
   `<lowercase_key>.md` (e.g., `wright2010_sand2010-0171.md`). Use the
   template in §6 below.
3. **Transcribe values into the CSV** with `source_ref` per §4 and a
   `confidence` grade per §3.
4. **Run the validator** (`python -m src.tools.validate_against_sandia
   --data <csv>`) and confirm CoolProp agrees within the grade's tolerance
   band. If it does not, do *not* widen tolerance silently — investigate.
5. **Two-pass review.** A second human (or, failing that, the same human
   in a fresh session) verifies the transcribed numbers character-by-
   character against the PDF. Mark `confidence` only after pass 2.

---

## 6. Data-Extract Document Template

`docs/data_extracts/<key>.md` is the human-readable companion to a
`references.bib` entry. It records *what we found in the source that is
useful to this project* — not a re-summary of the source itself.

The template lives at the top of every extract document:

```markdown
# <Source title>

> **BibTeX key:** `Key2010_xxx`
> **Source:** Authors, Title, Publisher, Year, URL
> **Read-through date:** YYYY-MM-DD
> **Reviewer:** <handle>

## What this document is

A bookmark of every fact, table, figure, or pointer in the source that has
been (or might be) used by this toolkit. New uses append; old entries are
not deleted even if superseded — they remain a citation trail.

## § N.N — <Topic> [Confidence A|B|C|D]

- **Source location:** [Table 2.1, p.23] / [§5.3.1, p.54] / etc.
- **Content:** terse summary of the fact.
- **Used in this repo by:** path/to/file.py:LN, path/to/doc.md.
- **Used as:** verbatim row | derived bound | qualitative motivation.
- **Verbatim quote (only if needed for traceability):** <one line>
```

Rule of thumb: each entry should fit in ~5 lines. If it grows longer,
split into sub-entries. The goal is *findability*, not exhaustive paraphrase.

---

## 7. What NOT to Cite

- **Do not** commit copyrighted PDFs to this repository. Cite via stable
  URL (OSTI, DOI, NASA-TR) and let the reader fetch the source.
- **Do not** create BibTeX entries for "future possible references." The
  bibliography is purged of speculative entries during release reviews.
- **Do not** transcribe a value with confidence A unless the locator is a
  *table cell or equation*. Prose claims are at most B; figures are at
  most C.
- **Do not** invent data to fill gaps. Use the
  `coolprop_self_consistency.csv` pattern instead — explicitly synthetic,
  loudly labelled.

---

## 8. Cross-Reference Map

| Repo location | What lives here | Cites by |
|---------------|-----------------|----------|
| `docs/references.bib` | BibTeX entries | full key |
| `docs/data_extracts/<key>.md` | Per-source extract notes | full key + locator |
| `docs/0N_*.md` (planning docs) | Strategy / plan prose | full key + locator |
| `validation/experimental_data/*.csv` | Numeric rows | `source_ref` short form |
| `validation/experimental_data/data_sources.md` | Per-CSV provenance | full key + locator |
| `src/**/*.py`, `cases/**/*` | Code & dict files | full key + brief locator in comments only when behaviour depends on the source |
| `docs/known_gaps.md` | Gap anchors | full key when a gap closure becomes possible |

When in doubt, cite the full key. Short forms are an optimisation, not
a default.

---

## 9. Acquisition SOP — Battle-Tested Recipes

> **Why this section exists:** Acquiring a public report is rarely a
> one-shot `curl`. Publisher CDNs throttle, OSTI's HTTP/2 frontend drops
> streams, dspace WAFs return 405 captchas. The recipes below are
> the ones that have actually worked in this repo. Every blocked or
> partial attempt is recorded in
> [`docs/data_extracts/_acquisition_log.md`](data_extracts/_acquisition_log.md);
> follow this SOP to keep that log auditable.

### 9.1 Decision tree

For each candidate source:

1. **Try direct fetch first** against the canonical URL.
2. **If direct fetch fails** (403 / 404 / SSL / timeout / connection drop), retry once via the local HTTP proxy `192.168.1.3:7890`.
3. **If proxy also fails**, mark `blocked` in the acquisition log, record the HTTP status or error, and move on. Do not retry in a tight loop. A blocked source today may be reachable tomorrow.
4. **On success**, save the PDF to `~/Downloads/` (do **not** commit it — § 7), then create the `docs/data_extracts/<key>.md` extract document and add the BibTeX entry to `docs/references.bib` *before* transcribing any numbers (§ 5).
5. **Always record the attempt** in the acquisition-log Attempt Records section, with date, method, command, outcome, next action.

### 9.2 Known-good fetch patterns

**OSTI (SAND reports, conference papers):**
```bash
# Use --http1.1 — the OSTI HTTP/2 frontend reproducibly drops streams mid-transfer.
curl -L --http1.1 --max-time 600 \
     -o ~/Downloads/<key>.pdf \
     "https://www.osti.gov/servlets/purl/<biblio_id>"
```
The `servlets/purl/<id>` form is the direct PDF endpoint. The `biblio/<id>` form is the landing page — do not fetch that as a PDF.

**NTRS (NASA technical reports):**
```bash
# Fast, single-shot. Use the NTRS API search to find the correct submission ID;
# the ID printed on the landing page is sometimes wrong.
curl -sL "https://ntrs.nasa.gov/api/citations/search?q=<query>" | jq '.results[].id'
curl -L --max-time 120 \
     -o ~/Downloads/<key>.pdf \
     "https://ntrs.nasa.gov/api/citations/<submission_id>/downloads/<submission_id>.pdf"
```

**Slow / large download (15 MB+ via proxy, server resets mid-transfer):**
```bash
# -C - is HTTP Range resume; combine with proxy + http/1.1.
# Re-invoke until the file size matches the server's Content-Length.
for i in {1..15}; do
  curl -L --http1.1 --max-time 600 --connect-timeout 30 \
       --proxy http://192.168.1.3:7890 -C - \
       -o ~/Downloads/<key>.pdf \
       "<canonical_url>"
done
```
Proven on `Allison2025_STEP_extended` (12 attempts, 15.2 MB) and `Dostal2004_MIT_PhD` (next-day retry after rate-limit cleared).

**MIT DSpace (dspace.mit.edu) — bypass CloudFront WAF:**
DSpace canonical URLs return HTTP/2 405 captcha pages. Try the author webpage URL instead:
```bash
curl -L --http1.1 --proxy http://192.168.1.3:7890 -C - \
     -o ~/Downloads/<key>.pdf \
     "https://web.mit.edu/<dept>/www/<file>.pdf"
```

### 9.3 Verification (mandatory after every download)

```python
import pathlib
data = pathlib.Path("~/Downloads/<key>.pdf").expanduser().read_bytes()
assert b"%%EOF" in data[-1024:], "PDF EOF marker missing — file truncated"
print(f"{len(data):,} bytes")
# Compare against the server's Content-Length (curl prints it on -i).
```
A PDF that lacks `%%EOF` in the final 1 KB is corrupt — do not extract from it. If the size differs from the server `Content-Length`, the transfer was truncated; resume with `-C -`.

### 9.4 Publisher paywalls (Elsevier / AIP / Springer)

These reproducibly fail both direct and proxy:

- AIP (`pubs.aip.org`) — Cloudflare WAF 403, even via DOI redirect.
  Example: `SpanWagner1996_CO2_EOS`.
- Elsevier (`linkinghub.elsevier.com` → `sciencedirect.com`) — landing page reachable, full-text PDF paywalled.
  Examples: `Kim2014_NED_PCHE`, `Ngo2007_ETFS_PCHE`.

**Action:** mark `blocked` and record substitute strategy in the acquisition log.
- For reference-quality EOS values, NIST Standard Reference Data (SRD 23 / REFPROP documentation) typically tabulates the same values without paywall.
- For paywalled journal articles, defer to institutional access; do not attempt scraping.

### 9.5 What is logged

The acquisition log
([`docs/data_extracts/_acquisition_log.md`](data_extracts/_acquisition_log.md))
is the single audit trail. It contains:

- Candidate source table — one row per BibTeX key with priority (P0 highest), status, last attempt date.
- Status legend — `pending`, `downloaded`, `extracted`, `transcribed`, `blocked`, `skipped`.
- Attempt records — append-only; each attempt gets a date-stamped section with method, command, outcome, next action. **Do not edit prior records.**

PDFs themselves are never committed (§ 7). Only metadata crosses the repo boundary.
