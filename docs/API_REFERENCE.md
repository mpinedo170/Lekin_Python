# lekinpy — Reference

<!--
Main reference for the lekinpy library (v0.1.0).
Use this as both developer documentation and student learning material.
-->

- Install: `pip install lekinpy`
- Optional plotting: `pip install lekinpy[plot]`

## Table of Contents
  - [Core Entities](#core-entities)
    - [Job](#job)
    - [Operation](#operation)
    - [Machine](#machine)
    - [Workcenter](#workcenter)
    - [ScheduledOperation](#scheduledoperation)
    - [MachineSchedule](#machineschedule)
    - [Schedule](#schedule)
    - [System](#system)
  - [Validation & Exceptions](#validation--exceptions)
  - [IO Helpers](#io-helpers)
    - [load_jobs_from_json](#load_jobs_from_json)
    - [load_workcenters_from_json](#load_workcenters_from_json)
    - [save_schedule_to_json](#save_schedule_to_json)
    - [load_schedule_from_json](#load_schedule_from_json)
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

### ScheduledOperation
Represents a single operation's placement in a finished schedule: which
job/operation it is, where it runs, when it runs, and where it falls in the
machine's sequence. This is the unit of data `MachineSchedule` stores — one
record per operation, not one bare job-id string per job.

**Constructor**
```python
ScheduledOperation(
    job_id: str,
    operation_index: int,
    workcenter: Optional[str],
    machine: str,
    start_time: float,
    end_time: float,
    sequence_position: int,
    status: Optional[str] = None,
)
```
- **job_id** (`str`): Which job this operation belongs to.
- **operation_index** (`int`): Index into that job's `operations` list —
  needed because a job's operations may run on different machines, or even
  revisit the same machine, so `job_id` alone doesn't identify *which*
  operation this is.
- **workcenter** / **machine** (`str`): Where this operation ran.
- **start_time** / **end_time** (`float`): When this operation ran.
- **sequence_position** (`int`): This operation's position (0-based) within
  its machine's own operation list.
- **status** (`str | None`): A snapshot of the source `Operation.status` at
  scheduling time.

**Static Methods**
- `from_dict(data: Dict[str, Any]) -> ScheduledOperation`

**Instance Methods**
- `to_dict() -> Dict[str, Any]`

**Example**
```python
from lekinpy.schedule import ScheduledOperation
so = ScheduledOperation(
    job_id="J1", operation_index=0, workcenter="W01", machine="A1",
    start_time=0, end_time=5, sequence_position=0, status="A",
)
```

---

### MachineSchedule
Represents every operation assigned to a specific machine within a
workcenter, in the order they run.

**Constructor**
```python
MachineSchedule(workcenter: Optional[str], machine: str, operations: list[ScheduledOperation])
```
- **workcenter** (`str | None`): Identifier of the parent workcenter, or `None`.
- **machine** (`str`): Machine identifier.
- **operations** (`list[ScheduledOperation]`): Every operation scheduled
  on this machine, in run order. A job with multiple operations on this
  machine (or spread across several machines) appears once per operation,
  not once per job — read `operation_index` to tell them apart.

**Static Methods**
- `from_dict(data: Dict[str, Any]) -> MachineSchedule`

**Instance Methods**
- `to_dict() -> dict[str, Any]`  
  Serialize to `{ "workcenter": ..., "machine": ..., "operations": [...] }`,
  where each operation is a full `ScheduledOperation.to_dict()`.

**Example**
```python
from lekinpy.schedule import MachineSchedule, ScheduledOperation
ms = MachineSchedule(workcenter="W01", machine="A1", operations=[
    ScheduledOperation("J1", 0, "W01", "A1", 0, 5, 0, "A"),
    ScheduledOperation("J2", 0, "W01", "A1", 5, 8, 1, "A"),
])
print(ms.to_dict())
```

---

### Schedule
Represents a full scheduling result across machines, including display and
plotting utilities. All of the display/plotting methods below read timing
directly from each machine's `ScheduledOperation` records — nothing is
recomputed from `job.operations[0]` on the fly, so they give correct
results for multi-operation jobs and work the same whether the `Schedule`
was just computed or loaded back from JSON/`.seq`.

**Constructor**
```python
Schedule(
    schedule_type: str,
    time: int,
    machines: list[MachineSchedule],
    rgb: Optional[Tuple[int, int, int]] = None,
)
```
- **schedule_type** (`str`): Name of the scheduling algorithm or type.
- **time** (`int`): Total makespan or completion time.
- **machines** (`list[MachineSchedule]`): Machine schedules.
- **rgb** (`tuple[int,int,int] | None`): Optional display color, mainly for
  round-tripping the RGB line in `.seq` files.

**Static Methods**
- `from_dict(data: dict[str, Any]) -> Schedule`  
  Rebuild a `Schedule` (and its nested `MachineSchedule`/`ScheduledOperation`
  objects) from serialized data — works with dicts produced by either
  `to_dict()` or `parse_seq_file()`.

**Instance Methods**
- `to_dict() -> dict[str, Any]`  
  Serialize including nested machines and their `ScheduledOperation` records.
- `display_machine_details() -> None`  
  Print each machine with the job IDs of its scheduled operations.
- `display_job_details(system) -> None`  
  Print a tabular view with job-level details and timing (begin, end, total
  processing time, tardiness), read from each job's `ScheduledOperation`
  records.
- `plot_gantt_chart(system) -> None`  
  Draw a Gantt chart using matplotlib. Multi-operation jobs are labeled per
  operation (e.g. `"J1.0"`, `"J1.1"`) since a job can appear more than once.
- `display_sequence(system) -> None`  
  Show each operation's actual start/stop time and duration, per machine.
- `display_summary(system) -> None`  
  Summarize key performance metrics (C_max, T_max, ΣU_j, etc.), computed
  from each job's `ScheduledOperation` records rather than from mutated
  `Job.start_time`/`Job.end_time` attributes.

**Examples**
```python
from lekinpy.schedule import Schedule, MachineSchedule, ScheduledOperation

machines = [
    MachineSchedule("W01", "A1", [
        ScheduledOperation("J1", 0, "W01", "A1", 0, 5, 0, "A"),
        ScheduledOperation("J2", 0, "W01", "A1", 5, 9, 1, "A"),
    ]),
]
sched = Schedule(schedule_type="FCFS", time=9, machines=machines)

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
  Add a `Job` to the system. Raises `TypeError` if not a `Job`, or
  `DuplicateJobIdError` if a job with the same `job_id` was already added.
- `add_workcenter(workcenter: Workcenter) -> None`  
  Add a `Workcenter` to the system. Raises `TypeError` if not a
  `Workcenter`, or `DuplicateMachineIdError` if one of its machines shares
  a name with a machine already in the system (from a different workcenter).
- `set_schedule(schedule: Schedule) -> None`  
  Attach a `Schedule` to the system. Raises `TypeError` if not a `Schedule`.
- `validate() -> None`  
  Check that every job operation's `workcenter` references a workcenter
  actually present in the system. Raises `MissingWorkcenterError` if not.
  Jobs and workcenters can be added in either order — this is safe to call
  once the system is fully built, and every built-in `SchedulingAlgorithm`
  calls it automatically before scheduling (see
  [SchedulingAlgorithm](#schedulingalgorithm-base)).
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
from lekinpy.schedule import Schedule, MachineSchedule, ScheduledOperation

# create system
sys = System()

# add a workcenter with one machine
m1 = Machine("A1", release=0, status="A")
wc = Workcenter("W01", release=0, status="A", machines=[m1])
sys.add_workcenter(wc)

# add a job with one operation
job = Job("J01", release=0, due=10, weight=1, operations=[Operation("W01", 5, "A")])
sys.add_job(job)

sys.validate()  # raises MissingWorkcenterError if any operation's workcenter is unknown

# attach a schedule
sched = Schedule("FCFS", time=5, machines=[
    MachineSchedule("W01", "A1", [ScheduledOperation("J01", 0, "W01", "A1", 0, 5, 0, "A")]),
])
sys.set_schedule(sched)

print(sys.to_dict())
```

---

## Validation & Exceptions

`lekinpy.exceptions` defines typed exceptions for invalid data, all
subclasses of `LekinValidationError` (itself an `Exception`). They're
raised as early as possible: object-level invariants are checked in the
relevant constructor; invariants that need the whole `System` are checked
when objects are added to it, or by `System.validate()`.

| Exception | Raised by | When |
|---|---|---|
| `EmptyOperationsError` | `Job(...)` | `operations` is an empty list |
| `NonPositiveProcessingTimeError` | `Operation(...)` | `processing_time <= 0` |
| `EmptyMachineListError` | `Workcenter(...)` | `machines` is an empty list |
| `DuplicateMachineIdError` | `Workcenter(...)` | two machines in the same list share a name |
| `DuplicateJobIdError` | `System.add_job(...)` | a job with that `job_id` is already in the system |
| `DuplicateMachineIdError` | `System.add_workcenter(...)` | a machine name collides with one already in the system |
| `MissingWorkcenterError` | `System.validate()` (also called automatically by every `SchedulingAlgorithm` before scheduling) | an operation's `workcenter` string doesn't match any workcenter in the system |

**Example**
```python
from lekinpy import System, Job, Operation, Machine, Workcenter, MissingWorkcenterError

system = System()
system.add_workcenter(Workcenter("W01", 0, "A", [Machine("A1", 0, "A")]))
system.add_job(Job("J1", 0, 10, 1, [Operation("W99", 5, "A")]))  # W99 doesn't exist

try:
    system.validate()
except MissingWorkcenterError as e:
    print(e)  # "Job 'J1' has an operation referencing unknown workcenter 'W99'. ..."
```

Before this validation existed, scheduling a system like the one above
failed deep inside the scheduling engine with an opaque
`ValueError: min() arg is an empty sequence`, with no indication of which
job or workcenter was at fault.

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
Save a `Schedule` object to a JSON file, including every machine's full
`ScheduledOperation` records.

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

### load_schedule_from_json
Load a `Schedule` previously saved with `save_schedule_to_json` — the
round-trip is lossless, including per-operation `start_time`/`end_time`/
`operation_index`/etc.

**Signature**
```python
load_schedule_from_json(filepath: str) -> Schedule
```

**Example**
```python
from lekinpy.io import load_schedule_from_json
schedule = load_schedule_from_json("schedule.json")
schedule.display_summary(system)  # works even though `system`'s jobs were
                                   # never run through an algorithm in this
                                   # process — display methods read timing
                                   # from the Schedule itself, not from Job
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
Parse a `.seq` file into a list of serialized schedule dictionaries, one
per `Schedule:` block, each shaped so it can be passed straight to
`Schedule.from_dict(...)`.

Each machine's `Oper:` line can be in either of two formats:
- **This library's extended format** (written by `save_schedule_to_seq`):
  `job_id;operation_index;start_time;end_time;sequence_position;status` —
  parses into a full `ScheduledOperation`-compatible dict.
- **Original LEKIN format**: a bare job id (e.g. `J01`), with no other
  fields. Still parses without error; `operation_index`/`start_time`/
  `end_time`/`status` come back as `None` since that data was never in the
  file, and `sequence_position` is inferred from line order.

**Signature**
```python
parse_seq_file(filepath: str) -> list[dict[str, Any]]
```

**Example**
```python
from lekinpy.io import parse_seq_file
from lekinpy.schedule import Schedule

seqs = parse_seq_file("example.seq")
schedule = Schedule.from_dict(seqs[0])
```

---

### save_schedule_to_seq
Save a `Schedule` to a `.seq` file, one `Oper:` line per
`ScheduledOperation` with the extended
`job_id;operation_index;start_time;end_time;sequence_position;status`
format described above. Round-trips losslessly through `parse_seq_file` +
`Schedule.from_dict`.

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
Base class providing common utilities for building scheduling algorithms:
mapping machines to workcenters, tracking machine availability, and
producing `MachineSchedule` lists. It's also the extension point for
adding new algorithms — see [Authoring Custom
Algorithms](#authoring-custom-algorithms).

All four built-in algorithms correctly schedule **every operation of every
job**, including multi-operation jobs, respecting precedence (an
operation can't start before the previous operation on the same job
ends). Before scheduling, `prepare()` calls `system.validate()`
automatically (see [Validation & Exceptions](#validation--exceptions)), so
a job whose operation references an unknown workcenter fails with a clear
`MissingWorkcenterError` up front rather than crashing deep inside the
scheduling loop.

**Constructor**
```python
SchedulingAlgorithm()
```
Raises `NotImplementedError` if the subclass didn't set a complete
`metadata` class attribute (see below).

**Class Attribute**
- `metadata: dict` — every subclass must set this to a dict with four keys:
  `id` (short unique string), `display_name` (human-readable name),
  `supports_multi_operation` (bool), and `version` (string). Checked at
  instantiation time.

**Public Methods**
- `prepare(system: System) -> None`  
  Calls `system.validate()`, then initializes internal maps
  (machine→workcenter, availability, job lists) using the given `system`.
- `schedule(system: System) -> Schedule`  
  Abstract. Subclasses must implement to return a `Schedule`.
- `get_machine_schedules(system: System) -> list[MachineSchedule]`  
  Build `MachineSchedule` objects (of `ScheduledOperation` records) from
  internal job assignments.
- `dynamic_schedule(system: System, job_selector_fn: Callable[[list[Job]], Job]) -> tuple[int, list[MachineSchedule]]`  
  Generic engine that advances time, discovers available jobs, chooses one
  via `job_selector_fn`, then schedules **every operation of that job, in
  order**, on the earliest-available eligible machine for each operation's
  workcenter — the same pattern `FCFSAlgorithm` uses. Continues until all
  jobs are scheduled.
  **Returns**: `(total_time, machines)` where `machines` is a list of
  `MachineSchedule`.
  > **Note on interleaving:** once a job is selected, all of its
  > operations run back-to-back before the next dispatch decision — a job
  > "monopolizes" the machines it needs until finished, even if a
  > higher-priority job is released partway through. This is a
  > deliberate simplification (matching `FCFSAlgorithm`'s structure)
  > rather than a fully interleaved, operation-level dynamic dispatcher.
  > Worth knowing if you're comparing makespans against a textbook
  > job-shop solver.

**Minimal Example — authoring a custom rule**
```python
from lekinpy.algorithms.base import SchedulingAlgorithm
from lekinpy.schedule import Schedule

class MyShortestProcessingTime(SchedulingAlgorithm):
    metadata = {
        "id": "custom-spt",
        "display_name": "My Shortest Processing Time",
        "supports_multi_operation": True,
        "version": "1.0.0",
    }

    def schedule(self, system):
        # select job with minimum processing time of its first operation;
        # dynamic_schedule then schedules ALL of that job's operations.
        def pick_spT(available_jobs):
            return min(available_jobs, key=lambda j: j.operations[0].processing_time)
        total_time, machines = self.dynamic_schedule(system, pick_spT)
        return Schedule(schedule_type="Custom-SPT", time=total_time, machines=machines)
```

---

### FCFSAlgorithm
First-Come, First-Served: among released jobs at the current time, pick the one with the **earliest release time** (ties broken by job_id), then schedule all of that job's operations in order.

**Metadata**: `id="fcfs"`, `supports_multi_operation=True`, `version="1.0.0"`

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
Shortest Processing Time: among released jobs, pick the one with the smallest `processing_time` on its **first operation**, then schedule all of that job's operations in order.

**Metadata**: `id="spt"`, `supports_multi_operation=True`, `version="1.0.0"`

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
Earliest Due Date: among released jobs, pick the one with the smallest `due`, then schedule all of that job's operations in order.

**Metadata**: `id="edd"`, `supports_multi_operation=True`, `version="1.0.0"`

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
Weighted Shortest Processing Time: among released jobs, pick the one maximizing `weight / processing_time` on its **first operation**, then schedule all of that job's operations in order.

**Metadata**: `id="wspt"`, `supports_multi_operation=True`, `version="1.0.0"`

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

You can plug in your own rule by subclassing `SchedulingAlgorithm`:
implement `schedule(self, system) -> Schedule`, and set a `metadata` class
attribute (see [SchedulingAlgorithm](#schedulingalgorithm-base)) — that's
the whole contract, no decorators or entry-point registration needed. Use
the built‑in `dynamic_schedule(...)` helper, which already handles
multi-operation jobs correctly, or implement your own loop.

### Minimal Template
```python
from lekinpy.algorithms import SchedulingAlgorithm
from lekinpy.schedule import Schedule

class MyRule(SchedulingAlgorithm):
    metadata = {
        "id": "my-rule",
        "display_name": "My Rule",
        "supports_multi_operation": True,
        "version": "1.0.0",
    }

    def schedule(self, system):
        # Choose among currently released jobs; dynamic_schedule then
        # schedules every operation of the chosen job, in order, before
        # picking the next job.
        def pick(available_jobs):
            # example: tie‑break by job_id after shortest processing time
            # of the job's first operation
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

### Multi-Operation Jobs
`dynamic_schedule` (and `FCFSAlgorithm`'s own loop) already schedule
**every** operation of a job once that job is selected, respecting
precedence automatically. There's nothing extra you need to do for a
`job_selector_fn`-based algorithm to support multi-operation jobs — set
`"supports_multi_operation": True` in your `metadata` and it just works.

One tradeoff to know about: once `dynamic_schedule` selects a job, all of
its operations run back-to-back before the next dispatch decision — a job
"monopolizes" the machines it needs until finished, even if a
higher-priority job is released partway through. If you need full
operation-level interleaving across jobs (a newly-released job's operation
preempting another job's routing mid-way), don't use `dynamic_schedule` —
write your own loop that tracks per-job "next ready operation" instead of
whole-job availability.

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
- `save_schedule_to_json`/`load_schedule_from_json` (and `save_schedule_to_seq`/`parse_seq_file`) round-trip a *computed* `Schedule` losslessly, including every operation's real start/end times — separate from `export_system_to_json`, which only saves job/workcenter definitions, not a schedule.
