import hmac
from datetime import datetime

import pyotp

from app.modules.auth.ports.totp_authenticator import TotpAuthenticator
from app.modules.auth.typing.constants.auth_policy import TOTP_ISSUER


class PyotpTotpAuthenticator(TotpAuthenticator):
    def generate_key(self) -> str:
        return pyotp.random_base32()

    def build_setup_uri(self, key: str, account_name: str) -> str:
        return pyotp.TOTP(key).provisioning_uri(name=account_name, issuer_name=TOTP_ISSUER)

    def find_time_step(self, key: str, code: str, now: datetime) -> int | None:
        totp = pyotp.TOTP(key)
        current_time_step = totp.timecode(now)
        for time_step in (current_time_step - 1, current_time_step, current_time_step + 1):
            if hmac.compare_digest(totp.generate_otp(time_step), code.strip()):
                return time_step
        return None
