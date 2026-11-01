import argparse
import asyncio
import base64
import sys
from datetime import UTC, datetime
from uuid import uuid7

from redis.asyncio import Redis
from sqlalchemy import make_url, text

from app.config import Settings, get_settings
from app.container import Container
from app.modules.users import User, UserStatus, WorkspaceRole
from app.shared.rate_limit import RATE_LIMIT_KEY_PREFIX

E2E_DATABASE_SUFFIX = "_e2e"
INVALID_INPUT_EXIT_CODE = 2
REFUSED_DATABASE_MESSAGE = "Refusing to seed: the database name must end with _e2e.\n"
INVALID_TOTP_KEY_MESSAGE = "Refusing to seed: the TOTP key must be base32.\n"
TRUNCATE_ALL_TABLES_STATEMENT = """
DO $$
DECLARE
    table_names text;
BEGIN
    SELECT string_agg(format('%I.%I', schemaname, tablename), ', ')
    INTO table_names
    FROM pg_tables
    WHERE schemaname = 'public' AND tablename <> 'alembic_version';
    IF table_names IS NOT NULL THEN
        EXECUTE 'TRUNCATE TABLE ' || table_names || ' RESTART IDENTITY CASCADE';
    END IF;
END
$$;
"""


def is_e2e_database_url(database_url: str) -> bool:
    database_name = make_url(database_url).database
    return database_name is not None and database_name.endswith(E2E_DATABASE_SUFFIX)


def is_base32_key(totp_key: str) -> bool:
    try:
        base64.b32decode(totp_key, casefold=True)
    except ValueError:
        return False
    return True


async def delete_rate_limit_keys(redis_url: str) -> None:
    redis = Redis.from_url(redis_url)
    try:
        async for key in redis.scan_iter(match=f"{RATE_LIMIT_KEY_PREFIX}:*"):
            await redis.delete(key)
    finally:
        await redis.aclose()


async def seed_e2e(
    container: Container, redis_url: str, *, email: str, name: str, password: str, totp_key: str
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(text(TRUNCATE_ALL_TABLES_STATEMENT))
    password_hash = await container.password_hasher.hash_password(password)
    now = datetime.now(UTC)
    async with container.database.begin():
        await container.user_repository.add(
            User(
                id=uuid7(),
                email=email.strip().lower(),
                name=name,
                workspace_role=WorkspaceRole.OWNER,
                status=UserStatus.ACTIVE,
                password_hash=password_hash,
                totp_key_encrypted=container.secret_cipher.encrypt(totp_key.encode()),
                totp_confirmed_at=now,
                totp_last_time_step=None,
                failed_sign_ins=0,
                locked_until=None,
                created_at=now,
            )
        )
    await delete_rate_limit_keys(redis_url)


async def run_seed(settings: Settings, arguments: argparse.Namespace) -> None:
    container = Container(settings)
    try:
        await seed_e2e(
            container,
            settings.queue.redis_url,
            email=arguments.owner_email,
            name=arguments.owner_name,
            password=arguments.owner_password,
            totp_key=arguments.owner_totp_key,
        )
    finally:
        await container.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset an e2e database and seed its workspace owner.")
    parser.add_argument("--owner-email", required=True)
    parser.add_argument("--owner-name", required=True)
    parser.add_argument("--owner-password", required=True)
    parser.add_argument("--owner-totp-key", required=True)
    arguments = parser.parse_args()
    settings = get_settings()
    if not is_e2e_database_url(settings.database.database_url):
        sys.stderr.write(REFUSED_DATABASE_MESSAGE)
        raise SystemExit(INVALID_INPUT_EXIT_CODE)
    if not is_base32_key(arguments.owner_totp_key):
        sys.stderr.write(INVALID_TOTP_KEY_MESSAGE)
        raise SystemExit(INVALID_INPUT_EXIT_CODE)
    asyncio.run(run_seed(settings, arguments))
    sys.stdout.write(f"Seeded e2e owner {arguments.owner_email.strip().lower()}\n")


if __name__ == "__main__":
    main()
