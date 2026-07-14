"""Continuity detection for sequence-ID-ordered depth update streams.

Detects breaks in update-ID continuity (not wall-clock continuity — see
docs/why_validity_matters.md for why that distinction matters) and marks
the resulting segments as valid or gap-bounded.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContinuitySegment:
    """A maximal run of depth updates with no detected sequence gap."""
    # TODO(owner): fields — start_update_id, end_update_id, start_time, end_time


@dataclass(frozen=True)
class ContinuityReport:
    """Result of scanning a depth-update stream for continuity."""
    # TODO(owner): fields — segments: list[ContinuitySegment], gaps: list[...]


def detect_continuity(events) -> ContinuityReport:
    """Scan an ordered stream of depth events and partition it into
    continuity segments, marking gaps rather than interpolating across them.

    # TODO(owner): implementation
    """
    raise NotImplementedError