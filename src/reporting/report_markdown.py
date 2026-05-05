from __future__ import annotations

from pathlib import Path

from src.utils.timecodes import format_timecode


DISCLAIMER_HE = (
    "הדוח הוא כלי עזר להתבוננות בדפוסי תקשורת בלבד. "
    "הוא אינו אבחון פסיכולוגי, אינו קובע כוונות, ואינו מחליף איש מקצוע. "
    "במקטעים עם דיבור חופף, רעש או תמלול לא ברור — רמת הביטחון נמוכה."
)


def build_basic_markdown_report(
    *,
    source_name: str,
    speech_segments: list[dict],
    transcript_segments: list[dict],
) -> str:
    duration = transcript_segments[-1]["end"] if transcript_segments else 0
    lines = [
        "# דוח בסיסי - Family Mirror",
        "",
        f"**קובץ מקור:** {source_name}",
        f"**משך מתומלל:** {format_timecode(duration)}",
        f"**מספר מקטעי דיבור שזוהו:** {len(speech_segments)}",
        f"**מספר מקטעי תמלול:** {len(transcript_segments)}",
        "",
        "## הערת זהירות",
        "",
        DISCLAIMER_HE,
        "",
        "## תמלול לפי זמנים",
        "",
    ]
    if not transcript_segments:
        lines.extend(
            [
                "לא הופקו מקטעי תמלול. ייתכן שחסרה התקנת faster-whisper, שהאודיו שקט מדי, או שאיכות ההקלטה נמוכה.",
                "",
            ]
        )
    for segment in transcript_segments:
        start = format_timecode(float(segment["start"]))
        end = format_timecode(float(segment["end"]))
        text = segment.get("text", "")
        confidence = segment.get("confidence", "medium")
        speaker = segment.get("speaker") or "לא זוהה"
        flags = ", ".join(segment.get("flags", [])) or "ללא"
        lines.extend(
            [
                f"### {start}–{end}",
                "",
                f"**דובר:** {speaker}  ",
                f"**רמת ביטחון:** {confidence}  ",
                f"**סימונים:** {flags}",
                "",
                text,
                "",
            ]
        )
    lines.extend(
        [
            "## מגבלות השלב הנוכחי",
            "",
            "- בשלב זה אין יצירת זיהוי דוברים אוטומטי.",
            "- אם סופקו זמני דוברים, השיוך לדוברים מבוסס על חפיפת זמנים ויש לבדוק אותו ידנית.",
            "- בשלב זה אין ניתוח רגשי או משפחתי.",
            "- יש לבדוק ידנית מקטעים עם רעש, שתיקות ארוכות או דיבור חופף.",
            "",
        ]
    )
    return "\n".join(lines)


def build_communication_markdown_report(
    *,
    source_name: str,
    transcript_segments: list[dict],
    metrics: dict,
    events: list[dict],
) -> str:
    lines = [
        "# דוח תקשורת זהיר - Family Mirror",
        "",
        f"**מקור:** {source_name}",
        f"**משך מתומלל:** {format_timecode(float(metrics.get('conversation_end', 0.0)))}",
        f"**מספר מקטעי תמלול:** {metrics.get('total_segments', len(transcript_segments))}",
        "",
        "## הערת זהירות",
        "",
        DISCLAIMER_HE,
        "",
        "## מדדים תיאוריים",
        "",
    ]

    speakers = metrics.get("speakers", {})
    if speakers:
        for speaker, stats in speakers.items():
            lines.append(
                "- "
                f"{speaker}: זמן דיבור {format_timecode(float(stats.get('total_speaking_seconds', 0.0)))}, "
                f"{int(stats.get('turn_count', 0))} תורות, "
                f"אורך תור ממוצע {format_timecode(float(stats.get('average_turn_seconds', 0.0)))}"
            )
    else:
        lines.append("- לא נמצאו דוברים משויכים במדדים.")

    lines.extend(["", "## שתיקות ארוכות", ""])
    long_silences = metrics.get("long_silences", [])
    if long_silences:
        for silence in long_silences:
            lines.append(
                "- "
                f"{format_timecode(float(silence['start']))}–{format_timecode(float(silence['end']))}: "
                f"שתיקה של {format_timecode(float(silence['duration_seconds']))}"
            )
    else:
        lines.append("- לא זוהו שתיקות ארוכות לפי הסף שנבחר.")

    lines.extend(["", "## דיבור חופף וקטיעות אפשריות", ""])
    if events:
        for event in events:
            event_label = "קטיעה אפשרית" if event.get("type") == "interruption_candidate" else "דיבור חופף"
            speakers_text = ", ".join(event.get("speakers", [])) or "לא זוהה"
            lines.extend(
                [
                    f"### {event_label}: {format_timecode(float(event['start']))}–{format_timecode(float(event['end']))}",
                    "",
                    f"- דוברים: {speakers_text}",
                    f"- משך חפיפה: {format_timecode(float(event.get('duration_seconds', 0.0)))}",
                    f"- ראיה: {event.get('evidence', '')}",
                    f"- רמת ביטחון: {event.get('confidence', 'medium')}",
                    f"- הערה: {event.get('note_he', '')}",
                    "",
                ]
            )
    else:
        lines.append("- לא זוהו דיבור חופף או קטיעות אפשריות לפי הסף שנבחר.")

    lines.extend(["", "## תמלול לפי זמנים", ""])
    for segment in transcript_segments:
        start = format_timecode(float(segment["start"]))
        end = format_timecode(float(segment["end"]))
        speaker = segment.get("speaker") or "לא זוהה"
        text = segment.get("text", "")
        flags = ", ".join(segment.get("flags", [])) or "ללא"
        lines.extend(
            [
                f"### {start}–{end}",
                "",
                f"**דובר:** {speaker}  ",
                f"**סימונים:** {flags}",
                "",
                text,
                "",
            ]
        )

    lines.extend(
        [
            "## מגבלות",
            "",
            "- הדוח מתאר זמנים, דוברים משויכים ואירועי חפיפה בלבד.",
            "- אין בדוח אבחון, קביעה על כוונה, או ייחוס אשמה.",
            "- יש לבדוק ידנית מקטעים עם רעש, דיבור חופף או שיוך דובר לא בטוח.",
            "",
        ]
    )
    return "\n".join(lines)


def write_markdown_report(path: str | Path, content: str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target
