"""Beginner example: schedule two jobs on one machine with FCFS."""

from lekinpy import Job, Machine, Operation, System, Workcenter
from lekinpy.algorithms import FCFSAlgorithm


system = System()

machine = Machine(name="M1", release=0, status="A")
workcenter = Workcenter(
    name="Assembly",
    release=0,
    status="A",
    machines=[machine],
)
system.add_workcenter(workcenter)

system.add_job(
    Job(
        job_id="J1",
        release=0,
        due=10,
        weight=1,
        operations=[Operation("Assembly", processing_time=3, status="A")],
    )
)
system.add_job(
    Job(
        job_id="J2",
        release=1,
        due=10,
        weight=1,
        operations=[Operation("Assembly", processing_time=2, status="A")],
    )
)

schedule = FCFSAlgorithm().schedule(system)

print(f"Algorithm: {schedule.schedule_type}")
print(f"Makespan: {schedule.time}")

for machine_schedule in schedule.machines:
    print(f"\nMachine {machine_schedule.machine}")
    for operation in machine_schedule.operations:
        print(
            f"  {operation.job_id}: "
            f"start={operation.start_time}, end={operation.end_time}"
        )

