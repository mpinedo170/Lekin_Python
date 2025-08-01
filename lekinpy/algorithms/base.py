class SchedulingAlgorithm:
    def __init__(self):
        self.machine_workcenter_map = {}
        self.machine_available_time = {}

    def prepare(self, system):
        self.machine_workcenter_map = {}
        self.machine_available_time = {m.name: 0 for m in system.machines}
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

    def schedule(self, system):
        raise NotImplementedError("Subclasses should implement this!")
