

from lekinpy.algorithms.base import SchedulingAlgorithm
from lekinpy.schedule import Schedule, MachineSchedule

class FCFS_CPPStyle_Algorithm(SchedulingAlgorithm):
    def schedule(self, system):
        machine_workcenter_map = {}
        machine_available_time = {m.name: 0 for m in system.machines}
        machine_job_map = {m.name: [] for m in system.machines}

        if hasattr(system, 'workcenters'):
            for wc in system.workcenters:
                for m in wc.machines:
                    machine_workcenter_map[m.name] = wc.name

        # Each job has one operation
        operations = []
        for job in system.jobs:
            op = job.operations[0]
            op.job_id = job.job_id
            op.release = job.release
            op.weight = job.weight
            op.rgb = job.rgb
            op.est = job.release
            op.workcenter = op.workcenter
            operations.append(op)

        while operations:
            idx = index_fcfs(operations)
            op = operations.pop(idx)

            # Find candidate machines in the operation's workcenter
            candidate_machines = [m for m in system.machines if machine_workcenter_map.get(m.name) == op.workcenter]
            chosen_machine = min(candidate_machines, key=lambda m: machine_available_time[m.name])

            start = max(machine_available_time[chosen_machine.name], op.est)
            end = start + op.processing_time

            machine_job_map[chosen_machine.name].append(op.job_id)
            machine_available_time[chosen_machine.name] = end

        machines = []
        for machine in system.machines:
            workcenter = machine_workcenter_map.get(machine.name, None)
            machines.append(MachineSchedule(workcenter=workcenter, machine=machine.name, operations=machine_job_map[machine.name]))

        total_time = max(machine_available_time.values())
        return Schedule("FCFS_CPP", (50, 50, 200), total_time, machines)

def index_fcfs(oper_list):
    min_index = 0
    for i in range(1, len(oper_list)):
        if oper_list[i].est < oper_list[min_index].est:
            min_index = i
    return min_index