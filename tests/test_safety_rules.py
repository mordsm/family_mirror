from src.analysis.safety_rules import find_forbidden_language
from src.reporting.report_markdown import build_communication_markdown_report


def test_find_forbidden_language_detects_hebrew_and_english_terms():
    findings = find_forbidden_language("הוא אשם וזה manipulative.")

    assert {"term": "אשם", "reason": "Avoid blame language."} in findings
    assert {"term": "manipulative", "reason": "Avoid personality labeling."} in findings


def test_find_forbidden_language_allows_cautious_observable_terms():
    findings = find_forbidden_language("קטיעה אפשרית ודיבור חופף עם רמת ביטחון בינונית.")

    assert findings == []


def test_communication_report_passes_safety_rules():
    report = build_communication_markdown_report(
        source_name="safe.json",
        transcript_segments=[],
        metrics={"total_segments": 0, "conversation_end": 0.0, "speakers": {}, "long_silences": []},
        events=[],
    )

    assert find_forbidden_language(report) == []
