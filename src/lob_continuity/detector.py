"""Continuity detection for sequence-ID-ordered depth update streams.

Detects breaks in update-ID continuity (not wall-clock continuity — see
docs/why_validity_matters.md for why that distinction matters) and marks
the resulting segments as valid or gap-bounded.

Domain rule (do not violate): continuity is defined by the update-ID sequence,
*never* by timestamps. Two consecutive depth updates are continuous iff the
first update ID of the later event immediately follows the final update ID of
the earlier event. A wall-clock pause is not a break; a sequence jump is. When
a break is found it is *marked* as a gap — the stream is never interpolated
across it.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class DepthUpdate(Protocol):
    """Structural type for a single depth-update event.

    Any object exposing an integer ``first_update_id`` and ``final_update_id``
    satisfies this protocol. These correspond to the ``U`` (first update ID in
    the event) and ``u`` (final update ID in the event) fields of an exchange
    depth-diff message. The values must satisfy
    ``first_update_id <= final_update_id`` within a single well-formed event.
    """

    @property
    def first_update_id(self) -> int: ...

    @property
    def final_update_id(self) -> int: ...


@dataclass(frozen=True)
class ContinuitySegment:
    """A maximal run of depth updates with no detected sequence gap.

    Update IDs from ``start_update_id`` through ``end_update_id`` are contiguous
    across the events at stream positions ``start_index``..``end_index``
    (inclusive). A book reconstructed from a single segment is trustworthy;
    across a gap it is not.
    """

    start_update_id: int
    end_update_id: int
    start_index: int
    end_index: int
    event_count: int


@dataclass(frozen=True)
class ContinuityGap:
    """A detected break in update-ID continuity between two adjacent events.

    ``missing_update_count`` is the number of update IDs that fall between the
    two events and were never observed. The gap sits between stream positions
    ``index_before`` and ``index_after`` (which are adjacent: ``index_after ==
    index_before + 1``).
    """

    last_update_id_before: int
    first_update_id_after: int
    missing_update_count: int
    index_before: int
    index_after: int


@dataclass(frozen=True)
class ContinuityReport:
    """Result of scanning a depth-update stream for continuity.

    Holds the ordered list of continuous ``segments`` and the ``gaps`` between
    them. For a stream with ``N`` gaps there are ``N + 1`` segments (or zero
    segments for an empty stream).
    """

    segments: list[ContinuitySegment]
    gaps: list[ContinuityGap]

    @property
    def is_continuous(self) -> bool:
        """True iff the stream is one unbroken segment (non-empty, no gaps)."""
        return len(self.gaps) == 0 and len(self.segments) == 1

    @property
    def total_events(self) -> int:
        """Total number of events across all segments."""
        return sum(segment.event_count for segment in self.segments)

    @property
    def total_missing_updates(self) -> int:
        """Total update IDs lost across all detected gaps."""
        return sum(gap.missing_update_count for gap in self.gaps)


def detect_continuity(events: Iterable[DepthUpdate]) -> ContinuityReport:
    """Partition an ordered depth-update stream into continuity segments.

    Scans ``events`` in order, splitting the stream wherever update-ID
    continuity breaks and recording the break as a :class:`ContinuityGap`
    rather than interpolating across it.

    Two adjacent events ``prev`` and ``cur`` are classified by comparing
    ``cur.first_update_id`` against ``prev.final_update_id``:

    - ``cur.first_update_id == prev.final_update_id + 1`` — contiguous; the
      events belong to the same segment.
    - ``cur.first_update_id > prev.final_update_id + 1`` — a gap; the current
      segment is closed and a new one begins.
    - ``cur.first_update_id <= prev.final_update_id`` — overlapping or
      out-of-order input, which this layer does not resolve.

    Args:
        events: An iterable of depth updates, already ordered by update ID.

    Returns:
        A :class:`ContinuityReport` with the segments and the gaps between them.

    Raises:
        ValueError: If an event is malformed (``first_update_id >
            final_update_id``) or if the stream is overlapping / out of order
            (``cur.first_update_id <= prev.final_update_id``). Ordering and
            de-duplication are the caller's responsibility.
    """
    segments: list[ContinuitySegment] = []
    gaps: list[ContinuityGap] = []

    seg_start_update_id: int | None = None
    seg_start_index = 0
    prev: DepthUpdate | None = None
    prev_index = -1

    for index, event in enumerate(events):
        first_id = event.first_update_id
        final_id = event.final_update_id

        if first_id > final_id:
            raise ValueError(
                f"malformed event at index {index}: first_update_id={first_id} "
                f"> final_update_id={final_id}"
            )

        if prev is None:
            seg_start_update_id = first_id
            seg_start_index = index
        else:
            prev_final = prev.final_update_id
            if first_id <= prev_final:
                raise ValueError(
                    f"overlapping or out-of-order stream at index {index}: "
                    f"first_update_id={first_id} <= previous final_update_id="
                    f"{prev_final}; caller must pre-order and de-duplicate"
                )
            if first_id > prev_final + 1:
                # Continuity break: close the current segment, record the gap.
                assert seg_start_update_id is not None
                segments.append(
                    ContinuitySegment(
                        start_update_id=seg_start_update_id,
                        end_update_id=prev_final,
                        start_index=seg_start_index,
                        end_index=prev_index,
                        event_count=prev_index - seg_start_index + 1,
                    )
                )
                gaps.append(
                    ContinuityGap(
                        last_update_id_before=prev_final,
                        first_update_id_after=first_id,
                        missing_update_count=first_id - prev_final - 1,
                        index_before=prev_index,
                        index_after=index,
                    )
                )
                seg_start_update_id = first_id
                seg_start_index = index
            # else: contiguous — extend the current segment.

        prev = event
        prev_index = index

    # Close the final open segment (if any events were seen).
    if prev is not None:
        assert seg_start_update_id is not None
        segments.append(
            ContinuitySegment(
                start_update_id=seg_start_update_id,
                end_update_id=prev.final_update_id,
                start_index=seg_start_index,
                end_index=prev_index,
                event_count=prev_index - seg_start_index + 1,
            )
        )

    return ContinuityReport(segments=segments, gaps=gaps)
