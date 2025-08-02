from ..schedule import MachineSchedule, Schedule

class SchedulingAlgorithm:
    def __init__(self):
        self.machine_workcenter_map = {}
        self.machine_available_time = {}
        self.machine_job_map = {}  # Tracks jobs per machine

    def prepare(self, system):
        """Prepare scheduling structures."""
        self.machine_workcenter_map = {}
        self.machine_available_time = {m.name: getattr(m, 'release', 0) for m in system.machines}
        self.machine_job_map = {m.name: [] for m in system.machines}

        if hasattr(system, 'workcenters'):
            for wc in getattr(system, 'workcenters', []):
                for m in wc.machines:
                    self.machine_workcenter_map[m.name] = wc.name
        else:
            for m in system.machines:
                self.machine_workcenter_map[m.name] = m.name

    def _get_machines_for_workcenter(self, system, workcenter_name):
        """Returns machines belonging to the specified workcenter."""
        return [m for m in system.machines if self.machine_workcenter_map.get(m.name) == workcenter_name]

    def _get_earliest_machine(self, machines):
        """Returns machine that becomes available earliest."""
        return min(machines, key=lambda m: self.machine_available_time[m.name])

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
            wc = self.machine_workcenter_map.get(machine.name, None)
            machines.append(MachineSchedule(
                workcenter=wc,
                machine=machine.name,
                operations=self.machine_job_map[machine.name]
            ))
        return machines