"""Gate parsing utilities.

These functions intentionally accept a small amount of format variance,
while still enforcing clear PASS/FAIL and APPROVED yes/no decisions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GateDecision:
    status: str  # e.g. PASS/FAIL/APPROVED/VETO/UNKNOWN
    raw: str | None = None


_QC_STATUS_RE = re.compile(r"^\s*-\s*\*\*Status:\*\*\s*(PASS|FAIL)\s*$", re.IGNORECASE | re.MULTILINE)


def parse_qc_status(markdown: str) -> GateDecision:
    """Parse QC PASS/FAIL from the qc_report markdown."""
    m = _QC_STATUS_RE.search(markdown or "")
    if not m:
        return GateDecision(status="UNKNOWN", raw=None)
    value = m.group(1).upper()
    return GateDecision(status=value, raw=value)


# Accept a few human-friendly variants.
_CURATOR_APPROVED_RE = re.compile(
    r"^\s*(?:-|\*)?\s*Approved\s*:\s*(yes|no|true|false)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def parse_curator_approval(markdown: str) -> GateDecision:
    """Parse curator approval yes/no from curator_decision.md."""
    m = _CURATOR_APPROVED_RE.search(markdown or "")
    if not m:
        return GateDecision(status="UNKNOWN", raw=None)

    token = m.group(1).lower()
    if token in {"yes", "true"}:
        return GateDecision(status="APPROVED", raw=token)
    return GateDecision(status="VETO", raw=token)
