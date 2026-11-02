from collections.abc import Mapping, Sequence
from uuid import UUID

from app.modules.gaps.domains.gap_route.entity import GapRoute
from app.modules.gaps.errors import GapRouteNotSingleError, ViewerRouteError
from app.modules.gaps.typing.constants import ENVIRONMENT_DATA_ROLE, FALLBACK_ROLE, ROUTED_ROLE_BY_GAP_TYPE
from app.modules.gaps.typing.enums import GapDataScope, GapType
from app.shared.permissions import ProjectRole


def resolve_routed_role(gap_type: GapType, data_scope: GapDataScope | None) -> ProjectRole:
    if gap_type is GapType.MISSING_TEST_DATA and data_scope is GapDataScope.ENVIRONMENT:
        return ENVIRONMENT_DATA_ROLE
    return ROUTED_ROLE_BY_GAP_TYPE[gap_type]


def choose_gap_route(routed_role: ProjectRole, active_member_ids: Mapping[ProjectRole, Sequence[UUID]]) -> GapRoute:
    for role in (routed_role, FALLBACK_ROLE):
        member_ids = active_member_ids.get(role, ())
        if len(member_ids) == 1:
            return GapRoute(assignee_id=member_ids[0], assignee_role=None)
        if member_ids:
            return GapRoute(assignee_id=None, assignee_role=role)
    return GapRoute(assignee_id=None, assignee_role=FALLBACK_ROLE)


def build_requested_gap_route(assignee_id: UUID | None, assignee_role: ProjectRole | None) -> GapRoute:
    if (assignee_id is None) == (assignee_role is None):
        raise GapRouteNotSingleError
    if assignee_role is ProjectRole.VIEWER:
        raise ViewerRouteError
    return GapRoute(assignee_id=assignee_id, assignee_role=assignee_role)
