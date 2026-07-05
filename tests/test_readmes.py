"""Tests for per-problem and root README generation."""

from dsa_sync.models import Problem
from dsa_sync.readmes import render_problem_readme, render_root_readme


def _problem(number, title, difficulty, language, topics=None, added_at="2026-01-01T00:00:00"):
    return Problem(
        number=number,
        title=title,
        slug=title.lower().replace(" ", "-"),
        difficulty=difficulty,
        language=language,
        topics=topics or [],
        added_at=added_at,
    )


def test_render_problem_readme_matches_template():
    problem = _problem(217, "Contains Duplicate", "Easy", "C++", ["Array", "Hash Table"])
    readme = render_problem_readme(problem)

    assert readme.startswith("# 217. Contains Duplicate\n")
    assert "**Difficulty:** Easy" in readme
    assert "**Topics:** Array, Hash Table" in readme
    assert "**Language:** C++" in readme
    assert "**Link:** https://leetcode.com/problems/contains-duplicate/" in readme
    assert "## Approach" in readme
    assert "_Add approach notes._" in readme
    assert "## Complexity" in readme
    assert "- Time: O( )" in readme
    assert "- Space: O( )" in readme


def test_render_problem_readme_no_topics():
    problem = _problem(1, "Two Sum", "Easy", "Python", topics=[])
    readme = render_problem_readme(problem)
    assert "**Topics:** None" in readme


def test_root_readme_statistics_section():
    problems = [_problem(1, "Two Sum", "Easy", "C++")]
    readme = render_root_readme(problems, "LeetCode", 10, "%Y-%m-%d")
    assert "# DSA" in readme
    assert "## Statistics" in readme
    assert "**Total Problems Solved:** 1" in readme
    assert "**Last Updated:**" in readme


def test_root_readme_languages_sorted_by_count_desc():
    problems = [
        _problem(1, "Two Sum", "Easy", "Python"),
        _problem(2, "Add Two Numbers", "Medium", "C++"),
        _problem(3, "Longest Substring", "Medium", "C++"),
    ]
    readme = render_root_readme(problems, "LeetCode", 10, "%Y-%m-%d")
    languages_section = readme.split("## Languages")[1].split("## Difficulty")[0]
    assert languages_section.index("C++") < languages_section.index("Python")


def test_root_readme_difficulty_table_has_all_three_rows():
    problems = [_problem(1, "Two Sum", "Easy", "C++")]
    readme = render_root_readme(problems, "LeetCode", 10, "%Y-%m-%d")
    difficulty_section = readme.split("## Difficulty")[1].split("## Recently Solved")[0]
    assert "| Easy | 1 |" in difficulty_section
    assert "| Medium | 0 |" in difficulty_section
    assert "| Hard | 0 |" in difficulty_section


def test_root_readme_recently_solved_ordered_by_added_at_desc():
    problems = [
        _problem(1, "Two Sum", "Easy", "C++", added_at="2026-01-01T00:00:00"),
        _problem(2, "Add Two Numbers", "Medium", "C++", added_at="2026-02-01T00:00:00"),
    ]
    readme = render_root_readme(problems, "LeetCode", 10, "%Y-%m-%d")
    recent_section = readme.split("## Recently Solved")[1].split("## Problem Index")[0]
    assert recent_section.index("Add Two Numbers") < recent_section.index("Two Sum")


def test_root_readme_recently_solved_respects_count_limit():
    problems = [_problem(i, f"Problem {i}", "Easy", "C++", added_at=f"2026-01-{i:02d}T00:00:00") for i in range(1, 6)]
    readme = render_root_readme(problems, "LeetCode", 3, "%Y-%m-%d")
    recent_section = readme.split("## Recently Solved")[1].split("## Problem Index")[0]
    assert recent_section.count("](LeetCode/") == 3


def test_root_readme_problem_index_sorted_by_number_asc():
    problems = [
        _problem(217, "Contains Duplicate", "Easy", "C++"),
        _problem(1, "Two Sum", "Easy", "Python"),
    ]
    readme = render_root_readme(problems, "LeetCode", 10, "%Y-%m-%d")
    index_section = readme.split("## Problem Index")[1]
    assert index_section.index("Two Sum") < index_section.index("Contains Duplicate")


def test_root_readme_problem_index_links_to_folder_and_solution():
    problems = [_problem(217, "Contains Duplicate", "Easy", "C++")]
    readme = render_root_readme(problems, "LeetCode", 10, "%Y-%m-%d")
    assert "LeetCode/0217-Contains-Duplicate" in readme
    assert "LeetCode/0217-Contains-Duplicate/solution.cpp" in readme
