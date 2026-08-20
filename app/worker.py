import logging
import time

from app.db.session import SessionLocal
from app.services.scheduler_service import SchedulerService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("scheduler-worker")


POLL_INTERVAL_SECONDS = 5


def process_once() -> int:
    db = SessionLocal()

    try:
        scheduler = SchedulerService(db)
        processed = scheduler.process_due_records()

        if processed:
            logger.info(
                "Scheduler processed %s due record(s).",
                processed,
            )

        return processed

    except Exception:
        logger.exception("Scheduler iteration failed.")
        return 0

    finally:
        db.close()


def run_worker() -> None:
    logger.info("Scheduler worker started.")
    logger.info(
        "Polling every %s seconds.",
        POLL_INTERVAL_SECONDS,
    )

    while True:
        process_once()
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_worker()