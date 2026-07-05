"""Filename/folder sanitization and naming rules. The only module that owns naming logic."""

import re

# Characters invalid on Windows filesystems (also fine to strip on macOS/Linux).
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')
_WHITESPACE = re.compile(r"\s+")

# Windows reserved device names (case-insensitive, with or without extension).
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def sanitize_component(raw: str) -> str:
    """Strip filesystem-invalid characters and trailing dots/spaces from a path component."""
    cleaned = _INVALID_CHARS.sub("", raw)
    cleaned = cleaned.strip().rstrip(". ")
    if cleaned.upper() in _WINDOWS_RESERVED:
        cleaned = f"_{cleaned}"
    return cleaned or "untitled"


def title_to_hyphenated(title: str) -> str:
    """Convert a problem title to its hyphenated folder form, e.g. 'Contains Duplicate' -> 'Contains-Duplicate'."""
    sanitized = sanitize_component(title)
    hyphenated = _WHITESPACE.sub("-", sanitized)
    return hyphenated


def folder_name(number: int, title: str) -> str:
    """Build the deterministic folder name: '{4-digit number}-{Title-With-Hyphens}'."""
    return f"{number:04d}-{title_to_hyphenated(title)}"
