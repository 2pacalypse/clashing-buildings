import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from httpx import request
from app.core.db import get_db
from app.models.clash_detection_response import (
    ClashDetectionResponse,
    ClashResultFeatureCollection,
)
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.job_status import JobStatus
from app.services import clash_service

router = APIRouter()
#TODO: VALIDATIONS - max features, max vertices, valid GeoJSON structure, etc.

@router.post("/detect-clashes", response_model=ClashDetectionResponse)
async def detect_clashes_endpoint(request: ClashDetectionRequest):
    return await clash_service.process_clash_detection(request)

@router.get("/results/{job_id}", response_model=ClashDetectionResponse)
async def get_results(job_id: str):
    """Poll for job results (placeholder for async implementation)."""
    # TODO: Implement Redis-based job status polling
    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        result=None,
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
