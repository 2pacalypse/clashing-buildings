from typing import List
from shapely.geometry import Polygon
from app.models.canonical import (
    CanonicalBuilding,
    CanonicalBuildingSet,
    CanonicalPolygon,
    CanonicalBuildingIntersection,
)
from app.models.clash_detection_request import ClashDetectionRequest, GeoJSONFeature
from app.models.polygon_geometry import PolygonGeometry
from app.models.clash_detection_response import (
    ClashDetectionResponse,
    ClashFeature,
    ClashProperties,
    ClashResultFeatureCollection,
)

from app.models.job_status import JobStatus
from app.core.constants import SCALE


def _quantize_z(value: float) -> int:
    """Quantize a z-axis value (elevation or height) to integer using SCALE."""
    return int(round(value * SCALE))


def _unquantize_z(value: int) -> float:
    """Convert quantized z-axis value back to float."""
    return value / SCALE


def _quantize_coords(coord: tuple[float, float]) -> tuple[int, int]:
    x, y = coord
    return (int(round(x * SCALE)), int(round(y * SCALE)))


def _unquantize_coords(coords):
    return [(x / SCALE, y / SCALE) for x, y in coords]


def map_polygon_to_canonical(geometry: PolygonGeometry) -> CanonicalPolygon:
    coords = geometry.coordinates[0]
    coords_t = [_quantize_coords(tuple(c)) for c in coords]

    # Create shapely polygon and normalize it
    shapely_polygon = Polygon(coords_t).normalize()
    return CanonicalPolygon(polygon=shapely_polygon)


def map_building_to_canonical(building: GeoJSONFeature) -> CanonicalBuilding:
    """Map incoming building data to canonical format."""
    # Quantize elevation and height for canonical representation
    elevation_q = _quantize_z(building.properties.elevation)
    height_q = _quantize_z(building.properties.height)
    return CanonicalBuilding(
        elevation=elevation_q,
        height=height_q,
        base=map_polygon_to_canonical(building.geometry),
    )


def map_request_to_canonical(
    request: ClashDetectionRequest,
) -> tuple[CanonicalBuildingSet, tuple[int, ...]]:
    """Map incoming clash detection request to canonical building set.

    Returns:
        A tuple of (canonical_building_set, indices) where indices[i] is the
        original input index of the i-th building in the canonical set.
    """
    # Create list of (building, original_index) tuples
    buildings_with_indices = [
        (map_building_to_canonical(feat), idx)
        for idx, feat in enumerate(request.features)
    ]

    # Sort by elevation, then height, keeping track of original indices
    buildings_with_indices.sort(
        key=lambda x: (
            x[0].elevation,
            x[0].height,
            tuple(x[0].base.polygon.exterior.coords),
        )
    )

    # Extract sorted buildings and their original indices
    sorted_buildings = [building for building, _ in buildings_with_indices]
    original_indices = tuple(idx for _, idx in buildings_with_indices)

    return CanonicalBuildingSet(buildings=tuple(sorted_buildings)), original_indices


def map_collisions_to_response(
    collisions: List[CanonicalBuildingIntersection],
    buildings: List[List[str]],
    request_id: str,
) -> ClashDetectionResponse:
    """Map list of canonical collisions to a ClashDetectionResponse (GeoJSON FeatureCollection).

    Args:
        collisions: list of CanonicalBuildingIntersection objects returned by detector
        request: original ClashDetectionRequest (for mapping back building ids)
        original_indices: mapping from canonical ordering back to original feature indices
        request_id: server-side request id

    Returns:
        ClashDetectionResponse containing GeoJSON FeatureCollection of clashes.
    """

    clash_features: List[ClashFeature] = []
    for c, b in zip(collisions, buildings):
        intersection_coords = _unquantize_coords(
            c.intersection.base.polygon.exterior.coords
        )
        clash_features.append(
            ClashFeature(
                type="Feature",
                properties=ClashProperties(
                    elevation=_unquantize_z(c.intersection.elevation),
                    height=_unquantize_z(c.intersection.height),
                    buildings=b,
                ),
                geometry=PolygonGeometry(
                    type="Polygon",
                    coordinates=[intersection_coords],
                ),
            )
        )

    result = ClashResultFeatureCollection(features=clash_features)

    return ClashDetectionResponse(
        request_id=request_id,
        status=JobStatus.COMPLETED,
        result=result,
    )
