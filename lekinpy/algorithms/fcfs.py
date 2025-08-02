from .base import SchedulingAlgorithm
from ..schedule import Schedule, MachineSchedule

class FCFSAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        self.prepare(system)

        sorted_jobs = sorted(system.jobs, key=lambda job: job.release)

        for job in sorted_jobs:
            for op in job.operations:
                candidate_machines = self._get_machines_for_workcenter(system, op.workcenter)
                chosen_machine = self._get_earliest_machine(candidate_machines)
                self._assign_single_operation(job, op, chosen_machine)

        machines_schedules = self.get_machine_schedules(system)
        total_time = max(self.machine_available_time.values()) if self.machine_available_time else 0
        return Schedule("FCFS", total_time, machines_schedules)