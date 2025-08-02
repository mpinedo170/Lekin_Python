from lekinpy.io import *
from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.algorithms.fcfs import FCFSAlgorithm
from lekinpy.algorithms.wspt import WSPT
import matplotlib.pyplot as plt 

# jobs = parse_job_file("Data/Experiments/Jobs_fcfs.job")
# workcenter = parse_mch_file("Data/Experiments/Machines_fcfs.mch")

# Define a complex test case
jobs = [
    Job("J1", release=1, due=0, weight=1, operations=[Operation("W1", 5, "A")]),
    Job("J2", release=2, due=0, weight=2, operations=[Operation("W1", 3, "A")]),
    Job("J3", release=4, due=0, weight=1, operations=[Operation("W1", 6, "A")]),
    Job("J4", release=6, due=0, weight=3, operations=[Operation("W1", 2, "A")]),
    Job("J5", release=8, due=0, weight=2, operations=[Operation("W1", 4, "A")])
]

# Define a single-machine workcenter

machine = [Machine("M1", 0, "A")]
workcenter = Workcenter("W1", 0, "A", machines=machine)

# Build system

system = System()
for job in jobs:
    system.add_job(job)
# for workcenter in workcenter:
system.add_workcenter(workcenter)

# export_jobs_to_jobfile(system, "Data/Experiments/exported_test_complexfcfs.job")
# export_workcenters_to_mchfile(system, "Data/Experiments/exported_test_complexfcfs.mch")
# fcfs = WSPT()
fcfs = FCFSAlgorithm()
schedule = fcfs.schedule(system)
system.set_schedule(schedule)

schedule.display_machine_details()
schedule.display_job_details(system)  
schedule.display_summary(system) 
schedule.plot_gantt_chart(system) 