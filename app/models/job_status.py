from enum import Enum


class JobStatus(str, Enum):
    """Enum for clash detection job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
