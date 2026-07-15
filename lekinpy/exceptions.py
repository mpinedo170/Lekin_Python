"""Typed exceptions for invalid lekinpy data.

These are raised as early as possible: object-level invariants (a job must
have operations, an operation's processing time must be positive, a
workcenter must have machines) are checked in the relevant constructor;
cross-object invariants that need the whole System (duplicate ids, a job
operation referencing a workcenter that doesn't exist) are checked when
objects are added to a System, and defensively re-checked by
System.validate().
"""


class LekinValidationError(Exception):
    """Base class for all lekinpy data-validation errors."""


class EmptyOperationsError(LekinValidationError):
    """Raised when a Job is constructed with no operations."""


class NonPositiveProcessingTimeError(LekinValidationError):
    """Raised when an Operation's processing_time is not positive."""


class EmptyMachineListError(LekinValidationError):
    """Raised when a Workcenter is constructed with no machines."""


class DuplicateJobIdError(LekinValidationError):
    """Raised when a System already has a job with the given job_id."""


class DuplicateMachineIdError(LekinValidationError):
    """Raised when a machine name is already in use elsewhere in the System."""


class DuplicateWorkcenterIdError(LekinValidationError):
    """Raised when a System already has a workcenter with the given name."""


class MissingWorkcenterError(LekinValidationError):
    """Raised when a Job operation references a workcenter the System doesn't have."""
