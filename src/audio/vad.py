from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import wave


@dataclass(frozen=True)
class SpeechSegment:
    start: float
    end: float

    def to_dict(self) -> dict:
        return {"start": round(self.start, 3), "end": round(self.end, 3)}


def detect_speech(
    wav_path: str | Path,
    *,
    tool: str = "silero",
    min_speech_duration_ms: int = 250,
    min_silence_duration_ms: int = 500,
    fallback_frame_ms: int = 30,
    fallback_energy_threshold: int = 500,
) -> list[SpeechSegment]:
    if tool == "silero":
        try:
            return _detect_with_silero(
                wav_path,
                min_speech_duration_ms=min_speech_duration_ms,
                min_silence_duration_ms=min_silence_duration_ms,
            )
        except Exception:
            pass
    return _detect_with_energy(
        wav_path,
        min_speech_duration_ms=min_speech_duration_ms,
        min_silence_duration_ms=min_silence_duration_ms,
        frame_ms=fallback_frame_ms,
        energy_threshold=fallback_energy_threshold,
    )


def _detect_with_silero(
    wav_path: str | Path,
    *,
    min_speech_duration_ms: int,
    min_silence_duration_ms: int,
) -> list[SpeechSegment]:
    from silero_vad import get_speech_timestamps, load_silero_vad, read_audio

    model = load_silero_vad()
    wav = read_audio(str(wav_path), sampling_rate=16000)
    timestamps = get_speech_timestamps(
        wav,
        model,
        sampling_rate=16000,
        min_speech_duration_ms=min_speech_duration_ms,
        min_silence_duration_ms=min_silence_duration_ms,
        return_seconds=True,
    )
    return [SpeechSegment(start=float(item["start"]), end=float(item["end"])) for item in timestamps]


def _detect_with_energy(
    wav_path: str | Path,
    *,
    min_speech_duration_ms: int,
    min_silence_duration_ms: int,
    frame_ms: int,
    energy_threshold: int,
) -> list[SpeechSegment]:
    with wave.open(str(wav_path), "rb") as audio:
        channels = audio.getnchannels()
        sample_width = audio.getsampwidth()
        frame_rate = audio.getframerate()
        if sample_width != 2:
            raise RuntimeError("Energy VAD fallback expects 16-bit PCM wav audio.")
        frames_per_window = max(1, int(frame_rate * frame_ms / 1000))
        raw_frames = audio.readframes(audio.getnframes())

    samples = _pcm16_samples(raw_frames)
    if channels > 1:
        samples = samples[::channels]

    windows: list[tuple[float, bool]] = []
    for start_index in range(0, len(samples), frames_per_window):
        chunk = samples[start_index : start_index + frames_per_window]
        if not chunk:
            continue
        energy = sum(abs(value) for value in chunk) / len(chunk)
        windows.append((start_index / frame_rate, energy >= energy_threshold))

    segments: list[SpeechSegment] = []
    active_start: float | None = None
    last_speech_time: float | None = None
    silence_limit = min_silence_duration_ms / 1000
    min_speech = min_speech_duration_ms / 1000

    for window_start, is_speech in windows:
        window_end = window_start + frame_ms / 1000
        if is_speech:
            if active_start is None:
                active_start = window_start
            last_speech_time = window_end
        elif active_start is not None and last_speech_time is not None:
            if window_start - last_speech_time >= silence_limit:
                if last_speech_time - active_start >= min_speech:
                    segments.append(SpeechSegment(active_start, last_speech_time))
                active_start = None
                last_speech_time = None

    if active_start is not None and last_speech_time is not None and last_speech_time - active_start >= min_speech:
        segments.append(SpeechSegment(active_start, last_speech_time))

    return segments


def _pcm16_samples(raw_frames: bytes) -> list[int]:
    return [
        int.from_bytes(raw_frames[index : index + 2], byteorder="little", signed=True)
        for index in range(0, len(raw_frames), 2)
    ]
