import pytest

from app.modules.integrations.utils.webhook_url import is_allowed_webhook_url


@pytest.mark.parametrize(
    "url",
    [
        "https://hooks.example.com/tessio",
        "https://ci.example.org:8443/hooks?token=abc",
        "https://8.8.8.8/hook",
    ],
)
def test_public_https_urls_are_allowed(url: str) -> None:
    assert is_allowed_webhook_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://hooks.example.com/tessio",
        "https://localhost/hook",
        "https://api.localhost/hook",
        "https://printer.local/hook",
        "https://service.internal/hook",
        "https://127.0.0.1/hook",
        "https://10.0.0.5/hook",
        "https://192.168.1.10/hook",
        "https://169.254.169.254/latest/meta-data",
        "https://[::1]/hook",
        "https://[::ffff:10.0.0.1]/hook",
        "https://user:pass@hooks.example.com/hook",
        "https:///no-host",
        "https://intranet/hook",
        "https://hooks.example.com/with space",
        "ftp://hooks.example.com/hook",
    ],
)
def test_private_or_malformed_urls_are_refused(url: str) -> None:
    assert not is_allowed_webhook_url(url)
