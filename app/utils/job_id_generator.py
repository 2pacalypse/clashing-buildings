import hashlib
import json
from dataclasses import astuple
from shapely.geometry import Polygon
from app.models.canonical.buildings import CanonicalBuildingSet


def _serialize_default(obj):
    """Fallback serializer for shapely Polygon objects."""
    if isinstance(obj, Polygon):
        return list(obj.exterior.coords)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def generate_job_id(building_set: CanonicalBuildingSet) -> str:
    """Generate a canonical SHA256 job id for a CanonicalBuildingSet.

    The canonical model is already normalized (rounded and rotated), so
    we serialize the immutable dataclass tuple-structure and hash it.
    Uses a fallback serializer to handle shapely Polygon objects.
    """
    canonical_tuple = astuple(building_set)
    canonical = json.dumps(canonical_tuple, separators=(",", ":"), ensure_ascii=False, default=_serialize_default)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
