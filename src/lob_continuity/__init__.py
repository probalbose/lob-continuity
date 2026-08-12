"""lob-continuity: detect silent continuity gaps in LOB reconstruction.

Public API for scanning an ordered depth-update stream and partitioning it into
update-ID-continuous segments, marking (never interpolating) the gaps between
them.
"""

from lob_continuity.detector import (
    ContinuityGap,
    ContinuityReport,
    ContinuitySegment,
    DepthUpdate,
    detect_continuity,
)

__all__ = [
    "ContinuityGap",
    "ContinuityReport",
    "ContinuitySegment",
    "DepthUpdate",
    "detect_continuity",
]

__version__ = "0.1.0"
