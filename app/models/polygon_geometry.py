from typing import List, Annotated
from pydantic import BaseModel, Field
from typing_extensions import Literal

Coordinate = Annotated[List[float], Field(min_items=2, max_items=2, description="[lon, lat]")]

class PolygonGeometry(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[Coordinate]]

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.validate_simple_polygon

    @classmethod
    def validate_simple_polygon(cls, value):
        # Only one exterior ring (no holes, no multipolygons)
        coords = value["coordinates"] if isinstance(value, dict) else value.coordinates
        if not isinstance(coords, list) or len(coords) != 1:
            raise ValueError("Only simple polygons with a single exterior ring are allowed (no holes, no multipolygons).")
        ring = coords[0]
        if len(ring) < 4:
            raise ValueError("A polygon ring must have at least 4 coordinates (minimum for a triangle).")
        if ring[0] != ring[-1]:
            raise ValueError("Polygon ring must be closed: first and last coordinates must be identical.")
        return value
