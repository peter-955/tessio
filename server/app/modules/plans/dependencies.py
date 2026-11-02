from fastapi import Request

from app.modules.plans.usecases.close_plan import ClosePlanUseCase
from app.modules.plans.usecases.create_plan import CreatePlanUseCase
from app.modules.plans.usecases.get_plan import GetPlanUseCase
from app.modules.plans.usecases.list_plans import ListPlansUseCase
from app.modules.plans.usecases.set_plan_items import SetPlanItemsUseCase
from app.modules.plans.usecases.sign_off_plan import SignOffPlanUseCase
from app.modules.plans.usecases.update_plan import UpdatePlanUseCase


def get_list_plans(request: Request) -> ListPlansUseCase:
    use_case: ListPlansUseCase = request.app.state.container.list_plans
    return use_case


def get_create_plan(request: Request) -> CreatePlanUseCase:
    use_case: CreatePlanUseCase = request.app.state.container.create_plan
    return use_case


def get_get_plan(request: Request) -> GetPlanUseCase:
    use_case: GetPlanUseCase = request.app.state.container.get_plan
    return use_case


def get_update_plan(request: Request) -> UpdatePlanUseCase:
    use_case: UpdatePlanUseCase = request.app.state.container.update_plan
    return use_case


def get_set_plan_items(request: Request) -> SetPlanItemsUseCase:
    use_case: SetPlanItemsUseCase = request.app.state.container.set_plan_items
    return use_case


def get_sign_off_plan(request: Request) -> SignOffPlanUseCase:
    use_case: SignOffPlanUseCase = request.app.state.container.sign_off_plan
    return use_case


def get_close_plan(request: Request) -> ClosePlanUseCase:
    use_case: ClosePlanUseCase = request.app.state.container.close_plan
    return use_case
