from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="Building Clashes Detection API",
    description="Detect overlapping buildings in 3D space",
    version="1.0.0",
    docs_url=None,  # Disable default Swagger UI
    redoc_url=None  # Disable default ReDoc
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "redis": settings.REDIS_HOST}
