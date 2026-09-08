"""Beginner example: Johnson's rule on a two-machine flow shop.

The rules in 03_compare_algorithms.py are dispatching rules -- they pick
whichever job looks best at some instant. Johnson's rule is different: it
looks at every job's times up front and produces one order that both
machines follow. On a two-machine flow shop that order provably gives the
smallest possible makespan.

This example schedules the same five jobs with a dispatching rule and with
Johnson's rule, so the difference in makespan is visible.
"""

from lekinpy import Job, Machine, Operation, System, Workcenter
from lekinpy.algorithms import JohnsonAlgorithm, SPTAlgorithm

# Every job goes through Cutting first, then Polishing -- same order for
# all of them. That "same route for every job" is what makes it a flow shop.
#
# These times are chosen so the two rules genuinely disagree. Trim and Sand
# are quick to cut, so SPT starts with them; but they are also quick to
# polish, which leaves the polisher idle at the start and starved at the
# end. Johnson sends the slow-to-cut, slow-to-polish jobs first instead.
JOBS = {
    # job_id: (time on Cutting, time on Polishing)
    "Trim": (2, 1),
    "Sand": (3, 2),
    "Weld": (6, 12),
    "Paint": (7, 14),
}


def build_system() -> System:
    """Return a fresh system because scheduling records times on operations."""
    system = System()
    system.add_workcenter(
        Workcenter("Cutting", 0, "A", [Machine("Cutter", release=0, status="A")])
    )
    system.add_workcenter(
        Workcenter("Polishing", 0, "A", [Machine("Polisher", release=0, status="A")])
    )
    for job_id, (cutting_time, polishing_time) in JOBS.items():
        system.add_job(
            Job(
                job_id=job_id,
                release=0,
                due=100,
                weight=1,
                operations=[
                    Operation("Cutting", cutting_time, "A"),
                    Operation("Polishing", polishing_time, "A"),
                ],
            )
        )
    return system


for algorithm_class in (SPTAlgorithm, JohnsonAlgorithm):
    algorithm = algorithm_class()
    schedule = algorithm.schedule(build_system())
    order = [operation.job_id for operation in schedule.machines[0].operations]
    print(f"{algorithm.metadata['display_name']:<34} makespan={schedule.time}")
    print(f"{'':<34} order={order}")

# Johnson's rule can say whether its answer is provably the best possible,
# which a dispatching rule cannot. Here it is: two stages, one machine each,
# and every job released at time 0.
johnson = JohnsonAlgorithm()
print(f"\nProvably optimal for this system? {johnson.is_optimal_for(build_system())}")

# Ask for the order without building a schedule -- handy when you only want
# to check the sequence against a hand-computed answer.
print(f"Johnson order: {[job.job_id for job in johnson.sequence(build_system())]}")
