from app.core.cache import get_cache, set_cache
from app.mappers.building_mapper import map_request_to_canonical
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.job_status import JobStatus
from app.models.schemas import ClashDetectionResponse
from app.models.canonical.buildings import CanonicalBuildingSet, CanonicalBuilding, CanonicalPolygon
from app.algorithms.clash_detector import detect_clashes
from app.utils.job_id_generator import generate_job_id


async def process_clash_detection(request: ClashDetectionRequest) -> ClashDetectionResponse:
    # Generate server-side job ID
    job_id = generate_job_id(request)
    
    # Check cache first
    cached_result = await get_cache(job_id)
    if cached_result:
        return ClashDetectionResponse(
             job_id=job_id,
             status=JobStatus.COMPLETED,
             result=cached_result,
             from_cache=True
         )
    
    # Convert GeoJSON features to canonical building set
    building_set, original_indices = map_request_to_canonical(request)
    
    # Process synchronously (for smaller inputs)
    # For larger inputs, integrate with Celery here
    result = detect_clashes(building_set)
    
    # Cache the result
    await set_cache(job_id, result)
    
    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        result=result,
        from_cache=False
    )
