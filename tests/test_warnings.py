"""Tests for runtime placeholder warnings."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from sco2_warnings import KNOWN_GAPS_ANCHORS, warn_placeholder  # noqa: E402


def test_known_gaps_anchors_match_docs():
    """Every anchor declared in code must exist in docs/known_gaps.md."""
    docs = (REPO_ROOT / "docs" / "known_gaps.md").read_text()
    missing = [a for a in KNOWN_GAPS_ANCHORS if f'<a id="{a}">' not in docs]
    assert not missing, (
        f"Anchors declared in sco2_warnings.py but missing from "
        f"docs/known_gaps.md: {missing}"
    )


def test_unknown_anchor_raises():
    """A typo in the anchor must fail loudly, not log a broken link."""
    with pytest.raises(ValueError, match="Unknown gap anchor"):
        warn_placeholder("not-a-real-anchor", "test")


def test_warn_emits_under_normal_conditions(monkeypatch, caplog):
    """When the suppression env var is not set, the warning must be logged."""
    monkeypatch.delenv("SCO2_TMSR_SUPPRESS_PLACEHOLDER_WARNINGS", raising=False)
    with caplog.at_level(logging.WARNING, logger="sco2_tmsr.placeholder"):
        warn_placeholder("mixture-eos", "self-test message")
    assert any("self-test message" in r.message for r in caplog.records)
    assert any("known_gaps.md#mixture-eos" in r.message for r in caplog.records)


def test_warn_silenced_via_env(monkeypatch, caplog):
    """Tests run with suppression on — must not emit anything."""
    monkeypatch.setenv("SCO2_TMSR_SUPPRESS_PLACEHOLDER_WARNINGS", "1")
    with caplog.at_level(logging.WARNING, logger="sco2_tmsr.placeholder"):
        warn_placeholder("mixture-eos", "should not appear")
    assert not any("should not appear" in r.message for r in caplog.records)
