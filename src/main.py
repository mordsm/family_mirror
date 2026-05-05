from __future__ import annotations

import argparse
from pathlib import Path
import re

from src.alignment.align_segments import align_transcript_to_speakers
from src.analysis.interruptions import detect_overlap_events
from src.analysis.metrics import compute_basic_metrics
from src.analysis.safety_rules import find_forbidden_language
from src.audio.convert import convert_to_wav
from src.audio.vad import detect_speech
from src.reporting.report_markdown import (
    build_basic_markdown_report,
    build_communication_markdown_report,
    write_markdown_report,
)
from src.speakers.mapping import apply_speaker_mapping
from src.storage import read_json, stem_for_input, write_json
from src.transcription.whisper_transcriber import transcribe_hebrew
from src.utils.config import get_nested, load_config


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Family Mirror local Hebrew transcription MVP")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process_parser = subparsers.add_parser("process", help="Process one local audio file")
    process_parser.add_argument("audio_file", help="Path to mp3/m4a/wav/opus audio")
    process_parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    process_parser.add_argument("--skip-transcription", action="store_true", help="Only convert audio and run VAD")
    process_parser.add_argument(
        "--speaker-segments",
        help="Optional JSON file with diarization-style segments: start, end, speaker",
    )

    map_parser = subparsers.add_parser("map-speakers", help="Apply manual speaker labels to a transcript")
    map_parser.add_argument("conversation", help="Conversation stem or transcript JSON path")
    map_parser.add_argument("--speaker", action="append", required=True, help="Generic label, such as Speaker_1")
    map_parser.add_argument("--name", action="append", required=True, help="Manual display name for the speaker")
    map_parser.add_argument("--output", help="Optional output JSON path")

    metrics_parser = subparsers.add_parser("metrics", help="Compute basic observable conversation metrics")
    metrics_parser.add_argument("conversation", help="Conversation stem or transcript JSON path")
    metrics_parser.add_argument(
        "--long-silence-seconds",
        type=float,
        default=2.0,
        help="Minimum gap to report as a long silence",
    )
    metrics_parser.add_argument("--output", help="Optional output JSON path")

    events_parser = subparsers.add_parser("events", help="Detect cautious observable conversation events")
    events_parser.add_argument("conversation", help="Conversation stem or transcript JSON path")
    events_parser.add_argument(
        "--min-overlap-seconds",
        type=float,
        default=0.3,
        help="Minimum speaker overlap to report",
    )
    events_parser.add_argument(
        "--min-previous-turn-seconds",
        type=float,
        default=1.0,
        help="Minimum previous turn duration for interruption candidates",
    )
    events_parser.add_argument("--output", help="Optional output JSON path")

    report_parser = subparsers.add_parser("report", help="Build a cautious communication Markdown report")
    report_parser.add_argument("conversation", help="Conversation stem or transcript JSON path")
    report_parser.add_argument("--metrics", help="Optional metrics JSON path")
    report_parser.add_argument("--events", help="Optional events JSON path")
    report_parser.add_argument("--output", help="Optional Markdown output path")

    safety_parser = subparsers.add_parser("check-report", help="Scan a Markdown report for forbidden safety language")
    safety_parser.add_argument("report_file", help="Path to a generated Markdown report")

    args = parser.parse_args(argv)
    if args.command == "process":
        process_audio(
            Path(args.audio_file),
            config_path=Path(args.config),
            skip_transcription=args.skip_transcription,
            speaker_segments_path=Path(args.speaker_segments) if args.speaker_segments else None,
        )
    elif args.command == "map-speakers":
        map_speakers(
            args.conversation,
            speakers=args.speaker,
            names=args.name,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "metrics":
        write_metrics(
            args.conversation,
            long_silence_seconds=args.long_silence_seconds,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "events":
        write_events(
            args.conversation,
            min_overlap_seconds=args.min_overlap_seconds,
            min_previous_turn_seconds=args.min_previous_turn_seconds,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "report":
        write_communication_report(
            args.conversation,
            metrics_path=Path(args.metrics) if args.metrics else None,
            events_path=Path(args.events) if args.events else None,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "check-report":
        check_report_safety(Path(args.report_file))


def process_audio(
    audio_file: Path,
    *,
    config_path: Path,
    skip_transcription: bool = False,
    speaker_segments_path: Path | None = None,
) -> dict[str, str]:
    config = load_config(config_path)
    name = stem_for_input(audio_file)
    processed_wav = Path("data/processed") / f"{name}.wav"
    speech_json = Path("data/transcripts") / f"{name}.speech_segments.json"
    transcript_json = Path("data/transcripts") / f"{name}.segments.json"
    merged_json = Path("data/transcripts") / f"{name}.merged.json"
    report_path = Path("data/reports") / f"{name}.report.md"

    convert_to_wav(
        audio_file,
        processed_wav,
        sample_rate=int(get_nested(config, "audio", "sample_rate", default=16000)),
        mono=bool(get_nested(config, "audio", "mono", default=True)),
        normalize_volume=bool(get_nested(config, "audio", "normalize_volume", default=True)),
    )

    speech_segments = detect_speech(
        processed_wav,
        tool=str(get_nested(config, "vad", "tool", default="silero")),
        min_speech_duration_ms=int(get_nested(config, "vad", "min_speech_duration_ms", default=250)),
        min_silence_duration_ms=int(get_nested(config, "vad", "min_silence_duration_ms", default=500)),
        fallback_frame_ms=int(get_nested(config, "vad", "fallback_frame_ms", default=30)),
        fallback_energy_threshold=int(get_nested(config, "vad", "fallback_energy_threshold", default=500)),
    )
    speech_data = [segment.to_dict() for segment in speech_segments]
    write_json(speech_json, speech_data)

    transcript_data: list[dict] = []
    if not skip_transcription:
        transcript_segments = transcribe_hebrew(
            processed_wav,
            speech_segments,
            model_name=str(get_nested(config, "transcription", "model", default="medium")),
            language=str(get_nested(config, "transcription", "language", default="he")),
            compute_type=str(get_nested(config, "transcription", "compute_type", default="int8")),
        )
        transcript_data = [segment.to_dict() for segment in transcript_segments]
    else:
        transcript_data = _load_reference_transcript(audio_file, speech_data)
    write_json(transcript_json, transcript_data)

    report_transcript_data = transcript_data
    outputs = {
        "processed_wav": str(processed_wav),
        "speech_segments": str(speech_json),
        "transcript": str(transcript_json),
    }
    if speaker_segments_path is not None:
        speaker_data = read_json(speaker_segments_path)
        if not isinstance(speaker_data, list):
            raise ValueError("Speaker segments JSON must contain a list of segments.")
        report_transcript_data = align_transcript_to_speakers(transcript_data, speaker_data)
        write_json(merged_json, report_transcript_data)
        outputs["merged_transcript"] = str(merged_json)

    report = build_basic_markdown_report(
        source_name=audio_file.name,
        speech_segments=speech_data,
        transcript_segments=report_transcript_data,
    )
    write_markdown_report(report_path, report)

    outputs["report"] = str(report_path)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return outputs


def map_speakers(
    conversation: str,
    *,
    speakers: list[str],
    names: list[str],
    output_path: Path | None = None,
) -> Path:
    if len(speakers) != len(names):
        raise ValueError("Each --speaker value must have a matching --name value.")

    input_path = _resolve_transcript_path(conversation)
    speaker_map = dict(zip(speakers, names, strict=True))
    data = read_json(input_path)
    if not isinstance(data, list):
        raise ValueError("Transcript JSON must contain a list of segments.")

    mapped = apply_speaker_mapping(data, speaker_map)
    target = output_path or input_path.with_name(f"{input_path.stem}.mapped.json")
    write_json(target, mapped)
    print(f"mapped_transcript: {target}")
    return target


def write_metrics(
    conversation: str,
    *,
    long_silence_seconds: float = 2.0,
    output_path: Path | None = None,
) -> Path:
    input_path = _resolve_transcript_path(conversation)
    data = read_json(input_path)
    if not isinstance(data, list):
        raise ValueError("Transcript JSON must contain a list of segments.")

    metrics = compute_basic_metrics(data, long_silence_seconds=long_silence_seconds)
    target = output_path or input_path.with_name(f"{input_path.stem}.metrics.json")
    write_json(target, metrics)
    print(f"metrics: {target}")
    return target


def write_events(
    conversation: str,
    *,
    min_overlap_seconds: float = 0.3,
    min_previous_turn_seconds: float = 1.0,
    output_path: Path | None = None,
) -> Path:
    input_path = _resolve_transcript_path(conversation)
    data = read_json(input_path)
    if not isinstance(data, list):
        raise ValueError("Transcript JSON must contain a list of segments.")

    events = detect_overlap_events(
        data,
        min_overlap_seconds=min_overlap_seconds,
        min_previous_turn_seconds=min_previous_turn_seconds,
    )
    target = output_path or input_path.with_name(f"{input_path.stem}.events.json")
    write_json(target, events)
    print(f"events: {target}")
    return target


def write_communication_report(
    conversation: str,
    *,
    metrics_path: Path | None = None,
    events_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    input_path = _resolve_transcript_path(conversation)
    transcript_data = read_json(input_path)
    if not isinstance(transcript_data, list):
        raise ValueError("Transcript JSON must contain a list of segments.")

    metrics = _read_or_compute_metrics(input_path, transcript_data, metrics_path)
    events = _read_or_compute_events(input_path, transcript_data, events_path)
    report = build_communication_markdown_report(
        source_name=input_path.name,
        transcript_segments=transcript_data,
        metrics=metrics,
        events=events,
    )
    target = output_path or Path("data/reports") / f"{input_path.stem}.communication.md"
    write_markdown_report(target, report)
    print(f"report: {target}")
    return target


def check_report_safety(report_path: Path) -> list[dict[str, str]]:
    findings = find_forbidden_language(report_path.read_text(encoding="utf-8"))
    if findings:
        print(f"safety_check: failed ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding['term']}: {finding['reason']}")
        raise SystemExit(1)
    print("safety_check: passed")
    return findings


def _read_or_compute_metrics(input_path: Path, transcript_data: list[dict], metrics_path: Path | None) -> dict:
    path = metrics_path or input_path.with_name(f"{input_path.stem}.metrics.json")
    if path.exists():
        data = read_json(path)
        if isinstance(data, dict):
            return data
        raise ValueError("Metrics JSON must contain an object.")
    return compute_basic_metrics(transcript_data)


def _read_or_compute_events(input_path: Path, transcript_data: list[dict], events_path: Path | None) -> list[dict]:
    path = events_path or input_path.with_name(f"{input_path.stem}.events.json")
    if path.exists():
        data = read_json(path)
        if isinstance(data, list):
            return data
        raise ValueError("Events JSON must contain a list.")
    return detect_overlap_events(transcript_data)


def _resolve_transcript_path(conversation: str) -> Path:
    path = Path(conversation)
    if path.suffix == ".json":
        return path

    transcript_dir = Path("data/transcripts")
    merged_path = transcript_dir / f"{conversation}.merged.json"
    if merged_path.exists():
        return merged_path
    return transcript_dir / f"{conversation}.segments.json"


def _load_reference_transcript(audio_file: Path, speech_segments: list[dict]) -> list[dict]:
    reference_path = audio_file.with_name(f"{audio_file.stem}_reference.md")
    if not reference_path.exists():
        return []

    turns: list[str] = []
    pattern = re.compile(r"^\s*\d+\.\s+(.+?)\s*$")
    for line in reference_path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            turns.append(match.group(1))

    transcript: list[dict] = []
    for index, text in enumerate(turns, start=1):
        if index <= len(speech_segments):
            start = float(speech_segments[index - 1]["start"])
            end = float(speech_segments[index - 1]["end"])
        else:
            start = float(index - 1) * 2.0
            end = start + 1.5
        transcript.append(
            {
                "segment_id": f"ref_{index:04d}",
                "start": round(start, 3),
                "end": round(end, 3),
                "speaker": None,
                "text": text,
                "confidence": "reference",
                "flags": ["reference_transcript"],
            }
        )
    return transcript


if __name__ == "__main__":
    main()
