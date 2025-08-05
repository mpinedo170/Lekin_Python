from .job import Job
from .machine import Machine, Workcenter
from .schedule import Schedule
from typing import Any, Dict, List, Optional

class System:
    def __init__(self) -> None:
        self.jobs: List[Job] = []
        self.workcenters: List[Workcenter] = []
        self.schedule: Optional[Schedule] = None

    def add_job(self, job: Job) -> None:
        if not isinstance(job, Job):
            raise TypeError("job must be a Job instance")
        self.jobs.append(job)

    def add_workcenter(self, workcenter: Workcenter) -> None:
        if not isinstance(workcenter, Workcenter):
            raise TypeError("workcenter must be a Workcenter instance")
        self.workcenters.append(workcenter)

    def set_schedule(self, schedule: Schedule) -> None:
        if not isinstance(schedule, Schedule):
            raise TypeError("schedule must be a Schedule instance")
        self.schedule = schedule

    @property
    def machines(self) -> List[Machine]:
        all_machines: List[Machine] = []
        for wc in self.workcenters:
            all_machines.extend(wc.machines)
        return all_machines

    def to_dict(self) -> Dict[str, Any]:
        return {
            'jobs': [j.to_dict() for j in self.jobs],
            'workcenters': [wc.to_dict() for wc in self.workcenters],
            'schedule': self.schedule.to_dict() if self.schedule else None
        }
