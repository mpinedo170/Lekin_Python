
# lekinpy

A Python library for job shop scheduling, compatible with LEKIN file formats and JSON. Easily extensible for new algorithms and open source contributions.

## Installation

```bash
pip install lekinpy
```
Or for local development:
```bash
pip install .
```

## Features
- Parse and write `.job`, `.mch`, `.seq`, and `.json` files
- Add jobs and machines programmatically or via files
- Run scheduling algorithms (FCFS, SPT, EDD, WSPT)
- Output schedules in LEKIN-compatible or JSON format
- Plot Gantt charts (requires `matplotlib`)

## Example Usage
```python
from lekinpy.system import System
from lekinpy.job import Job, Operation
from lekinpy.machine import Machine, Workcenter
from lekinpy.algorithms.fcfs import FCFSAlgorithm

# Create a new scheduling system
system = System()

# Define a machine and assign it to a workcenter
machine = Machine("M1", release=0, status="A")
workcenter = Workcenter("WC1", release=0, status="A", machines=[machine])
system.add_workcenter(workcenter)

# Define a job with one operation assigned to WC1
job = Job("J1", release=0, due=10, weight=1, operations=[Operation("WC1", 5, "A")])
system.add_job(job)

# Choose the scheduling algorithm (First-Come First-Served)
algo = FCFSAlgorithm()

# Generate the schedule for the system
schedule = algo.schedule(system)

# Attach the computed schedule to the system
system.set_schedule(schedule)

# Print schedule details as a dictionary
print(system.schedule.to_dict())

# Plot a Gantt chart of the schedule (requires matplotlib)
schedule.plot_gantt_chart(system)
```

## API Reference
📚 **Full API Reference:** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

- `System`, `Job`, `Operation`, `Machine`, `Workcenter`
- Algorithms: `FCFSAlgorithm`, `SPTAlgorithm`, `EDDAlgorithm`, `WSPTAlgorithm`
- IO: `export_jobs_to_jobfile`, `export_workcenters_to_mchfile`, etc.

## Contributing

- Fork, branch, and submit pull requests for new algorithms or features.
- See `tests/` for unit test examples.

## License

MIT

## Contact

Author: Ruturaj Vasant  
Email: rvt2018@nyu.edu
