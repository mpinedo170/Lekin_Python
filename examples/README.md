# Lekinpy examples

Run these files from the `lekin-library` directory. Start with the numbered
examples and move to the comprehensive check when you are comfortable with
the basic objects.

```bash
python3 examples/01_first_schedule.py
python3 examples/02_multi_operation_job.py
python3 examples/03_compare_algorithms.py
python3 examples/04_johnson_flow_shop.py
```

## Learning path

1. `01_first_schedule.py` builds one machine and two jobs, runs FCFS, and
   prints the resulting start and end times.
2. `02_multi_operation_job.py` routes jobs through two workcenters and shows
   how operation precedence is represented in the schedule.
3. `03_compare_algorithms.py` runs FCFS, SPT, EDD, and WSPT on the same input
   and compares their job order and makespan.
4. `04_johnson_flow_shop.py` introduces Johnson's rule on a two-machine flow
   shop, where it beats SPT and can prove its answer is the best possible.
5. `complex_phase0_check.py` is the advanced end-to-end example. It validates
   feasibility, round-trips JSON, prints reports, and creates Gantt charts.
6. `exportsystemexample.py` demonstrates the `.job`, `.mch`, and JSON export
   helpers.

The advanced example writes its generated files to `complex_check_output/`.

