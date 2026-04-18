from app.core.cache import get_cache, set_cache
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.job_status import JobStatus
from app.models.schemas import ClashDetectionResponse
from app.services.clash_detector import detect_clashes


async def process_clash_detection(request: ClashDetectionRequest) -> ClashDetectionResponse:
    """
    Detect building clashes in 3D space.
    
    For large inputs that take >10s, returns a job_id for polling.
    """
    # Generate server-side job ID
    job_id = request.hash()
    
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
    buildings = [f.model_dump() for f in request.features]
    result = detect_clashes(buildings)
    
    # Cache the result
    await set_cache(job_id, result)
    
    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        result=result,
        from_cache=False
    )
