from typing import Optional, List

from app.models.job_status import JobStatus
from app.models.polygon_geometry import PolygonGeometry
from pydantic import BaseModel, Field


class ClashProperties(BaseModel):
    """Properties of a clash feature."""

    elevation: float = Field(ge=0, description="Elevation of the clash area in meters")
    height: float = Field(gt=0, description="Height of the clash area in meters")
    buildings: List[str] = Field(
        description="List of building IDs involved in the clash"
    )


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
    request_id: str
    status: JobStatus
    result: Optional[ClashResultFeatureCollection] = None
