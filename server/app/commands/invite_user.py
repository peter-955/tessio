import argparse
import asyncio

from app.config import get_settings
from app.container import Container
from app.modules.users import WorkspaceRole


async def invite_user(email: str, name: str, workspace_role: WorkspaceRole) -> None:
    container = Container(get_settings())
    try:
        await container.invite_user.execute(email, name, workspace_role)
    finally:
        await container.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Invite a user to the Tessio workspace by email.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", choices=[role.value for role in WorkspaceRole], default=WorkspaceRole.MEMBER.value)
    arguments = parser.parse_args()
    asyncio.run(invite_user(arguments.email, arguments.name, WorkspaceRole(arguments.role)))


if __name__ == "__main__":
    main()
