
import json
from app.core.cache import get_redis
from tasks.celery_worker import celery_app
from app.core.cache import claim_job, get_cache, set_cache, set_original_ids
from app.mappers.building_mapper import map_request_to_canonical, map_collisions_to_response
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.clash_detection_response import ClashDetectionResponse
from app.algorithms.clash_detector import detect_clashes
from app.models.job_status import JobStatus
from app.utils.job_id_generator import generate_job_id
from tasks.celery_worker import detect_clashes_task


async def process_clash_detection(request: ClashDetectionRequest) -> ClashDetectionResponse:
    
    # Convert GeoJSON features to canonical building set
    building_set, original_indices = map_request_to_canonical(request)
    
    # Generate server-side job ID
    job_id = generate_job_id(building_set)
    
    # Check cache first for canonical collisions
    cached_collisions = await get_cache(job_id)

    collisions = None

    # Calculate the number of buildings and total vertices
    n_buildings = len(building_set.buildings)
    n_vertices = sum(len(b.base.polygon.exterior.coords) for b in building_set.buildings)
    # Use the product as a proxy for complexity (O(n^2 * v)), threshold at 640,000
    suitable_for_sync_process = (n_buildings * n_vertices) <= 100_000

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

        await set_cache(job_id, collisions)

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
    original_ids = [request.features[idx].id for idx in original_indices]
    await set_original_ids(job_id, original_ids)

    # dispatch Celery task (pass serializable canonical dump + job_id)
    building_dump = building_set.model_dump()
    task = detect_clashes_task.apply_async(args=[building_dump, job_id])
    
    #???? await client.setex(f"job:{job_id}:task", settings.CACHE_TTL, task.id)

    
    # return PENDING immediately
    return ClashDetectionResponse(job_id=job_id, status=JobStatus.PENDING, result=None)



async def get_results(job_id: str) -> ClashDetectionResponse:
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