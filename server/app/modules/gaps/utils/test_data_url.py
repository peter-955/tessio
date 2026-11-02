from app.modules.gaps.typing.constants import TEST_DATA_PAGE_PATH


def build_test_data_url(client_url: str, project_key: str) -> str:
    return f"{client_url.rstrip('/')}{TEST_DATA_PAGE_PATH.format(project_key=project_key)}"
