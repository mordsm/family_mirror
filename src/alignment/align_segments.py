from __future__ import annotations

from copy import deepcopy

from src.utils.timecodes import overlap_seconds


def align_transcript_to_speakers(
    transcript_segments: list[dict],
    speaker_segments: list[dict],
    *,
    min_overlap_ratio: float = 0.35,
    ambiguity_margin_seconds: float = 0.2,
) -> list[dict]:
    """Attach the best speaker label to each transcript segment by timestamp overlap."""
    merged: list[dict] = []
    for segment in transcript_segments:
        updated = deepcopy(segment)
        matches = _speaker_matches(segment, speaker_segments)
        if not matches:
            updated["speaker"] = updated.get("speaker")
            _add_flag(updated, "speaker_unassigned")
            merged.append(updated)
            continue

        best = matches[0]
        duration = max(0.001, float(segment["end"]) - float(segment["start"]))
        updated["speaker"] = best["speaker"]

        if best["overlap"] / duration < min_overlap_ratio:
            _add_flag(updated, "low_confidence_speaker")

        if len(matches) > 1 and best["overlap"] - matches[1]["overlap"] <= ambiguity_margin_seconds:
            _add_flag(updated, "overlapping_speakers")
            _add_flag(updated, "low_confidence_speaker")

        merged.append(updated)
    return merged


def _speaker_matches(segment: dict, speaker_segments: list[dict]) -> list[dict]:
    start = float(segment["start"])
    end = float(segment["end"])
    matches: list[dict] = []
    for speaker_segment in speaker_segments:
        overlap = overlap_seconds(
            start,
            end,
            float(speaker_segment["start"]),
            float(speaker_segment["end"]),
        )
        if overlap <= 0:
            continue
        matches.append({"speaker": speaker_segment.get("speaker"), "overlap": overlap})
    return sorted(matches, key=lambda match: match["overlap"], reverse=True)


def _add_flag(segment: dict, flag: str) -> None:
    flags = list(segment.get("flags", []))
    if flag not in flags:
        flags.append(flag)
    segment["flags"] = flags
