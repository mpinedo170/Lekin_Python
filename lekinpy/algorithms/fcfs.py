from .base import SchedulingAlgorithm
from ..schedule import Schedule, MachineSchedule

class FCFSAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        self.prepare(system)

        machine_job_map = {machine.name: [] for machine in system.machines}

        sorted_jobs = sorted(system.jobs, key=lambda j: j.release)
        for job in sorted_jobs:
            op = job.operations[0]
            target_wc = op.workcenter

            candidate_machines = self.get_machines_for_workcenter(system, target_wc)
            if not candidate_machines:
                raise ValueError(f"No machines found for workcenter {target_wc}")

            chosen_machine = self.get_earliest_machine(candidate_machines)
            start_time = max(job.release, self.machine_available_time[chosen_machine.name])
            end_time = start_time + op.processing_time

            job.start_time = start_time
            job.end_time = end_time

            machine_job_map[chosen_machine.name].append(job.job_id)
            self.update_machine_time(chosen_machine.name, end_time)

        machines = []
        for machine in system.machines:
            workcenter = self.machine_workcenter_map.get(machine.name, None)
            machines.append(MachineSchedule(
                workcenter=workcenter,
                machine=machine.name,
                operations=machine_job_map[machine.name]
            ))

        total_time = max(self.machine_available_time.values()) if self.machine_available_time else 0
        return Schedule("FCFS", (0, 0, 0), total_time, machines)
