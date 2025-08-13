from .base import SchedulingAlgorithm
from ..schedule import Schedule

class WSPTAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        self.prepare(system)

        unscheduled_jobs = {job.job_id: job for job in system.jobs}

        # Simulate the scheduling process over time until all jobs are assigned
        while unscheduled_jobs:
            # Determine the current simulation time by finding the earliest available machine
            current_time = min(self.machine_available_time.values())

            # Check which jobs have been released (i.e., are available) at the current simulation time
            available_jobs = [
                job for job in unscheduled_jobs.values() if job.release <= current_time
            ]

            # No jobs are currently available (not yet released), so we need to advance time.
            # We find the next earliest job release, and update the earliest available machine's time to that point.
            # This simulates the machine idling until a job becomes available.
            if not available_jobs:
                # Find the earliest release time among unscheduled jobs
                next_release = min(job.release for job in unscheduled_jobs.values())
                # Find the machine that is available the earliest (i.e., whose clock is the lowest)
                earliest_machine = min(self.machine_available_time, key=self.machine_available_time.get)
                # Fast-forward this machine's clock to the next job release time so it can pick up the job next
                self.machine_available_time[earliest_machine] = next_release
                # Skip this iteration and let the loop continue with updated machine time
                continue

            # Apply the WSPT rule: pick the job with the highest weight-to-processing-time ratio.
            # This prioritizes jobs that are more 'important' relative to their processing time.
            available_jobs.sort(
                key=lambda job: (
                    job.weight / job.operations[0].processing_time
                    if job.operations and job.operations[0].processing_time > 0 else float('-inf')
                ),
                reverse=True
            )

            # Choose the best job based on WSPT, find an eligible machine, and assign it.
            # After assignment, remove the job from the pool of unscheduled jobs.
            job = available_jobs[0]
            op = job.operations[0]
            candidate_machines = self._get_machines_for_workcenter(system, op.workcenter)
            chosen_machine = self._get_earliest_machine(candidate_machines)
            self._assign_single_operation(job, op, chosen_machine)
            del unscheduled_jobs[job.job_id]

        # All jobs have been scheduled. Create the final schedule object and return it.
        machines = self.get_machine_schedules(system)
        total_time = max(self.machine_available_time.values()) if self.machine_available_time else 0
        return Schedule("WSPT", total_time, machines)
