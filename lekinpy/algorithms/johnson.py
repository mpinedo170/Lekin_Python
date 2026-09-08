"""Johnson's rule -- the SPT(1)-LPT(2) sequencing rule for flow shops.

Reference: Johnson, S. M. (1954), "Optimal two- and three-stage production
schedules with setup times included", *Naval Research Logistics Quarterly*
1(1), 61-68; presented as the SPT(1)-LPT(2) rule in Pinedo, *Scheduling:
Theory, Algorithms, and Systems*, Section 6.1 ("Flow Shops with Unlimited
Intermediate Storage").

Unlike FCFS/SPT/EDD/WSPT, this is not a dispatching rule. Those pick the
next job from whatever happens to be available at some instant; Johnson's
rule needs every job's processing times up front, partitions the jobs once,
and emits a single permutation that both machines then follow. That is why
it does not go through SchedulingAlgorithm.dynamic_schedule().
"""

from typing import Any, Callable, List, Sequence, Tuple, TypeVar

from .base import SchedulingAlgorithm
from ..exceptions import NotAFlowShopError
from ..schedule import Schedule

T = TypeVar("T")


def johnson_order(items: Sequence[Tuple[T, float, float]]) -> List[T]:
    """Order ``(item, first_stage_time, second_stage_time)`` triples by Johnson's rule.

    The rule itself, with nothing scheduling-specific attached:

      1. Split into set A (``a <= b``) and set B (``a > b``).
      2. Sort A by ``a`` ascending  -- SPT on the first machine.
      3. Sort B by ``b`` descending -- LPT on the second machine.
      4. Concatenate: A then B.

    Intuitively this front-loads jobs that clear machine 1 quickly (so
    machine 2 starts as early as possible) and back-loads jobs that finish
    quickly on machine 2 (so machine 2 idles as little as possible at the
    end).

    Ties are broken by the caller's input order: both sorts are Python's
    stable ``sorted``, so equal keys keep their relative position. Two jobs
    with identical times are therefore interchangeable and the makespan is
    unaffected, but the emitted sequence stays deterministic.
    """
    set_a = [entry for entry in items if entry[1] <= entry[2]]
    set_b = [entry for entry in items if entry[1] > entry[2]]
    set_a.sort(key=lambda entry: entry[1])
    set_b.sort(key=lambda entry: entry[2], reverse=True)
    return [entry[0] for entry in set_a + set_b]


class JohnsonAlgorithm(SchedulingAlgorithm):
    """Johnson's rule (SPT(1)-LPT(2)) for the flow shop makespan problem.

    For the two-machine flow shop (``F2 || Cmax``) this is *optimal*, not a
    heuristic: it provably minimizes the makespan. That guarantee holds when

      * every job visits the same two stages in the same order,
      * each stage has exactly one machine, and
      * all jobs are released at time 0.

    The first two are enforced (``NotAFlowShopError``). The third is not: a
    System with nonzero release times still schedules, and the sequence is
    still Johnson's, but the optimality proof no longer applies. Use
    :meth:`is_optimal_for` to test all three at once.

    **Flow shops with more than two stages.** ``Fm || Cmax`` is NP-hard for
    m >= 3, so there is no exact extension of this rule. By default the
    algorithm still accepts such a System and applies the standard
    two-machine reduction -- job j is given a proxy first-stage time of
    ``sum(p[1..m-1])`` and a proxy second-stage time of ``sum(p[2..m])``,
    then Johnson's rule runs on those proxies. That is a *heuristic with no
    optimality guarantee*, and it says so: the resulting Schedule's
    ``schedule_type`` is ``"Johnson (m-machine heuristic)"`` rather than
    ``"Johnson"``. Pass ``allow_multi_stage=False`` to reject anything but a
    genuine two-machine flow shop instead.
    """

    metadata = {
        "id": "johnson",
        "display_name": "Johnson's Rule (SPT(1)-LPT(2))",
        "supports_multi_operation": True,
        "version": "1.0.0",
    }

    #: schedule_type on the returned Schedule, by regime.
    EXACT_LABEL = "Johnson"
    HEURISTIC_LABEL = "Johnson (m-machine heuristic)"

    def __init__(self, allow_multi_stage: bool = True) -> None:
        super().__init__()
        self.allow_multi_stage: bool = allow_multi_stage

    # -- flow shop structure ------------------------------------------------

    def flow_shop_route(self, system: Any) -> Tuple[str, ...]:
        """Return the single workcenter route every job follows.

        Raises NotAFlowShopError unless the System is a flow shop: at least
        one job, every job visiting the same ordered list of at least two
        distinct workcenters, and exactly one machine at each of them.
        """
        if not system.jobs:
            raise NotAFlowShopError(
                "Johnson's rule needs at least one job; this system has none."
            )

        routes = {tuple(op.workcenter for op in job.operations) for job in system.jobs}
        if len(routes) > 1:
            sample = sorted(" -> ".join(route) for route in routes)[:3]
            raise NotAFlowShopError(
                "Johnson's rule needs a flow shop, where every job visits the same "
                "workcenters in the same order. This system has "
                f"{len(routes)} distinct routes, e.g. {'; '.join(sample)}."
            )

        route = routes.pop()
        if len(route) < 2:
            raise NotAFlowShopError(
                "Johnson's rule needs at least two stages; every job in this "
                f"system has only {len(route)} operation(s)."
            )
        if len(set(route)) != len(route):
            raise NotAFlowShopError(
                "Johnson's rule needs each job to visit every stage exactly once, "
                f"but the route {' -> '.join(route)} repeats a workcenter."
            )
        if len(route) > 2 and not self.allow_multi_stage:
            raise NotAFlowShopError(
                f"This is a {len(route)}-machine flow shop, and this "
                "JohnsonAlgorithm was constructed with allow_multi_stage=False, "
                "which restricts it to the exact two-machine rule."
            )

        for workcenter_name in route:
            machines = [
                wc for wc in system.workcenters if wc.name == workcenter_name
            ]
            if machines and len(machines[0].machines) != 1:
                raise NotAFlowShopError(
                    "Johnson's rule assumes one machine per stage, but workcenter "
                    f"'{workcenter_name}' has {len(machines[0].machines)} machines. "
                    "With parallel machines at a stage the rule is no longer optimal."
                )

        return route

    def is_optimal_for(self, system: Any) -> bool:
        """Whether this System meets every condition for Johnson's optimality proof.

        True only for a two-stage flow shop, one machine per stage, with all
        jobs released at time 0. False (rather than raising) for anything
        else, so callers can use it as a plain predicate -- for instance to
        decide whether to present a result as "optimal" or merely "good".
        """
        try:
            route = self.flow_shop_route(system)
        except NotAFlowShopError:
            return False
        if len(route) != 2:
            return False
        return all(job.release == 0 for job in system.jobs)

    # -- sequencing ---------------------------------------------------------

    def sequence(self, system: Any) -> List[Any]:
        """Return this System's jobs in Johnson order, without scheduling them.

        Exposed separately from :meth:`schedule` because the sequence is the
        interesting artifact when working through a textbook example -- it
        can be inspected, printed, or diffed against a hand-computed answer
        without building a full Schedule.
        """
        route = self.flow_shop_route(system)
        first_stage, second_stage = self._stage_time_functions(len(route))
        return johnson_order(
            [(job, first_stage(job), second_stage(job)) for job in system.jobs]
        )

    def _stage_time_functions(
        self, stage_count: int
    ) -> Tuple[Callable[[Any], float], Callable[[Any], float]]:
        """Pick the (a_j, b_j) pair of times Johnson's rule sorts on.

        Two stages: the real processing times, which is the rule as stated.
        More: the two-machine reduction described in the class docstring,
        where the "first machine" is every stage but the last and the
        "second machine" is every stage but the first.
        """
        if stage_count == 2:
            return (
                lambda job: job.operations[0].processing_time,
                lambda job: job.operations[1].processing_time,
            )
        return (
            lambda job: sum(op.processing_time for op in job.operations[:-1]),
            lambda job: sum(op.processing_time for op in job.operations[1:]),
        )

    # -- scheduling ---------------------------------------------------------

    def schedule(self, system: Any) -> Schedule:
        self.prepare(system)
        route = self.flow_shop_route(system)
        ordered_jobs = self.sequence(system)

        # Assigning a job's operations back-to-back, jobs in Johnson order,
        # is what makes this a permutation schedule: each machine receives
        # its operations in sequence order, and _assign_single_operation
        # holds an operation until both its machine is free and the job's
        # previous operation has finished. That is exactly the textbook
        # recursion C(k, i) = max(C(k, i-1), C(k-1, i)) + p(k, i).
        for job in ordered_jobs:
            for op in job.operations:
                candidate_machines = self._get_machines_for_workcenter(system, op.workcenter)
                chosen_machine = self._get_earliest_machine(candidate_machines)
                self._assign_single_operation(job, op, chosen_machine)

        machines_schedules = self.get_machine_schedules(system)
        total_time = max(self.machine_available_time.values()) if self.machine_available_time else 0
        label = self.EXACT_LABEL if len(route) == 2 else self.HEURISTIC_LABEL
        return Schedule(label, total_time, machines_schedules)
