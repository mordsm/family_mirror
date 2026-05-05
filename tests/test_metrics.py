from src.analysis.metrics import compute_basic_metrics


def test_compute_basic_metrics_by_speaker():
    metrics = compute_basic_metrics(
        [
            {"segment_id": "seg_0001", "start": 0.0, "end": 2.0, "speaker": "Speaker_1"},
            {"segment_id": "seg_0002", "start": 3.0, "end": 4.5, "speaker": "Speaker_2"},
            {"segment_id": "seg_0003", "start": 5.0, "end": 6.0, "speaker": "Speaker_1"},
        ]
    )

    assert metrics["total_segments"] == 3
    assert metrics["conversation_start"] == 0.0
    assert metrics["conversation_end"] == 6.0
    assert metrics["speakers"]["Speaker_1"] == {
        "total_speaking_seconds": 3.0,
        "turn_count": 2,
        "average_turn_seconds": 1.5,
    }
    assert metrics["speakers"]["Speaker_2"]["turn_count"] == 1


def test_compute_basic_metrics_tracks_unassigned_speaker():
    metrics = compute_basic_metrics(
        [{"segment_id": "seg_0001", "start": 0.0, "end": 1.25, "speaker": None}]
    )

    assert metrics["speakers"]["unassigned"]["total_speaking_seconds"] == 1.25
    assert metrics["speakers"]["unassigned"]["turn_count"] == 1


def test_compute_basic_metrics_detects_long_silences():
    metrics = compute_basic_metrics(
        [
            {"segment_id": "seg_0001", "start": 0.0, "end": 1.0, "speaker": "Speaker_1"},
            {"segment_id": "seg_0002", "start": 4.5, "end": 5.0, "speaker": "Speaker_2"},
            {"segment_id": "seg_0003", "start": 6.0, "end": 7.0, "speaker": "Speaker_1"},
        ],
        long_silence_seconds=2.0,
    )

    assert metrics["long_silences"] == [
        {
            "start": 1.0,
            "end": 4.5,
            "duration_seconds": 3.5,
            "after_segment_id": "seg_0001",
            "before_segment_id": "seg_0002",
        }
    ]


def test_compute_basic_metrics_handles_empty_segments():
    metrics = compute_basic_metrics([])

    assert metrics == {
        "total_segments": 0,
        "conversation_start": 0.0,
        "conversation_end": 0.0,
        "speakers": {},
        "long_silences": [],
    }
