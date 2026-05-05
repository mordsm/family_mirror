AGENTS.md — Project Brief for Codex
# Project: Family Mirror

## 1. Project purpose

Family Mirror is a private, local-first system for analyzing Hebrew family conversations.

The goal is NOT diagnosis, NOT judgment, and NOT determining who is right or wrong.

The goal is to help identify communication patterns:
- emotional load
- escalation
- interruptions
- overlapping speech
- moments of support
- moments of repair
- topics that increase tension
- communication patterns around insecurity, pressure, and social misunderstanding

This project is mainly for private family reflection with psychological sensitivity.

## 2. Family context and sensitivity

This project is used for a private family.

Important context:
- The conversations are in Hebrew.
- One son is coping with mental-health difficulties such as depression and anxiety.
- Another son, Yitav, may react aggressively, but this is understood as connected mainly to insecurity and social-communication difficulties.
- The system must never label people as “bad”, “aggressive”, “manipulative”, “unstable”, “dangerous”, “narcissistic”, etc.
- The system should describe observable behavior, not diagnose personality or intent.

Bad output:
- "Yitav was aggressive."
- "David is unstable."
- "Moshe caused the escalation."

Good output:
- "At 04:12–04:45, there was increased vocal intensity."
- "Speaker_2 was interrupted twice before completing the sentence."
- "This segment may indicate emotional load, but confidence is low because of overlapping speech."
- "The conversation moved from clarification to defensiveness."

## 3. Core design principle

Build a communication-reflection tool, not a psychological diagnosis tool.

The system should:
- describe events
- identify patterns
- show evidence
- include uncertainty
- avoid blame
- avoid clinical diagnosis
- avoid strong claims from weak data

## 4. Privacy and data policy

This project must be privacy-first.

Requirements:
- Prefer fully local processing.
- Do not send audio or transcripts to external APIs by default.
- Do not require paid services.
- Do not require cloud infrastructure.
- Store files locally.
- Support deletion of raw audio after processing.
- Keep generated reports local.
- Do not add analytics, telemetry, or external tracking.
- Do not upload family conversations anywhere unless explicitly requested later.

## 5. Cost constraint

Use free tools only.

Preferred tools:
- Python
- ffmpeg
- faster-whisper
- Whisper models
- silero-vad
- pyannote.audio if usable locally/free
- pydub
- numpy
- pandas
- markdown or HTML reports
- optional SQLite for local storage

Avoid:
- paid APIs
- paid transcription services
- paid cloud diarization services
- SaaS dependencies
- mandatory GPU-only design

## 6. Language constraint

The conversations are in Hebrew.

The system must:
- transcribe Hebrew audio
- preserve Hebrew text direction correctly
- generate Hebrew reports
- support Hebrew speaker labels
- handle mixed Hebrew/English words if present

Preferred transcription:
- faster-whisper
- Whisper model: start with `medium`, allow `large-v3` if hardware permits
- allow smaller models for weaker machines

## 7. MVP scope

Build the MVP in stages.

### Stage 1 — Audio preparation
Input:
- mp3, m4a, wav, opus, or phone-recorded audio

Output:
- normalized wav file
- mono
- 16kHz
- consistent volume if possible

Use:
- ffmpeg

### Stage 2 — Voice Activity Detection
Goal:
- detect where speech exists
- remove or mark long silences
- produce speech segments with timestamps

Use:
- silero-vad preferred
- fallback: simple energy-based VAD if silero is unavailable

Output example:
```json
[
  {"start": 0.53, "end": 4.80},
  {"start": 6.20, "end": 12.40}
]

Stage 3 — Transcription
Goal:
transcribe Hebrew speech using local Whisper/faster-whisper
Output:
[
  {
    "start": 0.53,
    "end": 4.80,
    "text": "אני חושב שצריך לדבר על זה."
  }
]

Stage 4 — Speaker diarization
Goal:
identify who spoke when
initially use generic labels: Speaker_1, Speaker_2, Speaker_3
Important:
Do not assume real identities automatically.
Provide a way for the user to map Speaker_1 to a real name later.
Output:
[
  {
    "start": 0.50,
    "end": 5.10,
    "speaker": "Speaker_1"
  },
  {
    "start": 5.20,
    "end": 9.00,
    "speaker": "Speaker_2"
  }
]

Stage 5 — Merge transcription and speakers
Goal:
align Whisper segments with diarization segments using timestamp overlap.
Output:
[
  {
    "start": 0.53,
    "end": 4.80,
    "speaker": "Speaker_1",
    "text": "אני חושב שצריך לדבר על זה.",
    "confidence": "medium"
  }
]

Stage 6 — Basic communication metrics
Compute:
total speaking time per speaker
number of turns per speaker
average turn length
interruptions
overlapping speech
long silences
emotional-load candidates
escalation candidates
Stage 7 — Hebrew report
Generate a local Markdown or HTML report in Hebrew.
Report should include:
neutral summary
main topics
speaking-time distribution
interruptions
overlap / unclear segments
moments of escalation
moments of repair
suggestions for better next conversation
uncertainty notes
8. Required output style
Reports must be careful, non-accusatory, and evidence-based.
Use formulations like:
"ייתכן ש..."
"נראה שבמקטע הזה..."
"רמת הביטחון נמוכה בגלל דיבור חופף."
"המקטע מצביע על עומס רגשי אפשרי."
"כדאי לבדוק ידנית את הקטע הזה."
Avoid:
"הוא תמיד..."
"היא אף פעם..."
"הוא גרם ל..."
"הוא אגרסיבי."
"היא מניפולטיבית."
"זה מוכיח ש..."
9. Special handling for Yitav
The system should not label Yitav as aggressive.
When analyzing segments involving Yitav, prefer language such as:
"תגובה בעוצמה גבוהה"
"עומס רגשי אפשרי"
"תחושת לחץ אפשרית"
"ייתכן שהמקטע קשור לחוסר ביטחון או קושי בהבנת הכוונה החברתית"
"כדאי לאפשר יותר זמן תגובה"
"כדאי לשאול שאלה אחת בכל פעם"
"כדאי להימנע מדיבור עליו במקום איתו"
Never output:
"Yitav is aggressive"
"Yitav is the problem"
"Yitav attacked"
"Yitav is unstable"
10. Technical architecture
Recommended folder structure:
family-mirror/
  AGENTS.md
  README.md
  requirements.txt
  config.yaml
  data/
    input/
    processed/
    transcripts/
    reports/
  src/
    main.py
    audio/
      convert.py
      vad.py
      normalize.py
    transcription/
      whisper_transcriber.py
    diarization/
      diarizer.py
      speaker_mapper.py
    alignment/
      align_segments.py
    analysis/
      metrics.py
      interruptions.py
      emotional_load.py
      topic_detection.py
      safety_rules.py
    reporting/
      report_markdown.py
      report_html.py
    storage/
      local_store.py
    utils/
      timecodes.py
      hebrew.py
      logging.py
  tests/
    test_alignment.py
    test_metrics.py
    test_safety_rules.py
    test_interruptions.py

11. Suggested CLI
Build a command-line interface first.
Example commands:
python -m src.main process data/input/family_call.m4a

Expected outputs:
data/processed/family_call.wav
data/transcripts/family_call.segments.json
data/transcripts/family_call.speakers.json
data/transcripts/family_call.merged.json
data/reports/family_call.report.md

Optional later:
python -m src.main map-speakers family_call --speaker Speaker_1 --name "משה"
python -m src.main report family_call
python -m src.main delete-audio family_call

12. Configuration file
Create config.yaml:
project:
  name: "Family Mirror"
  language: "he"

privacy:
  local_only: true
  delete_raw_audio_after_processing: false
  allow_external_api: false

audio:
  sample_rate: 16000
  mono: true
  normalize_volume: true

vad:
  tool: "silero"
  min_speech_duration_ms: 250
  min_silence_duration_ms: 500

transcription:
  engine: "faster-whisper"
  model: "medium"
  language: "he"
  compute_type: "int8"

diarization:
  engine: "pyannote"
  enabled: true
  fallback_without_diarization: true

analysis:
  detect_interruptions: true
  detect_overlap: true
  detect_emotional_load: true
  detect_topics: true
  cautious_mode: true

report:
  format: "markdown"
  language: "he"
  include_uncertainty: true
  include_evidence_segments: true

13. Data model
Use JSON for intermediate files.
Transcript segment
{
  "segment_id": "seg_0001",
  "start": 12.45,
  "end": 18.20,
  "speaker": "Speaker_1",
  "text": "אני רוצה להסביר למה זה הפריע לי.",
  "confidence": "medium",
  "flags": []
}

Flags
Possible flags:
[
  "overlap",
  "interruption_candidate",
  "high_emotional_load_candidate",
  "low_confidence_audio",
  "long_silence_before",
  "repair_attempt",
  "supportive_statement"
]

Analysis event
{
  "event_id": "event_0001",
  "type": "interruption_candidate",
  "start": 45.10,
  "end": 48.90,
  "speakers": ["Speaker_1", "Speaker_2"],
  "evidence": "Speaker_2 starts before Speaker_1 segment ends",
  "confidence": "medium",
  "note_he": "ייתכן שהייתה קטיעה, אך יש דיבור חופף ולכן רמת הביטחון בינונית."
}

14. Interruption detection logic
Initial heuristic:
If Speaker_B starts speaking before Speaker_A finished,
and overlap duration is greater than threshold,
mark as interruption candidate.
Do not state as fact.
Use:
"קטיעה אפשרית"
not:
"קטיעה ודאית"
Parameters:
interruption:
  min_overlap_ms: 300
  min_previous_turn_duration_ms: 1000
  confidence_when_overlap_clear: "medium"

15. Emotional-load detection
Start with simple rule-based signals. Do not build diagnosis.
Signals:
many interruptions
rapid turn-taking
long silence after direct question
repeated negation
repeated defensive phrases
exclamation markers if present
phrases such as:
"אתם לא מבינים"
"תעזבו אותי"
"לא מקשיבים לי"
"אני לא יכול"
"די"
"מספיק"
"תמיד"
"אף פעם"
Output:
emotional load candidate
not emotion certainty
Good:
במקטע הזה יש סימנים לעומס רגשי אפשרי.

Bad:
הדובר היה בחרדה.

16. Repair and support detection
Detect positive communication patterns too.
Examples:
"אני מבין"
"בוא ננסה שוב"
"סליחה"
"לא התכוונתי"
"אפשר להסביר?"
"אני שומע אותך"
"בוא נעצור רגע"
"מה יעזור לך עכשיו?"
These should be highlighted as useful moments.
17. Hebrew text handling
Requirements:
Preserve Hebrew text in UTF-8.
Markdown report should display Hebrew correctly.
Avoid reversing punctuation manually unless needed.
Do not transliterate Hebrew names.
Use Hebrew labels in final report.
Possible labels:
דובר 1
דובר 2
דובר 3

18. Testing requirements
Write tests for:
timestamp overlap alignment
interruption detection
report generation
safety language filtering
speaker mapping
Hebrew text preservation
Safety test examples:
The report generator must not output:
"אשם"
"מניפולטיבי"
"נרקיסיסט"
"לא יציב"
"מסוכן"
"תוקפן"
"אגרסיבי" when referring to a person
Allowed:
"תגובה בעוצמה גבוהה"
"עומס רגשי אפשרי"
"הסלמה אפשרית"
"קטיעה אפשרית"
19. Development style
Implement incrementally.
Do not build a GUI first.
Priority:
CLI pipeline
JSON outputs
Markdown report
tests
optional small local web UI later
Keep modules small.
Prefer clear code over clever code.
Avoid hidden external dependencies.
Document installation steps.
20. README requirements
README should include:
project purpose
privacy warning
installation
ffmpeg installation note
how to process first file
limitations
ethical warning
example output
troubleshooting
21. Known limitations to mention in the report
Every report should include this disclaimer:
הדוח הוא כלי עזר להתבוננות בדפוסי תקשורת בלבד. הוא אינו אבחון פסיכולוגי, אינו קובע כוונות, ואינו מחליף איש מקצוע. במקטעים עם דיבור חופף, רעש או תמלול לא ברור — רמת הביטחון נמוכה.

22. Premortem
Main ways this project can fail:
It becomes a tool for blaming family members.
It labels Yitav negatively instead of identifying pressure triggers.
The system overstates emotional conclusions.
Speaker diarization is wrong.
Hebrew transcription is inaccurate.
Overlapping speech creates false conclusions.
Audio quality is poor.
Family members feel monitored rather than helped.
Design countermeasures:
cautious language
uncertainty scores
evidence-based claims
local processing
no diagnosis
ability to manually correct speakers
ability to remove sensitive segments
ability to delete raw audio
23. First implementation task
Start by implementing Stage 1–3 only:
Input:
one Hebrew audio file
Output:
converted wav
speech segments
Hebrew transcript with timestamps
Markdown report with only basic transcript and timing
Do not implement psychological analysis yet.
After Stage 1–3 works, implement:
diarization
speaker alignment
communication metrics
cautious report

---

## פרומפט ראשון מומלץ לתת ל־Codex

אחרי שיש תיקייה ריקה עם `AGENTS.md`, תן ל־Codex את המשימה הזו:

```text
Build the initial MVP for Family Mirror according to AGENTS.md.

Implement only:
1. audio conversion with ffmpeg
2. voice activity detection using silero-vad if available, with a simple fallback
3. Hebrew transcription using faster-whisper
4. JSON transcript output with timestamps
5. basic Markdown report in Hebrew
6. README with setup instructions
7. minimal tests for timestamp handling and report generation

Do not implement psychological analysis yet.
Do not add paid APIs.
Do not use external cloud services.
Keep everything local.


החלטה קריטית
אל תבקש מ־Codex לבנות מיד “מערכת ניתוח פסיכולוגית”.
השלב הראשון צריך להיות טכני ויציב:
אודיו → תמלול עברית → זמנים → דוח בסיסי

רק אחרי שזה עובד, מוסיפים זיהוי דוברים, קטיעות, עומס רגשי ודפוסי תקשורת.

