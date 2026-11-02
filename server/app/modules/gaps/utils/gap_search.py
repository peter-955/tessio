import re

from app.modules.gaps.typing.constants import (
    MAX_SEARCH_TERMS,
    MIN_SEARCH_TERM_LENGTH,
    SEARCH_STOP_WORDS,
    SEARCH_TERM_PATTERN,
)


def build_search_terms(question: str) -> list[str]:
    terms: list[str] = []
    for word in re.findall(SEARCH_TERM_PATTERN, question.casefold()):
        term = word.strip("_")
        if len(term) < MIN_SEARCH_TERM_LENGTH or term in SEARCH_STOP_WORDS or term in terms:
            continue
        terms.append(term)
        if len(terms) == MAX_SEARCH_TERMS:
            break
    return terms
