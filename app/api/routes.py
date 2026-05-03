"""
API route definitions for clash detection endpoints.
Includes endpoints for detecting clashes and retrieving results.
"""

from fastapi import APIRouter, Depends
import redis.asyncio as redis
from app.models.clash_detection_response import ClashDetectionResponse
from app.models.clash_detection_request import ClashDetectionRequest
from app.models.error_response import ErrorResponse
from app.services import clash_service
from app.api.dependencies import get_redis

router = APIRouter()


@router.post(
    "/detect-clashes",
    response_model=ClashDetectionResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Bad Request - code: COMPLEXITY_LIMIT_EXCEEDED",
        },
        422: {
            "model": ErrorResponse,
            "description": "Unprocessable Entity - code: VALIDATION_ERROR",
        },
    },
)
async def detect_clashes_endpoint(
    request: ClashDetectionRequest, redis_client: redis.Redis = Depends(get_redis)
):
    """
    Endpoint to process a clash detection request.
    Accepts a ClashDetectionRequest and returns a ClashDetectionResponse.
    """
    return await clash_service.process_clash_detection(request, redis_client)


@router.get(
    "/results/{request_id}",
    response_model=ClashDetectionResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Not Found - code: JOB_NOT_FOUND"},
        422: {
            "model": ErrorResponse,
            "description": "Unprocessable Entity - code: VALIDATION_ERROR",
        },
    },
)
async def get_results(request_id: str, redis_client: redis.Redis = Depends(get_redis)):
    """
    Endpoint to retrieve clash detection results for a given request ID.
    Returns a ClashDetectionResponse with the job status and result if available.
    """
    return await clash_service.get_results(request_id, redis_client)
