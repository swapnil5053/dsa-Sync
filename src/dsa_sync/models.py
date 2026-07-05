"""Core data model for a solved problem."""

from dataclasses import dataclass, field

from .languages import extension_for
from .naming import folder_name

LEETCODE_PROBLEM_BASE_URL = "https://leetcode.com/problems"


@dataclass
class Problem:
    """A single solved LeetCode problem and its solution metadata."""

    number: int
    title: str
    slug: str
    difficulty: str
    language: str
    topics: list[str] = field(default_factory=list)
    added_at: str = ""

    @property
    def folder(self) -> str:
        """Deterministic folder name for this problem, e.g. '0217-Contains-Duplicate'."""
        return folder_name(self.number, self.title)

    @property
    def solution_filename(self) -> str:
        """Solution filename derived from the language map, e.g. 'solution.cpp'."""
        return f"solution.{extension_for(self.language)}"

    @property
    def url(self) -> str:
        """Public LeetCode problem URL."""
        return f"{LEETCODE_PROBLEM_BASE_URL}/{self.slug}/"

    def to_dict(self) -> dict:
        """Serialize to the plain dict shape stored in problems.json."""
        return {
            "number": self.number,
            "title": self.title,
            "slug": self.slug,
            "difficulty": self.difficulty,
            "language": self.language,
            "topics": self.topics,
            "folder": self.folder,
            "added_at": self.added_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Problem":
        """Deserialize from the dict shape stored in problems.json."""
        return cls(
            number=data["number"],
            title=data["title"],
            slug=data.get("slug", ""),
            difficulty=data.get("difficulty", ""),
            language=data.get("language", ""),
            topics=list(data.get("topics", [])),
            added_at=data.get("added_at", ""),
        )
