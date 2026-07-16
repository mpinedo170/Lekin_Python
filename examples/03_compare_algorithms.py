"""Beginner example: compare the four built-in scheduling rules."""

from lekinpy import Job, Machine, Operation, System, Workcenter
from lekinpy.algorithms import (
    EDDAlgorithm,
    FCFSAlgorithm,
    SPTAlgorithm,
    WSPTAlgorithm,
)


def build_system() -> System:
    """Return a fresh system because scheduling records times on operations."""
    system = System()
    system.add_workcenter(
        Workcenter(
            name="Main",
            release=0,
            status="A",
            machines=[Machine("M1", release=0, status="A")],
        )
    )

    jobs = [
        # job_id, processing time, due date, weight
        ("LongImportant", 7, 12, 10),
        ("Short", 2, 20, 1),
        ("Urgent", 4, 6, 3),
    ]
    for job_id, processing_time, due, weight in jobs:
        system.add_job(
            Job(
                job_id=job_id,
                release=0,
                due=due,
                weight=weight,
                operations=[Operation("Main", processing_time, "A")],
            )
        )
    return system


algorithms = [FCFSAlgorithm, SPTAlgorithm, EDDAlgorithm, WSPTAlgorithm]

for algorithm_class in algorithms:
    system = build_system()
    algorithm = algorithm_class()
    schedule = algorithm.schedule(system)
    sequence = [
        operation.job_id
        for operation in schedule.machines[0].operations
    ]
    print(
        f"{algorithm.metadata['display_name']:<34} "
        f"order={sequence}, makespan={schedule.time}"
    )

