from typing import Dict, Any
from shapely.geometry import Polygon, mapping
from app.models.canonical.buildings import CanonicalBuildingSet

def detect_clashes(building_set: CanonicalBuildingSet) -> Dict[str, Any]:
    """
    Detect 3D clashes between buildings using canonical building set model.
    
    Returns GeoJSON FeatureCollection with clash areas as features.
    """
    clash_features = []
    
    # Convert canonical buildings to Shapely geometries with 3D bounds
    geometries = []
    for idx, building in enumerate(building_set.buildings):
        try:
            # Create Shapely polygon from canonical polygon coordinates
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
    
    # Check for spatial overlaps and compute intersection geometries
    for i, geom1 in enumerate(geometries):
        for geom2 in geometries[i + 1:]:
            # Check 2D intersection
            if geom1["geometry"].intersects(geom2["geometry"]):
                # Check 3D overlap (elevation ranges)
                if not (geom1["top"] < geom2["elevation"] or geom2["top"] < geom1["elevation"]):
                    # Compute intersection polygon
                    intersection_geom = geom1["geometry"].intersection(geom2["geometry"])
                    
                    # Determine clash elevation and height
                    clash_elevation = max(geom1["elevation"], geom2["elevation"])
                    clash_top = min(geom1["top"], geom2["top"])
                    clash_height = clash_top - clash_elevation
                    
                    if clash_height > 0 and not intersection_geom.is_empty:
                        # Create feature for this clash
                        clash_feature = {
                            "type": "Feature",
                            "properties": {
                                "elevation": clash_elevation,
                                "height": clash_height,
                                "buildings": [geom1["id"], geom2["id"]]
                            },
                            "geometry": mapping(intersection_geom)
                        }
                        clash_features.append(clash_feature)
    
    return {
        "type": "FeatureCollection",
        "features": clash_features
    }
