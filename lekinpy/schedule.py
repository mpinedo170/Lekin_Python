class MachineSchedule:
    def __init__(self, workcenter, machine, operations):
        self.workcenter = workcenter
        self.machine = machine
        self.operations = operations  # List of job_ids

    def to_dict(self):
        return {
            'workcenter': self.workcenter,
            'machine': self.machine,
            'operations': self.operations
        }

class Schedule:
    def __init__(self, schedule_type, rgb, time, machines):
        self.schedule_type = schedule_type
        self.rgb = rgb
        self.time = time
        self.machines = machines  # List of MachineSchedule

    def to_dict(self):
        return {
            'schedule_type': self.schedule_type,
            'rgb': self.rgb,
            'time': self.time,
            'machines': [m.to_dict() for m in self.machines]
        }

    @staticmethod
    def from_dict(data):
        machines = [MachineSchedule(**m) for m in data.get('machines', [])]
        return Schedule(
            schedule_type=data['schedule_type'],
            rgb=data['rgb'],
            time=data['time'],
            machines=machines
        )
