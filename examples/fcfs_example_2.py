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

# 5. Print schedule
print("Schedule type:", schedule.schedule_type)
print("Total time:", schedule.time)
for ms in schedule.machines:
    print(f"{ms.machine}: {ms.operations}")

# 5.1. Print job timings per machine:
print("\nJob start-end times per machine:")
for ms in schedule.machines:
    print(f"\n{ms.machine}:")
    time_marker = 0
    for job_id in ms.operations:
        job = next(j for j in system.jobs if j.job_id == job_id)
        duration = job.operations[0].processing_time
        print(f"  {job_id}: start={time_marker}, end={time_marker + duration}")
        time_marker += duration

# 6. Plot Gantt chart
fig, ax = plt.subplots(figsize=(10, 4))
colors = {job.job_id: f"C{i}" for i, job in enumerate(system.jobs)}

yticks = []
yticklabels = []

for i, ms in enumerate(schedule.machines):
    y = i
    yticks.append(y)
    yticklabels.append(ms.machine)
    time_marker = 0
    for job_id in ms.operations:
        job = next(j for j in system.jobs if j.job_id == job_id)
        duration = job.operations[0].processing_time
        ax.barh(y, duration, left=time_marker, color=colors.get(job_id, 'gray'), edgecolor='black')
        ax.text(time_marker + duration / 2, y, job_id, ha='center', va='center', color='white', fontsize=10)
        print(f"{ms.machine} - {job_id}: start={time_marker}, end={time_marker + duration}")
        time_marker += duration

ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels)
ax.set_xlabel("Time")
ax.set_title("Gantt Chart - FCFS Example 2")
plt.tight_layout()
plt.show()