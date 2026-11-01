from app.shared.common import Entity


class JiraAccount(Entity):
    account_id: str
    display_name: str
    email_address: str | None
