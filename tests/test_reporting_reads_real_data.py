from lekinpy import System, Job, Operation, Machine, Workcenter
from lekinpy.algorithms import SPTAlgorithm
from lekinpy.io import save_schedule_to_json, load_schedule_from_json
from pathlib import Path


def _build_multi_op_system() -> System:
    system = System()
    system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    system.add_workcenter(Workcenter("W02", 0, "A", [Machine("B1", 0, "A")]))
    system.add_job(Job("J1", 0, 8, 1, [Operation("W01", 5, "A"), Operation("W02", 3, "A")]))
    system.add_job(Job("J2", 0, 5, 2, [Operation("W01", 2, "A")]))
    return system


def test_display_job_details_uses_stored_scheduled_operation_times(capsys):
    system = _build_multi_op_system()
    schedule = SPTAlgorithm().schedule(system)

    schedule.display_job_details(system)
    output = capsys.readouterr().out

    # J2 (shorter first op) runs first under SPT: A1 0-2. J1's first op then
    # runs 2-7 on A1, its second op 7-10 on B1. Old code would have
    # recomputed J1's row using only operations[0]'s duration (5) applied
    # twice, giving a wrong "Pr.tm." of 5 instead of the true 8 (5+3) and a
    # wrong End of ~7 instead of the true 10.
    assert "J1" in output and "J2" in output
    j1_line = next(line for line in output.splitlines() if line.startswith("J1"))
    fields = j1_line.split()
    # ID Wght Rls Due Pr.tm. Stat. Bgn End T wT
    assert fields[4] == "8.0"    # total processing time across both operations
    assert fields[6] == "2.0"   # begin = first operation's start_time
    assert fields[7] == "10.0"  # end = last operation's end_time


def test_display_methods_do_not_depend_on_mutated_job_attributes(tmp_path: Path, capsys):
    # Reporting must read timing from the Schedule's own ScheduledOperation
    # records, not from Job.start_time/Job.end_time attributes that only
    # exist as a side effect of having just run a scheduling algorithm in
    # this process. Prove it by reloading the schedule from JSON against
    # freshly-constructed Job objects that were never scheduled.
    system = _build_multi_op_system()
    schedule = SPTAlgorithm().schedule(system)

    json_path = tmp_path / "sched.json"
    save_schedule_to_json(schedule, str(json_path))
    reloaded_schedule = load_schedule_from_json(str(json_path))

    fresh_system = _build_multi_op_system()
    assert not hasattr(fresh_system.jobs[0], "start_time")
    assert not hasattr(fresh_system.jobs[0], "end_time")

    reloaded_schedule.display_job_details(fresh_system)
    reloaded_schedule.display_sequence(fresh_system)
    reloaded_schedule.display_summary(fresh_system)
    output = capsys.readouterr().out

    assert "C_max     10.0" in output
    assert "J1" in output and "J2" in output


def test_display_sequence_reports_each_operations_own_duration():
    system = _build_multi_op_system()
    schedule = SPTAlgorithm().schedule(system)

    machine_a1 = next(ms for ms in schedule.machines if ms.machine == "A1")
    machine_b1 = next(ms for ms in schedule.machines if ms.machine == "B1")

    # A1: J2 (0-2), then J1's first operation (2-7)
    assert [(so.job_id, so.start_time, so.end_time) for so in machine_a1.operations] == [
        ("J2", 0.0, 2.0),
        ("J1", 2.0, 7.0),
    ]
    # B1: J1's second operation, which cannot start before A1's op ends at 7
    assert [(so.job_id, so.start_time, so.end_time) for so in machine_b1.operations] == [
        ("J1", 7.0, 10.0),
    ]
