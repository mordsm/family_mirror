from src.speakers.mapping import apply_speaker_mapping


def test_apply_speaker_mapping_replaces_only_explicit_labels():
    mapped = apply_speaker_mapping(
        [
            {"segment_id": "seg_0001", "speaker": "Speaker_1", "flags": []},
            {"segment_id": "seg_0002", "speaker": "Speaker_2", "flags": []},
            {"segment_id": "seg_0003", "speaker": None, "flags": []},
        ],
        {"Speaker_1": "משה"},
    )

    assert mapped[0]["speaker"] == "משה"
    assert mapped[0]["speaker_label"] == "Speaker_1"
    assert mapped[0]["flags"] == ["speaker_mapped"]
    assert mapped[1]["speaker"] == "Speaker_2"
    assert "speaker_label" not in mapped[1]
    assert mapped[2]["speaker"] is None


def test_apply_speaker_mapping_preserves_existing_flags():
    mapped = apply_speaker_mapping(
        [{"segment_id": "seg_0001", "speaker": "Speaker_1", "flags": ["reference_transcript"]}],
        {"Speaker_1": "דויד"},
    )

    assert mapped[0]["flags"] == ["reference_transcript", "speaker_mapped"]
