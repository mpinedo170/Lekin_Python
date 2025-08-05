
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

system = System()
machine = Machine("M1", release=0, status="A")
workcenter = Workcenter("WC1", release=0, status="A", machines=[machine])
system.add_workcenter(workcenter)

job = Job("J1", release=0, due=10, weight=1, operations=[Operation("WC1", 5, "A")])
system.add_job(job)

algo = FCFSAlgorithm()
schedule = algo.schedule(system)
system.set_schedule(schedule)

print(system.schedule.to_dict())
schedule.plot_gantt_chart(system)
```

## API Reference

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
