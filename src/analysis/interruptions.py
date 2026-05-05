from __future__ import annotations

from src.utils.timecodes import overlap_seconds


NOTE_HE = "ייתכן שהייתה קטיעה, אך יש דיבור חופף ולכן רמת הביטחון בינונית."


def detect_overlap_events(
    segments: list[dict],
    *,
    min_overlap_seconds: float = 0.3,
    min_previous_turn_seconds: float = 1.0,
) -> list[dict]:
    """Detect overlap and interruption candidates from timestamped speaker turns."""
    ordered = sorted(segments, key=lambda segment: (float(segment["start"]), float(segment["end"])))
    events: list[dict] = []
    event_index = 1

    for previous, current in zip(ordered, ordered[1:], strict=False):
        previous_speaker = previous.get("speaker")
        current_speaker = current.get("speaker")
        if not previous_speaker or not current_speaker or previous_speaker == current_speaker:
            continue

        overlap = overlap_seconds(
            float(previous["start"]),
            float(previous["end"]),
            float(current["start"]),
            float(current["end"]),
        )
        if overlap < min_overlap_seconds:
            continue

        previous_duration = max(0.0, float(previous["end"]) - float(previous["start"]))
        event_type = "overlap"
        if float(current["start"]) < float(previous["end"]) and previous_duration >= min_previous_turn_seconds:
            event_type = "interruption_candidate"

        events.append(
            {
                "event_id": f"event_{event_index:04d}",
                "type": event_type,
                "start": round(float(current["start"]), 3),
                "end": round(min(float(previous["end"]), float(current["end"])), 3),
                "duration_seconds": round(overlap, 3),
                "speakers": [previous_speaker, current_speaker],
                "segment_ids": [previous.get("segment_id"), current.get("segment_id")],
                "evidence": (
                    f"{current_speaker} starts at {float(current['start']):.3f}s "
                    f"before {previous_speaker} ends at {float(previous['end']):.3f}s"
                ),
                "confidence": "medium",
                "note_he": NOTE_HE,
            }
        )
        event_index += 1

    return events
