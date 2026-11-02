from fastapi import Request

from app.modules.stories.usecases.change_test_status import ChangeTestStatusUseCase
from app.modules.stories.usecases.create_written_story import CreateWrittenStoryUseCase
from app.modules.stories.usecases.delete_written_story import DeleteWrittenStoryUseCase
from app.modules.stories.usecases.get_sprint import GetSprintUseCase
from app.modules.stories.usecases.get_story import GetStoryUseCase
from app.modules.stories.usecases.get_sync_status import GetSyncStatusUseCase
from app.modules.stories.usecases.list_sprints import ListSprintsUseCase
from app.modules.stories.usecases.list_stories import ListStoriesUseCase
from app.modules.stories.usecases.request_jira_sync import RequestJiraSyncUseCase
from app.modules.stories.usecases.update_written_story import UpdateWrittenStoryUseCase


def get_list_sprints(request: Request) -> ListSprintsUseCase:
    use_case: ListSprintsUseCase = request.app.state.container.list_sprints
    return use_case


def get_get_sprint(request: Request) -> GetSprintUseCase:
    use_case: GetSprintUseCase = request.app.state.container.get_sprint
    return use_case


def get_list_stories(request: Request) -> ListStoriesUseCase:
    use_case: ListStoriesUseCase = request.app.state.container.list_stories
    return use_case


def get_get_story(request: Request) -> GetStoryUseCase:
    use_case: GetStoryUseCase = request.app.state.container.get_story
    return use_case


def get_change_test_status(request: Request) -> ChangeTestStatusUseCase:
    use_case: ChangeTestStatusUseCase = request.app.state.container.change_test_status
    return use_case


def get_get_sync_status(request: Request) -> GetSyncStatusUseCase:
    use_case: GetSyncStatusUseCase = request.app.state.container.get_sync_status
    return use_case


def get_request_jira_sync(request: Request) -> RequestJiraSyncUseCase:
    use_case: RequestJiraSyncUseCase = request.app.state.container.request_jira_sync
    return use_case


def get_create_written_story(request: Request) -> CreateWrittenStoryUseCase:
    use_case: CreateWrittenStoryUseCase = request.app.state.container.create_written_story
    return use_case


def get_update_written_story(request: Request) -> UpdateWrittenStoryUseCase:
    use_case: UpdateWrittenStoryUseCase = request.app.state.container.update_written_story
    return use_case


def get_delete_written_story(request: Request) -> DeleteWrittenStoryUseCase:
    use_case: DeleteWrittenStoryUseCase = request.app.state.container.delete_written_story
    return use_case
