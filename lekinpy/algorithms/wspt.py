from .base import SchedulingAlgorithm
from ..schedule import Schedule, MachineSchedule

class WSPT(SchedulingAlgorithm):
    def schedule(self, system):
        self.prepare(system)

        unscheduled_jobs = {job.job_id: job for job in system.jobs}

        while unscheduled_jobs:
            current_time = min(self.machine_available_time.values())

            available_jobs = [
                job for job in unscheduled_jobs.values() if job.release <= current_time
            ]

            if not available_jobs:
                next_release = min(job.release for job in unscheduled_jobs.values())
                earliest_machine = min(self.machine_available_time, key=self.machine_available_time.get)
                self.machine_available_time[earliest_machine] = next_release
                continue

            # Sort by WSPT (weight / processing_time)
            available_jobs.sort(
                key=lambda job: (
                    job.weight / job.operations[0].processing_time
                    if job.operations and job.operations[0].processing_time > 0 else float('-inf')
                ),
                reverse=True
            )

            job = available_jobs[0]
            op = job.operations[0]
            candidate_machines = self._get_machines_for_workcenter(system, op.workcenter)
            chosen_machine = self._get_earliest_machine(candidate_machines)
            self._assign_single_operation(job, op, chosen_machine)
            del unscheduled_jobs[job.job_id]

        machines = self.get_machine_schedules(system)
        total_time = max(self.machine_available_time.values()) if self.machine_available_time else 0
        return Schedule("WSPT", total_time, machines)
