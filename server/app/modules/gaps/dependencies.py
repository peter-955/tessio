from fastapi import Request

from app.modules.gaps.usecases.answer_gap import AnswerGapUseCase
from app.modules.gaps.usecases.get_gap import GetGapUseCase
from app.modules.gaps.usecases.list_gap_inbox import ListGapInboxUseCase
from app.modules.gaps.usecases.list_gaps import ListGapsUseCase
from app.modules.gaps.usecases.raise_gaps import RaiseGapsUseCase
from app.modules.gaps.usecases.reassign_gap import ReassignGapUseCase
from app.modules.gaps.usecases.reopen_gap import ReopenGapUseCase


def get_list_gaps(request: Request) -> ListGapsUseCase:
    use_case: ListGapsUseCase = request.app.state.container.list_gaps
    return use_case


def get_raise_gaps(request: Request) -> RaiseGapsUseCase:
    use_case: RaiseGapsUseCase = request.app.state.container.raise_gaps
    return use_case


def get_get_gap(request: Request) -> GetGapUseCase:
    use_case: GetGapUseCase = request.app.state.container.get_gap
    return use_case


def get_answer_gap(request: Request) -> AnswerGapUseCase:
    use_case: AnswerGapUseCase = request.app.state.container.answer_gap
    return use_case


def get_reopen_gap(request: Request) -> ReopenGapUseCase:
    use_case: ReopenGapUseCase = request.app.state.container.reopen_gap
    return use_case


def get_reassign_gap(request: Request) -> ReassignGapUseCase:
    use_case: ReassignGapUseCase = request.app.state.container.reassign_gap
    return use_case


def get_list_gap_inbox(request: Request) -> ListGapInboxUseCase:
    use_case: ListGapInboxUseCase = request.app.state.container.list_gap_inbox
    return use_case
