import uuid
import asyncio
import redis.asyncio as redis
from celery.result import AsyncResult
from app.exceptions import AppException
from app.core.error_codes import (
    JOB_NOT_FOUND_CODE,
    REQUEST_NOT_FOUND_CODE,
    COMPLEXITY_LIMIT_EXCEEDED_CODE,
)
from app.services.clash_cache import (
    get_task_id,
    try_claim_job,
    store_task_id,
)
from app.services.request_cache import (
    get_request_job_id,
    get_request_building_names,
    set_request_job_id,
    set_request_building_names,
)
from app.mappers.building_mapper import (
    map_request_to_canonical,
    map_collisions_to_response,
)
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.clash_detection_response import ClashDetectionResponse
from app.models.canonical import CanonicalBuildingIntersection
from app.models.job_status import JobStatus
from app.utils.job_id_generator import generate_job_id

from app.core.constants import (
    MAX_CLASH_COMPLEXITY_THRESHOLD,
    POLL_TIMEOUT_SECONDS,
    POLL_INTERVAL_SECONDS,
)
from app.tasks.celery_worker import detect_clashes_task, celery_app


async def process_clash_detection(
    request: ClashDetectionRequest,
    redis_client: redis.Redis,
) -> ClashDetectionResponse:
    # Calculate the complexity
    n_buildings = len(request.features)
    n_vertices = sum(len(f.geometry.coordinates[0]) for f in request.features)
    complexity = n_buildings * n_vertices

    # Fail fast if too complex
    if complexity > MAX_CLASH_COMPLEXITY_THRESHOLD:
        raise AppException(
            code=COMPLEXITY_LIMIT_EXCEEDED_CODE,
            message=f"Complexity ({complexity}) exceeds the maximum allowed threshold ({MAX_CLASH_COMPLEXITY_THRESHOLD})",
            details={
                "complexity": complexity,
                "max_threshold": MAX_CLASH_COMPLEXITY_THRESHOLD,
            },
            status_code=400,
        )

    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Convert GeoJSON features to canonical building set
    building_set, original_indices = map_request_to_canonical(request)
    original_building_names = [request.features[idx].id for idx in original_indices]

    # Generate server-side job ID
    job_id = generate_job_id(building_set)

    # Store the mapping in cache
    await set_request_job_id(redis_client, request_id, job_id)
    await set_request_building_names(redis_client, request_id, original_building_names)

    # Try to claim the job atomically (only first request succeeds)
    claimed = await try_claim_job(redis_client, job_id)

    if claimed:
        # We got the lock - dispatch the task
        building_dump = building_set.model_dump()
        task = detect_clashes_task.apply_async(args=[building_dump])
        # Store the actual task_id (overwrites the "processing" placeholder)
        await store_task_id(redis_client, job_id, task.id)
        task_id = task.id
    else:
        # Another request claimed it - fetch their task_id
        task_id = await get_task_id(redis_client, job_id)

    # Poll for results up to POLL_TIMEOUT_SECONDS
    for attempt in range(POLL_TIMEOUT_SECONDS):
        # If task_id is "processing" placeholder, job was claimed but task not dispatched yet
        if task_id == "processing":
            # Task ID not ready yet, wait and retry
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            task_id = await get_task_id(redis_client, job_id)
            continue

        task_result = AsyncResult(task_id, app=celery_app)
        if task_result.ready():
            # Task completed - retrieve results from Celery backend
            collisions_data = task_result.get()
            # Deserialize from dicts back to models
            collisions = [
                CanonicalBuildingIntersection.model_validate(item)
                for item in collisions_data
            ]

            buildings = [
                [request.features[original_indices[i]].id for i in c.building_ids]
                for c in collisions
            ]
            return map_collisions_to_response(
                collisions=collisions,
                buildings=buildings,
                request_id=request_id,
            )

        # Wait before next poll
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
        task_id = await get_task_id(redis_client, job_id)

    # Timeout - results not ready yet
    return ClashDetectionResponse(
        request_id=request_id, status=JobStatus.PENDING, result=None
    )


async def get_results(
    request_id: str, redis_client: redis.Redis
) -> ClashDetectionResponse:
    # Check if there is a job for this request
    job_id = await get_request_job_id(redis_client, request_id)
    if job_id is None:
        raise AppException(
            code=REQUEST_NOT_FOUND_CODE,
            message="Request not found for the given request ID",
            details={"request_id": request_id},
            status_code=404,
        )

    # Check if task is still processing
    task_id = await get_task_id(redis_client, job_id)
    if task_id is None:
        raise AppException(
            code=JOB_NOT_FOUND_CODE,
            message="Job not found",
            details={"job_id": job_id},
            status_code=404,
        )

    # If task_id is "processing" placeholder, job was claimed but task not dispatched yet
    if task_id == "processing":
        return ClashDetectionResponse(
            request_id=request_id, status=JobStatus.PENDING, result=None
        )

    # Check task status
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        # Task completed - retrieve results from Celery backend
        collisions_data = task_result.get()
        # Deserialize from dicts back to models
        collisions = [
            CanonicalBuildingIntersection.model_validate(item)
            for item in collisions_data
        ]

        building_names = await get_request_building_names(redis_client, request_id)
        buildings = [[building_names[i] for i in c.building_ids] for c in collisions]
        return map_collisions_to_response(
            collisions=collisions, buildings=buildings, request_id=request_id
        )

    # Task still processing
    return ClashDetectionResponse(
        request_id=request_id, status=JobStatus.PENDING, result=None
    )
