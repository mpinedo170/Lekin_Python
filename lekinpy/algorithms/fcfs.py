from .base import SchedulingAlgorithm
from ..schedule import Schedule, MachineSchedule

class FCFSAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        # Simple First-Come-First-Serve: assign jobs to machines in order
        assignments = []
        time = 0
        machine_count = len(system.machines)
        machine_job_map = {machine.name: [] for machine in system.machines}
        machine_workcenter_map = {}
        # Try to get workcenter for each machine (if possible)
        if hasattr(system, 'workcenters'):
            for wc in getattr(system, 'workcenters', []):
                for m in wc.machines:
                    machine_workcenter_map[m.name] = wc.name
        for idx, job in enumerate(system.jobs):
            machine = system.machines[idx % machine_count]
            start_time = time
            processing_time = job.operations[0].processing_time  # or .duration, .time, etc.
            end_time = time + processing_time
            assignments.append({
                'job_id': job.job_id,
                'machine_id': machine.name,
                'start_time': start_time,
                'end_time': end_time
            })
            machine_job_map[machine.name].append(job.job_id)
            time = end_time
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
        total_time = time
        return Schedule(schedule_type, rgb, total_time, machines)
