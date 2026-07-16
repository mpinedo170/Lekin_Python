from lekinpy import System, Job, Operation, Machine, Workcenter
from lekinpy.algorithms import SPTAlgorithm, EDDAlgorithm, WSPTAlgorithm, FCFSAlgorithm
import pytest


def _build_multi_op_system() -> System:
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    system.add_workcenter(Workcenter("W02", 0, "A", [Machine("B1", 0, "A")]))
    system.add_workcenter(Workcenter("W03", 0, "A", [Machine("C1", 0, "A")]))
    # J1 has 3 operations across 3 different workcenters.
    system.add_job(Job("J1", 0, 50, 1, [
        Operation("W01", 5, "A"),
        Operation("W02", 3, "A"),
        Operation("W03", 4, "A"),
    ]))
    # J2 has 2 operations.
    system.add_job(Job("J2", 0, 50, 2, [
        Operation("W02", 2, "A"),
        Operation("W03", 6, "A"),
    ]))
    # J3 is single-operation, to make sure that path still works.
    system.add_job(Job("J3", 1, 50, 3, [Operation("W01", 1, "A")]))
    return system


def _operations_by_job(schedule):
    by_job = {}
    for ms in schedule.machines:
        for so in ms.operations:
            by_job.setdefault(so.job_id, []).append(so)
    return by_job


@pytest.mark.parametrize("algo_cls", [SPTAlgorithm, EDDAlgorithm, WSPTAlgorithm, FCFSAlgorithm])
def test_every_operation_of_every_job_gets_scheduled(algo_cls):
    # Regression test for the bug where SPT/EDD/WSPT silently dropped every
    # operation after job.operations[0]. Before the fix, a multi-operation
    # job would only ever produce one ScheduledOperation record total.
    system = _build_multi_op_system()
    schedule = algo_cls().schedule(system)

    by_job = _operations_by_job(schedule)
    for job in system.jobs:
        scheduled_indices = sorted(so.operation_index for so in by_job.get(job.job_id, []))
        expected_indices = list(range(len(job.operations)))
        assert scheduled_indices == expected_indices, (
            f"{algo_cls.__name__} dropped operations for {job.job_id}: "
            f"expected indices {expected_indices}, got {scheduled_indices}"
        )


@pytest.mark.parametrize("algo_cls", [SPTAlgorithm, EDDAlgorithm, WSPTAlgorithm, FCFSAlgorithm])
def test_operation_precedence_is_respected(algo_cls):
    # A job's operation i+1 must never start before operation i finishes.
    system = _build_multi_op_system()
    schedule = algo_cls().schedule(system)

    by_job = _operations_by_job(schedule)
    for job in system.jobs:
        ops_in_order = sorted(by_job[job.job_id], key=lambda so: so.operation_index)
        for prev_op, next_op in zip(ops_in_order, ops_in_order[1:]):
            assert next_op.start_time >= prev_op.end_time, (
                f"{algo_cls.__name__}: {job.job_id} operation {next_op.operation_index} "
                f"started at {next_op.start_time} before operation {prev_op.operation_index} "
                f"ended at {prev_op.end_time}"
            )


def test_spt_total_scheduled_operation_count_matches_system():
    system = _build_multi_op_system()
    schedule = SPTAlgorithm().schedule(system)

    total_expected = sum(len(job.operations) for job in system.jobs)
    total_scheduled = sum(len(ms.operations) for ms in schedule.machines)
    assert total_scheduled == total_expected == 6
