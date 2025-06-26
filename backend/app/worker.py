import asyncio

from app.core.celery_app import celery_app
from app.services import match as match_service


@celery_app.task(name="app.worker.verify_match_result", acks_late=True)
def verify_match_result(match_id: int):
    """Celery task to run the automated match verification."""
    asyncio.run(match_service.automated_match_verification(match_id))
