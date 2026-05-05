from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


SUPPORTED_INPUT_EXTENSIONS = {".mp3", ".m4a", ".wav", ".opus", ".ogg", ".flac", ".aac"}


def convert_to_wav(
    input_path: str | Path,
    output_path: str | Path,
    *,
    sample_rate: int = 16000,
    mono: bool = True,
    normalize_volume: bool = True,
) -> Path:
    source = Path(input_path)
    target = Path(output_path)
    if source.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        raise ValueError(f"Unsupported audio extension: {source.suffix}")
    ffmpeg = _ffmpeg_executable()

    target.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-vn",
        "-ar",
        str(sample_rate),
        "-ac",
        "1" if mono else "2",
    ]
    if normalize_volume:
        command.extend(["-af", "loudnorm"])
    command.extend(["-c:a", "pcm_s16le", str(target)])

    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed:\n{completed.stderr}")
    return target


def _ffmpeg_executable() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    try:
        import imageio_ffmpeg
    except ImportError as error:
        raise RuntimeError(
            "ffmpeg is required but was not found on PATH. Install ffmpeg or imageio-ffmpeg."
        ) from error
    return imageio_ffmpeg.get_ffmpeg_exe()
