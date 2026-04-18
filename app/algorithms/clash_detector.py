from typing import Dict, Any, List
from shapely.geometry import Polygon, mapping
from app.models.canonical import CanonicalBuilding, CanonicalBuildingSet, CanonicalBuildingIntersection, CanonicalPolygon



def detect_clashes(building_set: CanonicalBuildingSet) -> List[CanonicalBuildingIntersection]:
    """
    Detect 3D clashes between buildings using canonical building set model.
    Step 1: List all pairwise indices with collision and attributes.
    Step 2: Build GeoJSON output from those collisions.
    """
    collisions = []
    buildings = building_set.buildings
    for i, b1 in enumerate(buildings):
        top1 = b1.elevation + b1.height
        for j, b2 in enumerate(buildings[i + 1:], start=i + 1):
            # Check 2D intersection
            if b1.base.polygon.intersects(b2.base.polygon):
                # Check 3D overlap (elevation ranges)
                top2 = b2.elevation + b2.height
                if not (top1 < b2.elevation or top2 < b1.elevation):
                    intersection_geom = b1.base.polygon.intersection(b2.base.polygon)
                    clash_elevation = max(b1.elevation, b2.elevation)
                    clash_top = min(top1, top2)
                    clash_height = clash_top - clash_elevation
                    if clash_height > 0 and not intersection_geom.is_empty:
                        intersection_building = CanonicalBuilding(
                            elevation=clash_elevation,
                            height=clash_height,
                            base=CanonicalPolygon(polygon=intersection_geom)
                        )
                        intersection = CanonicalBuildingIntersection(
                            building_ids=(i, j),
                            intersection=intersection_building
                        )
                        collisions.append(intersection)
    return collisions
