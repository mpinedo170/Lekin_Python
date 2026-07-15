from lekinpy import System, Job, Operation, Machine, Workcenter
from lekinpy.algorithms import FCFSAlgorithm
from lekinpy.exceptions import (
    EmptyOperationsError,
    NonPositiveProcessingTimeError,
    EmptyMachineListError,
    DuplicateJobIdError,
    DuplicateMachineIdError,
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
