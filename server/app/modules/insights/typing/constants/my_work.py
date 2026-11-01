from collections.abc import Mapping

from app.modules.insights.typing.enums import MyWorkSection
from app.shared.permissions import ProjectRole

MAX_MY_WORK_ITEMS = 20
SECTIONS_BY_ROLE: Mapping[ProjectRole, tuple[MyWorkSection, ...]] = {
    ProjectRole.ADMIN: (MyWorkSection.CASES_TO_WRITE, MyWorkSection.FAILURES_TO_FIX, MyWorkSection.GAPS_TO_ANSWER),
    ProjectRole.QC: (MyWorkSection.CASES_TO_WRITE, MyWorkSection.GAPS_TO_ANSWER),
    ProjectRole.DEV: (MyWorkSection.FAILURES_TO_FIX, MyWorkSection.GAPS_TO_ANSWER),
    ProjectRole.BA: (MyWorkSection.GAPS_TO_ANSWER,),
    ProjectRole.PM: (MyWorkSection.GAPS_TO_ANSWER,),
    ProjectRole.VIEWER: (),
}
