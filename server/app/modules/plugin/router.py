from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from app.modules.plugin.dependencies import get_get_plugin_archive, get_get_plugin_marketplace
from app.modules.plugin.typing.constants import (
    PLUGIN_ARCHIVE_CACHE_CONTROL,
    PLUGIN_ARCHIVE_MEDIA_TYPE,
    PLUGIN_MARKETPLACE_CACHE_CONTROL,
    PLUGIN_MARKETPLACE_FILE_NAME,
    PLUGIN_ROUTE_PREFIX,
)
from app.modules.plugin.usecases.get_plugin_archive import GetPluginArchiveUseCase
from app.modules.plugin.usecases.get_plugin_marketplace import GetPluginMarketplaceUseCase

plugin_router = APIRouter(prefix=PLUGIN_ROUTE_PREFIX, tags=["plugin"], include_in_schema=False)


@plugin_router.get(f"/{PLUGIN_MARKETPLACE_FILE_NAME}")
async def get_plugin_marketplace(
    use_case: Annotated[GetPluginMarketplaceUseCase, Depends(get_get_plugin_marketplace)],
) -> JSONResponse:
    return JSONResponse(use_case.execute(), headers={"cache-control": PLUGIN_MARKETPLACE_CACHE_CONTROL})


@plugin_router.get("/{file_name}")
async def get_plugin_archive(
    file_name: str, use_case: Annotated[GetPluginArchiveUseCase, Depends(get_get_plugin_archive)]
) -> Response:
    bundle = use_case.execute(file_name)
    return Response(
        content=bundle.archive,
        media_type=PLUGIN_ARCHIVE_MEDIA_TYPE,
        headers={
            "cache-control": PLUGIN_ARCHIVE_CACHE_CONTROL,
            "content-disposition": f'attachment; filename="{bundle.file_name}"',
        },
    )
