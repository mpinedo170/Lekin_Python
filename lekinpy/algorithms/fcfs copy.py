from .base import SchedulingAlgorithm
from ..schedule import Schedule, MachineSchedule

class FCFSAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        # Simple First-Come-First-Serve: assign jobs to machines in order of availability
        assignments = []
        machine_count = len(system.machines)
        machine_job_map = {machine.name: [] for machine in system.machines}
        # Below code is similar to above code, written just for the sake of clarification.
        # machine_job_map = {}
        # for machine in machines:
        #     machine_job_map[machine.name] = []

        machine_workcenter_map = {}
        machine_available_time = {machine.name: 0 for machine in system.machines}
        # Try to get workcenter for each machine (if possible)
        if hasattr(system, 'workcenters'):
            for wc in getattr(system, 'workcenters', []):
                for m in wc.machines:
                    machine_workcenter_map[m.name] = wc.name
        for job in system.jobs:
            op = job.operations[0]
            target_wc = op.workcenter

            # Find machines in the target workcenter
            candidate_machines = [m for m in system.machines if machine_workcenter_map.get(m.name) == target_wc]
            if not candidate_machines:
                raise ValueError(f"No machines found for workcenter {target_wc}")

            # Choose the machine with the earliest available time
            # To Choose the machine available at the earliest, we have just initialised the machine_availabe_time_map but we have not assigned the values yet. 
            chosen_machine = min(candidate_machines, key=lambda m: machine_available_time[m.name])
            start_time = max(job.release, machine_available_time[chosen_machine.name])
            processing_time = op.processing_time
            end_time = start_time + processing_time

            job.start_time = start_time
            job.end_time = end_time

            assignments.append({
                'job_id': job.job_id,
                'machine_id': chosen_machine.name,
                'start_time': start_time,
                'end_time': end_time
            })

            machine_job_map[chosen_machine.name].append(job.job_id)
            machine_available_time[chosen_machine.name] = end_time
        # Build MachineSchedule list
        machines = []
        for machine in system.machines:
            workcenter = machine_workcenter_map.get(machine.name, None)
            machines.append(MachineSchedule(
                workcenter=workcenter,
                machine=machine.name,
                operations=machine_job_map[machine.name]
            ))
        schedule_type = "FCFS"
        rgb = (0, 0, 0)
        total_time = max(machine_available_time.values()) if machine_available_time else 0
        return Schedule(schedule_type, rgb, total_time, machines)
