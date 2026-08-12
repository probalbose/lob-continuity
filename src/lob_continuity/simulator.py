"""Deterministic synthetic depth-update streams for examples and tests.

The simulator creates update-ID spans only. It deliberately contains no real
market data, venue calibration, prices, quantities, or timing assumptions.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticDepthUpdate:
    """A minimal synthetic event accepted by ``detect_continuity``."""

    first_update_id: int
    final_update_id: int


def simulate_depth_updates(
    event_count: int,
    *,
    start_update_id: int = 1,
    updates_per_event: int = 1,
    gaps_after: Mapping[int, int] | None = None,
) -> tuple[SyntheticDepthUpdate, ...]:
    """Create a deterministic stream with optional sequence gaps.

    ``gaps_after`` maps a zero-based event index to the number of update IDs
    omitted after that event. For example, ``{1: 3}`` inserts three missing
    update IDs between events at indexes 1 and 2.

    The number of omitted update IDs is not necessarily the number of missing
    network messages. One message may cover a span of several update IDs.

    Args:
        event_count: Number of synthetic events to create.
        start_update_id: First update ID in the generated stream.
        updates_per_event: Width of every generated update-ID span.
        gaps_after: Optional mapping from event index to omitted ID count.

    Returns:
        An immutable tuple of synthetic depth updates.

    Raises:
        ValueError: If a count is invalid or a gap is placed after an index
            that has no following event.
    """
    if event_count < 0:
        raise ValueError("event_count must be non-negative")
    if updates_per_event <= 0:
        raise ValueError("updates_per_event must be positive")

    requested_gaps = dict(gaps_after or {})
    for index, missing_count in requested_gaps.items():
        if index < 0 or index >= event_count - 1:
            raise ValueError(
                f"gap index {index} must have a following event in a stream "
                f"of {event_count} events"
            )
        if missing_count <= 0:
            raise ValueError(f"gap after index {index} must omit at least one update ID")

    events: list[SyntheticDepthUpdate] = []
    next_update_id = start_update_id

    for index in range(event_count):
        final_update_id = next_update_id + updates_per_event - 1
        events.append(
            SyntheticDepthUpdate(
                first_update_id=next_update_id,
                final_update_id=final_update_id,
            )
        )
        next_update_id = final_update_id + 1 + requested_gaps.get(index, 0)

    return tuple(events)
