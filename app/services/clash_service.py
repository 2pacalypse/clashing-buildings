import uuid
from app.exceptions import AppException
from app.core.error_codes import JOB_NOT_FOUND_CODE, REQUEST_NOT_FOUND_CODE, COMPLEXITY_LIMIT_EXCEEDED_CODE
from app.services.clash_cache import (
    get_clash_results, set_clash_results, claim_job, set_canonical_building_names, get_canonical_building_names, job_exists,
    get_request_job_id,get_request_building_names, set_request_job_id, set_request_building_names, set_request_original_indices, get_request_original_indices
)
from app.mappers.building_mapper import map_request_to_canonical, map_collisions_to_response
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.clash_detection_response import ClashDetectionResponse
from app.algorithms.clash_detector import detect_clashes
from app.models.job_status import JobStatus
from app.utils.job_id_generator import generate_job_id

from app.core.constants import SYNC_CLASH_COMPLEXITY_THRESHOLD, MAX_CLASH_COMPLEXITY_THRESHOLD
from app.tasks.celery_worker import detect_clashes_task

async def process_clash_detection(request: ClashDetectionRequest) -> ClashDetectionResponse:
    # Calculate the complexity
    n_buildings = len(request.features)
    n_vertices = sum(len(f.geometry.coordinates[0]) for f in request.features)
    complexity = n_buildings * n_vertices

    # Fail fast if too complex
    if complexity > MAX_CLASH_COMPLEXITY_THRESHOLD:
        raise AppException(
            code=COMPLEXITY_LIMIT_EXCEEDED_CODE,
            message=f"Complexity ({complexity}) exceeds the maximum allowed threshold ({MAX_CLASH_COMPLEXITY_THRESHOLD})",
            details={"complexity": complexity, "max_threshold": MAX_CLASH_COMPLEXITY_THRESHOLD},
            status_code=400
        )
    
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    
    # Convert GeoJSON features to canonical building set
    building_set, original_indices = map_request_to_canonical(request)
    original_building_names = [request.features[idx].id for idx in original_indices]
    
    # Generate server-side job ID
    job_id = generate_job_id(building_set)

    # Store the mapping in cache
    await set_request_job_id(request_id, job_id)
    #await set_request_original_indices(request_id, original_indices)
    await set_request_building_names(request_id, original_building_names)


    # Check cache first for canonical collisions
    cached_collisions = await get_clash_results(job_id)
    if cached_collisions is not None:
        # Retrieve original building IDs for the collisions
        buildings = [[request.features[original_indices[i]].id for i in c.building_ids] for c in cached_collisions ]
        # Step 2: Convert collisions to GeoJSON output via mapper
        return map_collisions_to_response(
            collisions=cached_collisions,
            buildings=buildings,
            request_id=request_id,
        )
    

    suitable_for_sync_process = complexity <= SYNC_CLASH_COMPLEXITY_THRESHOLD

    # process sync if low complexity
    if suitable_for_sync_process:
        collisions = detect_clashes(building_set)

        # Store results in cache for retrieval via results endpoint
        await set_clash_results(job_id, collisions)

        buildings = [[request.features[original_indices[i]].id for i in c.building_ids] for c in collisions ]

        # Step 2: Convert collisions to GeoJSON output via mapper
        return map_collisions_to_response(
            collisions=collisions,
            buildings=buildings,
            request_id=request_id,
        )
        

    # Request not in cache and too big for sync processing
    
    # Claim job for async processing
    claimed = await claim_job(job_id)
    
    if not claimed:
        # Another process is already working on this job, return PENDING
        return ClashDetectionResponse(
            request_id=request_id,
            status=JobStatus.PENDING,
            result=None,
        )


    # dispatch Celery task (pass serializable canonical dump + job_id)
    building_dump = building_set.model_dump()
    detect_clashes_task.apply_async(args=[building_dump, job_id])

    # return PENDING immediately
    return ClashDetectionResponse(request_id=request_id, status=JobStatus.PENDING, result=None)



async def get_results(request_id: str) -> ClashDetectionResponse:
    # Check if there is a job for this request
    job_id = await get_request_job_id(request_id)
    if job_id is None:
        raise AppException(
            code=REQUEST_NOT_FOUND_CODE,
            message="Request not found for the given request ID",
            details={"request_id": request_id},
            status_code=404
        )
    
    # Check if results are cached
    cached = await get_clash_results(job_id)
    if cached is not None:
        #original_indices = await get_request_original_indices(request_id)
        building_names = await get_request_building_names(request_id)

        buildings = [[building_names[i] for i in c.building_ids] for c in cached]
        return map_collisions_to_response(collisions=cached, buildings=buildings, request_id=request_id)

    # Check if job exists (was ever claimed/submitted)
    exists = await job_exists(job_id)
    if not exists:
        raise AppException(
            code=JOB_NOT_FOUND_CODE,
            message="Job not found",
            details={"job_id": job_id},
            status_code=404
        )

    # Results not cached yet — job is still queued/processing
    return ClashDetectionResponse(request_id=request_id, status=JobStatus.PENDING, result=None)