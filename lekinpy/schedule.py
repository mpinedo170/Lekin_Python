from typing import Any, Dict, List, Optional, Tuple

class MachineSchedule:
    def __init__(self, workcenter: Optional[str], machine: str, operations: List[str]) -> None:
        self.workcenter: Optional[str] = workcenter
        self.machine: str = machine
        self.operations: List[str] = operations  # List of job_ids

    def to_dict(self) -> Dict[str, Any]:
        return {
            'workcenter': self.workcenter,
            'machine': self.machine,
            'operations': self.operations
        }

class Schedule:
    def __init__(self, schedule_type: str, time: int, machines: List[MachineSchedule]) -> None:
        self.schedule_type: str = schedule_type
        self.time: int = time
        self.machines: List[MachineSchedule] = machines

    def to_dict(self) -> Dict[str, Any]:
        return {
            'schedule_type': self.schedule_type,
            'time': self.time,
            'machines': [m.to_dict() for m in self.machines]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Schedule':
        machines = [MachineSchedule(**m) for m in data.get('machines', [])]
        return Schedule(
            schedule_type=data['schedule_type'],
            time=data['time'],
            machines=machines
        )

    def display_machine_details(self) -> None:
        print("Schedule type:", self.schedule_type)
        print("Total time:", self.time)
        for ms in self.machines:
            print(f"{ms.machine}: {ms.operations}")

    def display_job_details(self, system: Any) -> None:
        print("\nDetailed Job Schedule:")
        print(f"{'ID':<6} {'Wght':<5} {'Rls':<4} {'Due':<4} {'Pr.tm.':<7} {'Stat.':<6} {'Bgn':<4} {'End':<4} {'T':<4} {'wT':<4}")
        job_timings: Dict[str, Tuple[int, int]] = {}

        # Collect timings per job from the schedule, respecting job release time
        for ms in self.machines:
            machine_time = 0  # assuming scheduling starts at time 1
            for job_id in ms.operations:
                job = next(j for j in system.jobs if j.job_id == job_id)
                release = job.release
                duration = job.operations[0].processing_time
                start_time = max(release, machine_time)
                end_time = start_time + duration
                job_timings[job_id] = (start_time, end_time)
                machine_time = end_time

        for job in system.jobs:
            job_id = job.job_id
            weight = job.weight
            release = job.release
            due = job.due
            duration = job.operations[0].processing_time
            status = job.operations[0].status
            bgn, end = job_timings.get(job_id, (None, None))
            if bgn is not None:
                T = end - due  # If this is negative this is zero
                T = max(T, 0)  # Ensure T is not negative
                wT = T * weight
                print(f"{job_id:<6} {weight:<5} {release:<4} {due:<4} {duration:<7} {status:<6} {bgn:<4} {end:<4} {T:<4} {wT:<4}")

    def plot_gantt_chart(self, system: Any) -> None:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = {job.job_id: f"C{i}" for i, job in enumerate(system.jobs)}

        yticks: List[int] = []
        yticklabels: List[str] = []

        for i, ms in enumerate(self.machines):
            y = i
            yticks.append(y)
            yticklabels.append(ms.machine)
            machine_time = 0
            for job_id in ms.operations:
                job = next(j for j in system.jobs if j.job_id == job_id)
                release = job.release
                duration = job.operations[0].processing_time
                start_time = max(release, machine_time)
                end_time = start_time + duration
                ax.barh(y, duration, left=start_time, color=colors.get(job_id, 'gray'), edgecolor='black')
                ax.text(start_time + duration / 2, y, job_id, ha='center', va='center', color='white', fontsize=10)
                machine_time = end_time

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
        ax.set_xlabel("Time")
        ax.set_title("Gantt Chart")
        ax.set_xlim(left=0)
        plt.tight_layout()
        plt.show()

    def display_sequence(self, system: Any) -> None:
        print("\nJob Sequence per Machine:")
        print(f"{'Mch/Job':<8} {'Setup':<6} {'Start':<6} {'Stop':<6} {'Pr.tm.':<6}")
        for ms in self.machines:
            print(f"{ms.machine:<8}")
            time_marker = 0
            for job_id in ms.operations:
                job = next(j for j in system.jobs if j.job_id == job_id)
                pr_tm = job.operations[0].processing_time
                setup = 0  # assuming 0 setup time
                start = time_marker
                stop = start + pr_tm
                print(f"  {job_id:<6} {setup:<6} {start:<6} {stop:<6} {pr_tm:<6}")
                time_marker = stop

    def display_summary(self, system: Any) -> None:
        start_times, end_times, T_list, wT_list, C_list, wC_list, U_list = [], [], [], [], [], [], []

        for job in system.jobs:
            start = getattr(job, 'start_time', None)
            end = getattr(job, 'end_time', None)
            due = job.due
            weight = job.weight
            if start is not None and end is not None:
                T = max(0, end - due)
                T_list.append(T)
                wT_list.append(T * weight)
                C_list.append(end)
                wC_list.append(end * weight)
                start_times.append(start)
                end_times.append(end)
                U_list.append(1 if T > 0 else 0)

        time_start = min(start_times) if start_times else 0
        C_max = max(end_times) if end_times else 0
        T_max = max(T_list) if T_list else 0
        U = sum(U_list)
        sum_Cj = sum(C_list)
        sum_Tj = sum(T_list)
        sum_wCj = sum(wC_list)
        sum_wTj = sum(wT_list)

        print("\nSummary:")
        print(f"{'Time':<10}{time_start}")
        print(f"{'C_max':<10}{C_max}")
        print(f"{'T_max':<10}{T_max}")
        print(f"{'ΣU_j':<10}{U}")
        print(f"{'ΣC_j':<10}{sum_Cj}")
        print(f"{'ΣT_j':<10}{sum_Tj}")
        print(f"{'ΣwC_j':<10}{sum_wCj}")
        print(f"{'ΣwT_j':<10}{sum_wTj}")