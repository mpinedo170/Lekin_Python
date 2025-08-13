"""Public API for lekinpy.
Expose the main classes and functions at the package root for convenient imports.
"""

__version__ = "0.1.0"

from .job import Job, Operation
from .machine import Machine, Workcenter
from .schedule import Schedule, MachineSchedule
from .system import System
from .io import (
    export_jobs_to_jobfile,
    export_workcenters_to_mchfile,
    export_system_to_json,
    parse_job_file,
    parse_mch_file,
    parse_seq_file,
    save_schedule_to_json,
    save_schedule_to_seq,
    load_jobs_from_json,
    load_workcenters_from_json,
)
from .algorithms import (
    SchedulingAlgorithm,
    FCFSAlgorithm,
    SPTAlgorithm,
    EDDAlgorithm,
    WSPTAlgorithm,
)

__all__ = [
    # Core entities
    "Job",
    "Operation",
    "Machine",
    "Workcenter",
    "Schedule",
    "MachineSchedule",
    "System",
    # IO helpers
    "export_jobs_to_jobfile",
    "export_workcenters_to_mchfile",
    "export_system_to_json",
    "parse_job_file",
    "parse_mch_file",
    "parse_seq_file",
    "save_schedule_to_json",
    "save_schedule_to_seq",
    "load_jobs_from_json",
    "load_workcenters_from_json",
    # Algorithms
    "SchedulingAlgorithm",
    "FCFSAlgorithm",
    "SPTAlgorithm",
    "EDDAlgorithm",
    "WSPTAlgorithm",
    # Metadata
    "__version__",
]
