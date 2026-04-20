# Constants for the application

SCALE = 10**6  # Used for floating point to integer quantization

# Threshold for sync clash detection (n_buildings * n_vertices)
SYNC_CLASH_COMPLEXITY_THRESHOLD = 100_000

# Absolute maximum complexity allowed (applies to both sync and async jobs)
MAX_CLASH_COMPLEXITY_THRESHOLD = 20_000_000
