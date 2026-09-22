import re

SENSATIONAL_PHRASES = [
    "breaking",
    "shocking",
    "share before deleted",
    "share before it's deleted",
    "share before it gets deleted",
]


def _shouting_ratio(text: str) -> float:
    """% of alphabetic characters that are uppercase."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    upper = [c for c in letters if c.isupper()]
    return len(upper) / len(letters)


def compute_flags(text: str, source_link: str | None) -> tuple[list[str], str]:
    """
    Returns (flags, risk_level).
    Rules (fixed, per brief):
      - "breaking" / "shocking" / "share before deleted" (case-insensitive) -> Sensational
      - >50% of letters are CAPS -> Shouting
      - no source link -> Unsourced
      - 2+ flags -> High Risk
    """
    flags: list[str] = []
    lowered = text.lower()

    if any(phrase in lowered for phrase in SENSATIONAL_PHRASES):
        flags.append("Sensational")

    if _shouting_ratio(text) > 0.5:
        flags.append("Shouting")

    if not source_link or not source_link.strip():
        flags.append("Unsourced")

    risk_level = "High Risk" if len(flags) >= 2 else "Normal"
    return flags, risk_level
