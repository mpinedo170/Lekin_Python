from lekinpy import System, Job, Operation, Machine, Workcenter
from lekinpy.algorithms import FCFSAlgorithm
from lekinpy.exceptions import (
    EmptyOperationsError,
    NonPositiveProcessingTimeError,
    EmptyMachineListError,
    DuplicateJobIdError,
    DuplicateMachineIdError,
    DuplicateWorkcenterIdError,
    MissingWorkcenterError,
)
import pytest


def test_job_with_no_operations_raises():
    with pytest.raises(EmptyOperationsError):
        Job("J1", release=0, due=10, weight=1, operations=[])


def test_operation_with_zero_processing_time_raises():
    with pytest.raises(NonPositiveProcessingTimeError):
        Operation("W01", 0, "A")


def test_operation_with_negative_processing_time_raises():
    with pytest.raises(NonPositiveProcessingTimeError):
        Operation("W01", -5, "A")


def test_workcenter_with_no_machines_raises():
    with pytest.raises(EmptyMachineListError):
        Workcenter("W01", release=0, status="A", machines=[])


def test_workcenter_with_duplicate_machine_names_raises():
    with pytest.raises(DuplicateMachineIdError):
        Workcenter("W01", release=0, status="A", machines=[
            Machine("A1", 0, "A"),
            Machine("A1", 0, "A"),
        ])


def test_system_rejects_duplicate_job_id():
    system = System()
    system.add_job(Job("J1", 0, 10, 1, [Operation("W01", 5, "A")]))
    with pytest.raises(DuplicateJobIdError):
        system.add_job(Job("J1", 0, 10, 1, [Operation("W01", 3, "A")]))


def test_system_rejects_duplicate_machine_id_across_workcenters():
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    with pytest.raises(DuplicateMachineIdError):
        system.add_workcenter(Workcenter("W02", 0, "A", [Machine("A1", 0, "A")]))


def test_system_rejects_duplicate_workcenter_id():
    # Regression test: two Workcenters with the same name (but different
    # machines) used to add cleanly. That's not just a bookkeeping problem
    # -- _get_machines_for_workcenter matches by workcenter *name*, so both
    # workcenters' machines would silently pool under the one name, and an
    # operation targeting that name could land on either workcenter.
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    with pytest.raises(DuplicateWorkcenterIdError):
        system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A2", 0, "A")]))


def test_validate_catches_duplicate_job_id_introduced_after_insertion():
    # Regression test: add_job only checks for duplicates at the moment of
    # insertion. Mutating job_id afterwards (e.g. j2.job_id = j1.job_id)
    # used to bypass that check entirely, since nothing re-validates on
    # mutation. validate() -- the checkpoint every algorithm runs before
    # scheduling -- must catch this defensively.
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    j1 = Job("J1", 0, 10, 1, [Operation("W01", 5, "A")])
    j2 = Job("J2", 0, 10, 1, [Operation("W01", 3, "A")])
    system.add_job(j1)
    system.add_job(j2)

    j2.job_id = "J1"

    with pytest.raises(DuplicateJobIdError):
        system.validate()


def test_validate_catches_duplicate_workcenter_id_introduced_after_insertion():
    system = System()
    wc1 = Workcenter("W01", 0, "A", [Machine("A1", 0, "A")])
    wc2 = Workcenter("W02", 0, "A", [Machine("A2", 0, "A")])
    system.add_workcenter(wc1)
    system.add_workcenter(wc2)

    wc2.name = "W01"

    with pytest.raises(DuplicateWorkcenterIdError):
        system.validate()


def test_validate_catches_duplicate_machine_id_introduced_after_insertion():
    system = System()
    wc1 = Workcenter("W01", 0, "A", [Machine("A1", 0, "A")])
    wc2 = Workcenter("W02", 0, "A", [Machine("A2", 0, "A")])
    system.add_workcenter(wc1)
    system.add_workcenter(wc2)

    wc2.machines[0].name = "A1"

    with pytest.raises(DuplicateMachineIdError):
        system.validate()


def test_validate_catches_operation_mutated_to_non_positive_processing_time():
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    job = Job("J1", 0, 10, 1, [Operation("W01", 5, "A")])
    system.add_job(job)

    job.operations[0].processing_time = 0

    with pytest.raises(NonPositiveProcessingTimeError):
        system.validate()


def test_system_validate_catches_missing_workcenter_reference():
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    system.add_job(Job("J1", 0, 10, 1, [Operation("W99", 5, "A")]))

    with pytest.raises(MissingWorkcenterError):
        system.validate()


def test_system_validate_is_order_independent():
    # Workcenters added after the job that references them should still
    # pass validation -- validate() checks the fully-built system, not the
    # order things were added in.
    system = System()
    system.add_job(Job("J1", 0, 10, 1, [Operation("W01", 5, "A")]))
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))

    system.validate()  # should not raise


def test_scheduling_a_system_with_missing_workcenter_raises_clear_error():
    # Regression test: before this validation existed, scheduling a job
    # whose operation referenced an unknown workcenter would fail deep
    # inside _get_earliest_machine with an opaque
    # "ValueError: min() arg is an empty sequence" instead of a clear,
    # actionable error surfaced up front.
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    system.add_job(Job("J1", 0, 10, 1, [Operation("W99", 5, "A")]))

    with pytest.raises(MissingWorkcenterError):
        FCFSAlgorithm().schedule(system)


def test_valid_system_still_schedules_normally():
    # The validation layer must not reject well-formed systems.
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    system.add_job(Job("J1", 0, 10, 1, [Operation("W01", 5, "A")]))

    schedule = FCFSAlgorithm().schedule(system)
    assert schedule.time == 5
