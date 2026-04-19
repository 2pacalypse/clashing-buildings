"""Application-wide exceptions."""


class JobNotFoundError(Exception):
    """Raised when a job ID does not exist."""
    pass
