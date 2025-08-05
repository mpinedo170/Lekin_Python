from ..schedule import MachineSchedule, Schedule

class SchedulingAlgorithm:
    def __init__(self):
        self.machine_workcenter_map = {}
        self.machine_available_time = {}
        self.machine_job_map = {}  # Tracks jobs per machine

    def prepare(self, system):
        """Prepare scheduling structures and track machine availability and workcenter mapping."""
        self.machine_workcenter_map = {}
        # Initialize machine availability with release time (default to 0)
        self.machine_available_time = {machine.name: getattr(machine, 'release', 0) for machine in system.machines}
        self.machine_job_map = {machine.name: [] for machine in system.machines}

        # Map machines to workcenters
        if hasattr(system, 'workcenters'):
            for workcenter in getattr(system, 'workcenters', []):
                for machine in workcenter.machines:
                    self.machine_workcenter_map[machine.name] = workcenter.name
        else:
            for machine in system.machines:
                # If no explicit workcenters, use machine name as workcenter
                self.machine_workcenter_map[machine.name] = machine.name

    def _get_machines_for_workcenter(self, system, workcenter_name):
        """Returns machines that belong to a specific workcenter."""
        return [machine for machine in system.machines if self.machine_workcenter_map.get(machine.name) == workcenter_name]

    def _get_earliest_machine(self, machines):
        """Returns the machine that becomes available the earliest."""
        return min(machines, key=lambda machine: self.machine_available_time[machine.name])

    def _update_machine_time(self, machine_name, end_time):
        """Updates the availability time of a machine."""
        self.machine_available_time[machine_name] = end_time

    def _assign_single_operation(self, job, operation, chosen_machine):
        """
        Assigns a single operation to a machine.
        """
        previous_end_time = job.operations[job.operations.index(operation) - 1].end_time if job.operations.index(operation) > 0 else job.release
        start_time = max(previous_end_time, self.machine_available_time[chosen_machine.name])
        end_time = start_time + operation.processing_time

        # Update operation
        operation.start_time = start_time
        operation.end_time = end_time

        # Update job's overall start/end
        job.start_time = job.operations[0].start_time
        job.end_time = operation.end_time

        # Update machine
        self._update_machine_time(chosen_machine.name, end_time)
        self.machine_job_map[chosen_machine.name].append(job.job_id)

    def _get_available_jobs(self, unscheduled_jobs, current_time):
        """
        Returns jobs released at or before the current time.
        """
        return [job for job in unscheduled_jobs if job.release <= current_time]

    def schedule(self, system):
        raise NotImplementedError("Subclasses must implement this method!")

    def get_machine_schedules(self, system):
        machines = []
        for machine in system.machines:
            workcenter = self.machine_workcenter_map.get(machine.name, None)
            machines.append(MachineSchedule(
                workcenter=workcenter,
                machine=machine.name,
                operations=self.machine_job_map[machine.name]
            ))
        return machines