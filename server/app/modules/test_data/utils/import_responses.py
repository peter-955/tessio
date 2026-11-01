from app.modules.test_data.domains.import_preview.entity import ImportPreview
from app.modules.test_data.domains.import_result.entity import ImportResult
from app.modules.test_data.models.import_preview_item_response import ImportPreviewItemResponse
from app.modules.test_data.models.import_preview_response import ImportPreviewResponse
from app.modules.test_data.models.import_result_response import ImportResultResponse
from app.modules.test_data.models.import_skip_response import ImportSkipResponse


def build_import_preview_response(preview: ImportPreview) -> ImportPreviewResponse:
    return ImportPreviewResponse(
        format=preview.format,
        items=[
            ImportPreviewItemResponse(key=item.key, kind=item.kind, value=item.value, action=item.action)
            for item in preview.items
        ],
        skipped=[ImportSkipResponse(location=skip.location, reason=skip.reason) for skip in preview.skipped],
    )


def build_import_result_response(result: ImportResult) -> ImportResultResponse:
    return ImportResultResponse(created=result.created, updated=result.updated, unchanged=result.unchanged)
