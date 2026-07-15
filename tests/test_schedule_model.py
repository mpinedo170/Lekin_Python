from lekinpy import System, Job, Operation, Machine, Workcenter
from lekinpy import ScheduledOperation, MachineSchedule, Schedule
from lekinpy import FCFSAlgorithm
from lekinpy.io import save_schedule_to_json, load_schedule_from_json, save_schedule_to_seq, parse_seq_file
from pathlib import Path


def _build_multi_op_system() -> System:
    sys1 = System()
    sys1.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
    sys1.add_job(Job("J1", 0, 10, 1, [Operation("W01", 5, "A"), Operation("W01", 3, "A")]))
    sys1.add_job(Job("J2", 0, 10, 1, [Operation("W01", 2, "A")]))
    return sys1


def test_machine_schedule_holds_scheduled_operations_not_job_ids():
    system = _build_multi_op_system()
    sched = FCFSAlgorithm().schedule(system)

    for ms in sched.machines:
        assert isinstance(ms, MachineSchedule)
        for op in ms.operations:
            assert isinstance(op, ScheduledOperation)


def test_scheduled_operation_carries_full_placement_data():
    system = _build_multi_op_system()
    sched = FCFSAlgorithm().schedule(system)

    ops = sched.machines[0].operations
    # J1's two operations, then J2's operation, in FCFS/precedence order.
    assert [(o.job_id, o.operation_index) for o in ops] == [("J1", 0), ("J1", 1), ("J2", 0)]
    j1_op0, j1_op1, j2_op0 = ops

    assert j1_op0.start_time == 0 and j1_op0.end_time == 5
    # J1's second operation cannot start before its first operation ends.
    assert j1_op1.start_time == 5 and j1_op1.end_time == 8
    assert j2_op0.start_time == 8 and j2_op0.end_time == 10
    assert [o.sequence_position for o in ops] == [0, 1, 2]
    assert all(o.workcenter == "W01" and o.machine == "A1" for o in ops)


def test_schedule_json_round_trip_is_lossless(tmp_path: Path):
    system = _build_multi_op_system()
    sched = FCFSAlgorithm().schedule(system)

    json_path = tmp_path / "schedule.json"
    save_schedule_to_json(sched, str(json_path))
    reloaded = load_schedule_from_json(str(json_path))

    assert reloaded.schedule_type == sched.schedule_type
    assert reloaded.time == sched.time
    assert len(reloaded.machines) == len(sched.machines)
    for original_ms, reloaded_ms in zip(sched.machines, reloaded.machines):
        assert original_ms.machine == reloaded_ms.machine
        assert original_ms.workcenter == reloaded_ms.workcenter
        assert [o.to_dict() for o in original_ms.operations] == [o.to_dict() for o in reloaded_ms.operations]


def test_schedule_seq_round_trip_is_lossless(tmp_path: Path):
    system = _build_multi_op_system()
    sched = FCFSAlgorithm().schedule(system)

    seq_path = tmp_path / "schedule.seq"
    save_schedule_to_seq(sched, str(seq_path))
    parsed = parse_seq_file(str(seq_path))
    reloaded = Schedule.from_dict(parsed[0])

    assert reloaded.schedule_type == sched.schedule_type
    for original_ms, reloaded_ms in zip(sched.machines, reloaded.machines):
        assert original_ms.machine == reloaded_ms.machine
        for original_op, reloaded_op in zip(original_ms.operations, reloaded_ms.operations):
            assert original_op.job_id == reloaded_op.job_id
            assert original_op.operation_index == reloaded_op.operation_index
            assert original_op.start_time == reloaded_op.start_time
            assert original_op.end_time == reloaded_op.end_time
            assert original_op.sequence_position == reloaded_op.sequence_position
            assert original_op.status == reloaded_op.status


def test_parse_seq_file_tolerates_legacy_bare_job_id_format(tmp_path: Path):
    # Original LEKIN .seq files only have a bare job id per "Oper:" line, with
    # no operation_index/timing suffix. parse_seq_file must not crash on these.
    legacy_seq = tmp_path / "legacy.seq"
    legacy_seq.write_text(
        "Schedule:           WSPT\n"
        "  RGB:                255;0;0\n"
        "  Time:               10\n"
        "  Machine:            W01\n"
        "    Oper:               J01\n"
        "    Oper:               J02\n"
    )

    parsed = parse_seq_file(str(legacy_seq))
    assert len(parsed) == 1
    ops = parsed[0]['machines'][0]['operations']
    assert [o['job_id'] for o in ops] == ["J01", "J02"]
    assert [o['sequence_position'] for o in ops] == [0, 1]
    assert ops[0]['operation_index'] is None
