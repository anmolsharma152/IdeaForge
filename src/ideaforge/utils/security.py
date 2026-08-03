"""Security utilities — input sanitization, boundaries, and prompt injection mitigation."""

from __future__ import annotations

import re

# Common prompt injection override markers to neutralize
_INJECTION_PATTERNS = [
    re.compile(r"(?i)\b(ignore previous instructions|forget all instructions|system prompt:|<\|im_start\|>|\[INST\])\b"),
]


def sanitize_prompt_input(text: str, max_length: int = 2000) -> str:
    """Sanitize user input or web search context before injecting into LLM prompts.

    - Truncates to max_length
    - Neutralizes common prompt injection attack vectors
    - Strips invalid non-printable control characters
    """
    if not text:
        return ""

    # Remove non-printable control characters except standard whitespace
    clean_text = "".join(c for c in text if c.isprintable() or c in "\n\r\t")

    # Neutralize injection override attempts by wrapping or neutralizing keywords
    for pattern in _INJECTION_PATTERNS:
        clean_text = pattern.sub("[filtered]", clean_text)

    # Bound maximum input length
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length] + "..."

    return clean_text.strip()


def validate_input_length(val: str, max_len: int = 500, field_name: str = "Input") -> str:
    """Validate string inputs before processing or DB insertion."""
    if not val:
        return ""
    val_str = str(val).strip()
    if len(val_str) > max_len:
        return val_str[:max_len]
    return val_str
