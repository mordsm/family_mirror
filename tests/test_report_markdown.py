from src.reporting.report_markdown import build_basic_markdown_report, build_communication_markdown_report


FORBIDDEN_WORDS = [
    "אשם",
    "מניפולטיבי",
    "נרקיסיסט",
    "לא יציב",
    "מסוכן",
    "תוקפן",
    "אגרסיבי",
]


def test_basic_report_preserves_hebrew_text_and_timecodes():
    report = build_basic_markdown_report(
        source_name="family_call.m4a",
        speech_segments=[{"start": 0.5, "end": 3.0}],
        transcript_segments=[
            {
                "segment_id": "seg_0001",
                "start": 0.5,
                "end": 3.0,
                "text": "אני רוצה להסביר את זה.",
                "confidence": "medium",
                "flags": [],
            }
        ],
    )

    assert "אני רוצה להסביר את זה." in report
    assert "00:00.500–00:03.000" in report
    assert "אינו אבחון פסיכולוגי" in report


def test_basic_report_avoids_forbidden_safety_language():
    report = build_basic_markdown_report(
        source_name="short.wav",
        speech_segments=[],
        transcript_segments=[],
    )

    for word in FORBIDDEN_WORDS:
        assert word not in report


def test_communication_report_includes_metrics_and_candidate_events():
    report = build_communication_markdown_report(
        source_name="family_call.merged.json",
        transcript_segments=[
            {
                "segment_id": "seg_0001",
                "start": 0.0,
                "end": 2.0,
                "speaker": "משה",
                "text": "שלום",
                "flags": [],
            }
        ],
        metrics={
            "total_segments": 1,
            "conversation_end": 2.0,
            "speakers": {
                "משה": {
                    "total_speaking_seconds": 2.0,
                    "turn_count": 1,
                    "average_turn_seconds": 2.0,
                }
            },
            "long_silences": [
                {
                    "start": 2.0,
                    "end": 5.0,
                    "duration_seconds": 3.0,
                }
            ],
        },
        events=[
            {
                "type": "interruption_candidate",
                "start": 1.5,
                "end": 2.0,
                "duration_seconds": 0.5,
                "speakers": ["משה", "דויד"],
                "evidence": "דויד starts at 1.500s before משה ends at 2.000s",
                "confidence": "medium",
                "note_he": "ייתכן שהייתה קטיעה, אך יש דיבור חופף ולכן רמת הביטחון בינונית.",
            }
        ],
    )

    assert "דוח תקשורת זהיר" in report
    assert "משה: זמן דיבור 00:02.000" in report
    assert "שתיקה של 00:03.000" in report
    assert "קטיעה אפשרית" in report
    assert "ייתכן שהייתה קטיעה" in report


def test_communication_report_avoids_forbidden_safety_language():
    report = build_communication_markdown_report(
        source_name="empty.json",
        transcript_segments=[],
        metrics={"total_segments": 0, "conversation_end": 0.0, "speakers": {}, "long_silences": []},
        events=[],
    )

    for word in FORBIDDEN_WORDS:
        assert word not in report
