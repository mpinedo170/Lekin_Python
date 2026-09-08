"""Tests for Johnson's rule (SPT(1)-LPT(2)).

Two things are worth testing here that the dispatching-rule tests don't
cover. First, Johnson's rule makes an *optimality* claim on the two-machine
flow shop, not just a "produces some schedule" claim, so the interesting
assertion is against a brute-force minimum rather than against a
hand-copied expected output. Second, it is the first algorithm that refuses
problems: everything else schedules any valid System, and this one is only
defined on a flow shop.

Makespans are compared with == on small integer inputs, which is exact in
float (Machine.release is cast to float, so every algorithm's total comes
back as one).
"""

from itertools import permutations

import pytest

from lekinpy import Job, Machine, Operation, System, Workcenter
from lekinpy.algorithms import JohnsonAlgorithm, johnson_order
from lekinpy.exceptions import LekinValidationError, NotAFlowShopError


# -- helpers ---------------------------------------------------------------


# Every Job and Workcenter below is given an explicit rgb. Both classes
# auto-assign from a 64-entry class-level _available_colors list that is
# popped and never refilled, so letting them auto-assign would make this file
# drain a finite process-wide resource shared with every other test file --
# exhausting it makes *later* tests fail with an opaque "IndexError: pop from
# empty list" from a constructor that looks unrelated. Passing rgb keeps
# these tests hermetic. (The 64-object ceiling itself is a pre-existing
# library limitation, out of scope for this branch.)
_RGB = (128, 128, 128)


def _flow_shop(times, releases=None, machines_per_stage=None):
    """Build a flow shop from {job_id: (p1, p2, ...)}.

    A fresh System per call is deliberate: _assign_single_operation mutates
    Operation/Job objects in place, so a System reused across two algorithm
    runs would carry the first run's start/end times into the second.
    """
    releases = releases or {}
    machines_per_stage = machines_per_stage or {}
    stage_count = len(next(iter(times.values())))

    system = System()
    for stage in range(stage_count):
        name = f"WC{stage + 1}"
        count = machines_per_stage.get(name, 1)
        system.add_workcenter(
            Workcenter(
                name,
                0,
                "A",
                [Machine(f"M{stage + 1}_{i}", 0, "A") for i in range(count)],
                rgb=_RGB,
            )
        )
    for job_id, processing_times in times.items():
        system.add_job(
            Job(
                job_id=job_id,
                release=releases.get(job_id, 0),
                due=1000,
                weight=1,
                operations=[
                    Operation(f"WC{stage + 1}", p, "A") for stage, p in enumerate(processing_times)
                ],
                rgb=_RGB,
            )
        )
    return system


def _job_shop():
    """Two jobs whose routes disagree -- the canonical non-flow-shop."""
    system = System()
    system.add_workcenter(Workcenter("WC1", 0, "A", [Machine("M1", 0, "A")], rgb=_RGB))
    system.add_workcenter(Workcenter("WC2", 0, "A", [Machine("M2", 0, "A")], rgb=_RGB))
    system.add_job(
        Job("A", 0, 50, 1, [Operation("WC1", 3, "A"), Operation("WC2", 2, "A")], rgb=_RGB)
    )
    system.add_job(
        Job("B", 0, 50, 1, [Operation("WC2", 4, "A"), Operation("WC1", 1, "A")], rgb=_RGB)
    )
    return system


def _makespan(order, times):
    """Makespan of a permutation schedule, computed independently.

    The textbook recursion C(k, i) = max(C(k, i-1), C(k-1, i)) + p(k, i),
    written out here rather than obtained from the library, so a bug in the
    scheduler cannot make the scheduler look correct.
    """
    stage_count = len(next(iter(times.values())))
    stage_free = [0.0] * stage_count
    for job_id in order:
        previous_stage_end = 0.0
        for stage in range(stage_count):
            start = max(stage_free[stage], previous_stage_end)
            previous_stage_end = start + times[job_id][stage]
            stage_free[stage] = previous_stage_end
    return max(stage_free)


def _brute_force_minimum(times):
    return min(_makespan(order, times) for order in permutations(times))


def _sequence_ids(system):
    return [job.job_id for job in JohnsonAlgorithm().sequence(system)]


# The worked example: set A (a <= b) is J4, J2; set B is J1, J3, J5.
# A ascending by a -> J4(1), J2(2); B descending by b -> J1(4), J3(3), J5(2).
TEXTBOOK = {
    "J1": (5, 4),
    "J2": (2, 7),
    "J3": (6, 3),
    "J4": (1, 9),
    "J5": (8, 2),
}


# -- the rule itself -------------------------------------------------------


def test_johnson_order_partitions_and_sorts():
    order = johnson_order([(job_id, a, b) for job_id, (a, b) in TEXTBOOK.items()])
    assert order == ["J4", "J2", "J1", "J3", "J5"]


def test_johnson_order_is_stable_on_ties():
    # Equal keys must keep input order, so the emitted sequence is
    # deterministic even though tied jobs are interchangeable.
    items = [("first", 3, 3), ("second", 3, 3), ("third", 3, 3)]
    assert johnson_order(items) == ["first", "second", "third"]


def test_johnson_order_places_equal_times_in_set_a():
    # a == b is set A (the rule is a <= b), so it sorts ascending by a and
    # lands before a set B job with a larger a.
    assert johnson_order([("equal", 4, 4), ("bigger_a", 9, 1)]) == ["equal", "bigger_a"]


def test_sequence_matches_the_worked_example():
    assert _sequence_ids(_flow_shop(TEXTBOOK)) == ["J4", "J2", "J1", "J3", "J5"]


# -- optimality on two machines -------------------------------------------


def test_two_machine_makespan_is_the_brute_force_minimum():
    schedule = JohnsonAlgorithm().schedule(_flow_shop(TEXTBOOK))
    assert schedule.time == _brute_force_minimum(TEXTBOOK)


@pytest.mark.parametrize(
    "times",
    [
        pytest.param({"A": (3, 1), "B": (1, 3)}, id="two-jobs-mirrored"),
        pytest.param({"A": (1, 1), "B": (1, 1), "C": (1, 1)}, id="all-identical"),
        pytest.param({"A": (9, 1), "B": (8, 2), "C": (7, 3)}, id="all-set-b"),
        pytest.param({"A": (1, 9), "B": (2, 8), "C": (3, 7)}, id="all-set-a"),
        pytest.param({"A": (5, 5), "B": (2, 8), "C": (7, 1), "D": (4, 4)}, id="mixed-with-ties"),
        pytest.param({"A": (2, 3), "B": (6, 1), "C": (4, 4), "D": (1, 7), "E": (5, 2)}, id="five-jobs"),
    ],
)
def test_johnson_is_optimal_on_two_machines(times):
    # The actual guarantee: not "some schedule" but the minimum makespan,
    # checked against every permutation.
    schedule = JohnsonAlgorithm().schedule(_flow_shop(times))
    assert schedule.time == _brute_force_minimum(times)


def test_single_job_flow_shop():
    schedule = JohnsonAlgorithm().schedule(_flow_shop({"only": (4, 6)}))
    assert schedule.time == 10


def test_schedule_is_labeled_exact_on_two_stages():
    assert JohnsonAlgorithm().schedule(_flow_shop(TEXTBOOK)).schedule_type == "Johnson"


def test_every_operation_is_scheduled_once():
    system = _flow_shop(TEXTBOOK)
    schedule = JohnsonAlgorithm().schedule(system)
    scheduled = [so for ms in schedule.machines for so in ms.operations]
    assert len(scheduled) == sum(len(job.operations) for job in system.jobs)
    assert len({(so.job_id, so.operation_index) for so in scheduled}) == len(scheduled)


def test_operation_precedence_is_respected():
    system = _flow_shop(TEXTBOOK)
    schedule = JohnsonAlgorithm().schedule(system)
    by_job = {}
    for ms in schedule.machines:
        for so in ms.operations:
            by_job.setdefault(so.job_id, []).append(so)
    for job_id, ops in by_job.items():
        ops.sort(key=lambda so: so.operation_index)
        for previous, following in zip(ops, ops[1:]):
            assert following.start_time >= previous.end_time, (
                f"{job_id} operation {following.operation_index} started before "
                f"operation {previous.operation_index} finished"
            )


def test_release_times_are_honored_even_though_optimality_lapses():
    # A late release still delays the job -- the schedule stays feasible,
    # it just isn't provably optimal any more (see is_optimal_for).
    system = _flow_shop({"early": (2, 2), "late": (2, 2)}, releases={"late": 50})
    schedule = JohnsonAlgorithm().schedule(system)
    starts = {so.job_id: so.start_time for ms in schedule.machines for so in ms.operations}
    assert starts["late"] >= 50


# -- more than two stages --------------------------------------------------


THREE_STAGE = {"A": (3, 2, 4), "B": (1, 5, 2), "C": (6, 1, 3)}


def test_multi_stage_is_accepted_by_default():
    schedule = JohnsonAlgorithm().schedule(_flow_shop(THREE_STAGE))
    assert schedule.time > 0


def test_multi_stage_schedule_is_labeled_a_heuristic():
    # Fm||Cmax is NP-hard for m >= 3, so the label must not claim otherwise.
    schedule = JohnsonAlgorithm().schedule(_flow_shop(THREE_STAGE))
    assert schedule.schedule_type == "Johnson (m-machine heuristic)"


def test_multi_stage_can_be_rejected_outright():
    algorithm = JohnsonAlgorithm(allow_multi_stage=False)
    with pytest.raises(NotAFlowShopError, match="allow_multi_stage=False"):
        algorithm.schedule(_flow_shop(THREE_STAGE))


def test_multi_stage_reduction_uses_the_documented_proxy_times():
    # first proxy = sum of all but the last stage, second = all but the first.
    # A: (5, 6)  B: (6, 7)  C: (7, 4) -> set A is A, B; set B is C.
    assert _sequence_ids(_flow_shop(THREE_STAGE)) == ["A", "B", "C"]


# -- problems it must refuse ----------------------------------------------


def test_job_shop_is_rejected():
    with pytest.raises(NotAFlowShopError, match="same order"):
        JohnsonAlgorithm().schedule(_job_shop())


def test_system_with_no_jobs_is_rejected():
    system = System()
    system.add_workcenter(Workcenter("WC1", 0, "A", [Machine("M1", 0, "A")], rgb=_RGB))
    with pytest.raises(NotAFlowShopError, match="at least one job"):
        JohnsonAlgorithm().schedule(system)


def test_single_stage_system_is_rejected():
    with pytest.raises(NotAFlowShopError, match="at least two stages"):
        JohnsonAlgorithm().schedule(_flow_shop({"A": (3,), "B": (5,)}))


def test_route_revisiting_a_workcenter_is_rejected():
    system = System()
    system.add_workcenter(Workcenter("WC1", 0, "A", [Machine("M1", 0, "A")], rgb=_RGB))
    system.add_workcenter(Workcenter("WC2", 0, "A", [Machine("M2", 0, "A")], rgb=_RGB))
    for job_id in ("A", "B"):
        system.add_job(Job(job_id, 0, 50, 1, [
            Operation("WC1", 2, "A"),
            Operation("WC2", 3, "A"),
            Operation("WC1", 1, "A"),
        ], rgb=_RGB))
    with pytest.raises(NotAFlowShopError, match="repeats a workcenter"):
        JohnsonAlgorithm().schedule(system)


def test_parallel_machines_at_a_stage_are_rejected():
    # With two machines at a stage the rule is no longer optimal, so it is
    # refused rather than quietly returning a worse-than-claimed schedule.
    system = _flow_shop({"A": (3, 2), "B": (1, 4)}, machines_per_stage={"WC2": 2})
    with pytest.raises(NotAFlowShopError, match="one machine per stage"):
        JohnsonAlgorithm().schedule(system)


def test_not_a_flow_shop_error_is_a_validation_error():
    # lekin-web funnels LekinValidationError subclasses into its
    # "can't schedule that way" channel; this is what makes that work.
    assert issubclass(NotAFlowShopError, LekinValidationError)


# -- the optimality predicate ---------------------------------------------


def test_is_optimal_for_accepts_a_two_stage_flow_shop_released_at_zero():
    assert JohnsonAlgorithm().is_optimal_for(_flow_shop(TEXTBOOK)) is True


def test_is_optimal_for_rejects_more_than_two_stages():
    assert JohnsonAlgorithm().is_optimal_for(_flow_shop(THREE_STAGE)) is False


def test_is_optimal_for_rejects_nonzero_release_times():
    system = _flow_shop({"A": (3, 2), "B": (1, 4)}, releases={"B": 5})
    assert JohnsonAlgorithm().is_optimal_for(system) is False


def test_is_optimal_for_returns_false_rather_than_raising_on_a_job_shop():
    # A predicate, not a validator -- callers use it to decide whether to
    # present a result as optimal, and shouldn't need a try/except to ask.
    assert JohnsonAlgorithm().is_optimal_for(_job_shop()) is False


def test_flow_shop_route_returns_the_shared_route():
    assert JohnsonAlgorithm().flow_shop_route(_flow_shop(TEXTBOOK)) == ("WC1", "WC2")
