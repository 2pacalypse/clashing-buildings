"""
Models for clash detection request payloads, including GeoJSON features and validation.
"""
from typing import List
from pydantic import BaseModel, Field, field_validator
from app.models.polygon_geometry import PolygonGeometry


class BuildingProperties(BaseModel):
    """
    Properties for a building, including height and elevation.
    """
    height: float = Field(gt=0, description="Building height in meters")
    elevation: float = Field(ge=0, description="Building base elevation in meters")


class GeoJSONFeature(BaseModel):
    """
    GeoJSON Feature representing a building with properties and geometry.
    """
    type: str = "Feature"
    id: str
    properties: BuildingProperties
    geometry: PolygonGeometry


class GeoJSONFeatureCollection(BaseModel):
    """
    GeoJSON FeatureCollection containing a list of building features.
    """
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

    @field_validator("features")
    @classmethod
    def validate_features(cls, v):
        """
        Validates that the FeatureCollection contains at least one feature.
        Raises a ValueError if the list is empty.
        """
        if not v:
            raise ValueError("FeatureCollection must have at least one feature")
        return v


class ClashDetectionRequest(GeoJSONFeatureCollection):
    """Request schema for clash detection - accepts GeoJSON FeatureCollection directly."""

    pass
