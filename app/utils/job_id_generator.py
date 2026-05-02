import hashlib
import json

from app.models.canonical import CanonicalBuildingSet


def generate_job_id(building_set: CanonicalBuildingSet) -> str:
    """Generate a canonical SHA256 job id for a CanonicalBuildingSet.

    The canonical model is already normalized (rounded and rotated).
    Uses Pydantic's field_serializer to automatically convert Polygons to coordinates.
    """
    canonical_dict = building_set.model_dump()
    canonical = json.dumps(canonical_dict, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
