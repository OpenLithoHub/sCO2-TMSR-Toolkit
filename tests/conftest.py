"""Pytest configuration shared across the suite.

Suppress placeholder warnings during tests by default — the warnings exist
to inform interactive users, not to clutter test output. Tests that need
to assert on warning emission can set the env var off explicitly.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

os.environ.setdefault("SCO2_TMSR_SUPPRESS_PLACEHOLDER_WARNINGS", "1")
