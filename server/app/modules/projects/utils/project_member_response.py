from app.modules.projects.domains.member_profile.entity import MemberProfile
from app.modules.projects.models.project_member_response import ProjectMemberResponse


def build_project_member_response(member_profile: MemberProfile) -> ProjectMemberResponse:
    return ProjectMemberResponse(
        user_id=member_profile.user_id,
        name=member_profile.name,
        email=member_profile.email,
        user_status=member_profile.user_status,
        role=member_profile.role,
        added_at=member_profile.created_at,
    )
