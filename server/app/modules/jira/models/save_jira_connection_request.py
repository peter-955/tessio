from typing import Annotated

from pydantic import EmailStr, StringConstraints

from app.shared.common import WireModel


class SaveJiraConnectionRequest(WireModel):
    site_url: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    account_email: EmailStr
    api_token: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)] | None = None
