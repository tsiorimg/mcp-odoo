import os
import pytest

from mcp_odoo.core.factory import MCPOdoo
from mcp_odoo.connectors.json2 import JSON2Connector
from mcp_odoo.connectors.xmlrpc import XMLRPCConnector


@pytest.mark.integration
def test_partner_crud_xmlrpc(odoo_urls):
    creds = {
        "odoo_14": os.getenv("ODOO14_PASSWORD", "admin"),
        "odoo_17": os.getenv("ODOO17_PASSWORD", "admin"),
    }
    for key in ("odoo_14", "odoo_17"):
        if key not in odoo_urls:
            continue
        url = odoo_urls[key]
        api_key = creds.get(key, "admin")
        version_override = 14.0 if key == "odoo_14" else 17.0
        mcp = MCPOdoo(url=url, database="mcp_test", api_key=api_key, user="admin", version=version_override)
        assert isinstance(mcp.connector, XMLRPCConnector)
        pid = mcp.create("res.partner", {"name": f"Test {key}"})
        rec = mcp.read("res.partner", [pid], ["name"])[0]
        assert rec["name"].startswith("Test")
        mcp.unlink("res.partner", [pid])
        assert mcp.search("res.partner", [("id", "=", pid)]) == []


@pytest.mark.integration
def test_partner_crud_json2(odoo_urls):
    if "odoo_19" not in odoo_urls:
        pytest.skip("Odoo 19 non disponible")
    api_key = os.getenv("ODOO19_API_KEY")
    if not api_key:
        pytest.skip("Set ODOO19_API_KEY pour tester JSON-2")
    url = odoo_urls["odoo_19"]
    mcp = MCPOdoo(url=url, database="mcp_test", api_key=api_key, user="admin")
    assert isinstance(mcp.connector, JSON2Connector)
    pid = mcp.create("res.partner", {"name": "Test 19"})
    rec = mcp.read("res.partner", [pid], ["name"])[0]
    assert rec["name"] == "Test 19"
    mcp.unlink("res.partner", [pid])
    assert mcp.search("res.partner", [("id", "=", pid)]) == []
