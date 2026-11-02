from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.integrations.chat_channel_dependencies import (
    get_create_chat_channel,
    get_delete_chat_channel,
    get_list_chat_channels,
    get_send_chat_channel_test,
    get_update_chat_channel,
)
from app.modules.integrations.domains.chat_channel_change.entity import ChatChannelChange
from app.modules.integrations.domains.new_chat_channel.entity import NewChatChannel
from app.modules.integrations.models.chat_channel_response import ChatChannelResponse
from app.modules.integrations.models.create_chat_channel_request import CreateChatChannelRequest
from app.modules.integrations.models.update_chat_channel_request import UpdateChatChannelRequest
from app.modules.integrations.usecases.create_chat_channel import CreateChatChannelUseCase
from app.modules.integrations.usecases.delete_chat_channel import DeleteChatChannelUseCase
from app.modules.integrations.usecases.list_chat_channels import ListChatChannelsUseCase
from app.modules.integrations.usecases.send_chat_channel_test import SendChatChannelTestUseCase
from app.modules.integrations.usecases.update_chat_channel import UpdateChatChannelUseCase
from app.modules.integrations.utils.chat_channel_response import build_chat_channel_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

chat_channels_router = APIRouter(prefix="/api", tags=["chat-channels"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]
CHAT_CHANNELS_PATH = "/projects/{project_key}/chat-channels"
CHAT_CHANNEL_PATH = "/projects/{project_key}/chat-channels/{chat_channel_id}"


@chat_channels_router.get(CHAT_CHANNELS_PATH)
async def list_chat_channels(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListChatChannelsUseCase, Depends(get_list_chat_channels)],
) -> list[ChatChannelResponse]:
    return [build_chat_channel_response(chat_channel) for chat_channel in await use_case.execute(actor, project_key)]


@chat_channels_router.post(CHAT_CHANNELS_PATH, status_code=status.HTTP_201_CREATED)
async def create_chat_channel(
    project_key: str,
    body: CreateChatChannelRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateChatChannelUseCase, Depends(get_create_chat_channel)],
) -> ChatChannelResponse:
    new_chat_channel = NewChatChannel(
        kind=body.kind, name=body.name, webhook_url=body.webhook_url, events=body.events, is_active=body.is_active
    )
    return build_chat_channel_response(await use_case.execute(actor, project_key, new_chat_channel))


@chat_channels_router.patch(CHAT_CHANNEL_PATH)
async def update_chat_channel(
    project_key: str,
    chat_channel_id: UUID,
    body: UpdateChatChannelRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateChatChannelUseCase, Depends(get_update_chat_channel)],
) -> ChatChannelResponse:
    change = ChatChannelChange(
        name=body.name, webhook_url=body.webhook_url, events=body.events, is_active=body.is_active
    )
    return build_chat_channel_response(await use_case.execute(actor, project_key, chat_channel_id, change))


@chat_channels_router.delete(CHAT_CHANNEL_PATH, status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_channel(
    project_key: str,
    chat_channel_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[DeleteChatChannelUseCase, Depends(get_delete_chat_channel)],
) -> None:
    await use_case.execute(actor, project_key, chat_channel_id)


@chat_channels_router.post(f"{CHAT_CHANNEL_PATH}/test")
async def send_chat_channel_test(
    project_key: str,
    chat_channel_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[SendChatChannelTestUseCase, Depends(get_send_chat_channel_test)],
) -> ChatChannelResponse:
    return build_chat_channel_response(await use_case.execute(actor, project_key, chat_channel_id))
