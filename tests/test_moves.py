"""Test 10.3 -- the reversible move primitive (v0.2.0 task 2.1).

Covers the four states of table 8.5, re-running a finished move, retrying
through a lock, and undoing a plan. This is the primitive the whole migration
rests on: if it is not idempotent an interrupted run leaves a hybrid vault, and
if its inverse is wrong the rollback cannot put anything back.
"""

import errno
import hashlib

import pytest

from wolta.core import moves
from wolta.core.moves import Move, MoveConflict, MoveLocked, MovePlan, MoveState

MOVE = Move(src="IDENTITY", dst="SYSTEM/IDENTITY")


def _dir_with_note(vault, rel, text="original content\n"):
    target = vault / rel
    target.mkdir(parents=True, exist_ok=True)
    (target / "note.md").write_text(text, encoding="utf-8")
    return target


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _never_sleep(_seconds):
    """Keep the retry tests instant; the delay itself is not what we verify."""


# --- table 8.5: the four states -------------------------------------------


def test_source_present_destination_free_is_moved(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY")

    assert moves.apply(tmp_path, MOVE) is MoveState.PENDING

    assert not (tmp_path / "IDENTITY").exists()
    assert (tmp_path / "SYSTEM" / "IDENTITY" / "note.md").exists()


def test_already_at_destination_is_left_alone(tmp_path):
    _dir_with_note(tmp_path, "SYSTEM/IDENTITY")

    assert moves.apply(tmp_path, MOVE) is MoveState.DONE

    assert (tmp_path / "SYSTEM" / "IDENTITY" / "note.md").exists()


def test_both_ends_present_refuses_to_choose(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY", "the user's\n")
    _dir_with_note(tmp_path, "SYSTEM/IDENTITY", "a half-finished run's\n")

    with pytest.raises(MoveConflict, match="both ends"):
        moves.apply(tmp_path, MOVE)

    # Neither side may be touched by the refusal.
    assert (tmp_path / "IDENTITY" / "note.md").read_text(encoding="utf-8") == "the user's\n"
    assert (tmp_path / "SYSTEM" / "IDENTITY" / "note.md").read_text(
        encoding="utf-8"
    ) == "a half-finished run's\n"


def test_neither_end_present_is_a_no_op(tmp_path):
    """A category the user deleted is not an error."""
    assert moves.apply(tmp_path, MOVE) is MoveState.ABSENT
    assert not (tmp_path / "SYSTEM").exists()


# --- idempotency and integrity --------------------------------------------


def test_running_twice_changes_nothing_the_second_time(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY")

    assert moves.apply(tmp_path, MOVE) is MoveState.PENDING
    assert moves.apply(tmp_path, MOVE) is MoveState.DONE

    assert (tmp_path / "SYSTEM" / "IDENTITY" / "note.md").exists()


def test_contents_survive_the_move_byte_for_byte(tmp_path):
    """8.1: not a byte of the user's content may change."""
    _dir_with_note(tmp_path, "IDENTITY", "acentos: café, ñandú\n")
    before = _sha256(tmp_path / "IDENTITY" / "note.md")

    moves.apply(tmp_path, MOVE)

    assert _sha256(tmp_path / "SYSTEM" / "IDENTITY" / "note.md") == before


def test_a_single_file_moves_too(tmp_path):
    """8.3 step 3 relocates DESIGN.md, so the primitive cannot be dirs-only."""
    (tmp_path / "DESIGN.md").write_text("# DESIGN\n", encoding="utf-8")

    moves.apply(tmp_path, Move(src="DESIGN.md", dst="SYSTEM/DESIGN.md"))

    assert (tmp_path / "SYSTEM" / "DESIGN.md").read_text(encoding="utf-8") == "# DESIGN\n"


def test_dry_run_reports_without_touching_anything(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY")
    plan = MovePlan()

    assert moves.apply(tmp_path, MOVE, plan=plan, dry_run=True) is MoveState.PENDING

    assert (tmp_path / "IDENTITY").exists()
    assert not (tmp_path / "SYSTEM").exists()
    assert len(plan) == 0


# --- batches ---------------------------------------------------------------


def test_a_batch_with_one_conflict_moves_nothing(tmp_path):
    """Fail-fast: a batch that cannot finish must not be allowed to start."""
    _dir_with_note(tmp_path, "IDENTITY")
    _dir_with_note(tmp_path, "WORK")
    _dir_with_note(tmp_path, "SYSTEM/WORK")

    batch = [MOVE, Move(src="WORK", dst="SYSTEM/WORK")]
    with pytest.raises(MoveConflict, match="WORK"):
        moves.apply_all(tmp_path, batch)

    assert (tmp_path / "IDENTITY").exists(), "the clean move ran despite the conflict"


def test_a_clean_batch_reports_each_state(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY")
    _dir_with_note(tmp_path, "SYSTEM/WORK")

    result = moves.apply_all(
        tmp_path,
        [MOVE, Move(src="WORK", dst="SYSTEM/WORK"), Move(src="GONE", dst="SYSTEM/GONE")],
    )

    assert result == [MoveState.PENDING, MoveState.DONE, MoveState.ABSENT]


# --- locking ---------------------------------------------------------------


def test_a_transient_lock_is_retried(tmp_path, monkeypatch):
    _dir_with_note(tmp_path, "IDENTITY")
    real_rename = type(tmp_path).rename
    attempts = []

    def flaky(self, target):
        attempts.append(target)
        if len(attempts) < 3:
            raise PermissionError(errno.EACCES, "locked by a sync client")
        return real_rename(self, target)

    monkeypatch.setattr(type(tmp_path), "rename", flaky)

    assert moves.apply(tmp_path, MOVE, sleep=_never_sleep) is MoveState.PENDING
    assert len(attempts) == 3
    assert (tmp_path / "SYSTEM" / "IDENTITY" / "note.md").exists()


def test_a_permanent_lock_gives_up_with_an_actionable_error(tmp_path, monkeypatch):
    _dir_with_note(tmp_path, "IDENTITY")

    def always_locked(self, target):
        raise PermissionError(errno.EACCES, "locked by a sync client")

    monkeypatch.setattr(type(tmp_path), "rename", always_locked)

    with pytest.raises(MoveLocked, match="pause"):
        moves.apply(tmp_path, MOVE, retries=2, sleep=_never_sleep)


def test_a_real_error_is_not_retried(tmp_path, monkeypatch):
    """Retrying a genuine bug would only hide it behind a delay."""
    _dir_with_note(tmp_path, "IDENTITY")
    attempts = []

    def broken(self, target):
        attempts.append(target)
        raise OSError(errno.EXDEV, "cross-device link")

    monkeypatch.setattr(type(tmp_path), "rename", broken)

    with pytest.raises(OSError) as caught:
        moves.apply(tmp_path, MOVE, sleep=_never_sleep)

    assert caught.value.errno == errno.EXDEV
    assert len(attempts) == 1


# --- the inverse plan ------------------------------------------------------


def test_the_plan_records_what_was_actually_attempted(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY")
    _dir_with_note(tmp_path, "SYSTEM/WORK")  # already migrated, nothing to record
    plan = MovePlan()

    moves.apply_all(
        tmp_path, [MOVE, Move(src="WORK", dst="SYSTEM/WORK")], plan=plan
    )

    assert list(plan) == [MOVE]


def test_the_inverse_runs_backwards(tmp_path):
    """Order matters once moves nest; the last one done is the first undone."""
    plan = MovePlan()
    plan.record(Move("a", "SYSTEM/a"))
    plan.record(Move("b", "SYSTEM/b"))

    assert plan.inverse() == [Move("SYSTEM/b", "b"), Move("SYSTEM/a", "a")]


def test_undo_puts_a_half_finished_run_back(tmp_path):
    """R-02: an interrupted migration must be able to return to the start."""
    _dir_with_note(tmp_path, "IDENTITY", "identity\n")
    _dir_with_note(tmp_path, "WORK", "work\n")
    plan = MovePlan()

    moves.apply(tmp_path, MOVE, plan=plan)
    # ...and then the run dies before WORK is touched.

    moves.undo(tmp_path, plan)

    assert (tmp_path / "IDENTITY" / "note.md").read_text(encoding="utf-8") == "identity\n"
    assert (tmp_path / "WORK" / "note.md").read_text(encoding="utf-8") == "work\n"
    assert not (tmp_path / "SYSTEM" / "IDENTITY").exists()


def test_undo_tolerates_a_plan_ahead_of_reality(tmp_path):
    """The plan records intent before the rename, so it may list one that never landed."""
    plan = MovePlan()
    plan.record(MOVE)  # nothing was ever moved

    assert moves.undo(tmp_path, plan) == [MoveState.ABSENT]


def test_undo_is_idempotent(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY")
    plan = MovePlan()
    moves.apply(tmp_path, MOVE, plan=plan)

    moves.undo(tmp_path, plan)
    moves.undo(tmp_path, plan)

    assert (tmp_path / "IDENTITY" / "note.md").exists()


# --- cleanup ---------------------------------------------------------------


def test_an_emptied_directory_can_be_removed(tmp_path):
    _dir_with_note(tmp_path, "IDENTITY")
    plan = MovePlan()
    moves.apply(tmp_path, MOVE, plan=plan)
    moves.undo(tmp_path, plan)

    assert moves.remove_if_empty(tmp_path, "SYSTEM") is True
    assert not (tmp_path / "SYSTEM").exists()


def test_a_directory_with_anything_left_in_it_is_kept(tmp_path):
    _dir_with_note(tmp_path, "SYSTEM/leftover")

    assert moves.remove_if_empty(tmp_path, "SYSTEM") is False
    assert (tmp_path / "SYSTEM" / "leftover").exists()


def test_removing_a_directory_that_is_not_there_is_not_an_error(tmp_path):
    assert moves.remove_if_empty(tmp_path, "SYSTEM") is False
