import asyncio
import signal

from app.config import get_settings
from app.container import Container
from app.shared.logging import configure_logging

STOP_SIGNALS = (signal.SIGINT, signal.SIGTERM)


async def run_worker() -> None:
    container = Container(get_settings())
    stop_requested = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signal_number in STOP_SIGNALS:
        loop.add_signal_handler(signal_number, stop_requested.set)
    job_workers = container.job_workers
    live_event_listener = container.live_event_listener
    try:
        await container.job_queue.replace_schedules(container.job_schedules)
        for job_worker in job_workers:
            job_worker.start()
        live_event_listener.start()
        await stop_requested.wait()
    finally:
        await live_event_listener.close()
        await asyncio.gather(*(job_worker.close() for job_worker in job_workers))
        await container.close()
        for signal_number in STOP_SIGNALS:
            loop.remove_signal_handler(signal_number)


def main() -> None:
    settings = get_settings()
    configure_logging(
        settings.observability.log_level, settings.observability.sentry_dsn, settings.observability.sentry_environment
    )
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
