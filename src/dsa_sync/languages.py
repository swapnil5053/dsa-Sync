"""Language name to file extension mapping, plus alias normalization."""

# Canonical language name -> solution file extension. The only place this mapping lives.
LANGUAGE_EXTENSIONS: dict[str, str] = {
    "C++": "cpp",
    "Python": "py",
    "Java": "java",
    "JavaScript": "js",
    "TypeScript": "ts",
    "Go": "go",
    "Rust": "rs",
    "Kotlin": "kt",
    "C#": "cs",
    "Ruby": "rb",
    "C": "c",
}

# Common aliases users might type -> canonical language name.
LANGUAGE_ALIASES: dict[str, str] = {
    "cpp": "C++",
    "c++": "C++",
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "rs": "Rust",
    "kotlin": "Kotlin",
    "kt": "Kotlin",
    "c#": "C#",
    "csharp": "C#",
    "cs": "C#",
    "ruby": "Ruby",
    "rb": "Ruby",
    "c": "C",
}


def normalize_language(raw: str) -> str | None:
    """Normalize a user-entered language name/alias to its canonical form, or None if unknown."""
    key = raw.strip().lower()
    if not key:
        return None
    if key in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[key]
    for canonical in LANGUAGE_EXTENSIONS:
        if canonical.lower() == key:
            return canonical
    return None


def extension_for(language: str) -> str:
    """Return the file extension for a canonical language name, defaulting to 'txt'."""
    return LANGUAGE_EXTENSIONS.get(language, "txt")
