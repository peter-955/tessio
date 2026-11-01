from uuid import UUID

from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion
from app.modules.test_cases.domains.case_import_preview_item.entity import CaseImportPreviewItem
from app.modules.test_cases.domains.case_story.entity import CaseStory
from app.shared.common import Entity


class CaseImportPlan(Entity):
    items: list[CaseImportPreviewItem]
    stories_by_key: dict[str, CaseStory]
    criteria_by_story_id: dict[UUID, list[CaseCriterion]]
