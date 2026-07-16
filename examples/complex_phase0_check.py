from pathlib import Path
import json

import matplotlib.pyplot as plt

from lekinpy import Job, Machine, Operation, System, Workcenter
from lekinpy.algorithms import (
    EDDAlgorithm,
    FCFSAlgorithm,
    SPTAlgorithm,
    WSPTAlgorithm,
)
from lekinpy.io import load_schedule_from_json, save_schedule_to_json


OUTPUT_DIR = Path(__file__).resolve().parent / "complex_check_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def example_relative_path(path: Path) -> str:
    """Return a portable path relative to the examples directory."""
    return str(path.relative_to(Path(__file__).resolve().parent))


def build_system() -> System:
    """Build a multi-machine job-shop problem with releases and machine revisits."""
    system = System()

    system.add_workcenter(
        Workcenter(
            name="Cutting",
            release=0,
            status="A",
            rgb=(90, 130, 180),
            machines=[
                Machine("CUT-1", release=0, status="A"),
                Machine("CUT-2", release=2, status="A"),
            ],
        )
    )

    system.add_workcenter(
        Workcenter(
            name="Drilling",
            release=0,
            status="A",
            rgb=(120, 150, 100),
            machines=[
                Machine("DRILL-1", release=0, status="A"),
                Machine("DRILL-2", release=4, status="A"),
            ],
        )
    )

    system.add_workcenter(
        Workcenter(
            name="Welding",
            release=0,
            status="A",
            rgb=(170, 100, 90),
            machines=[
                Machine("WELD-1", release=0, status="A"),
            ],
        )
    )

    system.add_workcenter(
        Workcenter(
            name="Painting",
            release=0,
            status="A",
            rgb=(130, 90, 160),
            machines=[
                Machine("PAINT-1", release=0, status="A"),
            ],
        )
    )

    jobs = [
        Job(
            job_id="J-A",
            release=0,
            due=28,
            weight=5,
            rgb=(70, 120, 170),
            operations=[
                Operation("Cutting", 5, "A"),
                Operation("Drilling", 3, "A"),
                Operation("Welding", 6, "A"),
                Operation("Painting", 4, "A"),
            ],
        ),
        Job(
            job_id="J-B",
            release=0,
            due=18,
            weight=2,
            rgb=(220, 120, 70),
            operations=[
                Operation("Drilling", 2, "A"),
                Operation("Cutting", 4, "A"),
                Operation("Painting", 3, "A"),
            ],
        ),
        Job(
            job_id="J-C",
            release=3,
            due=24,
            weight=8,
            rgb=(70, 160, 100),
            operations=[
                Operation("Welding", 5, "A"),
                Operation("Drilling", 4, "A"),
                Operation("Cutting", 2, "A"),
                Operation("Painting", 5, "A"),
            ],
        ),
        Job(
            job_id="J-D",
            release=5,
            due=35,
            weight=3,
            rgb=(150, 100, 180),
            operations=[
                Operation("Cutting", 3, "A"),
                Operation("Welding", 4, "A"),
                Operation("Drilling", 2, "A"),
                Operation("Cutting", 3, "A"),  # Revisit Cutting
                Operation("Painting", 2, "A"),
            ],
        ),
        Job(
            job_id="J-E",
            release=1,
            due=16,
            weight=10,
            rgb=(190, 150, 50),
            operations=[
                Operation("Drilling", 3, "A"),
                Operation("Welding", 2, "A"),
                Operation("Painting", 3, "A"),
            ],
        ),
        Job(
            job_id="J-F",
            release=8,
            due=40,
            weight=1,
            rgb=(80, 150, 160),
            operations=[
                Operation("Cutting", 6, "A"),
                Operation("Drilling", 5, "A"),
                Operation("Welding", 3, "A"),
                Operation("Painting", 2, "A"),
            ],
        ),
    ]

    for job in jobs:
        system.add_job(job)

    system.validate()
    return system


def assert_schedule_is_feasible(system: System, schedule) -> None:
    """Independently check the important schedule invariants."""
    scheduled = [
        operation
        for machine_schedule in schedule.machines
        for operation in machine_schedule.operations
    ]

    expected_count = sum(len(job.operations) for job in system.jobs)
    assert len(scheduled) == expected_count, (
        f"Expected {expected_count} operations, found {len(scheduled)}"
    )

    by_operation = {
        (operation.job_id, operation.operation_index): operation
        for operation in scheduled
    }
    assert len(by_operation) == expected_count, (
        "An operation is duplicated or missing from the schedule"
    )

    # Check releases, durations, workcenters, machines, and job precedence.
    for job in system.jobs:
        for index, source_operation in enumerate(job.operations):
            placed = by_operation[(job.job_id, index)]

            assert placed.start_time >= job.release
            assert placed.end_time > placed.start_time
            assert (
                placed.end_time - placed.start_time
                == source_operation.processing_time
            )
            assert placed.workcenter == source_operation.workcenter

            eligible_machines = {
                machine.name
                for workcenter in system.workcenters
                if workcenter.name == source_operation.workcenter
                for machine in workcenter.machines
            }
            assert placed.machine in eligible_machines

            if index > 0:
                previous = by_operation[(job.job_id, index - 1)]
                assert placed.start_time >= previous.end_time, (
                    f"Precedence violation for {job.job_id}, operation {index}"
                )

    # Check that operations do not overlap on a machine.
    for machine_schedule in schedule.machines:
        ordered = sorted(
            machine_schedule.operations,
            key=lambda operation: operation.start_time,
        )

        for previous, current in zip(ordered, ordered[1:]):
            assert previous.end_time <= current.start_time, (
                f"Machine overlap on {machine_schedule.machine}: "
                f"{previous.job_id}.{previous.operation_index} and "
                f"{current.job_id}.{current.operation_index}"
            )

        expected_positions = list(range(len(machine_schedule.operations)))
        actual_positions = [
            operation.sequence_position
            for operation in machine_schedule.operations
        ]
        assert actual_positions == expected_positions

    expected_makespan = max(operation.end_time for operation in scheduled)
    assert schedule.time == expected_makespan


def save_and_show_gantt(schedule, system: System, destination: Path) -> None:
    """Save the library's Gantt chart, then display it interactively."""
    original_show = plt.show

    def save_then_show() -> None:
        figure = plt.gcf()
        figure.savefig(destination, dpi=180, bbox_inches="tight")
        print(f"Saved Gantt chart: {destination.resolve()}")
        original_show()

    try:
        # plot_gantt_chart() calls plt.show() internally. Intercept that call
        # so the exact figure being displayed is also saved as a PNG.
        plt.show = save_then_show
        schedule.plot_gantt_chart(system)
    finally:
        plt.show = original_show
        plt.close("all")


def print_operation_table(schedule) -> None:
    print("\nMachine operation table:")

    for machine_schedule in schedule.machines:
        print(
            f"\n{machine_schedule.machine} "
            f"(workcenter={machine_schedule.workcenter})"
        )

        if not machine_schedule.operations:
            print("  No operations")
            continue

        for operation in machine_schedule.operations:
            print(
                f"  position={operation.sequence_position:<2} "
                f"{operation.job_id}.{operation.operation_index} "
                f"start={operation.start_time:>5.1f} "
                f"end={operation.end_time:>5.1f} "
                f"duration={operation.end_time - operation.start_time:>4.1f}"
            )


def run_algorithm(algorithm_class) -> dict:
    # Build a fresh system because scheduling mutates operation timing.
    system = build_system()
    algorithm = algorithm_class()
    schedule = algorithm.schedule(system)
    system.set_schedule(schedule)

    assert_schedule_is_feasible(system, schedule)

    algorithm_id = algorithm.metadata["id"]
    json_path = OUTPUT_DIR / f"{algorithm_id}_schedule.json"
    gantt_path = OUTPUT_DIR / f"{algorithm_id}_gantt.png"

    save_schedule_to_json(schedule, str(json_path))
    reloaded = load_schedule_from_json(str(json_path))

    # Exact serialized-data comparison, including RGB type normalization.
    assert reloaded.to_dict() == schedule.to_dict()

    # Validate the reloaded schedule independently as well.
    assert_schedule_is_feasible(system, reloaded)
    save_and_show_gantt(reloaded, system, gantt_path)

    print("\n" + "=" * 72)
    print(algorithm.metadata["display_name"])
    print("=" * 72)
    print(f"Makespan:          {schedule.time}")
    print(f"Scheduled ops:     {sum(len(m.operations) for m in schedule.machines)}")
    print(f"JSON output:       {json_path}")
    print(f"Gantt chart:       {gantt_path}")

    schedule.display_summary(system)
    schedule.display_job_details(system)
    print_operation_table(schedule)

    return {
        "algorithm": algorithm.metadata["display_name"],
        "makespan": schedule.time,
        "operations": sum(
            len(machine.operations) for machine in schedule.machines
        ),
        "json": example_relative_path(json_path),
        "gantt": example_relative_path(gantt_path),
    }


def main() -> None:
    algorithms = [
        FCFSAlgorithm,
        SPTAlgorithm,
        EDDAlgorithm,
        WSPTAlgorithm,
    ]

    results = [run_algorithm(algorithm) for algorithm in algorithms]

    print("\n" + "#" * 72)
    print("ALGORITHM COMPARISON")
    print("#" * 72)

    for result in sorted(results, key=lambda row: row["makespan"]):
        print(
            f"{result['algorithm']:<36} "
            f"makespan={result['makespan']:>6.1f}  "
            f"operations={result['operations']}"
        )

    comparison_path = OUTPUT_DIR / "comparison.json"
    comparison_path.write_text(json.dumps(results, indent=2))

    print(f"\nComparison saved to: {comparison_path}")
    print(f"Open the PNG files in: {OUTPUT_DIR.resolve()}")
    print("\nAll feasibility and round-trip checks passed.")


if __name__ == "__main__":
    main()
