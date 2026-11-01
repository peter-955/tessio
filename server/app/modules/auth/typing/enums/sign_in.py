from enum import StrEnum


class SignInStep(StrEnum):
    TWO_FACTOR_SETUP_REQUIRED = "two_factor_setup_required"
    TWO_FACTOR_REQUIRED = "two_factor_required"
    SIGNED_IN = "signed_in"
