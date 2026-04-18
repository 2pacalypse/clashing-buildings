from shapely.geometry import Polygon
from app.models.canonical.buildings import CanonicalBuilding, CanonicalBuildingSet, CanonicalPolygon
from app.models.clash_detection_request import ClashDetectionRequest, GeoJSONFeature, PolygonGeometry

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
        base=map_polygon_to_canonical(building.geometry)
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
    
    # Sort by building, keeping track of original indices
    buildings_with_indices.sort(key=lambda x: x[0])
    
    # Extract sorted buildings and their original indices
    sorted_buildings = [building for building, _ in buildings_with_indices]
    original_indices = tuple(idx for _, idx in buildings_with_indices)
    
    return CanonicalBuildingSet(buildings=tuple(sorted_buildings)), original_indices