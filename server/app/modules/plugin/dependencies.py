from fastapi import Request

from app.modules.plugin.usecases.get_plugin_archive import GetPluginArchiveUseCase
from app.modules.plugin.usecases.get_plugin_marketplace import GetPluginMarketplaceUseCase


def get_get_plugin_marketplace(request: Request) -> GetPluginMarketplaceUseCase:
    use_case: GetPluginMarketplaceUseCase = request.app.state.container.get_plugin_marketplace
    return use_case


def get_get_plugin_archive(request: Request) -> GetPluginArchiveUseCase:
    use_case: GetPluginArchiveUseCase = request.app.state.container.get_plugin_archive
    return use_case
