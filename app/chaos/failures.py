import logging

from fastapi import HTTPException

from app.chaos.config import (
    ENABLE_FAILURES,
    FAILURE_PROBABILITY,
    random_event
)

logger = logging.getLogger(__name__)


def inject_random_failure():

    if not ENABLE_FAILURES:
        return

    if random_event(FAILURE_PROBABILITY):

        logger.error(
            "synthetic_failure_injected",
            extra={
                "event": "synthetic_failure",
                "failure_type": "random_500"
            }
        )

        raise HTTPException(
            status_code=500,
            detail="Synthetic chaos failure"
        )
