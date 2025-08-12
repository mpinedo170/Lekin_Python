from lekinpy.io import export_jobs_to_jobfile, export_workcenters_to_mchfile
from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.algorithms.fcfs import FCFSAlgorithm
# from lekinpy.algorithms.spt import SPTAlgorithm
# from lekinpy.algorithms.edd import EDDAlgorithm
from lekinpy.algorithms.wspt import WSPTAlgorithm
import matplotlib.pyplot as plt

# 1. Create system
system = System()

# 2. Define workcenters and machines
# Single workcenter with a single machine
single_machine = [Machine(name="M1", release=0, status="A")]
single_workcenter = Workcenter(name="MainWC", release=0, status="A", rgb=(200, 150, 100), machines=single_machine)

system.add_workcenter(single_workcenter)

# 3. Define jobs (each job has an operation in the single workcenter)
jobs = [
    Job("J1", release=0, due=22, weight=3, rgb=(255, 0, 0), operations=[Operation("MainWC", 7, "A")]),
    Job("J2", release=1, due=24, weight=2, rgb=(0, 255, 0), operations=[Operation("MainWC", 5, "A")]),
    Job("J3", release=7, due=26, weight=5, rgb=(0, 0, 255), operations=[Operation("MainWC", 1, "A")]),
    Job("J4", release=4, due=20, weight=1, rgb=(255, 255, 0), operations=[Operation("MainWC", 3, "A")]),
    Job("J5", release=6, due=30, weight=4, rgb=(255, 128, 0), operations=[Operation("MainWC", 9, "A")]),
    Job("J6", release=8, due=28, weight=2, rgb=(128, 0, 255), operations=[Operation("MainWC", 4, "A")]),
    Job("J7", release=8, due=35, weight=3, rgb=(0, 255, 255), operations=[Operation("MainWC", 5, "A")])
]

for job in jobs:
    system.add_job(job)

wspt = WSPTAlgorithm()
schedule_wspt = wspt.schedule(system)
system.set_schedule(schedule_wspt)
# 5. Print schedule and job details using new methods
schedule_wspt.display_machine_details()
schedule_wspt.display_job_details(system)
# 7. Display sequence
schedule_wspt.display_sequence(system)
# 8. Display summary
schedule_wspt.display_summary(system)
# 6. Plot Gantt chart using new method
schedule_wspt.plot_gantt_chart(system)  


# export_jobs_to_jobfile(system, "Data/Exported/Wspt_jobs.job")
# export_workcenters_to_mchfile(system, "Data/Exported/wspt_workcenters.mch")

# 4. Run FCFS algorithm
# fcfs = FCFSAlgorithm()
# schedule = fcfs.schedule(system)
# system.set_schedule(schedule)
# # 5. Print schedule and job details using new methods
# schedule.display_machine_details()
# schedule.display_job_details(system)
# # 7. Display sequence
# schedule.display_sequence(system)
# # 8. Display summary
# schedule.display_summary(system)
# # 6. Plot Gantt chart using new method
# schedule.plot_gantt_chart(system)


# Non-preemptive forced idelness, Premeptive scheduling forced idelness

# spt = SPTAlgorithm()
# schedule_spt = spt.schedule(system)
# system.set_schedule(schedule_spt)
# # 5. Print schedule and job details using new methods
# schedule_spt.display_machine_details()
# schedule_spt.display_job_details(system)
# # 7. Display sequence
# schedule_spt.display_sequence(system)
# # 8. Display summary
# schedule_spt.display_summary(system)
# # 6. Plot Gantt chart using new method
# schedule_spt.plot_gantt_chart(system)

# edd = EDDAlgorithm()
# schedule_edd = edd.schedule(system)
# system.set_schedule(schedule_edd)
# # 5. Print schedule and job details using new methods
# schedule_edd.display_machine_details()
# schedule_edd.display_job_details(system)
# # 7. Display sequence
# schedule_edd.display_sequence(system)
# # 8. Display summary
# schedule_edd.display_summary(system)
# # 6. Plot Gantt chart using new method
# schedule_edd.plot_gantt_chart(system)