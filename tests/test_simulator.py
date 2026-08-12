"""Tests for deterministic synthetic depth-update generation."""

from __future__ import annotations

import pytest

from lob_continuity import detect_continuity, simulate_depth_updates


def test_simulator_builds_contiguous_multi_id_events() -> None:
    events = simulate_depth_updates(3, start_update_id=10, updates_per_event=4)
    assert [(event.first_update_id, event.final_update_id) for event in events] == [
        (10, 13),
        (14, 17),
        (18, 21),
    ]
    assert detect_continuity(events).is_continuous


def test_simulator_injects_declared_gaps() -> None:
    events = simulate_depth_updates(5, updates_per_event=2, gaps_after={1: 3, 3: 1})
    report = detect_continuity(events)
    assert [gap.missing_update_count for gap in report.gaps] == [3, 1]
    assert len(report.segments) == 3


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"event_count": -1}, "event_count"),
        ({"event_count": 1, "updates_per_event": 0}, "updates_per_event"),
        ({"event_count": 2, "gaps_after": {1: 1}}, "following event"),
        ({"event_count": 2, "gaps_after": {0: 0}}, "at least one"),
    ],
)
def test_simulator_rejects_invalid_configuration(
    kwargs: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        simulate_depth_updates(**kwargs)  # type: ignore[arg-type]
