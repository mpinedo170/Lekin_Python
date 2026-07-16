"""Beginner example: route multi-operation jobs through two workcenters."""

from lekinpy import Job, Machine, Operation, System, Workcenter
from lekinpy.algorithms import FCFSAlgorithm


system = System()

system.add_workcenter(
    Workcenter(
        name="Cutting",
        release=0,
        status="A",
        machines=[Machine("CUT-1", release=0, status="A")],
    )
)
system.add_workcenter(
    Workcenter(
        name="Painting",
        release=0,
        status="A",
        machines=[Machine("PAINT-1", release=0, status="A")],
    )
)

system.add_job(
    Job(
        job_id="Table",
        release=0,
        due=20,
        weight=2,
        operations=[
            Operation("Cutting", processing_time=4, status="A"),
            Operation("Painting", processing_time=3, status="A"),
        ],
    )
)
system.add_job(
    Job(
        job_id="Chair",
        release=0,
        due=15,
        weight=1,
        operations=[
            Operation("Cutting", processing_time=2, status="A"),
            Operation("Painting", processing_time=2, status="A"),
        ],
    )
)

system.validate()
schedule = FCFSAlgorithm().schedule(system)

print(f"Makespan: {schedule.time}\n")
for machine_schedule in schedule.machines:
    print(f"{machine_schedule.machine}:")
    for operation in machine_schedule.operations:
        print(
            f"  {operation.job_id}, operation {operation.operation_index}: "
            f"{operation.start_time} -> {operation.end_time}"
        )

print("\nNotice that operation 1 of each job starts only after operation 0 ends.")

