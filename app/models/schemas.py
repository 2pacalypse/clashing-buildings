from typing import Optional, List, Dict, Any, Literal, Annotated
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import json

class JobStatus(str, Enum):
    """Enum for clash detection job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

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

    def content_hash(self) -> str:
        """Generate content-based hash for caching."""
        import hashlib
        canonical = self.model_dump_json()
        return hashlib.sha256(canonical.encode()).hexdigest()

class ClashProperties(BaseModel):
    """Properties of a clash feature."""
    elevation: float = Field(ge=0, description="Elevation of the clash area in meters")
    height: float = Field(gt=0, description="Height of the clash area in meters")
    buildings: List[str] = Field(description="List of building IDs involved in the clash")

class ClashFeature(BaseModel):
    """A single clash feature in the result."""
    type: str = "Feature"
    properties: ClashProperties
    geometry: PolygonGeometry

class ClashResultFeatureCollection(BaseModel):
    """Result of clash detection - GeoJSON FeatureCollection of clashes."""
    type: str = "FeatureCollection"
    features: List[ClashFeature]

class ClashDetectionResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[ClashResultFeatureCollection] = None
    from_cache: bool = False
    task_id: Optional[str] = None
