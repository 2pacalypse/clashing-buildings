import hashlib
import json
from dataclasses import astuple
from app.models.canonical.buildings import CanonicalBuildingSet


def generate_job_id(building_set: CanonicalBuildingSet) -> str:
    """Generate a canonical SHA256 job id for a CanonicalBuildingSet.

    The canonical model is already normalized (rounded and rotated), so
    we serialize the immutable dataclass tuple-structure and hash it.
    """
    canonical_tuple = astuple(building_set)
    canonical = json.dumps(canonical_tuple, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
