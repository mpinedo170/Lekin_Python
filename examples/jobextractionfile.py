from lekinpy.io import parse_job_file as parse_job_file_io
from lekinpy.job import parse_job_file as parse_job_file_custom
from lekinpy.io import parse_mch_file

# Path to the .job file
job_file_path = "Data/Single Machine/single.job"

# Method 1: using io.py
jobs_io = parse_job_file_io(job_file_path)
print("\nJobs from io.py:")
for job in jobs_io:
    print(job)

# Method 2: using custom function from job.py
jobs_custom = parse_job_file_custom(job_file_path)
print("\nJobs from job.py:")
for job in jobs_custom:
    print(job)



# Path to the .mch file
mch_file_path = "Data/Single Machine/single.mch"

# Parse the machine file
workcenters = parse_mch_file(mch_file_path)

# Print each workcenter and its machines
print("\nWorkcenters from .mch file:")
for wc in workcenters:
    print(wc)
    for machine in wc.machines:
        print("  ", machine)