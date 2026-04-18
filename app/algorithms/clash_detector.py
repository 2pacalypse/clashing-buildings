from typing import Dict, Any, List
from shapely.geometry import Polygon, mapping
from app.models.canonical.buildings import CanonicalBuilding, CanonicalBuildingSet, CanonicalBuildingIntersection, CanonicalPolygon


def _convert_buildings_to_geometries(building_set: CanonicalBuildingSet):
    """
    Convert CanonicalBuildingSet to list of dicts containing Shapely geometries
    and 3D bounds (elevation, height, top).
    """
    geometries = []
    for building in building_set.buildings:
        geom = Polygon(building.base.coordinates)
        geometries.append({
            "geometry": geom,
            "elevation": building.elevation,
            "top": building.elevation + building.height
        })
    return geometries

def detect_clashes(building_set: CanonicalBuildingSet) -> List[CanonicalBuildingIntersection]:
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

    # Return the list of CanonicalBuildingIntersection objects (collisions)
    return collisions
