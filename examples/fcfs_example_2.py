from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.algorithms.fcfs import FCFSAlgorithm
import matplotlib.pyplot as plt

# 1. Create system
system = System()

# 2. Define workcenters and machines
assembly_machines = [Machine(name="A1", release=0, status="A"), Machine(name="A2", release=0, status="A")]
packaging_machines = [Machine(name="P1", release=0, status="A"), Machine(name="P2", release=0, status="A")]

assembly = Workcenter(name="Assembly", release=0, status="A", rgb=(200, 150, 100), machines=assembly_machines)
packaging = Workcenter(name="Packaging", release=0, status="A", rgb=(100, 200, 150), machines=packaging_machines)

system.add_workcenter(assembly)
system.add_workcenter(packaging)

# 3. Define jobs (each job has an operation in one workcenter)
jobs = [
    Job("J1", release=0, due=20, weight=1, rgb=(255, 0, 0), operations=[Operation("Assembly", 5, "A")]),
    Job("J2", release=1, due=20, weight=1, rgb=(0, 255, 0), operations=[Operation("Packaging", 3, "A")]),
    Job("J3", release=2, due=20, weight=1, rgb=(0, 0, 255), operations=[Operation("Assembly", 4, "A")]),
    Job("J4", release=3, due=20, weight=1, rgb=(255, 255, 0), operations=[Operation("Packaging", 2, "A")]),
    Job("J5", release=5, due=25, weight=1, rgb=(255, 128, 0), operations=[Operation("Assembly", 6, "A")]),
    Job("J6", release=6, due=26, weight=1, rgb=(128, 0, 255), operations=[Operation("Packaging", 5, "A")]),
    Job("J7", release=7, due=30, weight=1, rgb=(0, 255, 255), operations=[Operation("Assembly", 3, "A")])
]

for job in jobs:
    system.add_job(job)

# 4. Run FCFS algorithm

fcfs = FCFSAlgorithm()
schedule = fcfs.schedule(system)
system.set_schedule(schedule)

# 5. Print schedule and job details using new methods
schedule.display_machine_details()
schedule.display_job_details(system)

# 7. Display sequence
schedule.display_sequence(system)

# 8. Display summary
schedule.display_summary(system)

# 6. Plot Gantt chart using new method
schedule.plot_gantt_chart(system)

