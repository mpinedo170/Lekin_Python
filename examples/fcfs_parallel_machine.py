from lekinpy.io import *
from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.algorithms.fcfs import FCFSAlgorithm
import matplotlib.pyplot as plt 

jobs = parse_job_file("Data/Experiments/Jobs_fcfs_parallel.job")
workcenter = parse_mch_file("Data/Experiments/Machines_fcfs_parallel.mch")

# Build system

system = System()
for job in jobs:
    system.add_job(job)
# for wc in workcentre:
for wc in workcenter:
    system.add_workcenter(wc)

fcfs = FCFSAlgorithm()
schedule = fcfs.schedule(system)
system.set_schedule(schedule)

schedule.display_machine_details()
schedule.display_job_details(system)  
schedule.display_summary(system) 
schedule.plot_gantt_chart(system) 