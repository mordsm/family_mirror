from pathlib import Path

from src.main import _load_reference_transcript


def test_load_reference_transcript_aligns_turns_to_speech_segments(tmp_path: Path):
    audio = tmp_path / "sample.m4a"
    audio.write_bytes(b"fake")
    (tmp_path / "sample_reference.md").write_text(
        "\n".join(
            [
                "# Reference",
                "",
                "1. \u05de\u05e9\u05d4: \u05de\u05d4 \u05e7\u05d5\u05e8\u05d4 \u05d3\u05d5\u05d9\u05d3?",
                "2. \u05d3\u05d5\u05d9\u05d3: \u05ea\u05d5\u05d3\u05d4.",
            ]
        ),
        encoding="utf-8",
    )

    transcript = _load_reference_transcript(
        audio,
        [
            {"start": 0.5, "end": 1.4},
            {"start": 2.0, "end": 2.8},
        ],
    )

    assert len(transcript) == 2
    assert transcript[0]["text"] == "\u05de\u05e9\u05d4: \u05de\u05d4 \u05e7\u05d5\u05e8\u05d4 \u05d3\u05d5\u05d9\u05d3?"
    assert transcript[0]["start"] == 0.5
    assert transcript[1]["flags"] == ["reference_transcript"]
