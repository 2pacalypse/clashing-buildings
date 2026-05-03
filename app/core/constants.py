"""
Constants for API versioning, quantization, complexity thresholds, and polling configuration.
"""
# Constants for the application

# API versioning
API_PREFIX = "/api/v1"

SCALE = 10**6  # Used for floating point to integer quantization

# Threshold for sync clash detection (n_buildings * n_vertices)

# Absolute maximum complexity allowed (applies to both sync and async jobs)
MAX_CLASH_COMPLEXITY_THRESHOLD = 20_000_000

# Polling configuration for async task results
POLL_TIMEOUT_SECONDS = 5  # Max time to poll for results in POST request
POLL_INTERVAL_SECONDS = 1  # Interval between polls
