import random

class Machine:
    def __init__(self, name, release, status):
        self.name = name
        self.release = release
        self.status = status

    def __repr__(self):
        return f"Machine({self.name}, {self.release}, {self.status})"

# speed of the machine is not included in this class

    @staticmethod
    def from_dict(data):
        return Machine(
            name=data['name'],
            release=data['release'],
            status=data['status']
        )

    def to_dict(self):
        return {
            'name': self.name,
            'release': self.release,
            'status': self.status
        }

class Workcenter:
    _available_colors = [(r, g, b) for r in range(0, 256, 64)
                                   for g in range(0, 256, 64)
                                   for b in range(0, 256, 64)]
    random.shuffle(_available_colors)
    
    def __init__(self, name, release, status, machines, rgb=None):
        self.name = name
        self.release = release
        self.status = status
        self.rgb = rgb if rgb else Workcenter._available_colors.pop()
        self.machines = machines  # List of Machine objects

    def __repr__(self):
        return (f"Workcenter({self.name}, {self.release}, {self.status}, "
                f"{self.rgb}, {self.machines})")

    @staticmethod
    def from_dict(data):
        machines = [Machine.from_dict(m) for m in data.get('machines', [])]
        return Workcenter(
            name=data['name'],
            release=data['release'],
            status=data['status'],
            rgb=data['rgb'],
            machines=machines
        )

    def to_dict(self):
        return {
            'name': self.name,
            'release': self.release,
            'status': self.status,
            'rgb': self.rgb,
            'machines': [m.to_dict() for m in self.machines]
        }
