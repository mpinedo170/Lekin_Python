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
        print("\nJob start-end times per machine:")
        for ms in self.machines:
            print(f"\n{ms.machine}:")
            time_marker = 0
            for job_id in ms.operations:
                job = next(j for j in system.jobs if j.job_id == job_id)
                duration = job.operations[0].processing_time
                print(f"  {job_id}: start={time_marker}, end={time_marker + duration}")
                time_marker += duration

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
