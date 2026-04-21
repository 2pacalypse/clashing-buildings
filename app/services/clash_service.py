
from app.exceptions import AppException
from app.core.error_codes import JOB_NOT_FOUND_CODE, COMPLEXITY_LIMIT_EXCEEDED_CODE
from app.services.clash_cache import (
    get_clash_results, set_clash_results, claim_job, set_canonical_building_names, get_canonical_building_names, job_exists
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
    
    # Convert GeoJSON features to canonical building set
    building_set, original_indices = map_request_to_canonical(request)
    
    # Generate server-side job ID
    job_id = generate_job_id(building_set)
    
    # Check cache first for canonical collisions
    cached_collisions = await get_clash_results(job_id)

    collisions = None

    # Calculate the number of buildings and total vertices
    n_buildings = len(building_set.buildings)
    n_vertices = sum(len(b.base.polygon.exterior.coords) for b in building_set.buildings)
    complexity = n_buildings * n_vertices
    if complexity > MAX_CLASH_COMPLEXITY_THRESHOLD:
        raise AppException(
            code=COMPLEXITY_LIMIT_EXCEEDED_CODE,
            message=f"Complexity ({complexity}) exceeds the maximum allowed threshold ({MAX_CLASH_COMPLEXITY_THRESHOLD})",
            details={"complexity": complexity, "max_threshold": MAX_CLASH_COMPLEXITY_THRESHOLD},
            status_code=400
        )
    suitable_for_sync_process = complexity <= SYNC_CLASH_COMPLEXITY_THRESHOLD

    if cached_collisions is not None:
        collisions = cached_collisions
        # Retrieve original building IDs for the collisions
        buildings = [[request.features[original_indices[i]].id for i in c.building_ids] for c in collisions ]
    
        # Step 2: Convert collisions to GeoJSON output via mapper
        return map_collisions_to_response(
            collisions=collisions,
            buildings=buildings,
            job_id=job_id,
        )
    
    if suitable_for_sync_process:
        # If the job is small enough, process synchronously
        collisions = detect_clashes(building_set)
        buildings = [[request.features[original_indices[i]].id for i in c.building_ids] for c in collisions ]

        # Store both results and mapping for consistency with async path
        await set_clash_results(job_id, collisions)
        building_names = [request.features[idx].id for idx in original_indices]
        await set_canonical_building_names(job_id, building_names)

        # Step 2: Convert collisions to GeoJSON output via mapper
        return map_collisions_to_response(
            collisions=collisions,
            buildings=buildings,
            job_id=job_id,
        )
        

    claimed = await claim_job(job_id)
    
    if not claimed:
        # Another process is already working on this job, return PENDING
        return ClashDetectionResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            result=None,
        )

     # we claimed it: store canonical->original id mapping for later mapping
    building_names = [request.features[idx].id for idx in original_indices]
    await set_canonical_building_names(job_id, building_names)

    # dispatch Celery task (pass serializable canonical dump + job_id)
    building_dump = building_set.model_dump()
    detect_clashes_task.apply_async(args=[building_dump, job_id])

    # return PENDING immediately
    return ClashDetectionResponse(job_id=job_id, status=JobStatus.PENDING, result=None)



async def get_results(job_id: str) -> ClashDetectionResponse:
    # Check if results are cached
    cached = await get_clash_results(job_id)
    if cached is not None:
        building_names = await get_canonical_building_names(job_id)
        buildings = [[building_names[i] for i in c.building_ids] for c in cached]
        return map_collisions_to_response(collisions=cached, buildings=buildings, job_id=job_id)

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
    return ClashDetectionResponse(job_id=job_id, status=JobStatus.PENDING, result=None)