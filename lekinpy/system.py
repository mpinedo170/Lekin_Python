from .job import Job
from .machine import Machine, Workcenter
from .schedule import Schedule
from .exceptions import DuplicateJobIdError, DuplicateMachineIdError, MissingWorkcenterError
from typing import Any, Dict, List, Optional

class System:
    def __init__(self) -> None:
        self.jobs: List[Job] = []
        self.workcenters: List[Workcenter] = []
        self.schedule: Optional[Schedule] = None

    def add_job(self, job: Job) -> None:
        if not isinstance(job, Job):
            raise TypeError("job must be a Job instance")
        if any(existing.job_id == job.job_id for existing in self.jobs):
            raise DuplicateJobIdError(f"System already has a job with id '{job.job_id}'")
        self.jobs.append(job)

    def add_workcenter(self, workcenter: Workcenter) -> None:
        if not isinstance(workcenter, Workcenter):
            raise TypeError("workcenter must be a Workcenter instance")
        existing_machine_names = {m.name for m in self.machines}
        for machine in workcenter.machines:
            if machine.name in existing_machine_names:
                raise DuplicateMachineIdError(
                    f"System already has a machine named '{machine.name}' "
                    f"(adding workcenter '{workcenter.name}')"
                )
        self.workcenters.append(workcenter)

    def validate(self) -> None:
        """
        Check invariants that can only be verified once jobs and workcenters
        are both present, regardless of the order they were added in.
        Per-object invariants (non-empty operations/machines, positive
        processing times, duplicate ids) are already enforced at
        construction/add time; this only re-checks operation -> workcenter
        references, which can't be validated until both sides exist.
        """
        workcenter_names = {wc.name for wc in self.workcenters}
        for job in self.jobs:
            for op in job.operations:
                if op.workcenter not in workcenter_names:
                    raise MissingWorkcenterError(
                        f"Job '{job.job_id}' has an operation referencing unknown "
                        f"workcenter '{op.workcenter}'. Known workcenters: {sorted(workcenter_names)}"
                    )

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
