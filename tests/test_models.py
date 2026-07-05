"""Tests for the Problem dataclass and its derived properties."""

from dsa_sync.models import Problem


def _make_problem(**overrides) -> Problem:
    defaults = dict(
        number=217,
        title="Contains Duplicate",
        slug="contains-duplicate",
        difficulty="Easy",
        language="C++",
        topics=["Array", "Hash Table"],
        added_at="2026-07-05T14:32:00",
    )
    defaults.update(overrides)
    return Problem(**defaults)


def test_folder_property():
    assert _make_problem().folder == "0217-Contains-Duplicate"


def test_solution_filename_from_language_map():
    assert _make_problem(language="Python").solution_filename == "solution.py"


def test_solution_filename_unknown_language_defaults_to_txt():
    assert _make_problem(language="COBOL").solution_filename == "solution.txt"


def test_url_uses_slug():
    assert _make_problem().url == "https://leetcode.com/problems/contains-duplicate/"


def test_to_dict_contains_folder():
    data = _make_problem().to_dict()
    assert data["folder"] == "0217-Contains-Duplicate"
    assert data["number"] == 217
    assert data["topics"] == ["Array", "Hash Table"]


def test_from_dict_round_trip():
    problem = _make_problem()
    restored = Problem.from_dict(problem.to_dict())
    assert restored == problem


def test_from_dict_defaults_missing_topics():
    data = {
        "number": 1,
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": "Easy",
        "language": "C++",
        "added_at": "2026-07-05T14:32:00",
    }
    problem = Problem.from_dict(data)
    assert problem.topics == []
