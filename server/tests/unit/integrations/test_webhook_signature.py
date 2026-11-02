import hashlib
import hmac

from app.modules.integrations.utils.webhook_signature import is_valid_webhook_signature, sign_webhook_body


def test_the_signature_is_an_hmac_sha256_of_the_timestamp_and_the_body() -> None:
    body = b'{"event":"run.finished"}'

    signature = sign_webhook_body("whsec_secret", 1_762_000_000, body)

    expected = hmac.new(b"whsec_secret", b'1762000000.{"event":"run.finished"}', hashlib.sha256).hexdigest()
    assert signature == f"sha256={expected}"


def test_a_changed_body_timestamp_or_secret_does_not_verify() -> None:
    body = b'{"event":"run.finished"}'
    signature = sign_webhook_body("whsec_secret", 1_762_000_000, body)

    assert is_valid_webhook_signature("whsec_secret", 1_762_000_000, body, signature)
    assert not is_valid_webhook_signature("whsec_secret", 1_762_000_000, b'{"event":"run.started"}', signature)
    assert not is_valid_webhook_signature("whsec_secret", 1_762_000_001, body, signature)
    assert not is_valid_webhook_signature("whsec_other", 1_762_000_000, body, signature)
