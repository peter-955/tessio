from fastapi import Request

from app.modules.integrations.usecases.create_chat_channel import CreateChatChannelUseCase
from app.modules.integrations.usecases.delete_chat_channel import DeleteChatChannelUseCase
from app.modules.integrations.usecases.list_chat_channels import ListChatChannelsUseCase
from app.modules.integrations.usecases.send_chat_channel_test import SendChatChannelTestUseCase
from app.modules.integrations.usecases.update_chat_channel import UpdateChatChannelUseCase


def get_list_chat_channels(request: Request) -> ListChatChannelsUseCase:
    use_case: ListChatChannelsUseCase = request.app.state.container.list_chat_channels
    return use_case


def get_create_chat_channel(request: Request) -> CreateChatChannelUseCase:
    use_case: CreateChatChannelUseCase = request.app.state.container.create_chat_channel
    return use_case


def get_update_chat_channel(request: Request) -> UpdateChatChannelUseCase:
    use_case: UpdateChatChannelUseCase = request.app.state.container.update_chat_channel
    return use_case


def get_delete_chat_channel(request: Request) -> DeleteChatChannelUseCase:
    use_case: DeleteChatChannelUseCase = request.app.state.container.delete_chat_channel
    return use_case


def get_send_chat_channel_test(request: Request) -> SendChatChannelTestUseCase:
    use_case: SendChatChannelTestUseCase = request.app.state.container.send_chat_channel_test
    return use_case
