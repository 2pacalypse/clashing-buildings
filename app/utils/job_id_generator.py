from typing import List
import hashlib
import json
from app.models.clash_detection_request import ClashDetectionRequest


def generate_job_id(request: ClashDetectionRequest) -> str:
    """Generate a canonical SHA256 job id for a ClashDetectionRequest-like object."""
    def _format_num(n: float) -> str:
        return f"{n:.6f}"

    def _normalize_coordinate(coord: List[float]) -> List[str]:
        lon, lat = coord
        return [_format_num(lon), _format_num(lat)]

    def _rotate_ring_min_first(ring: List[List[float]]) -> List[List[str]]:
        if not ring:
            return []
        if len(ring) > 1:
            first = ring[0]
            last = ring[-1]
            if abs(first[0] - last[0]) < 1e-12 and abs(first[1] - last[1]) < 1e-12:
                ring = ring[:-1]
        formatted = [_normalize_coordinate(c) for c in ring]
        min_idx = min(range(len(formatted)), key=lambda i: (formatted[i][0], formatted[i][1]))
        rotated = formatted[min_idx:] + formatted[:min_idx]
        return rotated

    canonical_features = []
    for feat in request.features:
        rings = []
        for ring in feat.geometry.coordinates:
            rings.append(_rotate_ring_min_first(ring))

        props = {
            "height": _format_num(feat.properties.height),
            "elevation": _format_num(feat.properties.elevation),
        }

        canonical_feature = {"coordinates": rings, "properties": props}
        canonical_features.append(canonical_feature)

    canonical_features.sort(key=lambda f: json.dumps(f, separators=(",", ":"), ensure_ascii=False))
    canonical = json.dumps(canonical_features, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
