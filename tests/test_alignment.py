from src.alignment.align_segments import align_transcript_to_speakers


def test_aligns_transcript_to_best_speaker_overlap():
    merged = align_transcript_to_speakers(
        [
            {
                "segment_id": "seg_0001",
                "start": 1.0,
                "end": 4.0,
                "speaker": None,
                "text": "hello",
                "confidence": "medium",
                "flags": [],
            }
        ],
        [
            {"start": 0.5, "end": 2.0, "speaker": "Speaker_1"},
            {"start": 2.0, "end": 4.5, "speaker": "Speaker_2"},
        ],
    )

    assert merged[0]["speaker"] == "Speaker_2"
    assert merged[0]["flags"] == []


def test_marks_segment_without_speaker_overlap_as_unassigned():
    merged = align_transcript_to_speakers(
        [{"segment_id": "seg_0001", "start": 1.0, "end": 2.0, "flags": []}],
        [{"start": 3.0, "end": 4.0, "speaker": "Speaker_1"}],
    )

    assert merged[0]["speaker"] is None
    assert merged[0]["flags"] == ["speaker_unassigned"]


def test_marks_weak_overlap_as_low_confidence():
    merged = align_transcript_to_speakers(
        [{"segment_id": "seg_0001", "start": 1.0, "end": 5.0, "speaker": None, "flags": []}],
        [{"start": 1.0, "end": 2.0, "speaker": "Speaker_1"}],
    )

    assert merged[0]["speaker"] == "Speaker_1"
    assert "low_confidence_speaker" in merged[0]["flags"]


def test_marks_ambiguous_overlapping_speakers():
    merged = align_transcript_to_speakers(
        [{"segment_id": "seg_0001", "start": 1.0, "end": 3.0, "speaker": None, "flags": []}],
        [
            {"start": 1.0, "end": 2.2, "speaker": "Speaker_1"},
            {"start": 1.8, "end": 3.0, "speaker": "Speaker_2"},
        ],
    )

    assert merged[0]["speaker"] == "Speaker_1"
    assert "overlapping_speakers" in merged[0]["flags"]
    assert "low_confidence_speaker" in merged[0]["flags"]
