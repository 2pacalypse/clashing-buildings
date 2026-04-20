"""Application-wide exceptions."""



class JobNotFoundError(Exception):
    """Raised when a job ID does not exist."""
    pass


class ComplexityLimitExceededError(Exception):
    """Raised when the complexity of the request exceeds the allowed threshold (e.g., too many buildings or vertices)."""
    pass
