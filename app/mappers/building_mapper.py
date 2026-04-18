from shapely.geometry import Polygon
from typing import List, Tuple

from app.models.canonical.buildings import (
    CanonicalBuilding,
    CanonicalBuildingSet,
    CanonicalPolygon,
    CanonicalBuildingIntersection,
)
from app.models.clash_detection_request import ClashDetectionRequest, GeoJSONFeature, PolygonGeometry
from app.models.clash_detection_response import (
    ClashDetectionResponse,
    ClashFeature,
    ClashProperties,
    ClashResultFeatureCollection,
)
from app.models.job_status import JobStatus

SCALE = 10**6


def map_coordinate_to_canonical(coord: tuple[float, float]) -> tuple[int, int]:
    x, y = coord
    return (int(round(x * SCALE)), int(round(y * SCALE)))


def map_polygon_to_canonical(geometry: PolygonGeometry) -> CanonicalPolygon:
    coords = geometry.coordinates[0]
    coords_t = [map_coordinate_to_canonical(tuple(c)) for c in coords]

    # Create shapely polygon and normalize it
    shapely_polygon = Polygon(coords_t).normalize()
    return CanonicalPolygon(polygon=shapely_polygon)


def map_building_to_canonical(building: GeoJSONFeature) -> CanonicalBuilding:
    """Map incoming building data to canonical format."""
    return CanonicalBuilding(
        elevation=building.properties.elevation,
        height=building.properties.height,
        base=map_polygon_to_canonical(building.geometry),
    )


def map_request_to_canonical(request: ClashDetectionRequest) -> tuple[CanonicalBuildingSet, tuple[int, ...]]:
    """Map incoming clash detection request to canonical building set.

    Returns:
        A tuple of (canonical_building_set, indices) where indices[i] is the 
        original input index of the i-th building in the canonical set.
    """
    # Create list of (building, original_index) tuples
    buildings_with_indices = [
        (map_building_to_canonical(feat), idx) for idx, feat in enumerate(request.features)
    ]

    # Sort by elevation, then height, keeping track of original indices
    buildings_with_indices.sort(key=lambda x: (x[0].elevation, x[0].height))

    # Extract sorted buildings and their original indices
    sorted_buildings = [building for building, _ in buildings_with_indices]
    original_indices = tuple(idx for _, idx in buildings_with_indices)

    return CanonicalBuildingSet(buildings=tuple(sorted_buildings)), original_indices


def map_collisions_to_response(
    collisions: List[CanonicalBuildingIntersection],
    request: ClashDetectionRequest,
    original_indices: Tuple[int, ...],
    job_id: str,
) -> ClashDetectionResponse:
    """Map list of canonical collisions to a ClashDetectionResponse (GeoJSON FeatureCollection).

    Args:
        collisions: list of CanonicalBuildingIntersection objects returned by detector
        request: original ClashDetectionRequest (for mapping back building ids)
        original_indices: mapping from canonical ordering back to original feature indices
        job_id: server-side job id

    Returns:
        ClashDetectionResponse containing GeoJSON FeatureCollection of clashes.
    """

    def _unquantize_coords(coords):
        return [(x / SCALE, y / SCALE) for x, y in coords]

    clash_features: List[ClashFeature] = []
    for c in collisions:
        intersection_coords = _unquantize_coords(c.intersection.base.polygon.exterior.coords)
        clash_features.append(
            ClashFeature(
                type="Feature",
                properties=ClashProperties(
                    elevation=c.intersection.elevation,
                    height=c.intersection.height,
                    buildings=[request.features[original_indices[i]].id for i in c.building_ids],
                ),
                geometry=PolygonGeometry(
                    type="Polygon",
                    coordinates=[intersection_coords],
                ),
            )
        )

    result = ClashResultFeatureCollection(features=clash_features)

    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        result=result,
    )