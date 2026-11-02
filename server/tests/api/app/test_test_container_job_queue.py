from app.container import Container
from app.shared.typing.enums import JobName, QueueName
from tests.support.recording_job_queue import RecordedJob, RecordingJobQueue


async def test_test_container_records_jobs_instead_of_using_redis(
    container: Container, recording_job_queue: RecordingJobQueue
) -> None:
    await container.job_queue.add(QueueName.MAINTENANCE, JobName.RUNS_ABORT_STALE, {"marker": "test"}, job_id="job-1")

    assert container.job_queue is recording_job_queue
    assert recording_job_queue.jobs == [
        RecordedJob(
            queue_name=QueueName.MAINTENANCE,
            job_name=JobName.RUNS_ABORT_STALE,
            data={"marker": "test"},
            job_id="job-1",
        )
    ]
