import json
from .job import Job, Operation
from .machine import Workcenter, Machine

def load_jobs_from_json(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return [Job.from_dict(j) for j in data['jobs']]

def load_workcenters_from_json(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return [Workcenter.from_dict(wc) for wc in data['workcenters']]



def save_schedule_to_json(schedule, path):
    with open(path, 'w') as f:
        json.dump(schedule.to_dict(), f, indent=2)

def parse_job_file(filepath):
    jobs = []
    with open(filepath) as f:
        lines = f.readlines()
    job = None
    for line in lines:
        line = line.strip()
        if line.startswith("Job:"):
            if job:
                jobs.append(job)
            job = {"operations": []}
            job["job_id"] = line.split(":")[1].strip()
        elif line.startswith("Release:"):
            job["release"] = int(line.split(":")[1].strip())
        elif line.startswith("Due:"):
            job["due"] = int(line.split(":")[1].strip())
        elif line.startswith("Weight:"):
            job["weight"] = int(line.split(":")[1].strip())
        elif line.startswith("RGB:"):
            job["rgb"] = tuple(map(int, line.split(":")[1].strip().split(";")))
        elif line.startswith("Oper:"):
            parts = line.split(":")[1].strip().split(";")
            job["operations"].append({
                "workcenter": parts[0],
                "processing_time": int(parts[1]),
                "status": parts[2]
            })
    if job:
        jobs.append(job)
    return [Job.from_dict(j) for j in jobs]

def parse_mch_file(filepath):
    workcenters = []
    with open(filepath) as f:
        lines = f.readlines()
    wc = None
    machine = None
    for line in lines:
        if line.startswith("Workcenter:"):
            if wc:
                workcenters.append(wc)
            wc_name = line.split(":")[1].strip()
            wc = {'name': wc_name, 'machines': [], 'release': 0, 'status': 'A', 'rgb': (0,0,0)}
            machine = None
        elif line.strip().startswith("Machine:"):
            if machine:
                wc['machines'].append(machine)
            machine_name = line.split(":")[1].strip()
            machine = {'name': machine_name, 'release': 0, 'status': 'A'}
        elif line.strip().startswith("Release:"):
            value = int(line.split(":")[1].strip())
            if machine is not None:
                machine['release'] = value
            else:
                wc['release'] = value
        elif line.strip().startswith("Status:"):
            value = line.split(":")[1].strip()
            if machine is not None:
                machine['status'] = value
            else:
                wc['status'] = value
        elif line.strip().startswith("RGB:"):
            rgb = tuple(map(int, line.split(":")[1].strip().split(";")))
            wc['rgb'] = rgb
    if machine:
        wc['machines'].append(machine)
    if wc:
        workcenters.append(wc)
    # Ensure every workcenter has at least one machine
    for wc_dict in workcenters:
        if not wc_dict["machines"]:
            wc_dict["machines"].append({
                "name": f"{wc_dict['name']}.01",
                "release": wc_dict.get("release", 0),
                "status": wc_dict.get("status", "A")
            })
    # Convert dicts to objects and set workcenter attribute on each machine
    workcenter_objs = []
    for wc_dict in workcenters:
        machines = []
        for m_dict in wc_dict['machines']:
            m = Machine(
                name=m_dict['name'],
                release=m_dict['release'],
                status=m_dict['status']
            )
            machines.append(m)
        workcenter_objs.append(Workcenter(
            name=wc_dict['name'],
            release=wc_dict['release'],
            status=wc_dict['status'],
            rgb=wc_dict['rgb'],
            machines=machines
        ))
    return workcenter_objs


def parse_seq_file(filepath):
    schedules = []
    with open(filepath) as f:
        lines = f.readlines()
    schedule = None
    machines = []
    machine = None
    for line in lines:
        line = line.strip()
        if line.startswith("Schedule:"):
            if schedule:
                schedule['machines'] = machines
                schedules.append(schedule)
            schedule = {}
            machines = []
            schedule['schedule_type'] = line.split(":")[1].strip()
        elif line.startswith("RGB:"):
            schedule['rgb'] = tuple(map(int, line.split(":")[1].strip().split(";")))
        elif line.startswith("Time:"):
            schedule['time'] = int(line.split(":")[1].strip())
        elif line.startswith("Machine:"):
            if machine:
                machines.append(machine)
            parts = line.split(":")[1].strip().split(";")
            machine = {'workcenter': parts[0], 'machine': parts[1], 'operations': []}
        elif line.startswith("Oper:"):
            job_id = line.split(":")[1].strip()
            machine['operations'].append(job_id)
    if machine:
        machines.append(machine)
    if schedule:
        schedule['machines'] = machines
        schedules.append(schedule)
    return schedules

def save_schedule_to_seq(schedule, filepath):
    with open(filepath, "w") as f:
        # Write schedule header
        f.write(f"Schedule:           {schedule.schedule_type}\n")
        rgb_str = ";".join(str(x) for x in schedule.rgb)
        f.write(f"  RGB:                {rgb_str}\n")
        f.write(f"  Time:               {schedule.time}\n")
        for machine_schedule in schedule.machines:
            # Write both workcenter and machine name separated by semicolon
            f.write(f"  Machine:            {machine_schedule.workcenter};{machine_schedule.machine}\n")
            for job_id in machine_schedule.operations:
                f.write(f"    Oper:               {job_id}\n")


# def parse_mch_file(filepath):
#     workcenters = []
#     with open(filepath) as f:
#         lines = f.readlines()
#     wc = None
#     machine = None
#     for line in lines:
#         line = line.strip()
#         if line.startswith("Workcenter:"):
#             if wc:
#                 workcenters.append(wc)
#             wc = {"machines": []}
#             wc["name"] = line.split(":")[1].strip()
#         elif line.startswith("Release:") and machine is None:
#             wc["release"] = int(line.split(":")[1].strip())
#         elif line.startswith("Status:") and machine is None:
#             wc["status"] = line.split(":")[1].strip()
#         elif line.startswith("RGB:"):
#             wc["rgb"] = tuple(map(int, line.split(":")[1].strip().split(";")))
#         elif line.startswith("Machine:"):
#             if machine:
#                 wc["machines"].append(machine)
#             machine = {}
#             machine["name"] = line.split(":")[1].strip()
#         elif line.startswith("Release:") and machine is not None:
#             machine["release"] = int(line.split(":")[1].strip())
#         elif line.startswith("Status:") and machine is not None:
#             machine["status"] = line.split(":")[1].strip()
#         elif line.startswith("Batch:"):
#             machine["batch"] = int(line.split(":")[1].strip())
#     if machine:
#         wc["machines"].append(machine)
#     if wc:
#         workcenters.append(wc)
#     for wc_dict in workcenters:
#         if not wc_dict["machines"]:
#             wc_dict["machines"].append({
#                 "name": f"{wc_dict['name']}.01",
#                 "release": wc_dict.get("release", 0),
#                 "status": wc_dict.get("status", "A"),
#                 "batch": 1
#             })
#     return [Workcenter.from_dict(w) for w in workcenters]