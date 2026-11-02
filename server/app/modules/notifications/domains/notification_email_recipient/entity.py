from app.modules.users import UserLanguage
from app.shared.common import Entity


class NotificationEmailRecipient(Entity):
    email: str
    name: str
    language: UserLanguage
    project_key: str
    project_name: str
