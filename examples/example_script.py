from lekinpy.io import load_jobs_from_json, parse_job_file, parse_mch_file, save_schedule_to_seq, load_workcenters_from_json
from lekinpy.algorithms.fcfs import FCFSAlgorithm
from lekinpy.machine import Machine, Workcenter
from lekinpy.schedule import Schedule
from lekinpy.system import System
from lekinpy.job import Job, Operation
import json
# Load .job and .mch files
jobs = parse_job_file("Data/Single Machine/single.job")
workcenters = parse_mch_file("Data/Single Machine/single.mch")

print("\nJobs loaded:", len(jobs))
print("Jobs:", jobs)
print("\nWorkcenters loaded:", len(workcenters))
print("Workcenters:", workcenters)

# Print loaded data
# print("Jobs:")
# for job in jobs:
#     print(job)
#     print("Procesing Time",job.operations[0].processing_time)  # or .duration, .time, etc.

# print("Workcenters:")
# for wc in workcenters:
#     print(wc)

# Create system and add jobs and machines
system = System()
for job in jobs:
    system.add_job(job)
for wc in workcenters:
    system.add_workcenter(wc)

# print("\nSystem:")
# print(json.dumps(system.to_dict(), indent=2))

# # I want to add a job here through the job class
# job1 = Job(
#     job_id="Job1",
#     release=0,
#     due=10,
#     weight=1,
#     rgb=(255, 0, 0),
#     operations=[
#         Operation(workcenter="WC1", processing_time=5, status="active"),
#         Operation(workcenter="WC2", processing_time=3, status="active")
#     ]
# )

# system.add_job(job1)
# print("\nJob added to system:", job1)


# job2 = Job(
#     job_id="Job2",
#     release=1,
#     due=12,
#     weight=2,
#     operations=[
#         Operation(workcenter="WC1", processing_time=4, status="active"),
#         Operation(workcenter="WC3", processing_time=6, status="active")
#     ]
# )

# system.add_job(job2)
# print("\nJob added to system:", job2)

# jobs_json = load_jobs_from_json("Data/Experiments/parallel.json")
# print("\nJobs loaded from JSON:", len(jobs_json))
# for job in jobs_json:
#     print("\n",job)
#     system.add_job(job)

# print("\nUpdated System:")
# print(json.dumps(system.to_dict(), indent=2))

# machines_json = load_workcenters_from_json("Data/Experiments/parallel.json")
# print("\nMachines loaded from JSON:", len(machines_json))

# print("Machines:", machines_json)
# for wc in machines_json:
#     system.add_workcenter(wc)

# m1 = Machine(name="Machine1", release=0, status="active")
# m2 = Machine(name="Machine2", release=1, status="inactive")
# workcenter1 = Workcenter(name="Workcenter1", release=0, status="active", machines=[m1, m2])
# system.add_workcenter(workcenter1)


# print("Updated System:")
print(json.dumps(system.to_dict(), indent=2))


# Run FCFS scheduling algorithm
fcfs = FCFSAlgorithm()
system_schedule = fcfs.schedule(system)

# Print schedule
print("Schedule:")
print(system_schedule.to_dict())

# # Save schedule to .seq file
# # with open("Data/Single Machine/output.seq", "w") as f:
# #     for machine_schedule in system_schedule.machines:
# #         f.write(f"Machine: {machine_schedule.workcenter};{machine_schedule.machine}\n")
# #         for operation in machine_schedule.operations:
# #             f.write(f"  Oper: {operation}\n")

# save_schedule_to_seq(system_schedule, "Data/Single Machine/output.seq")