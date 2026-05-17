import random
import asyncio
import logging

from app.chaos.config import (
    ENABLE_LATENCY,
    LATENCY_PROBABILITY,
    MIN_LATENCY,
    MAX_LATENCY,
    random_event
)

logger = logging.getLogger(__name__)


async def inject_latency():

    if not ENABLE_LATENCY:
        return

    if random_event(LATENCY_PROBABILITY):

        delay = random.uniform(MIN_LATENCY, MAX_LATENCY)

        logger.warning(
            "synthetic_latency_injected",
            extra={
                "event": "synthetic_latency",
                "delay_seconds": delay
            }
        )

        await asyncio.sleep(delay)
