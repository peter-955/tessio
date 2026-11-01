from typing import Annotated

from pydantic import StringConstraints

from app.modules.auth.typing.constants.user_management import MAX_USER_NAME_LENGTH

UserName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_USER_NAME_LENGTH)]
