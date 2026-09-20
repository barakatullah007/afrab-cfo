from typing import List
import re

KEYWORDS = [
    "currency",
    "usd",
    "eur",
    "inr",
    "savings",
    "save",
    "investment",
    "invest",
    "debt",
    "loan",
    "retire",
    "retirement",
    "risk",
    "tolerance",
    "credit",
    "budget",
]


def _extract_lines_with_keywords(messages: List[str]) -> List[str]:
    found = []
    for m in messages:
        low = m.lower()
        for kw in KEYWORDS:
            if kw in low:
                found.append(m.strip())
                break
    return found


def summarize_messages(messages: List[str], max_chars: int = 500) -> str:
    """
    Deterministic summarizer: extract lines that contain financial keywords,
    deduplicate them, and join up to max_chars.

    This does NOT call any LLM and is intentionally simple and deterministic.
    """
    if not messages:
        return ""

    # prefer explicit lines with keywords
    candidates = _extract_lines_with_keywords(messages)

    # fall back to first few messages if none found
    if not candidates:
        candidates = messages[:5]

    # deduplicate while preserving order
    seen = set()
    out = []
    for c in candidates:
        key = re.sub(r"\s+", " ", c.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(c.strip())
        if sum(len(x) for x in out) > max_chars:
            break

    summary = "\n".join(out)
    # ensure summary length limit
    if len(summary) > max_chars:
        summary = summary[: max_chars - 3] + "..."
    return summary
