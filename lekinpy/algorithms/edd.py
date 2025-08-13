from .base import SchedulingAlgorithm
from ..schedule import Schedule

class EDDAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        def edd_selector_function(jobs):
            """
            Custom EDD selection function that calculates the EDD value for a job.
            """
            return min(jobs, key=lambda job: job.due)

        total_time, machines = self.dynamic_schedule(system, edd_selector_function)

        return Schedule("EDD", total_time, machines)
