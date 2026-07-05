"""Tests for filesystem scaffolding and SyncTransaction rollback behavior."""

import pytest
from rich.console import Console

from dsa_sync.scaffold import SyncTransaction, ensure_problem_folder, write_text_file


def _quiet_console() -> Console:
    return Console(quiet=True)


def test_ensure_problem_folder_creates_and_tracks(tmp_path):
    folder = tmp_path / "0217-Contains-Duplicate"
    txn = SyncTransaction(console=_quiet_console())
    created = ensure_problem_folder(txn, folder)
    assert created is True
    assert folder.is_dir()
    assert folder in txn._created_dirs


def test_ensure_problem_folder_existing_not_tracked(tmp_path):
    folder = tmp_path / "0217-Contains-Duplicate"
    folder.mkdir()
    txn = SyncTransaction(console=_quiet_console())
    created = ensure_problem_folder(txn, folder)
    assert created is False
    assert folder not in txn._created_dirs


def test_write_text_file_creates_file(tmp_path):
    path = tmp_path / "solution.cpp"
    txn = SyncTransaction(console=_quiet_console())
    write_text_file(txn, path, "int main() {}\n")
    assert path.read_text(encoding="utf-8") == "int main() {}\n"


def test_rollback_removes_newly_created_file_and_folder(tmp_path):
    folder = tmp_path / "0217-Contains-Duplicate"
    solution = folder / "solution.cpp"

    with pytest.raises(RuntimeError):
        with SyncTransaction(console=_quiet_console()) as txn:
            ensure_problem_folder(txn, folder)
            write_text_file(txn, solution, "int main() {}\n")
            raise RuntimeError("simulated failure before commit")

    assert not solution.exists()
    assert not folder.exists()


def test_rollback_restores_overwritten_file_content(tmp_path):
    path = tmp_path / "README.md"
    path.write_text("original content", encoding="utf-8")

    with pytest.raises(RuntimeError):
        with SyncTransaction(console=_quiet_console()) as txn:
            write_text_file(txn, path, "new content")
            assert path.read_text(encoding="utf-8") == "new content"
            raise RuntimeError("simulated failure")

    assert path.read_text(encoding="utf-8") == "original content"


def test_committed_transaction_does_not_roll_back(tmp_path):
    folder = tmp_path / "0217-Contains-Duplicate"

    with SyncTransaction(console=_quiet_console()) as txn:
        ensure_problem_folder(txn, folder)
        txn.mark_committed()

    assert folder.exists()


def test_keyboard_interrupt_triggers_rollback(tmp_path):
    folder = tmp_path / "0217-Contains-Duplicate"

    with pytest.raises(KeyboardInterrupt):
        with SyncTransaction(console=_quiet_console()) as txn:
            ensure_problem_folder(txn, folder)
            raise KeyboardInterrupt()

    assert not folder.exists()


def test_rollback_returns_action_descriptions(tmp_path):
    folder = tmp_path / "0217-Contains-Duplicate"
    txn = SyncTransaction(console=_quiet_console())
    ensure_problem_folder(txn, folder)
    actions = txn.rollback()
    assert any("removed directory" in action for action in actions)


def test_snapshot_only_records_first_call(tmp_path):
    path = tmp_path / "README.md"
    path.write_text("first", encoding="utf-8")
    txn = SyncTransaction(console=_quiet_console())
    txn.snapshot(path)
    path.write_text("second", encoding="utf-8")
    txn.snapshot(path)  # should be a no-op, original already recorded
    txn.rollback()
    assert path.read_text(encoding="utf-8") == "first"
