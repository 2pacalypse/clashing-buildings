from typing import List, Dict, Any
from shapely.geometry import shape, mapping

def detect_clashes(buildings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect 3D clashes between buildings.
    
    Expected input format:
    {
        "type": "Feature",
        "id": "building_0",
        "properties": {"height": 4, "elevation": 0},
        "geometry": {"type": "Polygon", "coordinates": [...]}
    }
    """
    clashes = []
    
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
    
    # Check for spatial overlaps
    for i, geom1 in enumerate(geometries):
        for geom2 in geometries[i + 1:]:
            # Check 2D intersection
            if geom1["geometry"].intersects(geom2["geometry"]):
                # Check 3D overlap (elevation ranges)
                if not (geom1["top"] < geom2["elevation"] or geom2["top"] < geom1["elevation"]):
                    clashes.append({
                        "building_1": geom1["id"],
                        "building_2": geom2["id"],
                        "type": "3D_overlap"
                    })
    
    return {
        "total_clashes": len(clashes),
        "clashes": clashes
    }
