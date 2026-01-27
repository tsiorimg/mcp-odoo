import pytest

from mcp_odoo.core.factory import ConnectorFactory


@pytest.mark.integration
def test_detection_matches_expected_versions(odoo_urls):
    for key, url in odoo_urls.items():
        connector = ConnectorFactory.create(url=url, database="mcp_test", api_key="admin", version=None)
        version = connector.version()
        if "19" in key:
            assert version >= 19.0
        else:
            assert version < 19.0
