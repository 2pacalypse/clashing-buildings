from typing import List
from pydantic import BaseModel, Field, field_validator
from app.models.polygon_geometry import PolygonGeometry


class BuildingProperties(BaseModel):
    height: float = Field(gt=0, description="Building height in meters")
    elevation: float = Field(ge=0, description="Building base elevation in meters")


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    id: str
    properties: BuildingProperties
    geometry: PolygonGeometry


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

    @field_validator("features")
    @classmethod
    def validate_features(cls, v):
        if not v:
            raise ValueError("FeatureCollection must have at least one feature")
        return v


class ClashDetectionRequest(GeoJSONFeatureCollection):
    """Request schema for clash detection - accepts GeoJSON FeatureCollection directly."""

    pass
