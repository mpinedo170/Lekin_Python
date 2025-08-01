from .base import SchedulingAlgorithm

class WSPT(SchedulingAlgorithm):
    def schedule(self, system):
        jobs = sorted(system.jobs, key=lambda job: job.processing_time / job.weight if job.weight != 0 else float('inf'))
        current_time = 0
        for job in jobs:
            job.start_time = current_time
            job.end_time = current_time + job.processing_time
            current_time = job.end_time
        system.scheduled_jobs = jobs
