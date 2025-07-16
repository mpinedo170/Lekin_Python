# lekinpy

A Python library for job shop scheduling, compatible with LEKIN file formats and JSON. Easily extensible for new algorithms and open source contributions.

## Features
- Parse and write `.job`, `.mch`, `.seq`, and `.json` files
- Add jobs and machines programmatically or via files
- Run scheduling algorithms (e.g., FCFS)
- Output schedules in LEKIN-compatible or JSON format

## Example Usage
```python
from lekinpy.system import System
from lekinpy.job import Job
from lekinpy.machine import Machine
from lekinpy.algorithms.fcfs import FCFSAlgorithm

system = System()
system.add_job(Job('J1', 5))
system.add_job(Job('J2', 3))
system.add_machine(Machine('M1'))
system.add_machine(Machine('M2'))

algo = FCFSAlgorithm()
schedule = algo.schedule(system)
system.set_schedule(schedule)

print(system.schedule.to_dict())
```

## Contributing
- Fork, branch, and submit pull requests for new algorithms or features.
- See `tests/` for unit test examples.
