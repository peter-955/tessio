from app.modules.shared_steps.domains.shared_step_detail.entity import SharedStepDetail
from app.modules.shared_steps.domains.shared_step_usage.entity import SharedStepUsage
from app.modules.shared_steps.domains.shared_step_version.entity import SharedStepVersion
from app.modules.shared_steps.models.shared_step_action_response import SharedStepActionResponse
from app.modules.shared_steps.models.shared_step_response import SharedStepResponse
from app.modules.shared_steps.models.shared_step_usage_response import SharedStepUsageResponse
from app.modules.shared_steps.models.shared_step_version_response import SharedStepVersionResponse


def build_shared_step_version_response(version: SharedStepVersion) -> SharedStepVersionResponse:
    return SharedStepVersionResponse(
        id=version.id,
        number=version.number,
        steps=[
            SharedStepActionResponse(order=step.order, action=step.action, expected=step.expected)
            for step in version.steps
        ],
        data_keys=version.data_keys,
        created_by=version.created_by,
        created_at=version.created_at,
    )


def build_shared_step_response(detail: SharedStepDetail) -> SharedStepResponse:
    shared_step = detail.shared_step
    return SharedStepResponse(
        id=shared_step.id,
        key=shared_step.key,
        title=shared_step.title,
        is_archived=shared_step.is_archived,
        archived_at=shared_step.archived_at,
        current_version=build_shared_step_version_response(detail.version),
        usage_count=detail.usage_count,
        created_by=shared_step.created_by,
        created_at=shared_step.created_at,
    )


def build_shared_step_usage_response(usage: SharedStepUsage) -> SharedStepUsageResponse:
    return SharedStepUsageResponse.model_validate(usage.model_dump())
