from typing import Any, Dict, List, Optional, Tuple

class ScheduledOperation:
    """
    A single operation's placement in the final schedule: which job/operation
    it is, where it runs, when it runs, and where it falls in the machine's
    sequence. This is the unit of data that MachineSchedule stores, replacing
    the old bare job-id strings.
    """
    def __init__(
        self,
        job_id: str,
        operation_index: int,
        workcenter: Optional[str],
        machine: str,
        start_time: float,
        end_time: float,
        sequence_position: int,
        status: Optional[str] = None,
    ) -> None:
        self.job_id: str = job_id
        self.operation_index: int = operation_index
        self.workcenter: Optional[str] = workcenter
        self.machine: str = machine
        self.start_time: float = start_time
        self.end_time: float = end_time
        self.sequence_position: int = sequence_position
        self.status: Optional[str] = status

    def __repr__(self) -> str:
        return (
            f"ScheduledOperation({self.job_id}, op={self.operation_index}, "
            f"{self.workcenter}, {self.machine}, {self.start_time}-{self.end_time}, "
            f"seq={self.sequence_position}, status={self.status})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'operation_index': self.operation_index,
            'workcenter': self.workcenter,
            'machine': self.machine,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'sequence_position': self.sequence_position,
            'status': self.status,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ScheduledOperation':
        return ScheduledOperation(
            job_id=data['job_id'],
            operation_index=data['operation_index'],
            workcenter=data.get('workcenter'),
            machine=data['machine'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            sequence_position=data['sequence_position'],
            status=data.get('status'),
        )

class MachineSchedule:
    def __init__(self, workcenter: Optional[str], machine: str, operations: List[ScheduledOperation]) -> None:
        self.workcenter: Optional[str] = workcenter
        self.machine: str = machine
        self.operations: List[ScheduledOperation] = operations

    def to_dict(self) -> Dict[str, Any]:
        return {
            'workcenter': self.workcenter,
            'machine': self.machine,
            'operations': [op.to_dict() for op in self.operations]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MachineSchedule':
        operations = [ScheduledOperation.from_dict(op) for op in data.get('operations', [])]
        return MachineSchedule(
            workcenter=data.get('workcenter'),
            machine=data['machine'],
            operations=operations
        )

class Schedule:
    def __init__(
        self,
        schedule_type: str,
        time: int,
        machines: List[MachineSchedule],
        rgb: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        self.schedule_type: str = schedule_type
        self.time: int = time
        self.machines: List[MachineSchedule] = machines
        self.rgb: Optional[Tuple[int, int, int]] = rgb

    def to_dict(self) -> Dict[str, Any]:
        return {
            'schedule_type': self.schedule_type,
            'time': self.time,
            'rgb': self.rgb,
            'machines': [m.to_dict() for m in self.machines]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Schedule':
        machines = [MachineSchedule.from_dict(m) for m in data.get('machines', [])]
        return Schedule(
            schedule_type=data['schedule_type'],
            time=data['time'],
            machines=machines,
            rgb=data.get('rgb'),
        )

    def display_machine_details(self) -> None:
        print("Schedule type:", self.schedule_type)
        print("Total time:", self.time)
        for ms in self.machines:
            print(f"{ms.machine}: {[so.job_id for so in ms.operations]}")

    def _operations_by_job(self) -> Dict[str, List['ScheduledOperation']]:
        """
        Group every ScheduledOperation in this schedule by job_id, in no
        particular order. Callers that need per-job ordering should sort by
        `operation_index`.
        """
        ops_by_job: Dict[str, List['ScheduledOperation']] = {}
        for ms in self.machines:
            for so in ms.operations:
                ops_by_job.setdefault(so.job_id, []).append(so)
        return ops_by_job

    def display_job_details(self, system: Any) -> None:
        print("\nDetailed Job Schedule:")
        print(f"{'ID':<6} {'Wght':<5} {'Rls':<4} {'Due':<4} {'Pr.tm.':<7} {'Stat.':<6} {'Bgn':<4} {'End':<4} {'T':<4} {'wT':<4}")

        ops_by_job = self._operations_by_job()

        for job in system.jobs:
            job_ops = sorted(ops_by_job.get(job.job_id, []), key=lambda so: so.operation_index)
            if not job_ops:
                continue
            weight = job.weight
            release = job.release
            due = job.due
            # Job begins when its first operation starts and ends when its
            # last operation ends; total processing time is the sum of each
            # operation's own duration (idle time between operations, if
            # any, isn't counted as processing time).
            bgn = job_ops[0].start_time
            end = job_ops[-1].end_time
            duration = sum(so.end_time - so.start_time for so in job_ops)
            status = job_ops[-1].status
            T = max(end - due, 0)  # Tardiness; never negative
            wT = T * weight
            print(f"{job.job_id:<6} {weight:<5} {release:<4} {due:<4} {duration:<7} {status:<6} {bgn:<4} {end:<4} {T:<4} {wT:<4}")

    def plot_gantt_chart(self, system: Any) -> None:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = {job.job_id: f"C{i}" for i, job in enumerate(system.jobs)}
        job_op_counts = {job.job_id: len(job.operations) for job in system.jobs}

        yticks: List[int] = []
        yticklabels: List[str] = []

        for i, ms in enumerate(self.machines):
            y = i
            yticks.append(y)
            yticklabels.append(ms.machine)
            for so in ms.operations:
                duration = so.end_time - so.start_time
                # For multi-operation jobs, disambiguate which operation this
                # bar represents (e.g. "J1.2"); single-operation jobs just
                # show the job id, matching the prior label format.
                label = so.job_id if job_op_counts.get(so.job_id, 1) <= 1 else f"{so.job_id}.{so.operation_index}"
                ax.barh(y, duration, left=so.start_time, color=colors.get(so.job_id, 'gray'), edgecolor='black')
                ax.text(so.start_time + duration / 2, y, label, ha='center', va='center', color='white', fontsize=10)

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
            for so in ms.operations:
                pr_tm = so.end_time - so.start_time
                setup = 0  # assuming 0 setup time
                print(f"  {so.job_id:<6} {setup:<6} {so.start_time:<6} {so.end_time:<6} {pr_tm:<6}")

    def display_summary(self, system: Any) -> None:
        ops_by_job = self._operations_by_job()
        start_times, end_times, T_list, wT_list, C_list, wC_list, U_list = [], [], [], [], [], [], []

        for job in system.jobs:
            job_ops = ops_by_job.get(job.job_id)
            due = job.due
            weight = job.weight
            if job_ops:
                start = min(so.start_time for so in job_ops)
                end = max(so.end_time for so in job_ops)
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