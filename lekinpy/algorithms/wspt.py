from .base import SchedulingAlgorithm
from ..schedule import Schedule

class WSPTAlgorithm(SchedulingAlgorithm):
    def schedule(self, system):
        def wspt_selector_function(jobs):
            """
            Apply the WSPT rule: pick the job with the highest weight-to-processing-time
            ratio (using its first operation's processing time), prioritizing jobs that
            are more 'important' relative to their processing time.
            """
            def priority(job):
                if job.operations and job.operations[0].processing_time > 0:
                    return job.weight / job.operations[0].processing_time
                return float('-inf')
            return max(jobs, key=priority)

        total_time, machines = self.dynamic_schedule(system, wspt_selector_function)

        return Schedule("WSPT", total_time, machines)
