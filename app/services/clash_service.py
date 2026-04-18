from app.core.cache import get_cache, set_cache
from app.mappers.building_mapper import map_request_to_canonical
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.job_status import JobStatus
from app.models.schemas import ClashDetectionResponse
from app.models.canonical.buildings import CanonicalBuildingSet, CanonicalBuilding, CanonicalPolygon
from app.algorithms.clash_detector import detect_clashes
from app.utils.job_id_generator import generate_job_id


async def process_clash_detection(request: ClashDetectionRequest) -> ClashDetectionResponse:
    
    # Convert GeoJSON features to canonical building set
    building_set, original_indices = map_request_to_canonical(request)
    
    # Generate server-side job ID
    job_id = generate_job_id(building_set)
    
    # Check cache first
    cached_result = await get_cache(job_id)
    if cached_result:
        return ClashDetectionResponse(
             job_id=job_id,
             status=JobStatus.COMPLETED,
             result=cached_result,
             from_cache=True
         )
    

    # Process synchronously (for smaller inputs)
    # For larger inputs, integrate with Celery here
    collisions = detect_clashes(building_set)

    # Step 2: Convert collisions to GeoJSON output
    from shapely.geometry import Polygon, mapping
    def _unquantize_coords(coords):
        SCALE = 10**6
        return [(x / SCALE, y / SCALE) for x, y in coords]

    clash_features = []
    for c in collisions:
        intersection_coords = _unquantize_coords(c.intersection.base.coordinates)
        intersection_geom = Polygon(intersection_coords)
        clash_features.append({
            "type": "Feature",
            "properties": {
                "elevation": c.intersection.elevation,
                "height": c.intersection.height,
                "buildingIds": list(map(str, c.building_ids))
            },
            "geometry": mapping(intersection_geom)
        })

    result = {
        "type": "FeatureCollection",
        "features": clash_features
    }

    # Cache the result
    await set_cache(job_id, result)
    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        result=result,
        from_cache=False
    )
