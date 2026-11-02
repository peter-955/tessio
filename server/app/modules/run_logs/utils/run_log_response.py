from app.modules.run_logs.domains.run_log_view.entity import RunLogView
from app.modules.run_logs.models.run_log_response import RunLogEntryResponse, RunLogResponse, RunLogUsageResponse


def build_run_log_response(view: RunLogView) -> RunLogResponse:
    run_log = view.run_log
    return RunLogResponse(
        received_at=None if run_log is None else run_log.received_at,
        is_cut=False if run_log is None else run_log.is_cut,
        usage=None
        if run_log is None
        else RunLogUsageResponse(
            input_tokens=run_log.input_tokens,
            cache_creation_input_tokens=run_log.cache_creation_input_tokens,
            cache_read_input_tokens=run_log.cache_read_input_tokens,
            output_tokens=run_log.output_tokens,
        ),
        entries=[
            RunLogEntryResponse(
                position=entry.position,
                phase=entry.phase,
                test_case_id=entry.test_case_id,
                kind=entry.kind,
                at=entry.at,
                tool=entry.tool,
                input=entry.input,
                output=entry.output,
                is_error=entry.is_error,
                duration_ms=entry.duration_ms,
            )
            for entry in view.entries
        ],
    )
