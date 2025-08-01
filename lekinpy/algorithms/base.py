from ..schedule import MachineSchedule, Schedule
class SchedulingAlgorithm:
    def __init__(self):
        self.machine_workcenter_map = {}
        self.machine_available_time = {}

    def prepare(self, system):
        self.machine_workcenter_map = {}
        self.machine_available_time = {m.name: getattr(m, 'release', 0) for m in system.machines}
        self.machine_job_map = {m.name: [] for m in system.machines}
        if hasattr(system, 'workcenters'):
            for wc in getattr(system, 'workcenters', []):
                for m in wc.machines:
                    self.machine_workcenter_map[m.name] = wc.name

    def get_machines_for_workcenter(self, system, workcenter_name):
        return [m for m in system.machines if self.machine_workcenter_map.get(m.name) == workcenter_name]

    def get_earliest_machine(self, machines):
        return min(machines, key=lambda m: self.machine_available_time[m.name])

    def update_machine_time(self, machine_name, end_time):
        self.machine_available_time[machine_name] = end_time

    def assign_operations(self, jobs, system):
        for job in jobs:
            previous_end_time = 0
            for op in job.operations:
                target_wc = op.workcenter
                candidate_machines = self.get_machines_for_workcenter(system, target_wc)
                if not candidate_machines:
                    raise ValueError(f"No machines found for workcenter {target_wc}")
                chosen_machine = self.get_earliest_machine(candidate_machines)
                start_time = max(job.release, self.machine_available_time[chosen_machine.name], previous_end_time)
                end_time = start_time + op.processing_time
                op.start_time = start_time
                op.end_time = end_time
                previous_end_time = end_time
                self.machine_job_map[chosen_machine.name].append(job.job_id)
                self.update_machine_time(chosen_machine.name, end_time)
            job.start_time = job.operations[0].start_time
            job.end_time = job.operations[-1].end_time

    def schedule(self, system):
        raise NotImplementedError("Subclasses should implement this!")

    def get_machine_schedules(self, system):
        machines = []
        for machine in system.machines:
            workcenter = self.machine_workcenter_map.get(machine.name, None)
            machines.append(MachineSchedule(
                workcenter=workcenter,
                machine=machine.name,
                operations=self.machine_job_map[machine.name]
            ))
        return machines
