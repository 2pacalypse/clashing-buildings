from app.core.cache import get_cache, set_cache
from app.mappers.building_mapper import map_request_to_canonical, map_collisions_to_response
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.clash_detection_response import ClashDetectionResponse
from app.algorithms.clash_detector import detect_clashes
from app.utils.job_id_generator import generate_job_id


async def process_clash_detection(request: ClashDetectionRequest) -> ClashDetectionResponse:
    
    # Convert GeoJSON features to canonical building set
    building_set, original_indices = map_request_to_canonical(request)
    
    # Generate server-side job ID
    job_id = generate_job_id(building_set)
    
    # Check cache first for canonical collisions
    cached_collisions = await get_cache(job_id)

    collisions = None

    suitable_for_sync_process = True

    if cached_collisions is not None:
        collisions = cached_collisions
    else:
        if suitable_for_sync_process:
            # If the job is small enough, process synchronously
            collisions = detect_clashes(building_set)
            await set_cache(job_id, collisions)
        else:
            # For larger jobs, we would kick off an async background task here
            # and return a PENDING status immediately. The background task would
            # compute the collisions and store them in cache for later retrieval.
            pass

    
    # Retrieve original building IDs for the collisions
    buildings = [[request.features[original_indices[i]].id for i in c.building_ids] for c in collisions ]
    
    # Step 2: Convert collisions to GeoJSON output via mapper
    return map_collisions_to_response(
        collisions=collisions,
        buildings=buildings,
        job_id=job_id,
    )
