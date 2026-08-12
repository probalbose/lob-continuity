"""Tests for lob_continuity.detector.detect_continuity."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from lob_continuity import (
    ContinuityReport,
    detect_continuity,
)


@dataclass(frozen=True)
class Event:
    """Minimal DepthUpdate for tests: (U, u) = (first_id, final_id)."""

    first_update_id: int
    final_update_id: int


def make_stream(*spans: tuple[int, int]) -> list[Event]:
    """Build events from (first_id, final_id) spans."""
    return [Event(first_update_id=a, final_update_id=b) for a, b in spans]


def test_empty_stream_has_no_segments_or_gaps() -> None:
    report = detect_continuity([])
    assert report.segments == []
    assert report.gaps == []
    assert report.total_events == 0
    assert report.total_missing_updates == 0
    assert not report.is_continuous


def test_single_event_is_one_continuous_segment() -> None:
    report = detect_continuity(make_stream((100, 105)))
    assert report.is_continuous
    assert len(report.segments) == 1
    seg = report.segments[0]
    assert (seg.start_update_id, seg.end_update_id) == (100, 105)
    assert (seg.start_index, seg.end_index, seg.event_count) == (0, 0, 1)
    assert report.gaps == []


def test_clean_contiguous_stream_is_one_segment() -> None:
    # Each event's first_id == previous final_id + 1.
    report = detect_continuity(make_stream((1, 3), (4, 4), (5, 9), (10, 12)))
    assert report.is_continuous
    assert len(report.segments) == 1
    seg = report.segments[0]
    assert (seg.start_update_id, seg.end_update_id) == (1, 12)
    assert seg.event_count == 4
    assert report.total_missing_updates == 0


def test_single_gap_splits_into_two_segments() -> None:
    # Break between final_id=3 and next first_id=8 -> 4 missing (4,5,6,7).
    report = detect_continuity(make_stream((1, 3), (8, 10)))
    assert not report.is_continuous
    assert len(report.segments) == 2
    assert len(report.gaps) == 1

    gap = report.gaps[0]
    assert gap.last_update_id_before == 3
    assert gap.first_update_id_after == 8
    assert gap.missing_update_count == 4
    assert (gap.index_before, gap.index_after) == (0, 1)

    first, second = report.segments
    assert (first.start_update_id, first.end_update_id) == (1, 3)
    assert (second.start_update_id, second.end_update_id) == (8, 10)
    assert report.total_missing_updates == 4
    assert report.total_events == 2


def test_multiple_gaps_produce_n_plus_one_segments() -> None:
    report = detect_continuity(
        make_stream((1, 2), (3, 3), (10, 11), (20, 25), (26, 26))
    )
    assert len(report.gaps) == 2
    assert len(report.segments) == 3
    assert [(s.start_update_id, s.end_update_id) for s in report.segments] == [
        (1, 3),
        (10, 11),
        (20, 26),
    ]
    assert [g.missing_update_count for g in report.gaps] == [6, 8]
    assert report.total_missing_updates == 14


def test_off_by_one_gap_of_exactly_one_missing_id() -> None:
    # final_id=5, next first_id=7 -> exactly one missing id (6).
    report = detect_continuity(make_stream((4, 5), (7, 8)))
    assert len(report.gaps) == 1
    assert report.gaps[0].missing_update_count == 1


def test_overlapping_stream_raises() -> None:
    # next first_id (3) <= previous final_id (5): overlap / out of order.
    with pytest.raises(ValueError, match="overlapping or out-of-order"):
        detect_continuity(make_stream((1, 5), (3, 9)))


def test_out_of_order_decreasing_raises() -> None:
    with pytest.raises(ValueError, match="overlapping or out-of-order"):
        detect_continuity(make_stream((10, 20), (1, 5)))


def test_malformed_event_raises() -> None:
    with pytest.raises(ValueError, match="malformed event"):
        detect_continuity(make_stream((10, 5)))


def test_report_is_typed_result() -> None:
    report = detect_continuity(make_stream((1, 1)))
    assert isinstance(report, ContinuityReport)


def test_accepts_a_lazy_iterator() -> None:
    # Continuity must not depend on the input being a concrete sequence.
    report = detect_continuity(iter(make_stream((1, 2), (3, 4))))
    assert report.is_continuous
    assert report.total_events == 2
