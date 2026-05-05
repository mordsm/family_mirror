# Family Mirror

Family Mirror is a private, local-first MVP for Hebrew family conversation transcription.

This first stage is intentionally technical and limited:

- convert one local audio file to normalized WAV
- detect speech regions
- transcribe Hebrew locally with `faster-whisper`
- write JSON files with timestamps
- write a basic Hebrew Markdown report

It does not diagnose, judge, identify who is right, or analyze family members.

## Privacy

The default design is local-only. Audio and transcripts stay on this machine. The project does not add analytics, telemetry, cloud services, or paid APIs.

Do not upload family recordings to any external service unless you explicitly decide to change the project policy later.

## Install

Install Python dependencies:

```powershell
cd C:\workspace\family_mirror
uv sync --extra transcription --extra vad --extra test
```

Install `ffmpeg` and make sure it is available on `PATH`:

```powershell
ffmpeg -version
```

If your machine is weak, edit `config.yaml` and use a smaller Whisper model, such as `small` or `base`.

## Process One File

Put an audio file under `data/input`, then run:

```powershell
uv run python -m src.main process data/input/family_call.m4a
```

Expected outputs:

```text
data/processed/family_call.wav
data/transcripts/family_call.speech_segments.json
data/transcripts/family_call.segments.json
data/reports/family_call.report.md
```

When `--speaker-segments` is provided, this is also written:

```text
data/transcripts/family_call.merged.json
```

For a quick conversion/VAD/report smoke test without Whisper:

```powershell
uv run python -m src.main process data/input/family_call.m4a --skip-transcription
```

If you already have diarization-style speaker timestamps, you can merge them into the transcript:

```powershell
uv run python -m src.main process data/input/family_call.m4a --speaker-segments data/transcripts/family_call.speakers.json
```

Speaker segment input:

```json
[
  {"start": 0.53, "end": 4.8, "speaker": "Speaker_1"}
]
```

To manually map generic speaker labels to names after a merged transcript exists:

```powershell
uv run python -m src.main map-speakers family_call --speaker Speaker_1 --name "משה" --speaker Speaker_2 --name "דויד"
```

This writes:

```text
data/transcripts/family_call.merged.mapped.json
```

The mapping is explicit only. Family Mirror does not guess real identities from audio or text.

To compute basic observable metrics from a transcript:

```powershell
uv run python -m src.main metrics family_call
```

This prefers `data/transcripts/family_call.merged.json` when it exists, and writes:

```text
data/transcripts/family_call.merged.metrics.json
```

You can also pass a specific transcript JSON:

```powershell
uv run python -m src.main metrics data/transcripts/family_call.merged.mapped.json --long-silence-seconds 2.0
```

To detect cautious overlap and interruption-candidate events:

```powershell
uv run python -m src.main events data/transcripts/family_call.merged.mapped.json
```

This writes:

```text
data/transcripts/family_call.merged.mapped.events.json
```

Events are candidates only. A timestamp overlap is evidence of overlapping speech, not proof of intent.

To build a cautious Markdown communication report from an existing transcript:

```powershell
uv run python -m src.main report data/transcripts/family_call.merged.mapped.json
```

This writes:

```text
data/reports/family_call.merged.mapped.communication.md
```

If matching `.metrics.json` or `.events.json` files exist beside the transcript, the report uses them. Otherwise it computes the descriptive metrics and candidate events while building the report.

To scan a generated report for forbidden blame, diagnosis, or person-labeling language:

```powershell
uv run python -m src.main check-report data/reports/family_call.merged.mapped.communication.md
```

The check exits with an error if risky terms are found.

## Output Files

Speech segments:

```json
[
  {"start": 0.53, "end": 4.8}
]
```

Transcript segments:

```json
[
  {
    "segment_id": "seg_0001",
    "start": 0.53,
    "end": 4.8,
    "speaker": null,
    "text": "אני חושב שצריך לדבר על זה.",
    "confidence": "medium",
    "flags": []
  }
]
```

## Tests

```powershell
uv run --extra test pytest
```

## Current Limitations

- No speaker diarization yet.
- Speaker alignment can consume manual or externally generated speaker timestamps, but it does not create them yet.
- Speaker names are manual mappings only; the system does not infer identities.
- No communication-pattern analysis yet.
- Basic metrics are descriptive only: speaking time, turn counts, average turn length, and long silences.
- Overlap and interruption outputs are candidate events with evidence and uncertainty, not blame statements.
- The communication report summarizes only descriptive metrics and candidate events.
- `check-report` scans generated Markdown for forbidden blame, diagnosis, and person-labeling language.
- No psychological analysis.
- Whisper transcription quality depends on audio quality, model size, and CPU speed.
- Energy VAD fallback is simple and less accurate than Silero.
- Reports are for reflection only and must be checked manually.

Every report includes this disclaimer:

> הדוח הוא כלי עזר להתבוננות בדפוסי תקשורת בלבד. הוא אינו אבחון פסיכולוגי, אינו קובע כוונות, ואינו מחליף איש מקצוע. במקטעים עם דיבור חופף, רעש או תמלול לא ברור — רמת הביטחון נמוכה.

## Next Stages

After Stage 1-3 work reliably:

- add speaker diarization
- align speaker labels to transcripts
- add interruption and overlap metrics
- add cautious communication-pattern reporting
