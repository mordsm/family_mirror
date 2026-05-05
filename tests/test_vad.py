import math
import wave

from src.audio.vad import detect_speech


def test_energy_vad_detects_synthetic_tone(tmp_path):
    wav_path = tmp_path / "tone.wav"
    sample_rate = 16000
    samples = []
    samples.extend([0] * int(sample_rate * 0.3))
    for index in range(int(sample_rate * 0.5)):
        samples.append(int(3000 * math.sin(2 * math.pi * 440 * index / sample_rate)))
    samples.extend([0] * int(sample_rate * 0.3))

    with wave.open(str(wav_path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(b"".join(value.to_bytes(2, "little", signed=True) for value in samples))

    segments = detect_speech(
        wav_path,
        tool="energy",
        min_speech_duration_ms=100,
        min_silence_duration_ms=100,
        fallback_energy_threshold=200,
    )

    assert len(segments) == 1
    assert 0.25 <= segments[0].start <= 0.35
    assert 0.75 <= segments[0].end <= 0.85
