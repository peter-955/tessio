import sys
from datetime import UTC, datetime
from uuid import uuid7

import pyotp
import pytest
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text

from app.commands import seed_e2e as seed_e2e_command
from app.commands.seed_e2e import is_e2e_database_url, seed_e2e
from app.config import Settings
from app.container import Container
from app.modules.projects.infrastructure import ProjectTable
from app.modules.users import UserStatus, WorkspaceRole
from tests.support.test_settings import build_test_settings

OWNER_EMAIL = "owner@tessio.e2e"
OWNER_NAME = "Olivia Owner"
OWNER_PASSWORD = "e2e owner password 2026"
OWNER_TOTP_KEY = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
RATE_LIMIT_KEY = "tessio:rate:sign_in:x"
OTHER_KEY = "other:key"
ROW_COUNT_PER_TABLE_QUERY = """
SELECT
    tablename,
    (
        xpath(
            '/row/count/text()',
            query_to_xml(format('SELECT count(*) FROM %I.%I', schemaname, tablename), false, true, '')
        )
    )[1]::text::integer
FROM pg_tables
WHERE schemaname = 'public' AND tablename <> 'alembic_version'
"""


async def seed_owner(container: Container, redis_url: str, email: str = OWNER_EMAIL) -> None:
    await seed_e2e(container, redis_url, email=email, name=OWNER_NAME, password=OWNER_PASSWORD, totp_key=OWNER_TOTP_KEY)


async def add_project(container: Container) -> None:
    async with container.database.begin():
        container.database.get_current_session().add(
            ProjectTable(
                id=uuid7(),
                key="SEED",
                name="Seed project",
                description=None,
                jira_project_key="SEED",
                jira_board_id=1,
                allowed_file_types=[],
                archived_at=None,
                created_at=datetime.now(UTC),
                default_environment_id=None,
            )
        )


async def count_rows_per_table(container: Container) -> dict[str, int]:
    async with container.database.begin():
        rows = (await container.database.get_current_session().execute(text(ROW_COUNT_PER_TABLE_QUERY))).all()
    return dict(rows)


def run_main(monkeypatch: pytest.MonkeyPatch, database_url: str, totp_key: str) -> None:
    settings = build_test_settings(database_url)

    def get_test_settings() -> Settings:
        return settings

    monkeypatch.setattr(seed_e2e_command, "get_settings", get_test_settings)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "seed_e2e",
            "--owner-email",
            OWNER_EMAIL,
            "--owner-name",
            OWNER_NAME,
            "--owner-password",
            OWNER_PASSWORD,
            "--owner-totp-key",
            totp_key,
        ],
    )
    seed_e2e_command.main()


@pytest.mark.parametrize(
    ("database_url", "is_e2e"),
    [
        ("postgresql+asyncpg://tessio:tessio@localhost:5432/tessio", False),
        ("postgresql+asyncpg://tessio:tessio@localhost:5432/tessio_e2e", True),
        ("postgresql+asyncpg://tessio:tessio@localhost:5432/e2e_tessio", False),
    ],
)
def test_only_database_names_ending_with_e2e_are_e2e_databases(database_url: str, is_e2e: bool) -> None:
    assert is_e2e_database_url(database_url) is is_e2e


def test_main_refuses_a_database_that_is_not_an_e2e_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as exit_information:
        run_main(monkeypatch, "postgresql+asyncpg://tessio:tessio@localhost:5432/tessio", OWNER_TOTP_KEY)

    assert exit_information.value.code == 2
    assert "Refusing to seed: the database name must end with _e2e." in capsys.readouterr().err


def test_main_refuses_a_totp_key_that_is_not_base32(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit) as exit_information:
        run_main(monkeypatch, "postgresql+asyncpg://tessio:tessio@localhost:5432/tessio_e2e", "not base32 !")

    assert exit_information.value.code == 2


async def test_seeded_owner_signs_in_with_password_and_totp(
    seed_container: Container, seed_client: AsyncClient, redis_url: str
) -> None:
    await seed_owner(seed_container, redis_url, email="  Owner@Tessio.E2E ")

    sign_in_response = await seed_client.post(
        "/api/auth/sign-in", json={"email": OWNER_EMAIL, "password": OWNER_PASSWORD}
    )
    two_factor_response = await seed_client.post(
        "/api/auth/two-factor", json={"code": pyotp.TOTP(OWNER_TOTP_KEY).now()}
    )
    me_response = await seed_client.get("/api/auth/me")

    assert sign_in_response.json() == {"nextStep": "two_factor_required"}
    assert two_factor_response.status_code == 200
    assert me_response.json()["email"] == OWNER_EMAIL
    assert me_response.json()["workspaceRole"] == WorkspaceRole.OWNER.value
    async with seed_container.database.begin():
        owner = await seed_container.user_repository.find_by_email(OWNER_EMAIL)
    assert owner is not None
    assert owner.status is UserStatus.ACTIVE
    assert owner.totp_confirmed_at is not None


async def test_seeding_twice_wipes_earlier_rows_and_keeps_one_user(seed_container: Container, redis_url: str) -> None:
    await seed_owner(seed_container, redis_url)
    await seed_container.invite_user.execute("quinn.qc@tessio.e2e", "Quinn Tester", WorkspaceRole.MEMBER)
    await add_project(seed_container)
    rows_before = await count_rows_per_table(seed_container)
    assert rows_before["users"] == 2
    assert rows_before["one_time_tokens"] == 1
    assert rows_before["projects"] == 1

    await seed_owner(seed_container, redis_url)

    rows_after = await count_rows_per_table(seed_container)
    assert "projects" in rows_after
    assert {table_name: row_count for table_name, row_count in rows_after.items() if row_count > 0} == {"users": 1}
    async with seed_container.database.begin():
        invited_user = await seed_container.user_repository.find_by_email("quinn.qc@tessio.e2e")
        owner = await seed_container.user_repository.find_by_email(OWNER_EMAIL)
    assert invited_user is None
    assert owner is not None


async def test_seed_deletes_rate_limit_keys_and_keeps_other_keys(seed_container: Container, redis_url: str) -> None:
    redis = Redis.from_url(redis_url)
    try:
        await redis.set(RATE_LIMIT_KEY, "5")
        await redis.set(OTHER_KEY, "kept")

        await seed_owner(seed_container, redis_url)

        assert await redis.exists(RATE_LIMIT_KEY) == 0
        assert await redis.get(OTHER_KEY) == b"kept"
    finally:
        await redis.delete(OTHER_KEY)
        await redis.aclose()
