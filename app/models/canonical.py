"""
Canonical models for building geometry and intersections, with polygon serialization and validation.
"""
from typing import Tuple
from pydantic import BaseModel, field_validator, ConfigDict, field_serializer
from shapely.geometry import Polygon


class CanonicalPolygon(BaseModel):
    """Canonical polygon representation for building footprints."""

    polygon: Polygon

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("polygon")
    def serialize_polygon(self, polygon: Polygon) -> list:
        return list(polygon.exterior.coords)

    @field_validator("polygon", mode="before")
    def _parse_polygon(cls, v):
        """
        Parse and convert input data to a shapely Polygon instance if needed.
        Accepts lists or tuples and handles different polygon input formats.
        """
        if isinstance(v, (list, tuple)):
            # handle either [ [ (x,y),... ] ] or [ (x,y), ... ]
            coords = v[0] if v and isinstance(v[0][0], (list, tuple)) else v
            return Polygon(coords)
        return v


class CanonicalBuilding(BaseModel):
    """Canonical building model"""

    elevation: float
    height: float
    base: CanonicalPolygon

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CanonicalBuildingSet(BaseModel):
    """Canonical building set model for clash detection."""

    buildings: Tuple[CanonicalBuilding, ...]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CanonicalBuildingIntersection(BaseModel):
    """Canonical building set model for clash detection."""

    building_ids: Tuple[int, int]
    intersection: CanonicalBuilding

    model_config = ConfigDict(arbitrary_types_allowed=True)
