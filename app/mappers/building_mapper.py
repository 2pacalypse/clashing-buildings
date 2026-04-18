from app.models.canonical.buildings import CanonicalBuilding, CanonicalBuildingSet, CanonicalPolygon
from app.models.clash_detection_request import ClashDetectionRequest, GeoJSONFeature, PolygonGeometry, PolygonGeometry


def map_polygon_to_canonical(geometry: PolygonGeometry) -> CanonicalPolygon:
    coords = geometry.coordinates[0]
    coords_t = [tuple(c) for c in coords]

    # Drop closing duplicate
    coords_t = coords_t[:-1]

    min_idx = min(range(len(coords_t)), key=lambda i: coords_t[i])
    rotated = coords_t[min_idx:] + coords_t[:min_idx]

    # Append first coordinate to close the polygon
    rotated.append(rotated[0])
    return CanonicalPolygon(coordinates=tuple(rotated))

def map_building_to_canonical(building: GeoJSONFeature) -> CanonicalBuilding:
    """Map incoming building data to canonical format."""
    return CanonicalBuilding(
        elevation=building.properties.elevation,
        height=building.properties.height,
        base=map_polygon_to_canonical(building.geometry)
    )


def map_request_to_canonical(request: ClashDetectionRequest) -> CanonicalBuildingSet:
    """Map incoming clash detection request to canonical building set."""
    canonical_buildings = [map_building_to_canonical(feat) for feat in request.features]
    canonical_buildings.sort()
    return CanonicalBuildingSet(buildings=tuple(canonical_buildings))