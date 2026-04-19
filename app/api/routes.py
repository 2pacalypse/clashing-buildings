import json
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from httpx import request
from app.core.cache import get_cache, get_redis
from app.mappers.building_mapper import map_collisions_to_response
from app.models.clash_detection_response import (
    ClashDetectionResponse,
    ClashResultFeatureCollection,
)
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.job_status import JobStatus
from app.exceptions import JobNotFoundError
from app.services import clash_service
from tasks.celery_worker import celery_app

router = APIRouter()

@router.post("/detect-clashes", response_model=ClashDetectionResponse)
async def detect_clashes_endpoint(request: ClashDetectionRequest):
    return await clash_service.process_clash_detection(request)

@router.get("/results/{job_id}", response_model=ClashDetectionResponse)
async def get_results(job_id: str):
    try:
        return await clash_service.get_results(job_id)
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")




