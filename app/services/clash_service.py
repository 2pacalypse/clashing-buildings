from app.core.cache import get_cache, set_cache
from app.mappers.building_mapper import map_request_to_canonical
from app.models.clash_detection_request import ClashDetectionRequest, PolygonGeometry
from app.models.job_status import JobStatus
from app.models.clash_detection_response import ClashDetectionResponse, ClashFeature, ClashProperties, ClashResultFeatureCollection
from app.models.canonical.buildings import CanonicalBuildingSet, CanonicalBuilding, CanonicalPolygon
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

    if cached_collisions is not None:
        collisions = cached_collisions
    else:
        #todo: celery here
        collisions = detect_clashes(building_set)

        # Cache the result
        await set_cache(job_id, collisions)

    
    

    # Step 2: Convert collisions to GeoJSON output
    def _unquantize_coords(coords):
        SCALE = 10**6
        return [(x / SCALE, y / SCALE) for x, y in coords]

    
    clash_features = []
    for c in collisions:
        intersection_coords = _unquantize_coords(c.intersection.base.polygon.exterior.coords)
        clash_features.append(
            ClashFeature(
                type = "Feature",
                properties=ClashProperties(
                    elevation=c.intersection.elevation,
                    height=c.intersection.height,
                    buildings= [request.features[original_indices[i]].id for i in c.building_ids]
                ),
                geometry=PolygonGeometry(
                    type="Polygon",
                    coordinates=[intersection_coords]
                )
            )
        )

    result = ClashResultFeatureCollection(features=clash_features)

    return ClashDetectionResponse(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        result=result,
        from_cache=False,
        task_id=None
    )
