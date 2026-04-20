
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
        400: {"model": ErrorResponse, "description": "Bad Request - code: COMPLEXITY_LIMIT_EXCEEDED"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity - code: VALIDATION_ERROR"}
    }
)
async def detect_clashes_endpoint(request: ClashDetectionRequest):
    return await clash_service.process_clash_detection(request)

@router.get(
    "/results/{job_id}",
    response_model=ClashDetectionResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Not Found - code: JOB_NOT_FOUND"},
        422: {"model": ErrorResponse, "description": "Unprocessable Entity - code: VALIDATION_ERROR"}
    }
)
async def get_results(job_id: str):
    return await clash_service.get_results(job_id)




