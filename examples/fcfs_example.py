from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.algorithms.fcfs import FCFSAlgorithm
import matplotlib.pyplot as plt

# 1. Create system
system = System()

# 2. Create machines and workcenter
m1 = Machine(name="M1", release=0, status="A")
m2 = Machine(name="M2", release=0, status="A")
wc1 = Workcenter(name="WC1", release=0, status="A", rgb=(100, 100, 255), machines=[m1, m2])
system.add_workcenter(wc1)

# 3. Create jobs (Example inspired by Michael Pinedo)
j1 = Job("J1", release=0, due=10, weight=1, rgb=(255, 0, 0), operations=[Operation("WC1", 3, "A")])
j2 = Job("J2", release=1, due=10, weight=1, rgb=(0, 255, 0), operations=[Operation("WC1", 2, "A")])
j3 = Job("J3", release=2, due=10, weight=1, rgb=(0, 0, 255), operations=[Operation("WC1", 4, "A")])
system.add_job(j1)
system.add_job(j2)
system.add_job(j3)

# 4. Run FCFS
fcfs = FCFSAlgorithm()
schedule = fcfs.schedule(system)
system.set_schedule(schedule)

# 5. Print results
print("Schedule type:", schedule.schedule_type)
print("Total time:", schedule.time)
print("Machine Schedules:")
for ms in schedule.machines:
    print(f"{ms.machine}: {ms.operations}")

# 6. Print Gantt Chart
print("\nGantt Chart:")
timeline = []
for ms in schedule.machines:
    line = f"{ms.machine}: "
    time_marker = 0
    for job_id in ms.operations:
        job = next(j for j in system.jobs if j.job_id == job_id)
        duration = job.operations[0].processing_time
        line += f"[{job_id} | {time_marker}-{time_marker + duration}] "
        time_marker += duration
    timeline.append(line)

print("\n".join(timeline))



fig, ax = plt.subplots(figsize=(10, 3))
colors = {'J1': 'red', 'J2': 'green', 'J3': 'blue'}

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
        ax.text(time_marker + duration/2, y, job_id, ha='center', va='center', color='white', fontsize=10)
        time_marker += duration

ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels)
ax.set_xlabel('Time')
ax.set_title('Gantt Chart - FCFS Schedule')
plt.tight_layout()
plt.show()