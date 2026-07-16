from .job import Job
from .machine import Machine, Workcenter
from .schedule import Schedule
from .exceptions import (
    DuplicateJobIdError,
    DuplicateMachineIdError,
    DuplicateWorkcenterIdError,
    EmptyMachineListError,
    EmptyOperationsError,
    MissingWorkcenterError,
    NonPositiveProcessingTimeError,
)
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
        if any(existing.name == workcenter.name for existing in self.workcenters):
            raise DuplicateWorkcenterIdError(
                f"System already has a workcenter named '{workcenter.name}'"
            )
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
        Defensively re-check every invariant this System's data must
        satisfy, not just the ones that could only be checked once jobs and
        workcenters were both present. add_job/add_workcenter and the
        Job/Operation/Workcenter constructors already enforce these at
        insertion time, but attributes are mutable after the fact (e.g.
        `job.job_id = other_job.job_id`), so this is the final gate every
        built-in SchedulingAlgorithm runs through before scheduling.
        """
        seen_job_ids = set()
        for job in self.jobs:
            if job.job_id in seen_job_ids:
                raise DuplicateJobIdError(f"System has more than one job with id '{job.job_id}'")
            seen_job_ids.add(job.job_id)
            if not job.operations:
                raise EmptyOperationsError(f"Job '{job.job_id}' must have at least one operation")

        seen_workcenter_names = set()
        seen_machine_names = set()
        for wc in self.workcenters:
            if wc.name in seen_workcenter_names:
                raise DuplicateWorkcenterIdError(f"System has more than one workcenter named '{wc.name}'")
            seen_workcenter_names.add(wc.name)
            if not wc.machines:
                raise EmptyMachineListError(f"Workcenter '{wc.name}' must have at least one machine")
            for m in wc.machines:
                if m.name in seen_machine_names:
                    raise DuplicateMachineIdError(f"System has more than one machine named '{m.name}'")
                seen_machine_names.add(m.name)

        for job in self.jobs:
            for op in job.operations:
                if op.processing_time <= 0:
                    raise NonPositiveProcessingTimeError(
                        f"Job '{job.job_id}' has an operation with non-positive "
                        f"processing_time {op.processing_time}"
                    )
                if op.workcenter not in seen_workcenter_names:
                    raise MissingWorkcenterError(
                        f"Job '{job.job_id}' has an operation referencing unknown "
                        f"workcenter '{op.workcenter}'. Known workcenters: {sorted(seen_workcenter_names)}"
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
