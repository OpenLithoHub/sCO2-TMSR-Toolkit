"""Runtime placeholder warnings — the Phase-1 'flag it' step.

Reference: docs/00_strategy.md § Standard handling protocol when data is missing.
           docs/known_gaps.md (anchor list).

The strategy mandates that every placeholder emit a *visible runtime log line*
pointing at the relevant ``known_gaps.md`` anchor. This module centralises the
formatting so the message is uniform across the codebase and the anchors are
always spelt correctly.

Usage::

    from sco2_warnings import warn_placeholder
    warn_placeholder("compressor-maps",
                     "default Sandia single-point map in use")

Each anchor must match a section in ``docs/known_gaps.md``. The valid set is
encoded here so a typo in the anchor string raises immediately rather than
emitting a silently-broken link.
"""

from __future__ import annotations

import logging
import os
from typing import Final

LOG = logging.getLogger("sco2_tmsr.placeholder")
if not LOG.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    LOG.addHandler(handler)
    LOG.setLevel(logging.WARNING)

KNOWN_GAPS_ANCHORS: Final[frozenset[str]] = frozenset(
    {
        "compressor-maps",      # Gap 1
        "pche-geometry",        # Gap 2
        "mixture-eos",          # Gap 3
        "tritium-constants",    # Gap 4
        "snl-step-rows",        # Gap 5
        "tmsr-lf1",             # Gap 6
    }
)

_DOCS_URL = (
    "https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit/blob/main/docs/known_gaps.md"
)
_SUPPRESS_ENV = "SCO2_TMSR_SUPPRESS_PLACEHOLDER_WARNINGS"


def _suppressed() -> bool:
    return os.environ.get(_SUPPRESS_ENV, "").lower() in {"1", "true", "yes"}


def warn_placeholder(anchor: str, message: str) -> None:
    """Emit a standard placeholder warning.

    Parameters
    ----------
    anchor : str
        Must match a section anchor in ``docs/known_gaps.md``.
    message : str
        Short human-readable summary of *what placeholder* is in effect.
    """
    if anchor not in KNOWN_GAPS_ANCHORS:
        raise ValueError(
            f"Unknown gap anchor {anchor!r}. Add it to docs/known_gaps.md "
            f"and to KNOWN_GAPS_ANCHORS in src/sco2_warnings.py first. "
            f"Valid anchors: {sorted(KNOWN_GAPS_ANCHORS)}"
        )
    if _suppressed():
        return
    LOG.warning(
        "%s — see %s#%s",
        message,
        _DOCS_URL,
        anchor,
    )


__all__ = ["warn_placeholder", "KNOWN_GAPS_ANCHORS"]
