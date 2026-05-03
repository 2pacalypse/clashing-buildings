"""
Naive pairwise clash detection strategy.
"""

from typing import List
from shapely.geometry import Polygon

from app.algorithms.clash_detection_strategy import ClashDetectionStrategy
from app.models.canonical import (
    CanonicalBuilding,
    CanonicalBuildingIntersection,
    CanonicalBuildingSet,
    CanonicalPolygon,
)


class NaiveClashDetection(ClashDetectionStrategy):
    """Pairwise clash detection strategy using a quadratic scan."""

    def detect_clashes(
        self,
        building_set: CanonicalBuildingSet,
    ) -> List[CanonicalBuildingIntersection]:
        """
        Detect 3D clashes between buildings using canonical building set model.
        Step 1: List all pairwise indices with collision and attributes.
        Step 2: Build GeoJSON output from those collisions.
        """
        collisions = []
        buildings = building_set.buildings
        buildings_len = len(buildings)
        for i in range(buildings_len):
            b1 = buildings[i]
            top1 = b1.elevation + b1.height
            for j in range(i + 1, buildings_len):
                b2 = buildings[j]
                top2 = b2.elevation + b2.height
                # Check 3D overlap (elevation ranges) first
                if not (top1 < b2.elevation or top2 < b1.elevation):
                    # Check 2D intersection
                    if b1.base.polygon.intersects(b2.base.polygon):
                        intersection_geom = b1.base.polygon.intersection(
                            b2.base.polygon
                        )
                        clash_elevation = max(b1.elevation, b2.elevation)
                        clash_top = min(top1, top2)
                        clash_height = clash_top - clash_elevation
                        if (
                            clash_height > 0
                            and not intersection_geom.is_empty
                            and isinstance(intersection_geom, Polygon)
                        ):
                            intersection_building = CanonicalBuilding(
                                elevation=clash_elevation,
                                height=clash_height,
                                base=CanonicalPolygon(polygon=intersection_geom),
                            )
                            intersection = CanonicalBuildingIntersection(
                                building_ids=(i, j),
                                intersection=intersection_building,
                            )
                            collisions.append(intersection)
        return collisions
