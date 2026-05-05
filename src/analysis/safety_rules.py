from __future__ import annotations


FORBIDDEN_LANGUAGE = {
    "אשם": "Avoid blame language.",
    "מניפולטיבי": "Avoid personality labeling.",
    "מניפולטיבית": "Avoid personality labeling.",
    "נרקיסיסט": "Avoid clinical/personality labels.",
    "נרקיסיסטית": "Avoid clinical/personality labels.",
    "לא יציב": "Avoid mental-state judgments.",
    "לא יציבה": "Avoid mental-state judgments.",
    "מסוכן": "Avoid risk labels unless explicitly reviewed by a human.",
    "מסוכנת": "Avoid risk labels unless explicitly reviewed by a human.",
    "תוקפן": "Avoid person-level aggression labels.",
    "תוקפנית": "Avoid person-level aggression labels.",
    "אגרסיבי": "Avoid person-level aggression labels.",
    "אגרסיבית": "Avoid person-level aggression labels.",
    "caused the escalation": "Avoid assigning causality or blame.",
    "is aggressive": "Avoid person-level aggression labels.",
    "is unstable": "Avoid mental-state judgments.",
    "manipulative": "Avoid personality labeling.",
    "narcissist": "Avoid clinical/personality labels.",
    "dangerous": "Avoid risk labels unless explicitly reviewed by a human.",
}


def find_forbidden_language(text: str) -> list[dict[str, str]]:
    lowered = text.lower()
    findings: list[dict[str, str]] = []
    for term, reason in FORBIDDEN_LANGUAGE.items():
        haystack = lowered if _is_ascii(term) else text
        needle = term.lower() if _is_ascii(term) else term
        if needle in haystack:
            findings.append({"term": term, "reason": reason})
    return findings


def _is_ascii(value: str) -> bool:
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        return False
    return True
