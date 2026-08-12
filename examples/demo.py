"""Run a small synthetic continuity scan."""

from lob_continuity import detect_continuity, simulate_depth_updates


def main() -> None:
    """Print segments and explicitly marked gaps from a synthetic stream."""
    events = simulate_depth_updates(
        8,
        start_update_id=100,
        updates_per_event=3,
        gaps_after={2: 4, 5: 2},
    )
    report = detect_continuity(events)

    print(f"events: {report.total_events}")
    print(f"continuous: {report.is_continuous}")
    print(f"segments: {len(report.segments)}")
    for segment in report.segments:
        print(
            "  "
            f"events {segment.start_index}-{segment.end_index}: "
            f"update IDs {segment.start_update_id}-{segment.end_update_id}"
        )

    print(f"gaps: {len(report.gaps)}")
    for gap in report.gaps:
        print(
            "  "
            f"after event {gap.index_before}: "
            f"{gap.missing_update_count} update IDs omitted "
            f"between {gap.last_update_id_before} and {gap.first_update_id_after}"
        )


if __name__ == "__main__":
    main()
