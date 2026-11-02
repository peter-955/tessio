from app.shared.common import Entity


class CaseReferences(Entity):
    data_keys: frozenset[str]
    file_keys: frozenset[str]
    parameter_names: frozenset[str] = frozenset()
