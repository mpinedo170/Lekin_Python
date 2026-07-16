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
system.set_schedule(schedule)

# Use the built-in human-readable reports for console output. Use
# schedule.to_dict() only when you need structured data for serialization.
schedule.display_machine_details()
schedule.display_job_details(system)
schedule.display_sequence(system)
schedule.display_summary(system)
