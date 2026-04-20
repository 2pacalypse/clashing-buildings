
from fastapi import APIRouter
from app.models.clash_detection_response import ClashDetectionResponse
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.error_response import ErrorResponse
from app.services import clash_service

router = APIRouter()

@router.post(
    "/detect-clashes",
    response_model=ClashDetectionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Complexity limit exceeded"},
        422: {"model": ErrorResponse, "description": "Request validation failed"}
    }
)
async def detect_clashes_endpoint(request: ClashDetectionRequest):
    return await clash_service.process_clash_detection(request)

@router.get(
    "/results/{job_id}",
    response_model=ClashDetectionResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        422: {"model": ErrorResponse, "description": "Request validation failed"}
    }
)
async def get_results(job_id: str):
    return await clash_service.get_results(job_id)




