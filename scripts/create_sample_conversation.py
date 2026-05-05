from __future__ import annotations

from pathlib import Path
import math
import subprocess
import wave


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "data" / "input"
WAV_PATH = INPUT_DIR / "sample_family_conversation.wav"
M4A_PATH = INPUT_DIR / "sample_family_conversation.m4a"
REFERENCE_PATH = INPUT_DIR / "sample_family_conversation_reference.md"
SAMPLE_RATE = 16_000


TURNS = [
    ("משה", "מה קורה דויד?", 440, 1.1),
    ("דויד", "עזוב אותי. אין לי כח אליך.", 660, 1.5),
    ("משה", "בא לך ללכת לפארק?", 440, 1.3),
    ("דויד", "אני אחשוב על זה. אני רוצה לנוח.", 660, 1.8),
    ("משה", "הכנתי ארוחת בוקר.", 440, 1.2),
    ("דויד", "תודה.", 660, 0.8),
]


def main() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    samples: list[int] = []
    timeline: list[tuple[str, float, float, str]] = []
    cursor = 0.0

    samples.extend(_silence(0.35))
    cursor += 0.35
    for speaker, text, frequency, duration in TURNS:
        start = cursor
        samples.extend(_tone(frequency, duration))
        cursor += duration
        end = cursor
        timeline.append((speaker, start, end, text))
        samples.extend(_silence(0.28))
        cursor += 0.28

    _write_wav(WAV_PATH, samples)
    _write_reference(REFERENCE_PATH, timeline)
    _encode_m4a(WAV_PATH, M4A_PATH)
    print(M4A_PATH)


def _tone(frequency: float, duration: float) -> list[int]:
    count = int(SAMPLE_RATE * duration)
    values: list[int] = []
    for index in range(count):
        t = index / SAMPLE_RATE
        envelope = min(1.0, index / (SAMPLE_RATE * 0.04), (count - index) / (SAMPLE_RATE * 0.04))
        signal = math.sin(2 * math.pi * frequency * t)
        # Add a quiet second harmonic so the turns are less sterile than pure beeps.
        signal += 0.25 * math.sin(2 * math.pi * frequency * 2 * t)
        values.append(int(8500 * envelope * signal))
    return values


def _silence(duration: float) -> list[int]:
    return [0] * int(SAMPLE_RATE * duration)


def _write_wav(path: Path, samples: list[int]) -> None:
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(b"".join(value.to_bytes(2, "little", signed=True) for value in samples))


def _encode_m4a(wav_path: Path, m4a_path: Path) -> None:
    try:
        import imageio_ffmpeg
    except ImportError as error:
        raise RuntimeError("Install imageio-ffmpeg to create the .m4a sample.") from error

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(wav_path),
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        str(m4a_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr)


def _write_reference(path: Path, timeline: list[tuple[str, float, float, str]]) -> None:
    lines = [
        "# דוגמת שיחה משפחתית",
        "",
        "זו דוגמת אודיו סינתטית לבדיקות מקומיות של הצינור.",
        "הגרסה הזו משתמשת בטונים מתחלפים במקום דיבור אמיתי כאשר אין מנוע דיבור עברי זמין.",
        "",
    ]
    for speaker, start, end, text in timeline:
        lines.append(f"- {start:.2f}-{end:.2f} {speaker}: {text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
