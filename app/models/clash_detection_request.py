from typing import List, Annotated, Literal
from pydantic import BaseModel, Field, field_validator
import hashlib
import json




class BuildingProperties(BaseModel):
    height: float = Field(gt=0, description="Building height in meters")
    elevation: float = Field(ge=0, description="Building base elevation in meters")


Coordinate = Annotated[List[float], Field(min_items=2, max_items=2, description="[lon, lat]")]


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[Coordinate]]


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    id: str
    properties: BuildingProperties
    geometry: PolygonGeometry


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        if not v:
            raise ValueError("FeatureCollection must have at least one feature")
        return v


class ClashDetectionRequest(GeoJSONFeatureCollection):
    """Request schema for clash detection - accepts GeoJSON FeatureCollection directly."""

    #todo: fix - feature id is important. do not ignore it.
    def hash(self) -> str:
        # Build a canonical representation:
        # - Format all numeric values to 6 decimals
        # - For each polygon ring: remove closing duplicate, rotate so minimum coordinate is first
        # - Ignore feature `id` and any ordering of features by sorting canonicalized features
        
        def _format_num(n: float) -> str:
            return f"{n:.6f}"

        def _normalize_coordinate(coord: List[float]) -> List[str]:
            lon, lat = coord
            return [_format_num(lon), _format_num(lat)]

        def _rotate_ring_min_first(ring: List[List[float]]) -> List[List[str]]:
            if not ring:
                return []
            # drop trailing duplicate if it exactly matches the first coordinate
            if len(ring) > 1:
                first = ring[0]
                last = ring[-1]
                if abs(first[0] - last[0]) < 1e-12 and abs(first[1] - last[1]) < 1e-12:
                    ring = ring[:-1]
            formatted = [_normalize_coordinate(c) for c in ring]
            # find lexicographically smallest coordinate and rotate so it is first
            min_idx = min(range(len(formatted)), key=lambda i: (formatted[i][0], formatted[i][1]))
            rotated = formatted[min_idx:] + formatted[:min_idx]
            return rotated
        
        canonical_features = []
        for feat in self.features:
            rings = []
            for ring in feat.geometry.coordinates:
                rings.append(_rotate_ring_min_first(ring))

            props = {
                "height": _format_num(feat.properties.height),
                "elevation": _format_num(feat.properties.elevation),
            }

            canonical_feature = {"coordinates": rings, "properties": props}
            canonical_features.append(canonical_feature)

        # Sort features so overall ordering does not affect the result
        canonical_features.sort(key=lambda f: json.dumps(f, separators=(",", ":"), ensure_ascii=False))

        
        canonical = json.dumps(canonical_features, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
        