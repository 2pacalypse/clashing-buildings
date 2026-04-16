from typing import List, Dict, Any
from shapely.geometry import shape, mapping

def detect_clashes(buildings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect 3D clashes between buildings and return as GeoJSON FeatureCollection.
    
    Expected input format:
    {
        "type": "Feature",
        "id": "building_0", 
        "properties": {"height": 4, "elevation": 0},
        "geometry": {"type": "Polygon", "coordinates": [...]}
    }
    
    Returns GeoJSON FeatureCollection with clash areas as features.
    """
    clash_features = []
    
    # Convert GeoJSON features to Shapely geometries with 3D bounds
    geometries = []
    for building in buildings:
        try:
            geom = shape(building.get("geometry", {}))
            height = building.get("properties", {}).get("height", 0)
            elevation = building.get("properties", {}).get("elevation", 0)
            geometries.append({
                "id": building.get("id"),
                "geometry": geom,
                "height": height,
                "elevation": elevation,
                "top": elevation + height
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
