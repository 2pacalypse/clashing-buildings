from typing import Dict, Any
from shapely.geometry import Polygon, mapping
from app.models.canonical.buildings import CanonicalBuilding, CanonicalBuildingSet, CanonicalBuildingIntersection, CanonicalPolygon


def _convert_buildings_to_geometries(building_set: CanonicalBuildingSet):
    """
    Convert CanonicalBuildingSet to list of dicts containing Shapely geometries
    and 3D bounds (elevation, height, top).
    """
    geometries = []
    for idx, building in enumerate(building_set.buildings):
        try:
            geom = Polygon(building.base.coordinates)
            geometries.append({
                "id": f"building_{idx}",
                "geometry": geom,
                "height": building.height,
                "elevation": building.elevation,
                "top": building.elevation + building.height
            })
        except Exception:
            continue
    return geometries

def detect_clashes(building_set: CanonicalBuildingSet) -> Dict[str, Any]:
    """
    Detect 3D clashes between buildings using canonical building set model.
    Step 1: List all pairwise indices with collision and attributes.
    Step 2: Build GeoJSON output from those collisions.
    """
    geometries = _convert_buildings_to_geometries(building_set)

    # Step 1: Find all colliding pairs and their attributes
    collisions = []
    for i, geom1 in enumerate(geometries):
        for j, geom2 in enumerate(geometries[i + 1:], start=i + 1):
            # Check 2D intersection
            if geom1["geometry"].intersects(geom2["geometry"]):
                # Check 3D overlap (elevation ranges)
                if not (geom1["top"] < geom2["elevation"] or geom2["top"] < geom1["elevation"]):
                    intersection_geom = geom1["geometry"].intersection(geom2["geometry"])
                    clash_elevation = max(geom1["elevation"], geom2["elevation"])
                    clash_top = min(geom1["top"], geom2["top"])
                    clash_height = clash_top - clash_elevation
                    if clash_height > 0 and not intersection_geom.is_empty:
                        # Use CanonicalBuildingIntersection for collisions
                        intersection_building = CanonicalBuilding(
                                elevation=clash_elevation,
                                height=clash_height,
                                base=CanonicalPolygon(coordinates=tuple(intersection_geom.exterior.coords))
                            )
                        
                        intersection = CanonicalBuildingIntersection(
                            building_ids=(i, j),
                            intersection= intersection_building
                        )
                        collisions.append(intersection)

    # Step 2: Build GeoJSON output from CanonicalBuildingIntersection list
    clash_features = []
    for c in collisions:
        # Reconstruct the intersection geometry as a Shapely Polygon
        intersection_geom = Polygon(c.intersection.base.coordinates)
        clash_features.append({
            "type": "Feature",
            "properties": {
                "elevation": c.intersection.elevation,
                "height": c.intersection.height,
                "buildings": list(map(str, c.building_ids))
            },
            "geometry": mapping(intersection_geom)
        })

    return {
        "type": "FeatureCollection",
        "features": clash_features
    }
