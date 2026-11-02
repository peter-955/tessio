from collections.abc import Iterable, Mapping


def count_expanded_steps(step_keys: Iterable[str | None], action_counts: Mapping[str, int]) -> int:
    return sum(1 if key is None else action_counts.get(key, 0) for key in step_keys)
