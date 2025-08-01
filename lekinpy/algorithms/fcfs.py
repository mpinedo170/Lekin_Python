from .base import SchedulingAlgorithm
from ..schedule import Schedule, MachineSchedule

class FCFSAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        self.prepare(system)

        sorted_jobs = sorted(system.jobs, key=lambda job: job.release)
        self.assign_operations(sorted_jobs, system)

        machines = self.get_machine_schedules(system)

        total_time = max(self.machine_available_time.values()) if self.machine_available_time else 0
        return Schedule("FCFS", total_time, machines)
