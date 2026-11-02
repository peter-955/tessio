from datetime import datetime

from app.modules.api_tokens.domains.api_token_summary.entity import ApiTokenSummary
from app.modules.api_tokens.models.api_token_response import ApiTokenResponse


def build_api_token_response(summary: ApiTokenSummary, now: datetime) -> ApiTokenResponse:
    api_token = summary.api_token
    return ApiTokenResponse(
        id=api_token.id,
        name=api_token.name,
        prefix=api_token.prefix,
        project_id=api_token.project_id,
        project_key=summary.project_key,
        project_name=summary.project_name,
        status=api_token.resolve_status(now),
        scope=api_token.scope,
        expires_at=api_token.expires_at,
        last_used_at=api_token.last_used_at,
        plugin_version=api_token.plugin_version,
        revoked_at=api_token.revoked_at,
        created_at=api_token.created_at,
    )
