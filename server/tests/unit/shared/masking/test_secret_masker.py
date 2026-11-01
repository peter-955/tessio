from app.shared.masking import MASKED_VALUE, SecretMasker


def test_every_occurrence_of_every_secret_is_masked() -> None:
    masker = SecretMasker(["hunter2", "s3cr3t"])

    masked_text = masker.mask("login hunter2 then s3cr3t, again hunter2")

    assert masked_text == f"login {MASKED_VALUE} then {MASKED_VALUE}, again {MASKED_VALUE}"


def test_the_longest_secret_is_masked_first() -> None:
    masker = SecretMasker(["abc", "abcdef"])

    assert masker.mask("value=abcdef") == f"value={MASKED_VALUE}"


def test_regex_characters_in_secrets_are_matched_literally() -> None:
    masker = SecretMasker(["p.ss*(1)"])

    assert masker.mask("p.ss*(1) and pass11") == f"{MASKED_VALUE} and pass11"


def test_text_without_secrets_is_unchanged() -> None:
    masker = SecretMasker(["hunter2"])

    assert masker.mask("nothing to hide") == "nothing to hide"


def test_empty_secret_values_are_ignored() -> None:
    masker = SecretMasker(["", "hunter2"])

    assert masker.mask("a hunter2 b") == f"a {MASKED_VALUE} b"


def test_a_masker_without_secrets_returns_the_text() -> None:
    masker = SecretMasker([""])

    assert masker.mask("plain text") == "plain text"


def test_mask_optional_passes_none_through() -> None:
    masker = SecretMasker(["hunter2"])

    assert masker.mask_optional(None) is None
    assert masker.mask_optional("hunter2") == MASKED_VALUE
