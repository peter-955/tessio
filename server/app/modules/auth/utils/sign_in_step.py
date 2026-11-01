from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.typing.enums import SignInStep


def resolve_sign_in_step(authenticated: AuthenticatedSession) -> SignInStep:
    if authenticated.user_session.is_two_factor_passed:
        return SignInStep.SIGNED_IN
    if authenticated.user.is_two_factor_set_up:
        return SignInStep.TWO_FACTOR_REQUIRED
    return SignInStep.TWO_FACTOR_SETUP_REQUIRED
