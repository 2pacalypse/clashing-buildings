from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.api.routes import router
from app.core.config import settings
from app.exceptions import AppException
from app.models.error_response import ErrorResponse
from app.core.error_codes import VALIDATION_ERROR_CODE

app = FastAPI(
    title="Building Clashes Detection API",
    description="Detect overlapping buildings in 3D space",
    version="1.0.0",
    docs_url=None,  # Disable default Swagger UI
    redoc_url=None  # Disable default ReDoc
)

# Exception handlers for structured error responses
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    error_response = ErrorResponse(
        code=exc.code,
        message=exc.message,
        details=exc.details if exc.details else None
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        code=VALIDATION_ERROR_CODE,
        message="Request validation failed",
        details={"errors": errors}
    )
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(exclude_none=True)
    )

app.include_router(router, prefix="/api/v1")

# Custom Swagger UI endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Building Clashes Detection API"
    )

@app.get("/openapi.json", include_in_schema=False)
async def openapi():
    return get_openapi(
        title="Building Clashes Detection API",
        version="1.0.0",
        description="Detect overlapping buildings in 3D space",
        routes=app.routes
    )
