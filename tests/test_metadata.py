"""Tests for atomic problems.json read/write."""

import json

import pytest

from dsa_sync.exceptions import MetadataError
from dsa_sync.metadata import (
    find_problem,
    load_problems,
    metadata_path,
    save_problems,
    upsert_problem,
)
from dsa_sync.models import Problem


def _problem(number=217, title="Contains Duplicate", added_at="2026-01-01T00:00:00"):
    return Problem(
        number=number,
        title=title,
        slug="contains-duplicate",
        difficulty="Easy",
        language="C++",
        topics=["Array"],
        added_at=added_at,
    )


def test_load_problems_missing_file_returns_empty(tmp_path):
    assert load_problems(tmp_path) == []


def test_save_then_load_round_trip(tmp_path):
    problem = _problem()
    save_problems(tmp_path, [problem])
    loaded = load_problems(tmp_path)
    assert loaded == [problem]


def test_save_problems_no_leftover_temp_file(tmp_path):
    save_problems(tmp_path, [_problem()])
    tmp_file = metadata_path(tmp_path).with_suffix(".tmp")
    assert not tmp_file.exists()
    assert metadata_path(tmp_path).exists()


def test_save_problems_sorted_by_number(tmp_path):
    save_problems(tmp_path, [_problem(number=217), _problem(number=1, title="Two Sum")])
    with metadata_path(tmp_path).open() as fh:
        raw = json.load(fh)
    assert [entry["number"] for entry in raw] == [1, 217]


def test_load_problems_malformed_json_raises(tmp_path):
    path = metadata_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(MetadataError):
        load_problems(tmp_path)


def test_load_problems_non_list_raises(tmp_path):
    path = metadata_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(MetadataError):
        load_problems(tmp_path)


def test_find_problem_found_and_missing():
    problems = [_problem(number=1), _problem(number=217)]
    assert find_problem(problems, 217).number == 217
    assert find_problem(problems, 999) is None


def test_upsert_problem_replaces_not_duplicates():
    problems = [_problem(number=217, title="Contains Duplicate")]
    updated = upsert_problem(problems, _problem(number=217, title="Contains Duplicate II"))
    assert len(updated) == 1
    assert updated[0].title == "Contains Duplicate II"


def test_upsert_problem_appends_new_number():
    problems = [_problem(number=217)]
    updated = upsert_problem(problems, _problem(number=1, title="Two Sum"))
    assert {p.number for p in updated} == {217, 1}
