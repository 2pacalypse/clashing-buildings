"""
STRtree-accelerated clash detection strategy using Shapely's spatial index.
"""

from typing import List
from shapely.geometry import Polygon
from shapely.strtree import STRtree

from app.algorithms.clash_detection_strategy import ClashDetectionStrategy
from app.models.canonical import (
    CanonicalBuilding,
    CanonicalBuildingIntersection,
    CanonicalBuildingSet,
    CanonicalPolygon,
)


class STRtreeClashDetection(ClashDetectionStrategy):
    """Clash detection strategy using Shapely's STRtree spatial index."""

    def detect_clashes(
        self,
        building_set: CanonicalBuildingSet,
    ) -> List[CanonicalBuildingIntersection]:
        """
        Detect 3D clashes using spatial indexing for 2D candidate filtering.
        
        Strategy:
        1. Build STRtree from all building footprints.
        2. For each building, query the tree to find candidates with overlapping bounding boxes.
        3. For each candidate pair, check 3D overlap and compute intersection geometry.
        4. Return all clashes found.
        """
        buildings = building_set.buildings
        if not buildings:
            return []

        # Build spatial index from all polygon footprints
        polygons = [b.base.polygon for b in buildings]
        tree = STRtree(polygons)
        
        collisions = []
        
        for i, b1 in enumerate(buildings):
            top1 = b1.elevation + b1.height
            
            # Query the tree for candidate indices that have overlapping bounding boxes
            candidate_indices = tree.query(b1.base.polygon)
            
            for j in candidate_indices:
                # Skip if this is a self-pair or duplicate pair (j should be > i)
                if j <= i:
                    continue
                
                b2 = buildings[j]
                top2 = b2.elevation + b2.height
                
                # Check 3D overlap (elevation ranges)
                if not (top1 < b2.elevation or top2 < b1.elevation):
                    # Compute the 2D intersection geometry
                    intersection_geom = b1.base.polygon.intersection(b2.base.polygon)
                    
                    # Compute clash elevation and height
                    clash_elevation = max(b1.elevation, b2.elevation)
                    clash_top = min(top1, top2)
                    clash_height = clash_top - clash_elevation
                    
                    # Only record if there is positive volume and valid geometry
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
