import pytest

from app.modules.gaps.utils.test_data_url import build_test_data_url


@pytest.mark.parametrize("client_url", ["https://tessio.example.com", "https://tessio.example.com/"])
def test_the_test_data_url_points_at_the_projects_test_data_page(client_url: str) -> None:
    assert build_test_data_url(client_url, "SHOP") == "https://tessio.example.com/projects/SHOP/test-data"
