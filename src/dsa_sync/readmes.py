"""Per-problem README and root README generation, fully derived from problems.json."""

from collections import Counter
from datetime import datetime

from .models import Problem

ROOT_DESCRIPTION = (
    "A personal archive of solved LeetCode problems, organized by problem number. "
    "Maintained automatically by dsa-sync."
)

DIFFICULTY_ORDER = ["Easy", "Medium", "Hard"]


def render_problem_readme(problem: Problem) -> str:
    """Render the per-problem README, with approach/complexity left as placeholders."""
    topics = ", ".join(problem.topics) if problem.topics else "None"
    return (
        f"# {problem.number}. {problem.title}\n\n"
        f"**Difficulty:** {problem.difficulty}\n"
        f"**Topics:** {topics}\n"
        f"**Language:** {problem.language}\n"
        f"**Link:** {problem.url}\n\n"
        "## Approach\n\n"
        "_Add approach notes._\n\n"
        "## Complexity\n\n"
        "- Time: O( )\n"
        "- Space: O( )\n"
    )


def _language_table(problems: list[Problem]) -> str:
    counts = Counter(p.language for p in problems)
    rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    lines = ["| Language | Count |", "| --- | --- |"]
    for language, count in rows:
        lines.append(f"| {language} | {count} |")
    return "\n".join(lines)


def _difficulty_table(problems: list[Problem]) -> str:
    counts = Counter(p.difficulty for p in problems)
    lines = ["| Difficulty | Count |", "| --- | --- |"]
    for difficulty in DIFFICULTY_ORDER:
        lines.append(f"| {difficulty} | {counts.get(difficulty, 0)} |")
    return "\n".join(lines)


def _recently_solved_table(problems: list[Problem], leetcode_dir: str, count: int) -> str:
    ordered = sorted(problems, key=lambda p: p.added_at, reverse=True)[:count]
    lines = ["| # | Problem | Difficulty | Language |", "| --- | --- | --- | --- |"]
    for problem in ordered:
        link = f"{leetcode_dir}/{problem.folder}"
        lines.append(
            f"| {problem.number} | [{problem.title}]({link}) | {problem.difficulty} | {problem.language} |"
        )
    return "\n".join(lines)


def _problem_index_table(problems: list[Problem], leetcode_dir: str) -> str:
    ordered = sorted(problems, key=lambda p: p.number)
    lines = [
        "| # | Problem | Difficulty | Topics | Language | Solution |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for problem in ordered:
        folder_link = f"{leetcode_dir}/{problem.folder}"
        solution_link = f"{leetcode_dir}/{problem.folder}/{problem.solution_filename}"
        topics = ", ".join(problem.topics) if problem.topics else "-"
        lines.append(
            f"| {problem.number} | [{problem.title}]({folder_link}) | {problem.difficulty} | "
            f"{topics} | {problem.language} | [Solution]({solution_link}) |"
        )
    return "\n".join(lines)


def render_root_readme(
    problems: list[Problem],
    leetcode_dir: str,
    recently_solved_count: int,
    date_format: str,
) -> str:
    """Render the full root README from scratch, based only on the given problems."""
    last_updated = datetime.now().strftime(date_format)
    total = len(problems)

    sections = [
        "# DSA\n",
        f"{ROOT_DESCRIPTION}\n",
        "## Statistics\n",
        f"- **Total Problems Solved:** {total}\n"
        f"- **Last Updated:** {last_updated}\n",
        "## Languages\n",
        _language_table(problems) + "\n",
        "## Difficulty\n",
        _difficulty_table(problems) + "\n",
        "## Recently Solved\n",
        _recently_solved_table(problems, leetcode_dir, recently_solved_count) + "\n",
        "## Problem Index\n",
        _problem_index_table(problems, leetcode_dir) + "\n",
    ]
    return "\n".join(sections)
