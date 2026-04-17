import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.db import get_db
from app.models.schemas import (
    ClashDetectionResponse,
    ClashResultFeatureCollection,
)
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.job_status import JobStatus
from app.core.cache import get_cache, set_cache
from app.services.clash_detector import detect_clashes

router = APIRouter()

@router.post("/detect-clashes", response_model=ClashDetectionResponse)
async def detect_clashes_endpoint(request: ClashDetectionRequest):
    """
    Detect building clashes in 3D space.
    
    For large inputs that take >10s, returns a job_id for polling.
    """
    # Generate server-side job ID
    job_id = request.content_hash()
    
    # Check cache first
    # cached_result = await get_cache(content_hash)
    # if cached_result:
    #     return ClashDetectionResponse(
    #         job_id=job_id,
    #         status=JobStatus.COMPLETED,
    #         result=cached_result,
    #         from_cache=True
    #     )
    
    # Process synchronously (for smaller inputs)
    # For larger inputs, integrate with Celery here
    buildings = [f.model_dump() for f in request.features]
    result = detect_clashes(buildings)
    
    # Cache the result
    # await set_cache(content_hash, result)
    
    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        result=result,
        from_cache=False
    )

@router.get("/results/{job_id}", response_model=ClashDetectionResponse)
async def get_results(job_id: str):
    """Poll for job results (placeholder for async implementation)."""
    # TODO: Implement Redis-based job status polling
    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        result=None,
        from_cache=False,
        task_id=None
    )


@router.get("/db-test")
async def db_test():
    """Simple endpoint to verify DB connectivity by inserting a doc."""
    try:
        db = get_db()
        result = db.test_collection.insert_one({"test": "ok"})
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
