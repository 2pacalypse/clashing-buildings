from typing import List, Annotated
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Literal

Coordinate = Annotated[
    List[float], Field(min_items=2, max_items=2, description="[lon, lat]")
]


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[Coordinate]]

    @model_validator(mode="after")
    def check_ring_closed(self):
        # Always runs after model is constructed, even if from another model
        coords = self.coordinates
        if not isinstance(coords, list) or len(coords) != 1:
            raise ValueError(
                "Only simple polygons with a single exterior ring are allowed (no holes, no multipolygons)."
            )
        ring = coords[0]
        if len(ring) < 4:
            raise ValueError(
                "A polygon ring must have at least 4 coordinates (minimum for a triangle)."
            )
        if ring[0] != ring[-1]:
            raise ValueError(
                "Polygon ring must be closed: first and last coordinates must be identical."
            )
        return self
