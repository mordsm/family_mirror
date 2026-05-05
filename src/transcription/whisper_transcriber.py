from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.audio.vad import SpeechSegment


@dataclass(frozen=True)
class TranscriptSegment:
    segment_id: str
    start: float
    end: float
    text: str
    confidence: str = "medium"
    flags: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "segment_id": self.segment_id,
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "speaker": None,
            "text": self.text,
            "confidence": self.confidence,
            "flags": list(self.flags),
        }


def transcribe_hebrew(
    wav_path: str | Path,
    speech_segments: list[SpeechSegment],
    *,
    model_name: str = "medium",
    language: str = "he",
    compute_type: str = "int8",
) -> list[TranscriptSegment]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise RuntimeError(
            "faster-whisper is not installed. Install transcription dependencies first."
        ) from error

    model = WhisperModel(model_name, device="cpu", compute_type=compute_type)
    raw_segments, _info = model.transcribe(
        str(wav_path),
        language=language,
        vad_filter=False,
        beam_size=5,
    )
    transcript: list[TranscriptSegment] = []
    speech_windows = [(segment.start, segment.end) for segment in speech_segments]
    for index, segment in enumerate(raw_segments, start=1):
        flags: list[str] = []
        if speech_windows and not _overlaps_any(segment.start, segment.end, speech_windows):
            flags.append("outside_vad_window")
        transcript.append(
            TranscriptSegment(
                segment_id=f"seg_{index:04d}",
                start=float(segment.start),
                end=float(segment.end),
                text=segment.text.strip(),
                confidence="medium",
                flags=tuple(flags),
            )
        )
    return transcript


def _overlaps_any(start: float, end: float, windows: list[tuple[float, float]]) -> bool:
    return any(max(0.0, min(end, win_end) - max(start, win_start)) > 0 for win_start, win_end in windows)
