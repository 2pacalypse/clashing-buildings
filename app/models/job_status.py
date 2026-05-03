"""
Enum for representing the status of a clash detection job.
"""
from enum import Enum


class JobStatus(str, Enum):
    """Enum for clash detection job status."""

    PENDING = "pending"
    COMPLETED = "completed"
