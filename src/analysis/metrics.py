from __future__ import annotations

from collections import defaultdict


def compute_basic_metrics(segments: list[dict], *, long_silence_seconds: float = 2.0) -> dict:
    ordered = sorted(segments, key=lambda segment: (float(segment["start"]), float(segment["end"])))
    speaker_totals: dict[str, dict] = defaultdict(
        lambda: {
            "total_speaking_seconds": 0.0,
            "turn_count": 0,
            "average_turn_seconds": 0.0,
        }
    )

    for segment in ordered:
        speaker = segment.get("speaker") or "unassigned"
        duration = max(0.0, float(segment["end"]) - float(segment["start"]))
        speaker_totals[speaker]["total_speaking_seconds"] += duration
        speaker_totals[speaker]["turn_count"] += 1

    for stats in speaker_totals.values():
        turn_count = stats["turn_count"]
        if turn_count:
            stats["average_turn_seconds"] = stats["total_speaking_seconds"] / turn_count
        stats["total_speaking_seconds"] = round(stats["total_speaking_seconds"], 3)
        stats["average_turn_seconds"] = round(stats["average_turn_seconds"], 3)

    return {
        "total_segments": len(ordered),
        "conversation_start": round(float(ordered[0]["start"]), 3) if ordered else 0.0,
        "conversation_end": round(float(ordered[-1]["end"]), 3) if ordered else 0.0,
        "speakers": dict(sorted(speaker_totals.items())),
        "long_silences": _long_silences(ordered, threshold=long_silence_seconds),
    }


def _long_silences(segments: list[dict], *, threshold: float) -> list[dict]:
    silences: list[dict] = []
    for previous, current in zip(segments, segments[1:], strict=False):
        start = float(previous["end"])
        end = float(current["start"])
        duration = end - start
        if duration >= threshold:
            silences.append(
                {
                    "start": round(start, 3),
                    "end": round(end, 3),
                    "duration_seconds": round(duration, 3),
                    "after_segment_id": previous.get("segment_id"),
                    "before_segment_id": current.get("segment_id"),
                }
            )
    return silences
