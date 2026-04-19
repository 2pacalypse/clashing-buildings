from typing import List, Annotated
from pydantic import BaseModel, Field
from typing_extensions import Literal

Coordinate = Annotated[List[float], Field(min_items=2, max_items=2, description="[lon, lat]")]

class PolygonGeometry(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[Coordinate]]
