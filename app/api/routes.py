import json
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from httpx import request
from app.core.cache import get_cache, get_redis
from app.core.db import get_db
from app.mappers.building_mapper import map_collisions_to_response
from app.models.clash_detection_response import (
    ClashDetectionResponse,
    ClashResultFeatureCollection,
)
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.job_status import JobStatus
from app.services import clash_service
from tasks.celery_worker import celery_app

router = APIRouter()
#TODO: VALIDATIONS - max features, max vertices, valid GeoJSON structure, etc.

@router.post("/detect-clashes", response_model=ClashDetectionResponse)
async def detect_clashes_endpoint(request: ClashDetectionRequest):
    return await clash_service.process_clash_detection(request)

@router.get("/results/{job_id}", response_model=ClashDetectionResponse)
async def get_results(job_id: str):
    cached = await get_cache(job_id)
    client = await get_redis()
    if cached is not None:
        mapping_raw = await client.get(f"job:{job_id}:mapping")
        original_ids = json.loads(mapping_raw) if mapping_raw else None
        if original_ids:
            buildings = [[original_ids[i] for i in c.building_ids] for c in cached]
        else:
            buildings = [[str(i) for i in c.building_ids] for c in cached]
        return map_collisions_to_response(collisions=cached, buildings=buildings, job_id=job_id)

    # not cached — check status / task
    status = await client.get(f"job:{job_id}:status")
    if status == "processing":
        return ClashDetectionResponse(job_id=job_id, status=JobStatus.PENDING, result=None)

    task_id = await client.get(f"job:{job_id}:task")
    if task_id:
        state = celery_app.AsyncResult(task_id).state
        if state == "FAILURE":
            return ClashDetectionResponse(job_id=job_id, status=JobStatus.FAILED, result=None)
        return ClashDetectionResponse(job_id=job_id, status=JobStatus.PENDING, result=None)

    # unknown job -> still return PENDING (or 404 if you prefer)
    return ClashDetectionResponse(job_id=job_id, status=JobStatus.PENDING, result=None)


@router.get("/db-test")
async def db_test():
    """Simple endpoint to verify DB connectivity by inserting a doc."""
    try:
        db = get_db()
        result = db.test_collection.insert_one({"test": "ok"})
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
