
from fastapi import APIRouter, HTTPException
from app.models.clash_detection_response import ClashDetectionResponse
from app.models.clash_detection_request import ClashDetectionRequest
from app.exceptions import JobNotFoundError, ComplexityLimitExceededError
from app.services import clash_service

router = APIRouter()

@router.post(
    "/detect-clashes",
    response_model=ClashDetectionResponse,
    responses={400: {"description": "Complexity limit exceeded"}}
)
async def detect_clashes_endpoint(request: ClashDetectionRequest):
    try:
        return await clash_service.process_clash_detection(request)
    except ComplexityLimitExceededError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get(
    "/results/{job_id}",
    response_model=ClashDetectionResponse,
    responses={404: {"description": "Job not found"}}
)
async def get_results(job_id: str):
    try:
        return await clash_service.get_results(job_id)
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")




