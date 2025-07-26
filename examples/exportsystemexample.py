

from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.io import export_jobs_to_jobfile, export_workcenters_to_mchfile, export_system_to_json

# Create a test system
system = System()

# Define workcenters and machines
wc1_machines = [Machine(name="A1", release=0, status="A"), Machine(name="A2", release=0, status="A")]
wc2_machines = [Machine(name="P1", release=0, status="A"), Machine(name="P2", release=0, status="A")]

wc1 = Workcenter(name="Assembly", release=0, status="A", rgb=(200, 150, 100), machines=wc1_machines)
wc2 = Workcenter(name="Packaging", release=0, status="A", rgb=(100, 200, 150), machines=wc2_machines)

system.add_workcenter(wc1)
system.add_workcenter(wc2)

# Define jobs
jobs = [
    Job("J1", release=0, due=20, weight=1, rgb=(255, 0, 0), operations=[Operation("Assembly", 5, "A")]),
    Job("J2", release=1, due=20, weight=1, rgb=(0, 255, 0), operations=[Operation("Packaging", 3, "A")]),
]

for job in jobs:
    system.add_job(job)

# Export the system to different formats
export_jobs_to_jobfile(system, "Data/Single Machine/exported_test.job")
export_workcenters_to_mchfile(system, "Data/Single Machine/exported_test.mch")
export_system_to_json(system, "Data/Single Machine/exported_system.json")

print("Export complete.")