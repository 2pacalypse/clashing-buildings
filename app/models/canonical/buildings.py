from dataclasses import dataclass
from typing import List, Annotated, Literal
from pydantic import BaseModel, Field, field_validator
from shapely.geometry import Polygon
import hashlib
import json



@dataclass
class CanonicalPolygon:
    """Canonical polygon representation for building footprints."""
    polygon: Polygon

@dataclass(order=True)
class CanonicalBuilding:
    """Canonical building model"""
    elevation: float
    height: float
    base: CanonicalPolygon


@dataclass
class CanonicalBuildingSet:
    """Canonical building set model for clash detection."""
    buildings: tuple[CanonicalBuilding]


@dataclass
class CanonicalBuildingIntersection:
    """Canonical building set model for clash detection."""
    building_ids: tuple[int, int]
    intersection: CanonicalBuilding
