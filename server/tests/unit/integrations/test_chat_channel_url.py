import pytest

from app.modules.integrations.utils.chat_channel_url import build_chat_webhook_url_hint, is_allowed_chat_webhook_url

SLACK_URL = "https://hooks.slack.com/services/T0001/B0002/abcdEFGHijkl9876"
TEAMS_URL = (
    "https://prod-01.westeurope.logic.azure.com:443/workflows/0a1b2c/triggers/manual/paths/invoke"
    "?api-version=2016-06-01&sig=SeCrEtSiGnAtUrE"
)


@pytest.mark.parametrize(
    "url",
    [
        SLACK_URL,
        TEAMS_URL,
        "https://8.8.8.8/hook",
        "https://hooks.slack.com./services/T0001",
        "https://bücher.example/hook",
    ],
)
def test_public_https_urls_are_allowed(url: str) -> None:
    assert is_allowed_chat_webhook_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://hooks.slack.com/services/T0001/B0002/abcd",
        "ftp://hooks.slack.com/services",
        "https:///services",
        "https://localhost/hook",
        "https://chat.localhost/hook",
        "https://printer.local/hook",
        "https://intranet/hook",
        "https://wiki.corp.internal/hook",
        "https://127.0.0.1/hook",
        "https://10.0.0.8/hook",
        "https://172.16.4.2/hook",
        "https://192.168.1.10/hook",
        "https://169.254.169.254/latest/meta-data",
        "https://[::1]/hook",
        "https://[fd00::1]/hook",
        "https://224.0.0.1/hook",
        "https://0.0.0.0/hook",
        "https://127.1/hook",
        "https://127.0.1/hook",
        "https://0x7f.0.0.1/hook",
        "https://0x7F000001/hook",
        "https://2130706433/hook",
        "https://0177.0.0.1/hook",
        "https://10.1/hook",
        "https://192.168.257/hook",
        "https://8.8.8.010/hook",
        "https://hooks.example.123/hook",
        "https://127。0。0.1/hook",
        "https://[::ffff:127.0.0.1]/hook",
        "https://[::ffff:10.0.0.8]/hook",
        "https://user:secret@hooks.slack.com/services",
        "https://hooks.slack.com:99999/services",
        "https://hooks.slack.com/ser vices",
        "not a url",
    ],
)
def test_private_plain_or_malformed_urls_are_refused(url: str) -> None:
    assert not is_allowed_chat_webhook_url(url)


def test_the_hint_keeps_only_the_host_and_the_last_four_characters() -> None:
    assert build_chat_webhook_url_hint(SLACK_URL) == "https://hooks.slack.com/…9876"
    assert build_chat_webhook_url_hint(TEAMS_URL) == "https://prod-01.westeurope.logic.azure.com/…tUrE"


def test_the_hint_shows_no_characters_of_a_short_path() -> None:
    assert build_chat_webhook_url_hint("https://chat.example.com/abc") == "https://chat.example.com/…"
