# lekinpy — API Reference

<!--
Main API reference for the lekinpy library (v0.1.0).
Use this as both developer documentation and student learning material.
-->


This document describes the public API exposed by `lekinpy 0.1.0`.

- Install: `pip install lekinpy`
- Optional plotting: `pip install lekinpy[plot]`

## Table of Contents
  - [Core Entities](#core-entities)
    - [Job](#job)
    - [Operation](#operation)
    - [Machine](#machine)
    - [Workcenter](#workcenter)
    - [Schedule](#schedule)
    - [System](#system)
  - [IO Helpers](#io-helpers)
    - [load_jobs_from_json](#load_jobs_from_json)
    - [load_workcenters_from_json](#load_workcenters_from_json)
    - [save_schedule_to_json](#save_schedule_to_json)
    - [parse_job_file](#parse_job_file)
    - [parse_mch_file](#parse_mch_file)
    - [parse_seq_file](#parse_seq_file)
    - [save_schedule_to_seq](#save_schedule_to_seq)
    - [export_jobs_to_jobfile](#export_jobs_to_jobfile)
    - [export_workcenters_to_mchfile](#export_workcenters_to_mchfile)
    - [export_system_to_json](#export_system_to_json)
  - [Algorithms](#algorithms)
    - [SchedulingAlgorithm (base)](#schedulingalgorithm-base)
    - [FCFSAlgorithm](#fcfsalgorithm)
    - [SPTAlgorithm](#sptalgorithm)
    - [EDDAlgorithm](#eddalgorithm)
    - [WSPTAlgorithm](#wsptalgorithm)
  - [Authoring Custom Algorithms](#authoring-custom-algorithms)
  - [End‑to‑End Examples](#end-to-end-examples)

---

## Core Entities

### Job
Represents a schedulable job composed of one or more operations, with optional visualization color.

**Constructor**
```python
Job(
    job_id: str,
    release: float,
    due: float,
    weight: float,
    operations: list[Operation],
    rgb: tuple[int, int, int] | None = None,
)
```
- **job_id** (`str`): Unique identifier (e.g., "J01").
- **release** (`float`): Release/ready time.
- **due** (`float`): Due date/time.
- **weight** (`float`): Job priority weight used by some algorithms.
- **operations** (`list[Operation]`): Ordered list of operations for this job.
- **rgb** (`tuple[int,int,int] | None`): Optional display color.

**Static Methods**
- `from_dict(data: Dict[str, Any]) -> Job`  
  Build a `Job` from a dictionary with keys `job_id`, `release`, `due`, `weight`, optional `rgb`, and `operations` (list of op dicts).

**Instance Methods**
- `to_dict() -> Dict[str, Any]`  
  Serialize the job, including nested operations.
- `__repr__() -> str`  
  Debug representation similar to `Job(J01, 0, 0, 2, (0, 128, 255), [...])`.

**Attributes**
- `job_id: str`
- `release: float`
- `due: float`
- `weight: float`
- `operations: list[Operation]`
- `rgb: tuple[int,int,int]`

**Examples**
```python
from lekinpy.job import Job, Operation

ops = [
    Operation("W01", 5, "A"),
    Operation("W02", 3, "A"),
]
job = Job("J01", release=0, due=10, weight=2, operations=ops)

# Access first op's processing time
pt = job.operations[0].processing_time  # 5

# Round-trip via dict
payload = job.to_dict()
job2 = Job.from_dict(payload)
```

---

### Operation
Represents a single operation step of a job: which workcenter it needs, how long it takes, and its status.

**Constructor**
```python
Operation(workcenter: str, processing_time: float, status: str)
```
- **workcenter** (`str`): Target workcenter identifier (e.g., "W01").
- **processing_time** (`float`): Required processing time at the workcenter.
- **status** (`str`): Status flag (e.g., "A" for active).

**Static Methods**
- `from_dict(data: Dict[str, Any]) -> Operation`  
  Build an operation from a dictionary with keys `workcenter`, `processing_time`, `status`.

**Instance Methods**
- `to_dict() -> Dict[str, Any]`  
  Serialize to a dictionary.
- `__repr__() -> str`  
  Debug representation, e.g., `Operation(W01, 5, A)`.

**Examples**
```python
from lekinpy.job import Operation

op = Operation("W01", 5, "A")
assert op.processing_time == 5
```

### Machine
Represents a single processing resource that can execute operations. A `Machine` has a name, a release time (availability), and a status.

**Constructor**
```python
Machine(name: str, release: float, status: str)
```
- **name** (`str`): Unique machine identifier (e.g., "A1").
- **release** (`float`): Earliest time the machine is available.
- **status** (`str`): Arbitrary status flag (e.g., "A" for active).  
  *Raises* `TypeError` if arguments are of invalid types.

**Static Methods**
- `from_dict(data: Dict[str, Any]) -> Machine`  
  Build a `Machine` from a dictionary with keys `name`, `release`, `status`.

**Instance Methods**
- `to_dict() -> Dict[str, Any]`  
  Serialize the machine into a dict: `{"name", "release", "status"}`.
- `__repr__() -> str`  
  Debug representation, e.g., `Machine(A1, 0.0, A)`.

**Examples**
```python
from lekinpy.machine import Machine

# direct construction
m1 = Machine(name="A1", release=0, status="A")

# from a dictionary
m2 = Machine.from_dict({
    "name": "A2",
    "release": 5,
    "status": "A",
})

# serialize
payload = m1.to_dict()  # {"name": "A1", "release": 0.0, "status": "A"}
```

---


### Workcenter
A group of one or more `Machine` instances that compete to process operations. Each workcenter can have an RGB color for visualization.

**Constructor**
```python
Workcenter(
    name: str,
    release: float,
    status: str,
    machines: list[Machine],
    rgb: tuple[int, int, int] | None = None,
)
```
- **name** (`str`): Workcenter identifier (e.g., "W01").
- **release** (`float`): Earliest time the workcenter is available.
- **status** (`str`): Arbitrary status flag (e.g., "A").
- **machines** (`list[Machine]`): Non-empty list of `Machine` objects.
- **rgb** (`tuple[int,int,int] | None`): Optional color. If omitted, a color is assigned from an internal palette.  
  *Raises* `TypeError` if arguments are invalid (including non-`Machine` items in `machines`).

**Static Methods**
- `from_dict(data: Dict[str, Any]) -> Workcenter`  
  Expects keys: `name`, `release`, `status`, optional `rgb`, and `machines` (list of machine dicts).

**Instance Methods**
- `to_dict() -> Dict[str, Any]`  
  Serialize including nested machines.
- `__repr__() -> str`  
  Debug representation with color and machines listed.

**Notes**
- When `rgb` is not provided, a color is popped from an internal shuffled palette, ensuring variety across workcenters.

**Examples**
```python
from lekinpy.machine import Machine, Workcenter

# create machines
m1 = Machine("A1", release=0, status="A")
m2 = Machine("A2", release=0, status="A")

# create a workcenter with an auto-assigned color
wc = Workcenter(name="W01", release=0, status="A", machines=[m1, m2])

# provide an explicit color
wc_blue = Workcenter(
    name="W02", release=0, status="A", machines=[Machine("B1", 0, "A")], rgb=(0, 128, 255)
)

# round-trip via dict
wc_dict = wc.to_dict()
wc2 = Workcenter.from_dict(wc_dict)
```

---

### MachineSchedule
Represents the list of jobs assigned to a specific machine within a workcenter.

**Constructor**
```python
MachineSchedule(workcenter: Optional[str], machine: str, operations: list[str])
```
- **workcenter** (`str | None`): Identifier of the parent workcenter, or `None`.
- **machine** (`str`): Machine identifier.
- **operations** (`list[str]`): Ordered job IDs assigned to this machine.

**Instance Methods**
- `to_dict() -> dict[str, Any]`  
  Serialize to `{ "workcenter": ..., "machine": ..., "operations": [...] }`.

**Example**
```python
from lekinpy.schedule import MachineSchedule
ms = MachineSchedule(workcenter="W01", machine="A1", operations=["J1", "J2"])
print(ms.to_dict())
```

---

### Schedule
Represents a full scheduling result across machines, including display and plotting utilities.

**Constructor**
```python
Schedule(schedule_type: str, time: int, machines: list[MachineSchedule])
```
- **schedule_type** (`str`): Name of the scheduling algorithm or type.
- **time** (`int`): Total makespan or completion time.
- **machines** (`list[MachineSchedule]`): Machine schedules.

**Static Methods**
- `from_dict(data: dict[str, Any]) -> Schedule`  
  Rebuild a `Schedule` from serialized data.

**Instance Methods**
- `to_dict() -> dict[str, Any]`  
  Serialize including nested machines.
- `display_machine_details() -> None`  
  Print each machine with its sequence of jobs.
- `display_job_details(system) -> None`  
  Print a tabular view with job-level details and timing.
- `plot_gantt_chart(system) -> None`  
  Draw a Gantt chart using matplotlib.
- `display_sequence(system) -> None`  
  Show start/stop times and processing durations per job/machine.
- `display_summary(system) -> None`  
  Summarize key performance metrics (C_max, T_max, ΣU_j, etc.).

**Examples**
```python
from lekinpy.schedule import Schedule, MachineSchedule

machines = [
    MachineSchedule("W01", "A1", ["J1", "J2"]),
    MachineSchedule("W01", "A2", ["J3"]),
]
sched = Schedule(schedule_type="FCFS", time=10, machines=machines)

sched.display_machine_details()
# sched.plot_gantt_chart(system)  # requires a populated System with jobs
```

---


### System
Represents the complete scheduling environment, holding jobs, workcenters, and an optional computed schedule.

**Constructor**
```python
System()
```
- Creates an empty system with no jobs, no workcenters, and no schedule.

**Instance Methods**
- `add_job(job: Job) -> None`  
  Add a `Job` to the system. Raises `TypeError` if not a `Job`.
- `add_workcenter(workcenter: Workcenter) -> None`  
  Add a `Workcenter` to the system. Raises `TypeError` if not a `Workcenter`.
- `set_schedule(schedule: Schedule) -> None`  
  Attach a `Schedule` to the system. Raises `TypeError` if not a `Schedule`.
- `to_dict() -> dict[str, Any]`  
  Serialize the entire system, including jobs, workcenters, and schedule.

**Properties**
- `machines: list[Machine]`  
  All `Machine` objects across all workcenters.

**Examples**
```python
from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.schedule import Schedule, MachineSchedule

# create system
sys = System()

# add a workcenter with one machine
m1 = Machine("A1", release=0, status="A")
wc = Workcenter("W01", release=0, status="A", machines=[m1])
sys.add_workcenter(wc)

# add a job with one operation
job = Job("J01", release=0, due=10, weight=1, operations=[Operation("W01", 5, "A")])
sys.add_job(job)

# attach a schedule
sched = Schedule("FCFS", time=5, machines=[MachineSchedule("W01", "A1", ["J01"])])
sys.set_schedule(sched)

print(sys.to_dict())
```

---

## IO Helpers

### load_jobs_from_json
Load jobs from a JSON file previously saved in `system.to_dict()` format.

**Signature**
```python
load_jobs_from_json(filepath: str) -> list[Job]
```
- **filepath** (`str`): Path to the JSON file.
- **Returns**: `list[Job]` objects.

**Example**
```python
from lekinpy.io import load_jobs_from_json
jobs = load_jobs_from_json("jobs.json")
```

---

### load_workcenters_from_json
Load workcenters from a JSON file.

**Signature**
```python
load_workcenters_from_json(filepath: str) -> list[Workcenter]
```
- **filepath** (`str`): Path to the JSON file.
- **Returns**: `list[Workcenter]` objects.

**Example**
```python
from lekinpy.io import load_workcenters_from_json
wcs = load_workcenters_from_json("workcenters.json")
```

---

### save_schedule_to_json
Save a `Schedule` object to a JSON file.

**Signature**
```python
save_schedule_to_json(schedule: Schedule, path: str) -> None
```

**Example**
```python
from lekinpy.io import save_schedule_to_json
save_schedule_to_json(schedule, "schedule.json")
```

---

### parse_job_file
Parse a `.job` text file into a list of `Job` objects.

**Signature**
```python
parse_job_file(filepath: str) -> list[Job]
```

**Example**
```python
from lekinpy.io import parse_job_file
jobs = parse_job_file("example.job")
```

---

### parse_mch_file
Parse a `.mch` text file into a list of `Workcenter` objects.

**Signature**
```python
parse_mch_file(filepath: str) -> list[Workcenter]
```

**Example**
```python
from lekinpy.io import parse_mch_file
wcs = parse_mch_file("example.mch")
```

---

### parse_seq_file
Parse a `.seq` file into a list of serialized schedule dictionaries.

**Signature**
```python
parse_seq_file(filepath: str) -> list[dict[str, Any]]
```

**Example**
```python
from lekinpy.io import parse_seq_file
seqs = parse_seq_file("example.seq")
```

---

### save_schedule_to_seq
Save a `Schedule` to a `.seq` file.

**Signature**
```python
save_schedule_to_seq(schedule: Schedule, filepath: str) -> None
```

**Example**
```python
from lekinpy.io import save_schedule_to_seq
save_schedule_to_seq(schedule, "output.seq")
```

---

### export_jobs_to_jobfile
Export jobs from a `System` to a `.job` file.

**Signature**
```python
export_jobs_to_jobfile(system: System, filepath: str) -> None
```

**Example**
```python
from lekinpy.io import export_jobs_to_jobfile
export_jobs_to_jobfile(system, "output.job")
```

---

### export_workcenters_to_mchfile
Export workcenters from a `System` to a `.mch` file.

**Signature**
```python
export_workcenters_to_mchfile(system: System, filepath: str) -> None
```

**Example**
```python
from lekinpy.io import export_workcenters_to_mchfile
export_workcenters_to_mchfile(system, "output.mch")
```

---

### export_system_to_json
Export the entire `System` to a JSON file.

**Signature**
```python
export_system_to_json(system: System, filepath: str) -> None
```

**Example**
```python
from lekinpy.io import export_system_to_json
export_system_to_json(system, "system.json")
```
## Algorithms

### SchedulingAlgorithm (base)
Base class providing common utilities for building scheduling algorithms: mapping machines to workcenters, tracking machine availability, and producing `MachineSchedule` lists.

> Note: Current dynamic engine assumes **single-operation jobs** (uses the first operation of each job). Multi-operation routing will be documented when supported.

**Constructor**
```python
SchedulingAlgorithm()
```

**Public Methods**
- `prepare(system: System) -> None`  
  Initialize internal maps (machine→workcenter, availability, job lists) using the given `system`.
- `schedule(system: System) -> Schedule`  
  Abstract. Subclasses must implement to return a `Schedule`.
- `get_machine_schedules(system: System) -> list[MachineSchedule]`  
  Build `MachineSchedule` objects from internal job assignments.
- `dynamic_schedule(system: System, job_selector_fn: Callable[[list[Job]], Job]) -> tuple[int, list[MachineSchedule]]`  
  Generic engine that advances time, discovers available jobs, chooses one via `job_selector_fn`, assigns it to the earliest-available eligible machine, and continues until all jobs are scheduled.  
  **Returns**: `(total_time, machines)` where `machines` is a list of `MachineSchedule`.

**Minimal Example — authoring a custom rule**
```python
from lekinpy.algorithms.base import SchedulingAlgorithm
from lekinpy.schedule import Schedule

class MyShortestProcessingTime(SchedulingAlgorithm):
    def schedule(self, system):
        # select job with minimum processing time of its first operation
        def pick_spT(available_jobs):
            return min(available_jobs, key=lambda j: j.operations[0].processing_time)
        total_time, machines = self.dynamic_schedule(system, pick_spT)
        return Schedule(schedule_type="Custom-SPT", time=total_time, machines=machines)
```

---

### FCFSAlgorithm
First-Come, First-Served: among released jobs at the current time, pick the one with the **earliest release time** (ties broken by job_id).
> Implementation note: the current FCFS schedules **all operations of each job in order**. Other dynamic-rule algorithms (SPT/EDD/WSPT) operate on the first operation under a single-operation assumption.

**Signature**
```python
FCFSAlgorithm().schedule(system: System) -> Schedule
```

**Example**
```python
from lekinpy.algorithms import FCFSAlgorithm
sched = FCFSAlgorithm().schedule(system)
sched.display_machine_details()
```

---

### SPTAlgorithm
Shortest Processing Time: among released jobs, pick the smallest `processing_time` of the **first operation**.

**Signature**
```python
SPTAlgorithm().schedule(system: System) -> Schedule
```

**Example**
```python
from lekinpy.algorithms import SPTAlgorithm
sched = SPTAlgorithm().schedule(system)
```

---

### EDDAlgorithm
Earliest Due Date: among released jobs, pick the smallest `due`.

**Signature**
```python
EDDAlgorithm().schedule(system: System) -> Schedule
```

**Example**
```python
from lekinpy.algorithms import EDDAlgorithm
sched = EDDAlgorithm().schedule(system)
```

---

### WSPTAlgorithm
Weighted Shortest Processing Time: among released jobs, pick the job minimizing `processing_time / weight` for the **first operation** (equivalently, maximizing `weight / processing_time`).

**Signature**
```python
WSPTAlgorithm().schedule(system: System) -> Schedule
```

**Example**
```python
from lekinpy.algorithms import WSPTAlgorithm
sched = WSPTAlgorithm().schedule(system)
```

---

## Authoring Custom Algorithms

You can plug in your own rule by subclassing `SchedulingAlgorithm`. Use the built‑in `dynamic_schedule(...)` helper (single‑operation assumption) or implement your own loop.

### Minimal Template
```python
from lekinpy.algorithms import SchedulingAlgorithm
from lekinpy.schedule import Schedule

class MyRule(SchedulingAlgorithm):
    def schedule(self, system):
        # Choose among currently released jobs
        def pick(available_jobs):
            # example: tie‑break by job_id after shortest processing time
            return min(
                available_jobs,
                key=lambda j: (j.operations[0].processing_time, j.job_id)
            )
        total_time, machines = self.dynamic_schedule(system, pick)
        return Schedule("MyRule", total_time, machines)
```

### Using Your Algorithm in a System
```python
from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter

sys = System()
sys.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
sys.add_job(Job("J1", 0, 10, 1, [Operation("W01", 5, "A")]))

algo = MyRule()
schedule = algo.schedule(sys)
sys.set_schedule(schedule)
```

### When You Need More Than One Operation per Job
- `dynamic_schedule` currently considers the **first** operation of each job. For multi‑operation routing, either:
  - Use `FCFSAlgorithm` (which executes all operations in order), or
  - Write a custom loop: advance time, track per‑operation readiness, and assign eligible operations to machines.

### Packaging (Optional)
If you publish your rule inside `lekinpy/algorithms/`, export it via `lekinpy/algorithms/__init__.py` and `lekinpy/__init__.py` so users can do:
```python
from lekinpy.algorithms import MyRule
```

### Data IO Patterns — Three Ways to Load & Save

This example uses **FCFS** on a single‑machine system, but focuses on showing different import methods for jobs/workcenters and exporting schedules/system data.

```python
from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.algorithms.fcfs import FCFSAlgorithm
from lekinpy.io import (
    parse_job_file, parse_mch_file,
    load_jobs_from_json, load_workcenters_from_json,
    export_jobs_to_jobfile, export_workcenters_to_mchfile, export_system_to_json
)

# --- 1) Import from .job and .mch files ---
system1 = System()
jobs_from_file = parse_job_file("Data/Single Machine/single.job")
wcs_from_file = parse_mch_file("Data/Single Machine/single.mch")
for wc in wcs_from_file:
    system1.add_workcenter(wc)
for job in jobs_from_file:
    system1.add_job(job)

# --- 2) Build in Python ---
system2 = System()
m1 = Machine("A1", release=0, status="A")
wc = Workcenter("W01", release=0, status="A", machines=[m1])
system2.add_workcenter(wc)
job = Job("J01", release=0, due=10, weight=1, operations=[Operation("W01", 5, "A")])
system2.add_job(job)

# --- 3) Import from JSON ---
system3 = System()
jobs_from_json = load_jobs_from_json("jobs.json")
wcs_from_json = load_workcenters_from_json("workcenters.json")
for wc in wcs_from_json:
    system3.add_workcenter(wc)
for job in jobs_from_json:
    system3.add_job(job)

# --- Run FCFS on system1 for demo ---
fcfs = FCFSAlgorithm()
schedule = fcfs.schedule(system1)
system1.set_schedule(schedule)
schedule.display_summary(system1)

# --- Export examples ---
# Jobs to .job file
export_jobs_to_jobfile(system1, "output.job")

# Workcenters to .mch file
export_workcenters_to_mchfile(system1, "output.mch")

# Entire system to JSON
export_system_to_json(system1, "system.json")
```

**Notes**
- The `.job` / `.mch` text formats are LEKIN‑style files parsed by `parse_job_file` / `parse_mch_file`.
- Building in Python is the most flexible for generating programmatic test cases.
- JSON import/export is ideal for saving system snapshots for later runs.