from celery import Celery
from app.algorithms.clash_detector import detect_clashes
from app.services.clash_cache import set_clash_results_sync
from app.core.config import settings
from app.models.canonical import CanonicalBuildingSet

celery_app = Celery(
    "clash_detector",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_time_limit=120,
)


@celery_app.task(name="detect_clashes_task")
def detect_clashes_task(buildings_dump: dict, job_id: str):
    """Async task for clash detection."""

    # Reconstruct canonical model and compute collisions
    building_set = CanonicalBuildingSet.model_validate(buildings_dump)
    collisions = detect_clashes(building_set)

    # Cache the results
    set_clash_results_sync(job_id, collisions)
