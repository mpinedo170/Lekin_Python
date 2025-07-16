from .job import Job
from .machine import Machine, Workcenter
from .schedule import Schedule


class System:
    def __init__(self):
        self.jobs = []
        self.workcenters = []
        self.schedule = None

    def add_job(self, job):
        self.jobs.append(job)

    def add_workcenter(self, workcenter):
        self.workcenters.append(workcenter)

    def set_schedule(self, schedule):
        self.schedule = schedule

    @property
    def machines(self):
        all_machines = []
        for wc in self.workcenters:
            all_machines.extend(wc.machines)
        return all_machines

    def to_dict(self):
        return {
            'jobs': [j.to_dict() for j in self.jobs],
            'workcenters': [wc.to_dict() for wc in self.workcenters],
            'schedule': self.schedule.to_dict() if self.schedule else None
        }
