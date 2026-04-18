from dataclasses import dataclass
from typing import List, Annotated, Literal
from pydantic import BaseModel, Field, field_validator
import hashlib
import json



@dataclass
class CanonicalPolygon:
    """Canonical polygon representation for building footprints."""
    coordinates: tuple[tuple[float, float]]

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
