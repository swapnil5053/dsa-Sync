"""Tests for filename/folder sanitization and naming rules."""

from dsa_sync.naming import folder_name, sanitize_component, title_to_hyphenated


def test_folder_name_two_sum():
    assert folder_name(1, "Two Sum") == "0001-Two-Sum"


def test_folder_name_3sum_no_spaces():
    assert folder_name(15, "3Sum") == "0015-3Sum"


def test_folder_name_contains_duplicate():
    assert folder_name(217, "Contains Duplicate") == "0217-Contains-Duplicate"


def test_folder_name_zero_pads_to_four_digits():
    assert folder_name(7, "Reverse Integer").startswith("0007-")


def test_folder_name_large_number_not_truncated():
    assert folder_name(12345, "Some Problem").startswith("12345-")


def test_sanitize_component_strips_windows_invalid_chars():
    assert sanitize_component('a<b>c:d"e/f\\g|h?i*j') == "abcdefghij"


def test_sanitize_component_strips_trailing_dots_and_spaces():
    assert sanitize_component("Trailing Dot. ") == "Trailing Dot"


def test_sanitize_component_handles_windows_reserved_name():
    assert sanitize_component("CON").startswith("_")


def test_sanitize_component_empty_falls_back():
    assert sanitize_component("...") == "untitled"


def test_title_to_hyphenated_collapses_whitespace():
    assert title_to_hyphenated("Longest   Common Prefix") == "Longest-Common-Prefix"


def test_folder_name_is_deterministic():
    assert folder_name(217, "Contains Duplicate") == folder_name(217, "Contains Duplicate")
