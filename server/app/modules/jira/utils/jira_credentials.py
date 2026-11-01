from pydantic import SecretStr

from app.modules.jira.domains.jira_connection.entity import JiraConnection
from app.modules.jira.domains.jira_credentials.entity import JiraCredentials
from app.modules.jira.errors import JiraNotConfiguredError
from app.shared.crypto import InvalidCipherTextError, SecretCipher


def build_jira_credentials(connection: JiraConnection, secret_cipher: SecretCipher) -> JiraCredentials:
    try:
        api_token = secret_cipher.decrypt(connection.api_token_encrypted).decode()
    except (InvalidCipherTextError, UnicodeDecodeError) as error:
        raise JiraNotConfiguredError from error
    return JiraCredentials(
        site_url=connection.site_url, account_email=connection.account_email, api_token=SecretStr(api_token)
    )
