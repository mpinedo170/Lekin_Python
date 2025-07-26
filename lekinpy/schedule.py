class MachineSchedule:
    def __init__(self, workcenter, machine, operations):
        self.workcenter = workcenter
        self.machine = machine
        self.operations = operations  # List of job_ids

    def to_dict(self):
        return {
            'workcenter': self.workcenter,
            'machine': self.machine,
            'operations': self.operations
        }

class Schedule:
    def __init__(self, schedule_type, rgb, time, machines):
        self.schedule_type = schedule_type
        self.rgb = rgb
        self.time = time
        self.machines = machines  # List of MachineSchedule

    def to_dict(self):
        return {
            'schedule_type': self.schedule_type,
            'rgb': self.rgb,
            'time': self.time,
            'machines': [m.to_dict() for m in self.machines]
        }

    @staticmethod
    def from_dict(data):
        machines = [MachineSchedule(**m) for m in data.get('machines', [])]
        return Schedule(
            schedule_type=data['schedule_type'],
            rgb=data['rgb'],
            time=data['time'],
            machines=machines
        )

    def display_machine_details(self):
        print("Schedule type:", self.schedule_type)
        print("Total time:", self.time)
        for ms in self.machines:
            print(f"{ms.machine}: {ms.operations}")

    def display_job_details(self, system):
        print("\nDetailed Job Schedule:")
        print(f"{'ID':<6} {'Wght':<5} {'Rls':<4} {'Due':<4} {'Pr.tm.':<7} {'Stat.':<6} {'Bgn':<4} {'End':<4} {'T':<4} {'wT':<4}")
        job_timings = {}

        # Collect timings per job from the schedule
        for ms in self.machines:
            time_marker = 0
            for job_id in ms.operations:
                job = next(j for j in system.jobs if j.job_id == job_id)
                duration = job.operations[0].processing_time
                job_timings[job_id] = (time_marker, time_marker + duration)
                time_marker += duration

        for job in system.jobs:
            job_id = job.job_id
            weight = job.weight
            release = job.release
            due = job.due
            duration = job.operations[0].processing_time
            status = job.operations[0].status
            bgn, end = job_timings.get(job_id, (None, None))
            if bgn is not None:
                T = end - release
                wT = T * weight
                print(f"{job_id:<6} {weight:<5} {release:<4} {due:<4} {duration:<7} {status:<6} {bgn:<4} {end:<4} {T:<4} {wT:<4}")

    def plot_gantt_chart(self, system):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = {job.job_id: f"C{i}" for i, job in enumerate(system.jobs)}

        yticks = []
        yticklabels = []

        for i, ms in enumerate(self.machines):
            y = i
            yticks.append(y)
            yticklabels.append(ms.machine)
            time_marker = 0
            for job_id in ms.operations:
                job = next(j for j in system.jobs if j.job_id == job_id)
                duration = job.operations[0].processing_time
                ax.barh(y, duration, left=time_marker, color=colors.get(job_id, 'gray'), edgecolor='black')
                ax.text(time_marker + duration / 2, y, job_id, ha='center', va='center', color='white', fontsize=10)
                time_marker += duration

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
        ax.set_xlabel("Time")
        ax.set_title("Gantt Chart - FCFS Example 2")
        plt.tight_layout()
        plt.show()

    def display_sequence(self, system):
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

    def display_summary(self, system):
        C_max = max(
            end for ms in self.machines for job_id in ms.operations
            for job in system.jobs if job.job_id == job_id
            for end in [sum(op.processing_time for op in job.operations)]
        )

        total_time = self.time
        total_jobs = len(system.jobs)
        U = total_jobs  # All jobs assumed completed
        T_sum = 0
        wT_sum = 0

        for job in system.jobs:
            start_time, end_time = None, None
            for ms in self.machines:
                if job.job_id in ms.operations:
                    idx = ms.operations.index(job.job_id)
                    time_marker = sum(
                        next(j for j in system.jobs if j.job_id == ms.operations[i]).operations[0].processing_time
                        for i in range(idx)
                    )
                    start_time = time_marker
                    end_time = time_marker + job.operations[0].processing_time
                    break
            if start_time is not None:
                T = end_time - job.release
                T_sum += T
                wT_sum += T * job.weight

        print("\nSummary:")
        print(f"{'Time':<10}{1}")
        print(f"{'C_max':<10}{C_max}")
        print(f"{'T_max':<10}{C_max}")
        print(f"{'ΣU_j':<10}{U}")
        print(f"{'ΣC_j':<10}{C_max}")
        print(f"{'ΣT_j':<10}{T_sum}")
        print(f"{'ΣwC_j':<10}{C_max}")
        print(f"{'ΣwT_j':<10}{wT_sum}")