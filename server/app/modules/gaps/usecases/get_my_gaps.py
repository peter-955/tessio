from uuid import UUID

from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_filter.entity import GapFilter
from app.modules.gaps.domains.gap_recipient.entity import GapRecipient
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.domains.my_gap.entity import MyGap
from app.modules.gaps.domains.my_gap_story.entity import MyGapStory
from app.modules.gaps.domains.my_gaps.entity import MyGaps
from app.modules.gaps.ports.gap_assignee_directory import GapAssigneeDirectory
from app.modules.gaps.ports.gap_target_reader import GapTargetReader
from app.modules.gaps.typing.constants import MAX_MY_GAPS, MAX_SIMILAR_ANSWERS
from app.modules.gaps.typing.enums import GapStatus, GapTargetType, GapType
from app.modules.gaps.utils.gap_search import build_search_terms
from app.modules.gaps.utils.my_gap_order import build_my_gap_sort_key
from app.modules.gaps.utils.test_data_url import build_test_data_url
from app.modules.stories import StoryNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class GetMyGapsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        gap_repository: GapRepository,
        gap_target_reader: GapTargetReader,
        gap_assignee_directory: GapAssigneeDirectory,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._gap_repository = gap_repository
        self._gap_target_reader = gap_target_reader
        self._gap_assignee_directory = gap_assignee_directory
        self._client_url = client_url

    async def execute_in_token_project(self, actor: Actor, story_key: str | None) -> MyGaps:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.GAP_ANSWER)
            story_id: UUID | None = None
            if story_key is not None:
                story = await self._gap_target_reader.find_story(access.project_id, story_key)
                if story is None:
                    raise StoryNotFoundError
                story_id = story.id
            views = await self._gap_repository.list_views(
                access.project_id,
                GapFilter(
                    story_id=story_id,
                    status=GapStatus.OPEN,
                    assigned_to=GapRecipient(user_id=actor.user_id, role=access.role),
                ),
            )
            shown_views = sorted(views, key=build_my_gap_sort_key)[:MAX_MY_GAPS]
            criterion_texts = await self._gap_target_reader.list_criterion_texts(
                self._list_target_ids(shown_views, GapTargetType.CRITERION)
            )
            cases = await self._gap_target_reader.list_cases(
                self._list_target_ids(shown_views, GapTargetType.TEST_CASE)
            )
            gaps = [
                MyGap(
                    view=view,
                    criterion_text=None if view.gap.target_id is None else criterion_texts.get(view.gap.target_id),
                    case=None if view.gap.target_id is None else cases.get(view.gap.target_id),
                    similar_answers=await self._gap_repository.list_similar_answers(
                        access.project_id,
                        view.gap.story_id,
                        build_search_terms(view.gap.question),
                        MAX_SIMILAR_ANSWERS,
                    ),
                )
                for view in shown_views
            ]
            open_counts = await self._gap_repository.count_open_by_story(
                frozenset(view.gap.story_id for view in shown_views)
            )
            assignees = await self._gap_assignee_directory.list_assignable_members(access.project_id)
        stories_by_id: dict[UUID, MyGapStory] = {}
        for view in shown_views:
            stories_by_id.setdefault(
                view.gap.story_id,
                MyGapStory(
                    id=view.gap.story_id,
                    jira_key=view.story_jira_key,
                    title=view.story_title,
                    open_gap_count=open_counts.get(view.gap.story_id, 0),
                ),
            )
        return MyGaps(
            gaps=gaps,
            gap_count=len(views),
            stories=sorted(stories_by_id.values(), key=lambda story: story.jira_key),
            assignees=assignees,
            test_data_url=(
                build_test_data_url(self._client_url, access.project_key)
                if any(view.gap.type is GapType.MISSING_TEST_DATA for view in shown_views)
                else None
            ),
        )

    @staticmethod
    def _list_target_ids(views: list[GapView], target_type: GapTargetType) -> frozenset[UUID]:
        return frozenset(
            view.gap.target_id
            for view in views
            if view.gap.target_type is target_type and view.gap.target_id is not None
        )
