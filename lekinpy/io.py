import json
import os
import tempfile
from .job import Job
from .machine import Workcenter, Machine
from typing import Any, List, Dict

# ---- internal helpers for integer-only semantics ----
def _coerce_int(value: Any, field: str) -> int:
    """
    Accept ints, or floats that are whole-numbered (e.g., 5.0 → 5).
    Raise ValueError for non-integer values like 5.5, 'abc', etc.
    """
    if isinstance(value, bool):
        # prevent True/False being treated as ints
        raise ValueError(f"Invalid value for {field}: {value}. The CPP LEKIN system accepts only integers.")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise ValueError(f"Invalid value for {field}: {value}. The CPP LEKIN system accepts only integers.")
    # strings or other objects: try float first
    try:
        f = float(str(value).strip())
    except Exception:
        raise ValueError(f"Invalid value for {field}: {value}. The CPP LEKIN system accepts only integers.")
    if f.is_integer():
        return int(f)
    raise ValueError(f"Invalid value for {field}: {value}. The CPP LEKIN system accepts only integers.")


def _parse_int_str(token: str, field: str) -> int:
    """
    Parse a numeric token that may be '5', '5.0', etc., enforcing integer semantics.
    """
    return _coerce_int(token, field)

def load_jobs_from_json(filepath: str) -> List[Job]:
    with open(filepath) as f:
        data = json.load(f)
    return [Job.from_dict(j) for j in data['jobs']]


def load_workcenters_from_json(filepath: str) -> List[Workcenter]:
    with open(filepath) as f:
        data = json.load(f)
    return [Workcenter.from_dict(wc) for wc in data['workcenters']]
def save_schedule_to_json(schedule: Any, path: str) -> None:
    with open(path, 'w') as f:
        json.dump(schedule.to_dict(), f, indent=2)


def parse_job_file(filepath: str) -> List[Job]:
    jobs: List[Dict[str, Any]] = []
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
            job["release"] = _parse_int_str(line.split(":")[1].strip(), "release")
        elif line.startswith("Due:"):
            job["due"] = _parse_int_str(line.split(":")[1].strip(), "due")
        elif line.startswith("Weight:"):
            job["weight"] = _parse_int_str(line.split(":")[1].strip(), "weight")
        elif line.startswith("RGB:"):
            job["rgb"] = tuple(map(int, line.split(":")[1].strip().split(";")))
        elif line.startswith("Oper:"):
            parts = line.split(":")[1].strip().split(";")
            job["operations"].append({
                "workcenter": parts[0],
                "processing_time": _parse_int_str(parts[1], "processing_time"),
                "status": parts[2]
            })
    if job:
        jobs.append(job)
    return [Job.from_dict(j) for j in jobs]


def parse_mch_file(filepath: str) -> List[Workcenter]:
    workcenters: List[Dict[str, Any]] = []
    with open(filepath) as f:
        lines = f.readlines()
    wc = None
    machine = None
    for line in lines:
        if line.startswith("Workcenter:"):
            if wc:
                workcenters.append(wc)
            wc_name = line.split(":")[1].strip()
            wc = {'name': wc_name, 'machines': [], 'release': 0, 'status': 'A', 'rgb': (0, 0, 0)}
            machine = None
        elif line.strip().startswith("Machine:"):
            if machine:
                wc['machines'].append(machine)
            machine_name = line.split(":")[1].strip()
            machine = {'name': machine_name, 'release': 0, 'status': 'A'}
        elif line.strip().startswith("Release:"):
            value = _parse_int_str(line.split(":")[1].strip(), "release")
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
    workcenter_objs: List[Workcenter] = []
    for wc_dict in workcenters:
        machines: List[Machine] = []
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



def parse_seq_file(filepath: str) -> List[Dict[str, Any]]:
    schedules: List[Dict[str, Any]] = []
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


def save_schedule_to_seq(schedule: Any, filepath: str) -> None:
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



# ------------------- Export Functions -------------------
def export_jobs_to_jobfile(system: Any, filepath: str) -> None:
    # Build content in-memory so we don't leave partial files on error
    lines = []
    lines.append("Shop:               Job\n")
    for job in system.jobs:
        rel = _coerce_int(job.release, "release")
        due = _coerce_int(job.due, "due")
        wgt = _coerce_int(job.weight, "weight")
        lines.append(f"Job:                {job.job_id}\n")
        lines.append(f"  RGB:                {';'.join(map(str, job.rgb))}\n")
        lines.append(f"  Release:            {rel}\n")
        lines.append(f"  Due:                {due}\n")
        lines.append(f"  Weight:             {wgt}\n")
        for op in job.operations:
            pt = _coerce_int(op.processing_time, "processing_time")
            lines.append(f"  Oper:               {op.workcenter};{pt};{op.status}\n")
        lines.append("\n")
    # Atomic write: write to temp then replace
    dir_name = os.path.dirname(filepath) or "."
    with tempfile.NamedTemporaryFile("w", delete=False, dir=dir_name, encoding="utf-8") as tmp:
        tmp.writelines(lines)
        tmp_path = tmp.name
    os.replace(tmp_path, filepath)



def export_workcenters_to_mchfile(system: Any, filepath: str) -> None:
    lines = []
    lines.append("Ordinary:\n")
    for wc in system.workcenters:
        wc_rel = _coerce_int(wc.release, "release")
        lines.append(f"Workcenter:         {wc.name}\n")
        lines.append(f"  RGB:                {';'.join(map(str, wc.rgb))}\n")
        lines.append(f"  Release:            {wc_rel}\n")
        lines.append(f"  Status:             {wc.status}\n")
        for m in wc.machines:
            m_rel = _coerce_int(m.release, "release")
            lines.append(f"Machine:            {m.name}\n")
            lines.append(f"    Release:            {m_rel}\n")
            lines.append(f"    Status:             {m.status}\n")
        lines.append("\n")
    dir_name = os.path.dirname(filepath) or "."
    with tempfile.NamedTemporaryFile("w", delete=False, dir=dir_name, encoding="utf-8") as tmp:
        tmp.writelines(lines)
        tmp_path = tmp.name
    os.replace(tmp_path, filepath)



def export_system_to_json(system: Any, filepath: str) -> None:
    system_dict = {
        "jobs": [job.to_dict() for job in system.jobs],
        "workcenters": [wc.to_dict() for wc in system.workcenters]
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(system_dict, f, indent=2)
    except (OSError, TypeError, ValueError) as e:
        print(f"Error exporting system to JSON: {e}")
