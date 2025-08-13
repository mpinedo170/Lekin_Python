from .base import SchedulingAlgorithm
from ..schedule import Schedule

class SPTAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        def spt_selector_function(jobs):
            """
            Custom SPT selection function that calculates the SPT value for a job.
            """
            return min(jobs, key=lambda job: job.operations[0].processing_time if job.operations else float('inf'))

        total_time, machines = self.dynamic_schedule(system, spt_selector_function)

        return Schedule("SPT", total_time, machines)