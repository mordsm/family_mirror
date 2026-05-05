from __future__ import annotations

from copy import deepcopy


def apply_speaker_mapping(segments: list[dict], speaker_map: dict[str, str]) -> list[dict]:
    """Replace generic speaker labels with user-provided names."""
    mapped: list[dict] = []
    for segment in segments:
        updated = deepcopy(segment)
        speaker = updated.get("speaker")
        if speaker in speaker_map:
            updated["speaker_label"] = speaker
            updated["speaker"] = speaker_map[speaker]
            _add_flag(updated, "speaker_mapped")
        mapped.append(updated)
    return mapped


def _add_flag(segment: dict, flag: str) -> None:
    flags = list(segment.get("flags", []))
    if flag not in flags:
        flags.append(flag)
    segment["flags"] = flags
