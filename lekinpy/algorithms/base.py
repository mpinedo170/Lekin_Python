from ..schedule import MachineSchedule, Schedule

class SchedulingAlgorithm:
    """
    Base class for scheduling algorithms.
    Provides shared methods and structures for machine assignment,
    tracking availability, and dynamic scheduling.
    """

    def __init__(self):
        # Maps each machine's name to its corresponding workcenter name
        self.machine_workcenter_map = {}

        # Tracks when each machine will next be available
        self.machine_available_time = {}

        # Stores the list of job IDs assigned to each machine for reporting and visualization
        self.machine_job_map = {}

    def prepare(self, system):
        """
        Prepares internal state: maps machines to workcenters, 
        sets initial machine availability, and initializes job mapping.
        """
        self.machine_workcenter_map = {}

        # Initialize machine availability to their release times (or zero by default)
        self.machine_available_time = {
            machine.name: getattr(machine, 'release', 0)
            for machine in system.machines
        }

        # Initialize empty job list per machine
        self.machine_job_map = {
            machine.name: []
            for machine in system.machines
        }

        # If system has workcenters, map each machine to its workcenter
        if hasattr(system, 'workcenters'):
            for workcenter in getattr(system, 'workcenters', []):
                for machine in workcenter.machines:
                    self.machine_workcenter_map[machine.name] = workcenter.name
        else:
            # If workcenters aren't explicitly defined, use machine name as default workcenter name
            for machine in system.machines:
                self.machine_workcenter_map[machine.name] = machine.name

    def _get_machines_for_workcenter(self, system, workcenter_name):
        """
        Returns list of machines belonging to a given workcenter.
        """
        return [
            machine
            for machine in system.machines
            if self.machine_workcenter_map.get(machine.name) == workcenter_name
        ]

    def _get_earliest_machine(self, machines):
        """
        From a list of machines, return the one that becomes available the earliest.
        """
        return min(
            machines,
            key=lambda machine: self.machine_available_time[machine.name]
        )

    def _update_machine_time(self, machine_name, end_time):
        """
        Updates the time when the given machine will next be available.
        """
        self.machine_available_time[machine_name] = end_time

    def _assign_single_operation(self, job, operation, chosen_machine):
        """
        Assigns a single operation of a job to the chosen machine.

        - Calculates when the job can start, considering:
            • its own release time, or
            • the end of the previous operation if it's not the first.
        - Updates the job and machine state accordingly.
        """
        # Determine the time this operation can start
        # If it's not the first operation, we must wait for the previous one to finish
        previous_end_time = (
            job.operations[job.operations.index(operation) - 1].end_time
            if job.operations.index(operation) > 0
            else job.release
        )

        # Actual start time is the later of machine availability and previous operation's end
        start_time = max(previous_end_time, self.machine_available_time[chosen_machine.name])
        end_time = start_time + operation.processing_time

        # Update the operation with start and end time
        operation.start_time = start_time
        operation.end_time = end_time

        # For consistency, update job's start and end time from operation times
        job.start_time = job.operations[0].start_time
        job.end_time = operation.end_time

        # Update machine's availability
        self._update_machine_time(chosen_machine.name, end_time)

        # Track which job was assigned to which machine
        self.machine_job_map[chosen_machine.name].append(job.job_id)

    def _get_available_jobs(self, unscheduled_jobs, current_time):
        """
        Returns all jobs from unscheduled list that are released by the current time.
        """
        return [
            job
            for job in unscheduled_jobs
            if job.release <= current_time
        ]

    def schedule(self, system):
        """
        Placeholder. Must be implemented by subclass algorithms.
        """
        raise NotImplementedError("Subclasses must implement this method!")

    def get_machine_schedules(self, system):
        """
        Returns a list of MachineSchedule objects representing final schedules per machine.
        """
        machines = []
        for machine in system.machines:
            workcenter = self.machine_workcenter_map.get(machine.name, None)
            machines.append(MachineSchedule(
                workcenter=workcenter,
                machine=machine.name,
                operations=self.machine_job_map[machine.name]
            ))
        return machines

    def dynamic_schedule(self, system, job_selector_fn):
        """
        Generic dynamic scheduling engine.

        Arguments:
            system: scheduling system with jobs and machines
            job_selector_fn: function that selects the next job to schedule from a list of available jobs

        This function loops over time, selecting and assigning jobs dynamically as they become available.
        """
        # Prepare all internal states
        self.prepare(system)

        # Track all unscheduled jobs by job_id
        unscheduled_jobs = {job.job_id: job for job in system.jobs}

        # Loop until all jobs are scheduled
        while unscheduled_jobs:
            # Get the current global simulation time as the earliest machine availability
            current_time = min(self.machine_available_time.values())

            # Find jobs that have been released by current_time
            available_jobs = [
                job
                for job in unscheduled_jobs.values()
                if job.release <= current_time
            ]

            # If no jobs are currently available, fast forward machine availability
            if not available_jobs:
                # Find the next job to be released
                next_release = min(job.release for job in unscheduled_jobs.values())

                # Advance the availability of the earliest machine to this next release
                earliest_machine = min(
                    self.machine_available_time,
                    key=self.machine_available_time.get
                )
                self.machine_available_time[earliest_machine] = next_release
                continue  # Retry with updated current_time

            # Use the algorithm-specific selection rule to pick one job from available ones
            job = job_selector_fn(available_jobs)

            # Select the first operation (assuming single-operation jobs for now)
            op = job.operations[0]

            # Find eligible machines for this operation and pick the earliest one
            candidate_machines = self._get_machines_for_workcenter(system, op.workcenter)
            chosen_machine = self._get_earliest_machine(candidate_machines)

            # Assign operation to the chosen machine
            self._assign_single_operation(job, op, chosen_machine)

            # Remove job from unscheduled pool
            del unscheduled_jobs[job.job_id]

        # After all jobs are scheduled, prepare the schedule summary
        machines = self.get_machine_schedules(system)
        total_time = max(self.machine_available_time.values()) if self.machine_available_time else 0
        return total_time, machines