from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.api_tokens.dependencies import get_create_api_token, get_list_api_tokens, get_revoke_api_token
from app.modules.api_tokens.models.api_token_response import ApiTokenResponse
from app.modules.api_tokens.models.create_api_token_request import CreateApiTokenRequest
from app.modules.api_tokens.models.created_api_token_response import CreatedApiTokenResponse
from app.modules.api_tokens.usecases.create_api_token import CreateApiTokenUseCase
from app.modules.api_tokens.usecases.list_api_tokens import ListApiTokensUseCase
from app.modules.api_tokens.usecases.revoke_api_token import RevokeApiTokenUseCase
from app.modules.api_tokens.utils.api_token_response import build_api_token_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

api_tokens_router = APIRouter(prefix="/api/me/api-tokens", tags=["api-tokens"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@api_tokens_router.get("")
async def list_api_tokens(
    actor: SignedInActor,
    use_case: Annotated[ListApiTokensUseCase, Depends(get_list_api_tokens)],
) -> list[ApiTokenResponse]:
    summaries = await use_case.execute(actor)
    now = datetime.now(UTC)
    return [build_api_token_response(summary, now) for summary in summaries]


@api_tokens_router.post("", status_code=status.HTTP_201_CREATED)
async def create_api_token(
    body: CreateApiTokenRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateApiTokenUseCase, Depends(get_create_api_token)],
) -> CreatedApiTokenResponse:
    created_api_token = await use_case.execute(actor, body.project_key, body.name, body.expires_in_days)
    return CreatedApiTokenResponse(
        token=created_api_token.token,
        api_token=build_api_token_response(created_api_token.summary, datetime.now(UTC)),
    )


@api_tokens_router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_token(
    token_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[RevokeApiTokenUseCase, Depends(get_revoke_api_token)],
) -> None:
    await use_case.execute(actor, token_id)
