import random

class Operation:
    def __init__(self, workcenter, processing_time, status):
        self.workcenter = workcenter
        self.processing_time = processing_time
        self.status = status

    def __repr__(self):
        return f"Operation({self.workcenter}, {self.processing_time}, {self.status})"

class Job:
    _available_colors = [(r, g, b) for r in range(0, 256, 64)
                                   for g in range(0, 256, 64)
                                   for b in range(0, 256, 64)]
    random.shuffle(_available_colors)

    def __init__(self, job_id, release, due, weight, operations, rgb=None):
        self.job_id = job_id
        self.release = release
        self.due = due
        self.weight = weight
        self.rgb = rgb if rgb else Job._available_colors.pop()
        self.operations = operations  # List of Operation objects

    def __repr__(self):
        return (f"Job({self.job_id}, {self.release}, {self.due}, "
                f"{self.weight}, {self.rgb}, {self.operations})")
    
    # route should be a part of the job, but not included in this class

    @staticmethod
    def from_dict(data):
        operations = [Operation(**op) for op in data.get('operations', [])]
        return Job(
            job_id=data['job_id'],
            release=data['release'],
            due=data['due'],
            weight=data['weight'],
            operations=operations,
            rgb=data.get('rgb')
        )

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'release': self.release,
            'due': self.due,
            'weight': self.weight,
            'rgb': self.rgb,
            'operations': [op.__dict__ for op in self.operations]
        }
