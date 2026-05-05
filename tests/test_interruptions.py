from src.analysis.interruptions import detect_overlap_events


def test_detects_interruption_candidate_between_different_speakers():
    events = detect_overlap_events(
        [
            {"segment_id": "seg_0001", "start": 0.0, "end": 3.0, "speaker": "Speaker_1"},
            {"segment_id": "seg_0002", "start": 2.4, "end": 4.0, "speaker": "Speaker_2"},
        ],
        min_overlap_seconds=0.3,
        min_previous_turn_seconds=1.0,
    )

    assert events == [
        {
            "event_id": "event_0001",
            "type": "interruption_candidate",
            "start": 2.4,
            "end": 3.0,
            "duration_seconds": 0.6,
            "speakers": ["Speaker_1", "Speaker_2"],
            "segment_ids": ["seg_0001", "seg_0002"],
            "evidence": "Speaker_2 starts at 2.400s before Speaker_1 ends at 3.000s",
            "confidence": "medium",
            "note_he": "ייתכן שהייתה קטיעה, אך יש דיבור חופף ולכן רמת הביטחון בינונית.",
        }
    ]


def test_ignores_same_speaker_overlap():
    events = detect_overlap_events(
        [
            {"segment_id": "seg_0001", "start": 0.0, "end": 3.0, "speaker": "Speaker_1"},
            {"segment_id": "seg_0002", "start": 2.0, "end": 4.0, "speaker": "Speaker_1"},
        ]
    )

    assert events == []


def test_ignores_overlap_below_threshold():
    events = detect_overlap_events(
        [
            {"segment_id": "seg_0001", "start": 0.0, "end": 3.0, "speaker": "Speaker_1"},
            {"segment_id": "seg_0002", "start": 2.9, "end": 4.0, "speaker": "Speaker_2"},
        ],
        min_overlap_seconds=0.3,
    )

    assert events == []


def test_short_previous_turn_is_overlap_not_interruption_candidate():
    events = detect_overlap_events(
        [
            {"segment_id": "seg_0001", "start": 0.0, "end": 0.8, "speaker": "Speaker_1"},
            {"segment_id": "seg_0002", "start": 0.4, "end": 1.2, "speaker": "Speaker_2"},
        ],
        min_overlap_seconds=0.3,
        min_previous_turn_seconds=1.0,
    )

    assert events[0]["type"] == "overlap"


def test_ignores_unassigned_speakers():
    events = detect_overlap_events(
        [
            {"segment_id": "seg_0001", "start": 0.0, "end": 3.0, "speaker": None},
            {"segment_id": "seg_0002", "start": 2.0, "end": 4.0, "speaker": "Speaker_2"},
        ]
    )

    assert events == []
