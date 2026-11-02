from app.modules.gaps.utils.gap_search import build_search_terms


def test_search_terms_drop_short_and_common_words_and_repeats() -> None:
    assert build_search_terms("Which currencies does the checkout accept? Checkout, or REFUNDS?") == [
        "currencies",
        "checkout",
        "accept",
        "refunds",
    ]


def test_search_terms_keep_words_of_any_language() -> None:
    assert build_search_terms("Phương thức thanh toán nào?") == ["phương", "thức", "thanh", "toán", "nào"]


def test_a_question_of_common_words_only_has_no_terms() -> None:
    assert build_search_terms("What is it?") == []


def test_search_terms_are_capped_at_twenty() -> None:
    terms = build_search_terms(" ".join(f"word{index}" for index in range(30)))

    assert terms == [f"word{index}" for index in range(20)]
