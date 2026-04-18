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
    pass
    
        