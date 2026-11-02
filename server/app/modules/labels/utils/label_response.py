from app.modules.labels.domains.label.entity import Label
from app.modules.labels.domains.label_summary.entity import LabelSummary
from app.modules.labels.models.case_label_response import CaseLabelResponse
from app.modules.labels.models.label_response import LabelResponse


def build_label_response(summary: LabelSummary) -> LabelResponse:
    return LabelResponse(
        id=summary.label.id,
        name=summary.label.name,
        color=summary.label.color,
        case_count=summary.case_count,
        created_at=summary.label.created_at,
    )


def build_case_label_response(label: Label) -> CaseLabelResponse:
    return CaseLabelResponse(id=label.id, name=label.name, color=label.color)
